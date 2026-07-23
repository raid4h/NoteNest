# services/drive_client.py
#
# Thin wrapper around Google Drive API v3, scoped ONLY to the
# appDataFolder space -- this app's own hidden, per-account folder,
# invisible in the user's normal Drive UI and reachable only by this
# app's own credentials. No other file in the project should import
# `requests` and talk to Drive directly -- this is the one place that
# knows the actual Drive API shape.
#
# Every function here calls auth_service.get_valid_access_token()
# itself, so callers never handle raw tokens directly.

import requests

from services.auth_service import auth_service, AuthError

DRIVE_FILES_ENDPOINT = "https://www.googleapis.com/drive/v3/files"
DRIVE_UPLOAD_ENDPOINT = "https://www.googleapis.com/upload/drive/v3/files"

# A short retry budget for transient, server-side failures only --
# see _request_with_retry for why 4xx errors are deliberately NOT
# retried the same way.
MAX_RETRIES = 2


class DriveError(Exception):
    """Raised for any Drive API failure the caller should be told about."""


def _auth_headers():
    try:
        token = auth_service.get_valid_access_token()
    except AuthError as exc:
        raise DriveError(f"Not connected to Google: {exc}")
    return {"Authorization": f"Bearer {token}"}


def _request_with_retry(method, url, **kwargs):
    last_exception = None
    for _ in range(MAX_RETRIES + 1):
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            if response.status_code >= 500:
                # Server-side problem -- likely transient, worth
                # retrying. A 4xx (bad request, expired token, wrong
                # scope) would fail identically on retry, so those are
                # returned immediately instead of wasting attempts.
                last_exception = DriveError(f"Drive returned {response.status_code}: {response.text}")
                continue
            return response
        except requests.RequestException as exc:
            last_exception = DriveError(f"Network error talking to Drive: {exc}")
    raise last_exception


def upload_new_file(local_path, drive_filename):
    """
    Uploads a NEW file into this app's hidden appDataFolder using
    Drive's resumable upload protocol. Returns the new file's Drive
    file ID.
    """
    headers = _auth_headers()

    metadata = {"name": drive_filename, "parents": ["appDataFolder"]}
    init_response = _request_with_retry(
        "POST",
        f"{DRIVE_UPLOAD_ENDPOINT}?uploadType=resumable",
        headers={**headers, "Content-Type": "application/json; charset=UTF-8"},
        json=metadata,
    )
    if init_response.status_code != 200:
        raise DriveError(f"Could not start upload: {init_response.status_code} {init_response.text}")

    upload_session_url = init_response.headers.get("Location")
    if not upload_session_url:
        raise DriveError("Drive did not return an upload session URL.")

    with open(local_path, "rb") as f:
        file_bytes = f.read()

    upload_response = _request_with_retry("PUT", upload_session_url, data=file_bytes)
    if upload_response.status_code not in (200, 201):
        raise DriveError(f"Upload failed: {upload_response.status_code} {upload_response.text}")

    return upload_response.json()["id"]


def update_existing_file(file_id, local_path):
    """
    Overwrites an existing Drive file's CONTENT with a new local
    file's bytes, keeping the same file ID/name. Same resumable
    handshake as upload_new_file, but a PATCH against an existing
    file id instead of a POST that creates a new one.
    """
    headers = _auth_headers()

    init_response = _request_with_retry(
        "PATCH",
        f"{DRIVE_UPLOAD_ENDPOINT}/{file_id}?uploadType=resumable",
        headers={**headers, "Content-Type": "application/json; charset=UTF-8"},
        json={},
    )
    if init_response.status_code != 200:
        raise DriveError(f"Could not start update: {init_response.status_code} {init_response.text}")

    upload_session_url = init_response.headers.get("Location")
    if not upload_session_url:
        raise DriveError("Drive did not return an upload session URL.")

    with open(local_path, "rb") as f:
        file_bytes = f.read()

    upload_response = _request_with_retry("PUT", upload_session_url, data=file_bytes)
    if upload_response.status_code not in (200, 201):
        raise DriveError(f"Update failed: {upload_response.status_code} {upload_response.text}")

    return upload_response.json()["id"]


def list_appdata_files():
    """
    Returns a list of dicts (id, name, createdTime, size) for every
    file currently in this app's hidden appDataFolder. Used by
    backup_manager (Phase 6) to discover existing backups -- e.g. to
    find the latest one, or enforce a retention limit.
    """
    headers = _auth_headers()
    params = {
        "spaces": "appDataFolder",
        "fields": "files(id, name, createdTime, size)",
        "orderBy": "createdTime desc",
        "pageSize": 100,
    }
    response = _request_with_retry("GET", DRIVE_FILES_ENDPOINT, headers=headers, params=params)
    if response.status_code != 200:
        raise DriveError(f"Could not list files: {response.status_code} {response.text}")
    return response.json().get("files", [])


def download_file(file_id, destination_path):
    """
    Downloads a file's raw content by its Drive file ID, streaming it
    to destination_path in chunks rather than loading it all into
    memory at once -- attachment files could be larger than the small
    JSON manifests.
    """
    headers = _auth_headers()
    response = _request_with_retry(
        "GET", f"{DRIVE_FILES_ENDPOINT}/{file_id}", headers=headers,
        params={"alt": "media"}, stream=True,
    )
    if response.status_code != 200:
        raise DriveError(f"Download failed: {response.status_code} {response.text}")

    with open(destination_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=65536):
            f.write(chunk)


def delete_file(file_id):
    """Permanently deletes one file from the appDataFolder by its ID."""
    headers = _auth_headers()
    response = _request_with_retry("DELETE", f"{DRIVE_FILES_ENDPOINT}/{file_id}", headers=headers)
    if response.status_code not in (200, 204):
        raise DriveError(f"Delete failed: {response.status_code} {response.text}")