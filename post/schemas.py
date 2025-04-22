from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CreateHashtags(BaseModel):
    id: int
    content: str
    
    
class CreatePost(BaseModel):
    content: Optional[str] = None
    images : Optional[str] = None  
    publish: bool = False
    
class Post(CreatePost):
    id: int
    author_id : int
    username: str
    likes_count: int 
    created_at: datetime
    
    class Config:
        from_attributes: True