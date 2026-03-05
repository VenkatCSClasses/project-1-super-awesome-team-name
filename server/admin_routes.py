from fastapi import FastAPI, HTTPException, Depends
from server_utils import verify_token
from dotenv import load_dotenv
import os
load_dotenv()

admin = FastAPI()

@admin.get("/delete_user/{user_id}")
async def delete_user(user_id: int, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 2 (admin) to delete users
    if current_user.get("permission", -1) < 2:
        raise HTTPException(status_code=403, detail="Must be an admin to delete users")
    
    # Logic to delete a user would go here
    return {"message": f"User {user_id} deleted successfully!"}
