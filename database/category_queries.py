from database.db import get_connection


def create_category(name, color, user_id):
    """Create a category and return its id.

    Category names are unique per user case-insensitively. Returning the
    existing id keeps older callers compatible while preventing duplicates.
    """
    cleaned_name = (name or "").strip()
    if not cleaned_name:
        raise ValueError("Category name cannot be empty.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id
        FROM categories
        WHERE user_id = ?
          AND LOWER(TRIM(name)) = LOWER(?)
        LIMIT 1
        """,
        (user_id, cleaned_name),
    )
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing[0]

    cursor.execute(
        """
        INSERT INTO categories(name, color, user_id)
        VALUES(?, ?, ?)
        """,
        (cleaned_name, color, user_id),
    )
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    return category_id


def get_all_categories(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT *
        FROM categories
        WHERE user_id = ?
        ORDER BY LOWER(name), id
        """,
        (user_id,),
    )
    categories = cursor.fetchall()
    conn.close()
    return categories


def get_categories_by_id(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT *
        FROM categories
        WHERE id = ?
        """,
        (category_id,),
    )
    category = cursor.fetchone()
    conn.close()
    return category


def update_categories(category_id, name, color):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE categories
        SET name = ?, color = ?
        WHERE id = ?
        """,
        ((name or "").strip(), color, category_id),
    )
    conn.commit()
    conn.close()


def delete_categories(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM categories
        WHERE id = ?
        """,
        (category_id,),
    )
    conn.commit()
    conn.close()


def assign_categories_to_notes(note_id, category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE notes
        SET category_id = ?
        WHERE id = ?
        """,
        (category_id, note_id),
    )
    conn.commit()
    conn.close()
