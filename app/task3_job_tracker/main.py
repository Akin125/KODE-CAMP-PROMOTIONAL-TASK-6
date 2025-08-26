"""
Task 3: Job Application Tracker with Secure Access

Goal: Build an API where each user can only see their own job applications.

Features:
- JobApplication class: job title, company, date applied, status
- Authenticated users can:
  - POST /applications/ — add
  - GET /applications/ — view only their applications
- Store per-user data in applications.json
- Use dependency to get current logged-in user and filter results
"""

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
import json
from datetime import date

app = FastAPI()

# Models
class User(BaseModel):
    username: str

class JobApplication(BaseModel):
    job_title: str
    company: str
    date_applied: date
    status: str

# Mock database
applications = {}

# Dependency for authentication
def get_current_user():
    # Mock authentication
    return User(username="user1")

# Routes
@app.post("/applications/")
def add_application(application: JobApplication, user: User = Depends(get_current_user)):
    if user.username not in applications:
        applications[user.username] = []
    applications[user.username].append(application.dict())
    with open("applications.json", "w") as f:
        json.dump(applications, f)
    return {"message": "Application added successfully"}

@app.get("/applications/")
def get_applications(user: User = Depends(get_current_user)):
    user_applications = applications.get(user.username, [])
    return user_applications
