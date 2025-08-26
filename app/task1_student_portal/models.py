"""
Student Portal Models

This module defines the Pydantic models used for data validation and serialization
in the Student Portal API. It includes models for student input and storage.
"""

from typing import List
from pydantic import BaseModel, Field


class StudentIn(BaseModel):
    """
    Input model for student registration and login.

    This model validates incoming student data for registration and authentication.
    It includes basic validation constraints for username and password fields.

    Attributes:
        username (str): Student's unique username. Must be at least 3 characters long.
        password (str): Student's password. Must be at least 6 characters long.
    """
    username: str = Field(min_length=3, description="Unique username for the student")
    password: str = Field(min_length=6, description="Password for authentication")


class Student(BaseModel):
    """
    Internal model for student data storage.

    This model represents how student data is stored internally in the system.
    It includes the hashed password for security and a list of grades.

    Attributes:
        username (str): Student's unique identifier.
        password_hash (str): Bcrypt hashed password for secure storage.
        grades (List[float]): List of student's grades. Defaults to empty list.
    """
    username: str
    password_hash: str
    grades: List[float] = []
