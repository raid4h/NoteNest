class Note:
    def __init__(self,id,notebook_id,title,content,is_pinned,is_archived,created_at,updated_at,category_id):
        self.id=id
        self.notebook_id=notebook_id
        self.title=title
        self.content=content
        self.is_pinned=is_pinned
        self.is_archived=is_archived
        self.created_at=created_at
        self.updated_at=updated_at
        self.category_id=category_id
        