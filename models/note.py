class Note:
    def __init__(self, id, notebook_id, title, content, is_pinned, is_archived,
                 created_at, updated_at, category_id, task_id=None):
        self.id = id
        self.notebook_id = notebook_id
        self.title = title
        self.content = content
        self.is_pinned = is_pinned
        self.is_archived = is_archived
        self.created_at = created_at
        self.updated_at = updated_at
        self.category_id = category_id
        self.task_id = task_id

    @classmethod
    def from_row(cls, row):
        """
        Builds a Note from a raw sqlite row, in the exact column order
        notes is created in db.py:
        id, notebook_id, title, content, is_pinned, is_archived,
        created_at, updated_at, category_id, task_id
        """
        if row is None:
            return None
        return cls(
            id=row[0], notebook_id=row[1], title=row[2], content=row[3],
            is_pinned=row[4], is_archived=row[5], created_at=row[6],
            updated_at=row[7], category_id=row[8],
            task_id=row[9] if len(row) > 9 else None,
        )