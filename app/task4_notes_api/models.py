"""
Data models for the Notes API
Defines the structure of notes, users, and authentication requests
"""

from pydantic import BaseModel, EmailStr
from typing import Optional

class Note(BaseModel):
    """
    Note model representing a personal note
    Contains all information about a user's note
    """
    id: int
    title: str
    content: str
    date_created: str  # Format: YYYY-MM-DD HH:MM:SS
    date_updated: str  # Format: YYYY-MM-DD HH:MM:SS

    class Config:
        # Example data for API documentation
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Meeting Notes",
                "content": "Discussed project timeline and deliverables",
                "date_created": "2025-08-26 14:30:00",
                "date_updated": "2025-08-26 14:30:00"
            }
        }

class NoteCreate(BaseModel):
    """
    Model for creating a new note
    Used when adding new notes (ID and dates are auto-generated)
    """
    title: str
    content: str

    class Config:
        schema_extra = {
            "example": {
                "title": "Shopping List",
                "content": "Milk, Bread, Eggs, Apples"
            }
        }

class User(BaseModel):
    """
    User model representing a user in the system
    Each user can manage their own personal notes
    """
    username: str
    email: str
    full_name: str
    hashed_password: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "username": "alice",
                "email": "alice@example.com",
                "full_name": "Alice Johnson"
            }
        }

class UserCreate(BaseModel):
    """
    Model for creating a new user account
    Used during registration
    """
    username: str
    email: EmailStr
    password: str
    full_name: str

    class Config:
        schema_extra = {
            "example": {
                "username": "new_user",
                "email": "newuser@example.com",
                "password": "mypassword123",
                "full_name": "New User"
            }
        }

class LoginRequest(BaseModel):
    """
    Model for login requests
    Used for user authentication
    """
    username: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "username": "alice",
                "password": "secret"
            }
        }

class Token(BaseModel):
    """
    Model for authentication tokens
    Used to return JWT tokens after successful login
    """
    access_token: str
    token_type: str

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class NotesStats(BaseModel):
    """
    Model for notes statistics
    Provides summary of user's notes activity
    """
    username: str
    full_name: str
    total_notes: int
    most_recent_note: dict

    class Config:
        schema_extra = {
            "example": {
                "username": "alice",
                "full_name": "Alice Johnson",
                "total_notes": 5,
                "most_recent_note": {
                    "title": "Project Ideas",
                    "date_updated": "2025-08-26 15:30:00"
                }
            }
        }
