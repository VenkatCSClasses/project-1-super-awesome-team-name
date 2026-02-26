from fastapi import FastAPI
from database_helper import login_user, register_user, get_user_by_id
from fastapi import Depends, HTTPException, Header
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "placeholder_secret_key")
ALGORITHM = "HS256"

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/register", response_model=dict)
async def register(user_data: dict):
    if register_user(user_data["username"], user_data["password"]):
        return {
            "message": "User registered successfully",
            "token": login_user(user_data["username"], user_data["password"])
        }
    else:
        raise HTTPException(status_code=400, detail="Username already exists")
    

@app.post("/login", response_model=dict)
async def login(form_data: dict):
    token = login_user(form_data["username"], form_data["password"])
    if token is False:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {
        "message": "Login successful",
        "login_success": True,
        "token": token
    }


def verify_token(authorization: str = Header(None)):
    """Verify JWT token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Extract token from "Bearer <token>" format
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
            
        return {"user_id": user_id}
        
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/protected")
async def protected_route(current_user: dict = Depends(verify_token)):
    """A protected route that requires valid JWT authentication"""
    return {
        "message": "Hello World from protected route!", 
        "user_id": current_user["user_id"]
    }


@app.get("/whoami")
async def whoami(current_user: dict = Depends(verify_token)):
    user = get_user_by_id(current_user["user_id"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "username": user.username
    }

    