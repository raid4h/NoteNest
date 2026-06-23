from database.db import get_connection

def create_notes(notebook_id, title, content, category_id=None, is_pinned=0, is_archived=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO notes (notebook_id, title, content, category_id, is_pinned, is_archived)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (notebook_id, title, content, category_id, is_pinned, is_archived))
    conn.commit()
    conn.close()
def get_all_notes(notebook_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute('''
    SELECT * FROM notes
    WHERE notebook_id = ?
    ORDER BY is_pinned DESC, updated_at DESC
    ''', (notebook_id,))
    notes=cursor.fetchall()
    conn.close()
    return notes
def get_notes_by_id(note_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute('''
    SELECT * FROM notes
    WHERE id=?               
    ''',(note_id,))
    note=cursor.fetchone()
    conn.close()
    return note
def update_notes(note_id,title,content):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute('''
    UPDATE notes SET title=?, content=?, updated_at=CURRENT_TIMESTAMP
    WHERE id=?               
    ''',(title,content,note_id))
    conn.commit()
    conn.close()
def delete_notes(note_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute('''
    DELETE FROM notes 
    WHERE id=?               
    ''',(note_id,))
    conn.commit()
    conn.close()
def search_notes(keyword):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute('''
    SELECT * FROM notes
    WHERE title LIKE ? OR content LIKE ?              
    ''',(f'%{keyword}%', f'%{keyword}%'))
    results=cursor.fetchall()
    conn.close()
    return results
def pin_notes(note_id,is_pinned):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute('''
    UPDATE notes SET is_pinned=?
    WHERE id=?
    ''',(is_pinned,note_id))
    conn.commit()
    conn.close()
def archive_notes(note_id,is_archived):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute('''
    UPDATE notes SET is_archived=?
    WHERE id=?
    ''',(is_archived,note_id))
    conn.commit()
    conn.close()
def sort_notes(notebook_id,sort_by="date"):
    if sort_by=="title":
      order_clause="title ASC"
    else:
      order_clause="updated_at DESC"
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(f'''
      SELECT * FROM notes
      WHERE notebook_id=?
      ORDER BY {order_clause}
      ''',(notebook_id,))
    notes=cursor.fetchall()
    conn.close()
    return notes
    
def duplicate_notes(note_id):
    og_note=get_notes_by_id(note_id)
    notebook_id=og_note[1]
    title=og_note[2]
    content=og_note[3]
    category_id = og_note[8]
    
    create_notes(notebook_id,title,content,category_id=category_id)
    
    
