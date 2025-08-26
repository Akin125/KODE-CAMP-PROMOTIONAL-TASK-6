"""
Task 2: Secure Shopping Cart API with Admin Access
This API allows admins to manage products and all users to browse and shop.
"""

from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
import json
import os
from models import Product, User, CartItem, UserCreate, ProductCreate
from auth import get_current_user, get_admin_user, authenticate_user, create_access_token

app = FastAPI(
    title="Shopping Cart API",
    description="A secure shopping cart API with admin access for product management",
    version="1.0.0"
)

# File paths for data storage
PRODUCTS_FILE = "products.json"
CART_FILE = "cart.json"
USERS_FILE = "users.json"

# Initialize data files if they don't exist
def initialize_files():
    """Initialize JSON files with empty data if they don't exist"""
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(CART_FILE):
        with open(CART_FILE, 'w') as f:
            json.dump({}, f)

    if not os.path.exists(USERS_FILE):
        # Create default admin user
        default_users = [
            {
                "username": "admin",
                "email": "admin@shop.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
                "role": "admin"
            },
            {
                "username": "customer1",
                "email": "customer1@shop.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
                "role": "customer"
            }
        ]
        with open(USERS_FILE, 'w') as f:
            json.dump(default_users, f, indent=2)

initialize_files()

@app.get("/")
def read_root():
    """Welcome endpoint with API information"""
    return {
        "message": "Welcome to the Shopping Cart API!",
        "endpoints": {
            "login": "POST /login/",
            "products": "GET /products/",
            "add_product": "POST /admin/add_product/ (admin only)",
            "add_to_cart": "POST /cart/add/ (authenticated users)"
        },
        "default_accounts": {
            "admin": {"username": "admin", "password": "secret"},
            "customer": {"username": "customer1", "password": "secret"}
        }
    }

@app.post("/login/")
def login(username: str, password: str):
    """
    Login endpoint to get access token
    Returns a token that must be used for authenticated requests
    """
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_role": user.role,
        "message": f"Welcome {user.username}! You are logged in as {user.role}."
    }

@app.post("/admin/add_product/", response_model=Product)
def add_product(
    product: ProductCreate,
    current_user: User = Depends(get_admin_user)
):
    """
    Add a new product - Only admins can access this endpoint
    Requires admin role authentication
    """
    try:
        # Load existing products
        with open(PRODUCTS_FILE, 'r') as f:
            products = json.load(f)
    except:
        products = []

    # Create new product with auto-generated ID
    new_product = Product(
        id=len(products) + 1,
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock
    )

    # Add to products list
    products.append(new_product.dict())

    # Save back to file
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(products, f, indent=2)

    return new_product

@app.get("/products/", response_model=List[Product])
def get_products():
    """
    Get all products - Public endpoint (no authentication required)
    Anyone can browse products
    """
    try:
        with open(PRODUCTS_FILE, 'r') as f:
            products = json.load(f)
        return [Product(**product) for product in products]
    except:
        return []

@app.post("/cart/add/")
def add_to_cart(
    item: CartItem,
    current_user: User = Depends(get_current_user)
):
    """
    Add item to cart - Requires authentication (any role)
    Both admins and customers can add items to their cart
    """
    try:
        # Load existing cart data
        with open(CART_FILE, 'r') as f:
            cart_data = json.load(f)
    except:
        cart_data = {}

    # Get user's cart or create new one
    username = current_user.username
    if username not in cart_data:
        cart_data[username] = []

    # Check if product exists
    try:
        with open(PRODUCTS_FILE, 'r') as f:
            products = json.load(f)

        product = next((p for p in products if p['id'] == item.product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product['stock'] < item.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No products available")

    # Add item to user's cart
    cart_item = {
        "product_id": item.product_id,
        "product_name": product['name'],
        "quantity": item.quantity,
        "price": product['price'],
        "total": product['price'] * item.quantity
    }

    cart_data[username].append(cart_item)

    # Save back to file
    with open(CART_FILE, 'w') as f:
        json.dump(cart_data, f, indent=2)

    return {
        "message": f"Added {item.quantity} x {product['name']} to cart",
        "item": cart_item,
        "cart_total_items": len(cart_data[username])
    }

@app.get("/cart/")
def view_cart(current_user: User = Depends(get_current_user)):
    """
    View user's cart - Requires authentication
    Users can only see their own cart items
    """
    try:
        with open(CART_FILE, 'r') as f:
            cart_data = json.load(f)
    except:
        cart_data = {}

    username = current_user.username
    user_cart = cart_data.get(username, [])

    total_amount = sum(item.get('total', 0) for item in user_cart)

    return {
        "username": username,
        "cart_items": user_cart,
        "total_items": len(user_cart),
        "total_amount": total_amount
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
