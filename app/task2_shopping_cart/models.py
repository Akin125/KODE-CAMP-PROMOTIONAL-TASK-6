"""
Data models for the Shopping Cart API
Defines the structure of users, products, and cart items
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    """
    User model representing a user in the system
    Can be either 'admin' or 'customer' role
    """
    username: str
    email: str
    role: str  # "admin" or "customer"
    hashed_password: Optional[str] = None

    class Config:
        # Example data for API documentation
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "role": "customer"
            }
        }

class UserCreate(BaseModel):
    """
    Model for creating a new user
    Used when registering new users
    """
    username: str
    email: str
    password: str
    role: str = "customer"  # Default role is customer

    class Config:
        schema_extra = {
            "example": {
                "username": "new_customer",
                "email": "customer@example.com",
                "password": "mypassword",
                "role": "customer"
            }
        }

class Product(BaseModel):
    """
    Product model representing items in the store
    Contains all product information including stock
    """
    id: int
    name: str
    description: str
    price: float
    stock: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Laptop",
                "description": "High-performance laptop for work and gaming",
                "price": 999.99,
                "stock": 10
            }
        }

class ProductCreate(BaseModel):
    """
    Model for creating a new product
    Used by admins to add new products (ID is auto-generated)
    """
    name: str
    description: str
    price: float
    stock: int

    class Config:
        schema_extra = {
            "example": {
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse with long battery life",
                "price": 29.99,
                "stock": 50
            }
        }

class CartItem(BaseModel):
    """
    Model for adding items to cart
    Represents a single item with quantity to be added
    """
    product_id: int
    quantity: int

    class Config:
        schema_extra = {
            "example": {
                "product_id": 1,
                "quantity": 2
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
