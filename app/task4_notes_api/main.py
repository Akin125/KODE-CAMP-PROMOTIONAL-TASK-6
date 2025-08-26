"""
Task 4: Notes API with Token Authentication
A secure notes management API with JWT token authentication.
Each user can manage their own personal notes.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from typing import List
import json
import os
from datetime import datetime
from models import Note, NoteCreate, User, UserCreate, LoginRequest
from auth import get_current_user, authenticate_user, create_access_token

app = FastAPI(
    title="Personal Notes API",
    description="A secure notes management system with JWT token authentication",
    version="1.0.0"
)

# File paths for data storage
NOTES_DIR = "notes_data"
USERS_FILE = "users.json"

def initialize_files():
    """Initialize data storage files and directories"""
    # Create notes directory if it doesn't exist
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)

    # Create users file with default users
    if not os.path.exists(USERS_FILE):
        default_users = [
            {
                "username": "alice",
                "email": "alice@example.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
                "full_name": "Alice Johnson"
            },
            {
                "username": "bob",
                "email": "bob@example.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
                "full_name": "Bob Smith"
            }
        ]
        with open(USERS_FILE, 'w') as f:
            json.dump(default_users, f, indent=2)

# Initialize files on startup
initialize_files()

@app.get("/")
def read_root():
    """Welcome endpoint with API information"""
    return {
        "message": "Welcome to the Personal Notes API!",
        "description": "Manage your personal notes securely with JWT token authentication",
        "endpoints": {
            "login": "POST /login/",
            "register": "POST /register/",
            "add_note": "POST /notes/",
            "view_notes": "GET /notes/",
            "get_note": "GET /notes/{note_id}",
            "update_note": "PUT /notes/{note_id}",
            "delete_note": "DELETE /notes/{note_id}"
        },
        "test_accounts": {
            "user1": {"username": "alice", "password": "secret"},
            "user2": {"username": "bob", "password": "secret"}
        }
    }

@app.post("/register/")
def register_user(user: UserCreate):
    """
    Register a new user account
    Creates a new user who can then manage personal notes
    """
    try:
        # Check if user already exists
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)

        # Check if username or email already exists
        for existing_user in users:
            if existing_user["username"] == user.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            if existing_user["email"] == user.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Hash the password and create new user
        from auth import get_password_hash
        new_user = {
            "username": user.username,
            "email": user.email,
            "hashed_password": get_password_hash(user.password),
            "full_name": user.full_name
        }

        # Add new user to the list
        users.append(new_user)

        # Save back to file
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)

        # Create empty notes file for the new user
        user_notes_file = os.path.join(NOTES_DIR, f"{user.username}_notes.json")
        with open(user_notes_file, 'w') as f:
            json.dump([], f)

        return {
            "message": f"User {user.username} registered successfully!",
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error during registration"
        )

@app.post("/login/")
def login(login_data: LoginRequest):
    """
    Login endpoint to get JWT access token
    Required for all notes operations
    """
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.username,
        "message": f"Welcome back, {user.full_name}!"
    }

@app.post("/notes/", response_model=Note)
def add_note(
    note: NoteCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Add a new note (requires JWT token)
    Each note is linked to the authenticated user
    """
    try:
        # Get user's notes file
        user_notes_file = os.path.join(NOTES_DIR, f"{current_user.username}_notes.json")

        # Load existing notes or create empty list
        if os.path.exists(user_notes_file):
            with open(user_notes_file, 'r') as f:
                notes = json.load(f)
        else:
            notes = []

        # Create new note with auto-generated ID and current date
        note_id = len(notes) + 1
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_note = Note(
            id=note_id,
            title=note.title,
            content=note.content,
            date_created=current_date,
            date_updated=current_date
        )

        # Add to user's notes
        notes.append(new_note.dict())

        # Save back to user's notes file
        with open(user_notes_file, 'w') as f:
            json.dump(notes, f, indent=2)

        return new_note

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating note"
        )

@app.get("/notes/", response_model=List[Note])
def get_my_notes(current_user: User = Depends(get_current_user)):
    """
    View all your notes (requires JWT token)
    Users can only see their own notes
    """
    try:
        # Get user's notes file
        user_notes_file = os.path.join(NOTES_DIR, f"{current_user.username}_notes.json")

        # Load user's notes or return empty list
        if os.path.exists(user_notes_file):
            with open(user_notes_file, 'r') as f:
                notes = json.load(f)
            return [Note(**note) for note in notes]
        else:
            return []

    except Exception:
        return []

@app.get("/notes/{note_id}", response_model=Note)
def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific note by ID (requires JWT token)
    Users can only access their own notes
    """
    try:
        # Get user's notes file
        user_notes_file = os.path.join(NOTES_DIR, f"{current_user.username}_notes.json")

        if not os.path.exists(user_notes_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )

        # Load user's notes
        with open(user_notes_file, 'r') as f:
            notes = json.load(f)

        # Find the specific note
        note = next((n for n in notes if n['id'] == note_id), None)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )

        return Note(**note)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving note"
        )

@app.put("/notes/{note_id}", response_model=Note)
def update_note(
    note_id: int,
    note_update: NoteCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific note (requires JWT token)
    Users can only update their own notes
    """
    try:
        # Get user's notes file
        user_notes_file = os.path.join(NOTES_DIR, f"{current_user.username}_notes.json")

        if not os.path.exists(user_notes_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )

        # Load user's notes
        with open(user_notes_file, 'r') as f:
            notes = json.load(f)

        # Find and update the specific note
        note_found = False
        for note in notes:
            if note['id'] == note_id:
                note['title'] = note_update.title
                note['content'] = note_update.content
                note['date_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                note_found = True
                updated_note = Note(**note)
                break

        if not note_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )

        # Save updated notes back to file
        with open(user_notes_file, 'w') as f:
            json.dump(notes, f, indent=2)

        return updated_note

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating note"
        )

@app.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific note (requires JWT token)
    Users can only delete their own notes
    """
    try:
        # Get user's notes file
        user_notes_file = os.path.join(NOTES_DIR, f"{current_user.username}_notes.json")

        if not os.path.exists(user_notes_file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )

        # Load user's notes
        with open(user_notes_file, 'r') as f:
            notes = json.load(f)

        # Find and remove the specific note
        original_length = len(notes)
        notes = [note for note in notes if note['id'] != note_id]

        if len(notes) == original_length:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )

        # Save updated notes back to file
        with open(user_notes_file, 'w') as f:
            json.dump(notes, f, indent=2)

        return {
            "message": f"Note {note_id} deleted successfully",
            "deleted_note_id": note_id
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting note"
        )

@app.get("/notes/stats/")
def get_notes_statistics(current_user: User = Depends(get_current_user)):
    """
    Get statistics about user's notes
    Shows total notes and recent activity
    """
    try:
        # Get user's notes file
        user_notes_file = os.path.join(NOTES_DIR, f"{current_user.username}_notes.json")

        if not os.path.exists(user_notes_file):
            return {
                "username": current_user.username,
                "total_notes": 0,
                "message": "No notes found. Start creating your first note!"
            }

        # Load user's notes
        with open(user_notes_file, 'r') as f:
            notes = json.load(f)

        if not notes:
            return {
                "username": current_user.username,
                "total_notes": 0,
                "message": "No notes found. Start creating your first note!"
            }

        # Find most recent note
        most_recent = max(notes, key=lambda x: x.get('date_updated', '1970-01-01'))

        return {
            "username": current_user.username,
            "full_name": current_user.full_name,
            "total_notes": len(notes),
            "most_recent_note": {
                "title": most_recent.get('title'),
                "date_updated": most_recent.get('date_updated')
            }
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Different port from other tasks
