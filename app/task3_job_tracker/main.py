"""
Task 3: Job Application Tracker with Secure Access
This API allows users to track their job applications with secure user isolation.
Each user can only see and manage their own applications.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from typing import List
import json
import os
from datetime import datetime
from models import JobApplication, JobApplicationCreate, User, UserCreate
from auth import get_current_user, authenticate_user, create_access_token

app = FastAPI(
    title="Job Application Tracker API",
    description="A secure job application tracking system where users can only access their own data",
    version="1.0.0"
)

# File paths for data storage
APPLICATIONS_FILE = "applications.json"
USERS_FILE = "users.json"

def initialize_files():
    """Initialize JSON files with empty data if they don't exist"""
    if not os.path.exists(APPLICATIONS_FILE):
        with open(APPLICATIONS_FILE, 'w') as f:
            json.dump({}, f)  # Dictionary with username as key

    if not os.path.exists(USERS_FILE):
        # Create some default users for testing
        default_users = [
            {
                "username": "john_doe",
                "email": "john@example.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
                "full_name": "John Doe"
            },
            {
                "username": "jane_smith",
                "email": "jane@example.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
                "full_name": "Jane Smith"
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
        "message": "Welcome to the Job Application Tracker API!",
        "description": "Track your job applications securely - each user can only see their own data",
        "endpoints": {
            "login": "POST /login/",
            "add_application": "POST /applications/",
            "view_applications": "GET /applications/",
            "register": "POST /register/"
        },
        "test_accounts": {
            "user1": {"username": "john_doe", "password": "secret"},
            "user2": {"username": "jane_smith", "password": "secret"}
        }
    }

@app.post("/login/")
def login(username: str, password: str):
    """
    Login endpoint to get access token
    Required for all job application operations
    """
    user = authenticate_user(username, password)
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

@app.post("/register/")
def register_user(user: UserCreate):
    """
    Register a new user account
    Creates a new user who can then track job applications
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

@app.post("/applications/", response_model=JobApplication)
def add_job_application(
    application: JobApplicationCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Add a new job application
    Each application is linked to the authenticated user
    """
    try:
        # Load existing applications
        with open(APPLICATIONS_FILE, 'r') as f:
            applications_data = json.load(f)
    except:
        applications_data = {}

    # Get or create user's application list
    username = current_user.username
    if username not in applications_data:
        applications_data[username] = []

    # Create new application with auto-generated ID and current date
    application_id = len(applications_data[username]) + 1
    current_date = datetime.now().strftime("%Y-%m-%d")

    new_application = JobApplication(
        id=application_id,
        job_title=application.job_title,
        company=application.company,
        date_applied=current_date,
        status=application.status,
        notes=application.notes
    )

    # Add to user's applications
    applications_data[username].append(new_application.dict())

    # Save back to file
    with open(APPLICATIONS_FILE, 'w') as f:
        json.dump(applications_data, f, indent=2)

    return new_application

@app.get("/applications/", response_model=List[JobApplication])
def get_my_applications(current_user: User = Depends(get_current_user)):
    """
    Get all job applications for the current user
    Users can only see their own applications - secure data isolation
    """
    try:
        with open(APPLICATIONS_FILE, 'r') as f:
            applications_data = json.load(f)
    except:
        applications_data = {}

    # Get user's applications or empty list
    username = current_user.username
    user_applications = applications_data.get(username, [])

    # Convert to JobApplication objects
    applications = [JobApplication(**app) for app in user_applications]

    return applications

@app.get("/applications/stats/")
def get_application_statistics(current_user: User = Depends(get_current_user)):
    """
    Get statistics about user's job applications
    Provides insights into application status distribution
    """
    try:
        with open(APPLICATIONS_FILE, 'r') as f:
            applications_data = json.load(f)
    except:
        applications_data = {}

    # Get user's applications
    username = current_user.username
    user_applications = applications_data.get(username, [])

    # Calculate statistics
    total_applications = len(user_applications)

    if total_applications == 0:
        return {
            "username": username,
            "total_applications": 0,
            "message": "No applications found. Start tracking your job search!"
        }

    # Count by status
    status_counts = {}
    for app in user_applications:
        status = app.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    # Find most recent application
    most_recent = max(user_applications, key=lambda x: x.get('date_applied', '1970-01-01'))

    return {
        "username": username,
        "full_name": current_user.full_name,
        "total_applications": total_applications,
        "status_breakdown": status_counts,
        "most_recent_application": {
            "job_title": most_recent.get('job_title'),
            "company": most_recent.get('company'),
            "date_applied": most_recent.get('date_applied')
        }
    }

@app.put("/applications/{application_id}")
def update_application_status(
    application_id: int,
    status: str,
    current_user: User = Depends(get_current_user)
):
    """
    Update the status of a specific job application
    Users can only update their own applications
    """
    try:
        # Load applications data
        with open(APPLICATIONS_FILE, 'r') as f:
            applications_data = json.load(f)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No applications found"
        )

    username = current_user.username
    user_applications = applications_data.get(username, [])

    # Find the application to update
    application_found = False
    for app in user_applications:
        if app.get('id') == application_id:
            app['status'] = status
            application_found = True
            break

    if not application_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or you don't have permission to modify it"
        )

    # Save back to file
    with open(APPLICATIONS_FILE, 'w') as f:
        json.dump(applications_data, f, indent=2)

    return {
        "message": f"Application {application_id} status updated to '{status}'",
        "application_id": application_id,
        "new_status": status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Different port from other tasks
