"""
Data models for the Job Application Tracker API
Defines the structure of job applications and users
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class JobApplication(BaseModel):
    """
    Job Application model representing a single job application
    Contains all information about a job application
    """
    id: int
    job_title: str
    company: str
    date_applied: str  # Format: YYYY-MM-DD
    status: str  # e.g., "applied", "interview", "rejected", "offer", "accepted"
    notes: Optional[str] = None

    class Config:
        # Example data for API documentation
        schema_extra = {
            "example": {
                "id": 1,
                "job_title": "Software Developer",
                "company": "Tech Corp",
                "date_applied": "2025-08-26",
                "status": "applied",
                "notes": "Found this position through LinkedIn"
            }
        }

class JobApplicationCreate(BaseModel):
    """
    Model for creating a new job application
    Used when adding new applications (ID and date are auto-generated)
    """
    job_title: str
    company: str
    status: str = "applied"  # Default status
    notes: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "job_title": "Frontend Developer",
                "company": "Startup Inc",
                "status": "applied",
                "notes": "Exciting opportunity in React development"
            }
        }

class User(BaseModel):
    """
    User model representing a user in the system
    Each user can track their own job applications
    """
    username: str
    email: str
    full_name: str
    hashed_password: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe"
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

class ApplicationStats(BaseModel):
    """
    Model for application statistics
    Provides summary of user's job application activity
    """
    username: str
    full_name: str
    total_applications: int
    status_breakdown: dict
    most_recent_application: dict

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "full_name": "John Doe",
                "total_applications": 5,
                "status_breakdown": {
                    "applied": 3,
                    "interview": 1,
                    "rejected": 1
                },
                "most_recent_application": {
                    "job_title": "Senior Developer",
                    "company": "Big Tech",
                    "date_applied": "2025-08-26"
                }
            }
        }
