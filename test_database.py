from database.db import create_tables
from database.notes_queries import create_notes, get_all_notes, search_notes
from database.task_queries import create_tasks, get_all_tasks, complete_tasks
from database.category_queries import create_category, get_all_categories

#setup - Create Tables
create_tables()
print("✅ Tables created")

# Test creating notes
create_notes(1, "Physics Chapter 1", "Newton's laws")
create_notes(1, "Math Notes", "Calculus formulas")
notes = get_all_notes(1)
print(f"✅ Notes created: {len(notes)} notes found")