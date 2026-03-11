from fastapi import APIRouter, Depends, HTTPException
from server_utils import verify_token
from dotenv import load_dotenv
from app_state import bank
load_dotenv()

admin = APIRouter()

@admin.get("/delete_user/{user_id}", response_model=dict)
async def delete_user(user_id: int, current_user: dict = Depends(verify_token)):
    """Delete a user from the bank. Only admins can delete users."""
    # Only allow users with permission level 2 (admin) to delete users
    if current_user.get("permission", -1) < 2:
        raise HTTPException(status_code=403, detail="Must be an admin to delete users")
    
    # Logic to delete a user would go here
    try:
        bank.remove_account_by_id(user_id)
        return {"message": f"User with ID {user_id} has been deleted."}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
