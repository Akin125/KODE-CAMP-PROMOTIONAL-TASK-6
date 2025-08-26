"""
Student Portal API

A FastAPI-based student management system that provides endpoints for student registration,
authentication, and grade management. The API uses HTTP Basic Authentication for protected
endpoints and stores data in JSON files.

Features:
- Student registration with password hashing
- Student authentication and login
- Grade retrieval with authentication
- JSON file-based data storage
"""

from typing import Dict, List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from utils import read_json, write_json, FileError
from models import StudentIn, Student

# Initialize FastAPI app and security components
app = FastAPI(title="Student Portal API")
security = HTTPBasic()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Data storage structure: { username: {"username": ..., "password_hash": ..., "grades": [...] } }


def _load_students() -> Dict[str, Dict]:
    """
    Load student data from JSON file.

    Returns:
        Dict[str, Dict]: Dictionary containing all student data keyed by username.
    """
    return read_json("students.json", default={})


def _save_students(data: Dict[str, Dict]):
    """
    Save student data to JSON file.

    Args:
        data (Dict[str, Dict]): Student data to save.
    """
    write_json("students.json", data)


@app.post("/register/", status_code=201)
def register(student: StudentIn):
    """
    Register a new student.

    Creates a new student account with hashed password and empty grades list.

    Args:
        student (StudentIn): Student registration data containing username and password.

    Returns:
        dict: Success message upon successful registration.

    Raises:
        HTTPException: 409 if username already exists, 500 for file errors.
    """
    try:
        students = _load_students()
        if student.username in students:
            raise HTTPException(status_code=409, detail="Username already exists")
        students[student.username] = Student(
            username=student.username,
            password_hash=pwd.hash(student.password),
            grades=[],
        ).model_dump()
        _save_students(students)
        return {"message": "Registered"}
    except FileError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login/")
def login(payload: StudentIn):
    """
    Authenticate a student.

    Verifies student credentials against stored data.

    Args:
        payload (StudentIn): Login credentials containing username and password.

    Returns:
        dict: Success message upon successful authentication.

    Raises:
        HTTPException: 401 for invalid credentials, 500 for file errors.
    """
    try:
        students = _load_students()
        user = students.get(payload.username)
        if not user or not pwd.verify(payload.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"message": "Authenticated"}
    except FileError as e:
        raise HTTPException(status_code=500, detail=str(e))


def authenticate(creds: HTTPBasicCredentials = Depends(security)) -> str:
    """
    HTTP Basic Authentication dependency.

    Validates credentials for protected endpoints using HTTP Basic Authentication.

    Args:
        creds (HTTPBasicCredentials): HTTP Basic credentials from request header.

    Returns:
        str: Authenticated username.

    Raises:
        HTTPException: 401 for invalid credentials, 500 for file errors.
    """
    try:
        students = _load_students()
        user = students.get(creds.username)
        if not user or not pwd.verify(creds.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return creds.username
    except FileError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/grades/")
def get_grades(username: str = Depends(authenticate)) -> List[float]:
    """
    Retrieve student grades.

    Protected endpoint that returns the grades for the authenticated student.

    Args:
        username (str): Authenticated username from the authenticate dependency.

    Returns:
        List[float]: List of the student's grades.

    Raises:
        HTTPException: 404 if student not found, 500 for file errors.
    """
    try:
        students = _load_students()
        return students[username]["grades"]
    except KeyError:
        raise HTTPException(status_code=404, detail="Student not found")
    except FileError as e:
        raise HTTPException(status_code=500, detail=str(e))
