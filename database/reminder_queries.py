from database.db import get_connection

def create_reminder(task_id,remind_at):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reminders(task_id,remind_at)
        VALUES(?,?)
    ''',(task_id,remind_at))
    conn.commit()
    conn.close()
def get_reminders_by_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM reminders
        WHERE task_id=?
    ''',(task_id,))
    reminders=cursor.fetchall()
    conn.close()
    return reminders
def get_active_reminders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM reminders
        WHERE is_active=1
        ORDER BY remind_at ASC
    ''')
    reminders=cursor.fetchall()
    conn.close()
    return reminders
def get_due_reminders():     #upcoming active reminders
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM reminders
        WHERE is_active=1
        and remind_at>=CURRENT_TIMESTAMP
        ORDER BY remind_at ASC
    ''')
    reminders=cursor.fetchall()
    conn.close()
    return reminders
def get_triggered_reminders():   #call this to fire notification
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM reminders
        WHERE is_active=1
        and remind_at<=CURRENT_TIMESTAMP
        ORDER BY remind_at ASC
    ''')
    reminders=cursor.fetchall()
    conn.close()
    return reminders
def deactivate_reminders(reminder_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE reminders SET is_active=0
        WHERE id=?
    ''',(reminder_id,))
    conn.commit()
    conn.close()
def update_reminders(reminder_id,remind_at):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE reminders SET remind_at=?, is_active=1
        WHERE id=?
    ''',(remind_at,reminder_id))
    conn.commit()
    conn.close()
def delete_reminder(reminder_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM reminders
        WHERE id=?
    ''',(reminder_id,))
    conn.commit()
    conn.close()    