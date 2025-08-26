from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import hashlib
from datetime import datetime

app = FastAPI(title="Student Portal API", description="Secure API for students to view grades")
security = HTTPBasic()