from fastapi import FastAPI, Depends, HTTPException, Query, Request, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bson import ObjectId
import json
import datetime
from typing import List, Optional
from models import NoteInDB, NoteCreate, NoteUpdate, User
from database import notes_collection, users_collection
from authentication import authenticate_user, create_access_token, get_current_user, get_password_hash

app = FastAPI()

def seriallize_note(note):
    note["_id"] = str(note["_id"])
    
    if "created_at" in note:
            if isinstance(note["created_at"], datetime.datetime):
                note["created_at"] = note["created_at"].strftime("%Y-%m-%d %H:%M:%S")
    return note


def get_token_from_request(req: Request):
    token = req.headers.get('authorization', '').split(' ')[1]
    return token

@app.post("/api/auth/signup")
def signup(user: User):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user_data = user.dict()
    user_data["password"] = get_password_hash(user_data.pop("password"))
    users_collection.insert_one(user_data)
    return {"message": "User created successfully"}

@app.post("/api/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/notes")
def read_notes(req: Request):
    current_user = get_current_user(get_token_from_request(req))
    user_notes = notes_collection.find({"owner": current_user.username})
    

    l = []
    for note in user_notes:
        l.append(seriallize_note(note))
    
    return l


@app.get("/api/notes/{note_id}", response_model=NoteInDB)
def read_note(note_id: str, req: Request):
    
    current_user = get_current_user(get_token_from_request(req))
    note_data = notes_collection.find_one({"_id": ObjectId(note_id)})
    if not note_data:
        raise HTTPException(status_code=404, detail="Note not found")
    if note_data["owner"] != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to access note")
    return seriallize_note(note_data)

@app.post("/api/notes", response_model=NoteInDB)
def create_note(note: NoteCreate, req: Request):
    
    current_user = get_current_user(get_token_from_request(req))
    
    note_data = note.dict()
    note_data["owner"] = current_user.username
    note_data["shared_with"] = []
    note_data["created_at"] = str(datetime.datetime.now())
    inserted_note = notes_collection.insert_one(note_data)
    note_data["_id"] = str(inserted_note.inserted_id)
    
    return note_data

@app.put("/api/notes/{note_id}", response_model=NoteInDB)
def update_note(note_id: str, note: NoteUpdate, req: Request):
    current_user = get_current_user(get_token_from_request(req))
    
    note_data = notes_collection.find_one({"_id": ObjectId(note_id)})
    if not note_data:
        raise HTTPException(status_code=404, detail="Note not found")
    if note_data["owner"] != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to update note")
    
    update_data = {}
    for key, value in note.dict(exclude_unset=True).items():
        if value is not None:
            update_data[key] = value
    
    notes_collection.update_one({"_id": ObjectId(note_id)}, {"$set": update_data})
    
    updated_note = notes_collection.find_one({"_id": ObjectId(note_id)})
    
    if not updated_note:
        raise HTTPException(status_code=404, detail="Updated note not found")
    
    updated_note['_id'] = str(updated_note['_id'])
    
    return updated_note

@app.delete("/api/notes/{note_id}", response_model=dict)
def delete_note(note_id: str, req: Request):
    
    current_user = get_current_user(get_token_from_request(req))

    note_data = notes_collection.find_one({"_id": ObjectId(note_id)})
    if not note_data:
        raise HTTPException(status_code=404, detail="Note not found")
    if note_data["owner"] != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to delete note")
    notes_collection.delete_one({"_id": ObjectId(note_id)})
    return {"message": "Note deleted successfully"}

@app.post("/api/notes/{note_id}/share", response_model=NoteInDB)
def share_note(
    note_id: str,
    req: Request,
    share_with: str = Body(..., embed=True, alias="share_with")
):

    current_user = get_current_user(get_token_from_request(req))
    note_data = notes_collection.find_one({"_id": ObjectId(note_id)})
    if not note_data:
        raise HTTPException(status_code=404, detail="Note not found")
    if note_data["owner"] != current_user.username:
        raise HTTPException(status_code=403, detail="Unauthorized to share note")
    user_to_share_with = users_collection.find_one({"username": share_with})
    if not user_to_share_with:
        raise HTTPException(status_code=404, detail="User to share with not found")
    if share_with in note_data["shared_with"]:
        raise HTTPException(
            status_code=400, detail=f"Note already shared with {share_with}"
        )
    notes_collection.update_one(
        {"_id": ObjectId(note_id)}, {"$addToSet": {"shared_with": share_with}}
    )
    
    users_collection.update_one(
        {"username": share_with},
        {"$addToSet": {"shared_notes": note_id}}
    )
    
    updated_note = notes_collection.find_one({"_id": ObjectId(note_id)})
    updated_note = seriallize_note(updated_note)
    return updated_note

@app.get("/api/search", response_model=List[NoteInDB])
def search_notes(req: Request, q: str = Query(..., min_length=1),):

    keywords = q.split()
    regex_pattern = '|'.join(keywords)

    search_result = notes_collection.find({"content": {"$regex": regex_pattern, "$options": "i"}})
    notes = [NoteInDB(**{**note, "_id": str(note["_id"]), "created_at": str(note["created_at"])}) for note in search_result]
    
    return notes
