from database.db import get_connection

def create_attachment(note_id,file_path):
   conn=get_connection()
   cursor=conn.cursor()  
   cursor.execute('''
      INSERT INTO attachments(note_id,file_path)
      VALUES(?,?)       
    ''',(note_id,file_path))
   conn.commit()
   conn.close()
def get_all_attachments(note_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute('''
    SELECT * FROM attachments
    WHERE note_id = ?
    ''', (note_id,))
    attachments=cursor.fetchall()
    conn.close()
    return attachments
def delete_attachment(attachment_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute('''
    DELETE FROM attachments 
    WHERE id=?               
    ''',(attachment_id,))
    conn.commit()
    conn.close()