from database.db import get_connection
from datetime import datetime

def create_pomodoro_session(task_id, duration):
    conn = get_connection()
    cursor = conn.cursor()
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO pomodoro_sessions(task_id, started_at, completed, duration)
        VALUES(?,?,0,?)
    ''', (task_id, started_at, duration))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def complete_pomodoro_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE pomodoro_sessions SET completed=1
        WHERE id=?
    ''', (session_id,))
    conn.commit()
    conn.close()

def get_sessions_by_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM pomodoro_sessions
        WHERE task_id=?
        ORDER BY started_at DESC
    ''', (task_id,))
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_completed_count_by_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM pomodoro_sessions
        WHERE task_id=? AND completed=1
    ''', (task_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_last_incomplete_session(task_id):
    # used by "Continue Studying" - finds a session the user started but didn't finish
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM pomodoro_sessions
        WHERE task_id=? AND completed=0
        ORDER BY started_at DESC
        LIMIT 1
    ''', (task_id,))
    session = cursor.fetchone()
    conn.close()
    return session

def get_most_recent_incomplete_session(user_id):
    # powers the Home screen "Continue Studying" card - across ALL of the user's tasks
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pomodoro_sessions.*, tasks.title, tasks.id as task_id
        FROM pomodoro_sessions
        JOIN tasks ON pomodoro_sessions.task_id = tasks.id
        WHERE tasks.user_id=? AND pomodoro_sessions.completed=0
        ORDER BY pomodoro_sessions.started_at DESC
        LIMIT 1
    ''', (user_id,))
    session = cursor.fetchone()
    conn.close()
    return session

def delete_pomodoro_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM pomodoro_sessions
        WHERE id=?
    ''', (session_id,))
    conn.commit()
    conn.close()