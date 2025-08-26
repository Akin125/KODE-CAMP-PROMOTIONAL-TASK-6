# Task 2: Secure Shopping Cart API with Admin Access

A FastAPI-based shopping cart system with role-based authentication where admins can manage products and all authenticated users can shop.

## Features

- **User Authentication**: JWT token-based authentication system
- **Role-based Access**: Admin and customer roles with different permissions
- **Product Management**: Admins can add new products to the store
- **Shopping Cart**: Authenticated users can browse products and add items to cart
- **Data Persistence**: All data stored in JSON files

## Project Structure

```
task2_shopping_cart/
├── main.py          # Main FastAPI application
├── models.py        # Pydantic models for data validation
├── auth.py          # Authentication and authorization logic
├── products.json    # Products database (auto-created)
├── cart.json        # Shopping carts database (auto-created)
├── users.json       # Users database (auto-created)
└── README.md        # This documentation
```

## API Endpoints

### Public Endpoints
- `GET /` - Welcome message and API information
- `GET /products/` - View all available products (no authentication required)

### Authentication
- `POST /login/` - Login and get access token

### Admin Only Endpoints
- `POST /admin/add_product/` - Add new product (requires admin role)

### Authenticated User Endpoints
- `POST /cart/add/` - Add item to shopping cart
- `GET /cart/` - View your shopping cart

## Setup Instructions

1. **Install Dependencies** (if not already installed):
   ```bash
   pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt]
   ```

2. **Run the Application**:
   ```bash
   cd task2_shopping_cart
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## Default User Accounts

The system creates default accounts on first run:

- **Admin Account**:
  - Username: `admin`
  - Password: `secret`
  - Role: admin

- **Customer Account**:
  - Username: `customer1`
  - Password: `secret`
  - Role: customer

## Usage Examples

### 1. Login to Get Access Token
```bash
curl -X POST "http://localhost:8000/login/" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=secret"
```

### 2. Add a Product (Admin Only)
```bash
curl -X POST "http://localhost:8000/admin/add_product/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Laptop",
       "description": "High-performance laptop",
       "price": 999.99,
       "stock": 10
     }'
```

### 3. Browse Products (Public)
```bash
curl -X GET "http://localhost:8000/products/"
```

### 4. Add Item to Cart (Authenticated Users)
```bash
curl -X POST "http://localhost:8000/cart/add/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "product_id": 1,
       "quantity": 2
     }'
```

### 5. View Your Cart
```bash
curl -X GET "http://localhost:8000/cart/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Data Models

### User
- username: string
- email: string
- role: "admin" or "customer"
- hashed_password: string (encrypted)

### Product
- id: integer (auto-generated)
- name: string
- description: string
- price: float
- stock: integer

### CartItem
- product_id: integer
- quantity: integer

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Stateless authentication with expiring tokens
- **Role-based Access**: Different permissions for admin vs customer users
- **Input Validation**: Pydantic models ensure data integrity

## Testing the API

1. **Start the server** and visit http://localhost:8000/docs
2. **Login** with admin credentials to get a token
3. **Add some products** using the admin endpoint
4. **Login** with customer credentials
5. **Browse products** and **add items to cart**

## Notes for Beginners

- **JWT Tokens**: After login, include the token in the Authorization header as "Bearer YOUR_TOKEN"
- **Role Permissions**: Only admins can add products, but anyone can view them
- **Data Persistence**: All data is saved to JSON files in the same directory
- **Error Handling**: The API provides clear error messages for common issues

## Troubleshooting

- **403 Forbidden**: Check if you're using the correct role for the endpoint
- **401 Unauthorized**: Make sure your token is valid and included in headers
- **404 Not Found**: Verify the product ID exists when adding to cart
- **400 Bad Request**: Check if there's enough stock for the requested quantity
