"""
Authentication module for the Job Application Tracker API
Handles user authentication and secure access to personal data
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import json
import os
from models import User

# Security configuration
SECRET_KEY = "job-tracker-secret-key-change-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token setup
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash
    Returns True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a plain password
    Returns the hashed version of the password for secure storage
    """
    return pwd_context.hash(password)

def get_user(username: str) -> User:
    """
    Get user from the users.json file by username
    Returns User object if found, None otherwise
    """
    try:
        with open("users.json", 'r') as f:
            users_data = json.load(f)

        for user_data in users_data:
            if user_data["username"] == username:
                return User(**user_data)
        return None
    except FileNotFoundError:
        return None

def authenticate_user(username: str, password: str) -> User:
    """
    Authenticate a user with username and password
    Returns User object if authentication successful, False otherwise
    """
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT access token
    Contains user information and expiration time
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Dependency to get the current authenticated user from JWT token
    This ensures users can only access their own job application data
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please login again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract token from credentials
        token = credentials.credentials
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get user from database
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user

# Helper function to create initial test users
def create_initial_users():
    """
    Create initial test users if users.json doesn't exist
    This is called when the application starts
    """
    if not os.path.exists("users.json"):
        test_users = [
            {
                "username": "john_doe",
                "email": "john@example.com",
                "hashed_password": get_password_hash("secret"),
                "full_name": "John Doe"
            },
            {
                "username": "jane_smith",
                "email": "jane@example.com",
                "hashed_password": get_password_hash("secret"),
                "full_name": "Jane Smith"
            }
        ]

        with open("users.json", 'w') as f:
            json.dump(test_users, f, indent=2)

        print("Initial test users created:")
        print("User 1: username=john_doe, password=secret")
        print("User 2: username=jane_smith, password=secret")
