from fastapi import FastAPI
from database_helper import login_user, register_user
from fastapi import Depends, HTTPException

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@router.post("/register")
async def register(user_data: dict):
    if register_user(user_data.username, user_data.password):
        return {
            "message": "User registered successfully",
            "token": login_user(user_data.username, user_data.password)
        }
    else:
        raise HTTPException(status_code=400, detail="Username already exists")
    

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = login_user(form_data.username, form_data.password)
    if token is False:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "message": "Login successful",
        "token": token
    }

    