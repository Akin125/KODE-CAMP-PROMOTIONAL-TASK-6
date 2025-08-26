"""
Task 2: Secure Shopping Cart API with Admin Access

Goal: Create a FastAPI shopping API where only admins can add products, but all users can browse and shop.

Features:
- User class with role (admin or customer)
- Module auth.py to handle authentication & role checking
- Endpoints:
  - POST /admin/add_product/ — admin only
  - GET /products/ — public
  - POST /cart/add/ — authenticated users only
- Save data to products.json and cart.json
- Use dependency injection for role-based access
"""

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

# Models
class User(BaseModel):
    username: str
    role: str  # 'admin' or 'customer'

class Product(BaseModel):
    name: str
    price: float

class CartItem(BaseModel):
    product_name: str
    quantity: int

# Mock database
products = []
carts = {}

# Dependency for role-based access
def get_current_user():
    # Mock authentication
    return User(username="admin", role="admin")

def admin_required(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

# Routes
@app.post("/admin/add_product/", dependencies=[Depends(admin_required)])
def add_product(product: Product):
    products.append(product.dict())
    with open("products.json", "w") as f:
        json.dump(products, f)
    return {"message": "Product added successfully"}

@app.get("/products/")
def get_products():
    return products

@app.post("/cart/add/")
def add_to_cart(item: CartItem, user: User = Depends(get_current_user)):
    if user.username not in carts:
        carts[user.username] = []
    carts[user.username].append(item.dict())
    with open("cart.json", "w") as f:
        json.dump(carts, f)
    return {"message": "Item added to cart"}
