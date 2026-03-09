from fastapi import Depends, FastAPI, HTTPException
import os
import uvicorn

from app_state import bank
from dotenv import load_dotenv
from server_utils import verify_token
from bank_account_routes import bank_routes
from admin_routes import admin

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "placeholder_secret_key")
ALGORITHM = "HS256"

app = FastAPI()
app.include_router(bank_routes, prefix="/bank")
app.include_router(admin, prefix="/admin")

@app.on_event("startup")
def _ensure_root():
    bank.ensure_root_user()


@app.on_event("shutdown")
def _save_bank_state():
    bank.save_to_file()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/register", response_model=dict)
async def register(user_data: dict):
    if bank.register_user(user_data["username"], user_data["password"]):
        return {
            "message": "User registered successfully",
            "token": bank.login_user(user_data["username"], user_data["password"])
        }
    else:
        raise HTTPException(status_code=400, detail="Username already exists")
    

@app.post("/login", response_model=dict)
async def login(form_data: dict):
    token = bank.login_user(form_data["username"], form_data["password"])
    if token is False:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {
        "message": "Login successful",
        "login_success": True,
        "token": token
    }
@app.get("/whoami")
async def whoami(current_user: dict = Depends(verify_token)):
    user = bank.get_user_by_id(current_user["user_id"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.get_id(),
        "username": user.get_name()
    } 

def main():
    try:
        uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
    except KeyboardInterrupt:
        print("Shutting down server...")
        bank.save_to_file()

if __name__ == "__main__":
    main()
