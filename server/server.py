from fastapi import FastAPI
from database_helper import login_user, register_user, get_user_by_id, ensure_root_user
from fastapi import Depends, HTTPException, Header
from server_utils import verify_token
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "placeholder_secret_key")
ALGORITHM = "HS256"

app = FastAPI()


@app.on_event("startup")
def _ensure_root():
    # Ensure the root account exists when the server starts
    try:
        ensure_root_user()
    except Exception:
        # avoid startup failure if DB not ready; keep silent
        pass

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



        
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/whoami")
async def whoami(current_user: dict = Depends(verify_token)):
    user = get_user_by_id(current_user["user_id"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "username": user.username
    } 