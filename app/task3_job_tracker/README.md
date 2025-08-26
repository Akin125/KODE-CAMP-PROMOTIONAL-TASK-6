# Task 3: Job Application Tracker with Secure Access

A FastAPI-based job application tracking system where each user can securely manage their own job applications with complete data isolation.

## Features

- **Secure User Authentication**: JWT token-based authentication
- **Data Isolation**: Users can only see and manage their own applications
- **Job Application Management**: Add, view, and update job applications
- **Application Statistics**: Get insights into your job search progress
- **User Registration**: Create new user accounts
- **Status Tracking**: Track application progress through different stages

## Project Structure

```
task3_job_tracker/
├── main.py            # Main FastAPI application
├── models.py          # Pydantic models for data validation
├── auth.py            # Authentication and user management
├── applications.json  # Job applications database (auto-created)
├── users.json         # Users database (auto-created)
└── README.md          # This documentation
```

## API Endpoints

### Public Endpoints
- `GET /` - Welcome message and API information
- `POST /register/` - Register a new user account

### Authentication
- `POST /login/` - Login and get access token

### Authenticated User Endpoints (Secure - Users only see their own data)
- `POST /applications/` - Add a new job application
- `GET /applications/` - View all your job applications
- `GET /applications/stats/` - Get statistics about your applications
- `PUT /applications/{id}` - Update application status

## Setup Instructions

1. **Install Dependencies** (if not already installed):
   ```bash
   pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] email-validator
   ```

2. **Run the Application**:
   ```bash
   cd task3_job_tracker
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --port 8001
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8001/docs
   - Alternative Docs: http://localhost:8001/redoc

## Default Test Accounts

The system creates default test accounts on first run:

- **User 1**:
  - Username: `john_doe`
  - Password: `secret`
  - Full Name: John Doe

- **User 2**:
  - Username: `jane_smith`
  - Password: `secret`
  - Full Name: Jane Smith

## Usage Examples

### 1. Register a New User
```bash
curl -X POST "http://localhost:8001/register/" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "new_user",
       "email": "newuser@example.com",
       "password": "mypassword",
       "full_name": "New User"
     }'
```

### 2. Login to Get Access Token
```bash
curl -X POST "http://localhost:8001/login/" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=john_doe&password=secret"
```

### 3. Add a Job Application
```bash
curl -X POST "http://localhost:8001/applications/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "job_title": "Software Developer",
       "company": "Tech Corp",
       "status": "applied",
       "notes": "Found through LinkedIn"
     }'
```

### 4. View Your Job Applications
```bash
curl -X GET "http://localhost:8001/applications/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Get Application Statistics
```bash
curl -X GET "http://localhost:8001/applications/stats/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 6. Update Application Status
```bash
curl -X PUT "http://localhost:8001/applications/1?status=interview" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Data Models

### JobApplication
- id: integer (auto-generated)
- job_title: string
- company: string
- date_applied: string (YYYY-MM-DD, auto-generated)
- status: string (e.g., "applied", "interview", "rejected", "offer")
- notes: string (optional)

### User
- username: string (unique)
- email: string (unique)
- full_name: string
- hashed_password: string (encrypted)

## Application Status Options

Common status values you can use:
- `applied` - Just submitted application
- `interview` - Interview scheduled/completed
- `rejected` - Application rejected
- `offer` - Job offer received
- `accepted` - Offer accepted
- `withdrawn` - Application withdrawn

## Security Features

- **Data Isolation**: Each user can only access their own applications
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Passwords are securely hashed using bcrypt
- **Input Validation**: All inputs are validated using Pydantic models

## Testing the API

1. **Start the server** and visit http://localhost:8001/docs
2. **Register a new account** or use the test accounts
3. **Login** to get your access token
4. **Add some job applications** to track your job search
5. **View your applications** and **check your statistics**
6. **Update application statuses** as you progress

## Data Storage

- **Per-user data**: Applications are stored per user in `applications.json`
- **User accounts**: All users are stored in `users.json`
- **JSON format**: Easy to read and modify for development
- **Automatic creation**: Files are created automatically on first run

## Notes for Beginners

- **Authentication Required**: All application endpoints require a valid JWT token
- **Data Privacy**: Users cannot see other users' applications
- **Token Usage**: Include your token in the Authorization header as "Bearer YOUR_TOKEN"
- **Automatic Dates**: Application date is automatically set to today when created
- **Status Tracking**: Update application status as you progress through the hiring process

## Troubleshooting

- **401 Unauthorized**: Your token may be expired or invalid - login again
- **404 Not Found**: Check if the application ID exists and belongs to you
- **400 Bad Request**: Check if username/email already exists during registration
- **403 Forbidden**: You're trying to access data that doesn't belong to you
