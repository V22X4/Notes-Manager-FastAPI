from pydantic import BaseModel, Field
from typing import List, Optional


class User(BaseModel):
    username: str
    password: str
    shared_notes: List[str] = []

class NoteInDB(BaseModel):
    id: str = Field(..., alias="_id")
    title: str
    content: str
    owner: str
    created_at: str
    shared_with: List[str]

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    

