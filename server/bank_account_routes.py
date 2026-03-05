from fastapi import FastAPI
from server_utils import verify_token
from dotenv import load_dotenv
import os
load_dotenv()

bank = FastAPI()

@bank.get("/create_bank_account")
async def create_bank_account(current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 1 (teller) or higher to create bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to create a bank account")
    
    # Logic to create a bank account would go here
    return {"message": "Bank account created successfully!"}


@bank.get("/view_bank_account")
async def view_bank_account(current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 0 (customer) or higher to view bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to view bank account details")
    
    # Logic to view a bank account would go here
    return {"message": "Bank account details displayed successfully!"}


@bank.get("/delete_bank_account")
async def delete_bank_account(current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 1 (teller) or higher to delete bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to delete a bank account")
    
    # Logic to delete a bank account would go here
    return {"message": "Bank account deleted successfully!"}


@bank.get("/deposit/{account_id}")
async def deposit(account_id: int, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 1 (teller) or higher to deposit into bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to deposit into a bank account")
    
    # Logic to deposit into a bank account would go here
    return {"message": f"Deposit into account {account_id} successful!"}


@bank.get("/withdraw/{account_id}")
async def withdraw(account_id: int, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 1 (teller) or higher to withdraw from bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to withdraw from a bank account")
    
    # Logic to withdraw from a bank account would go here
    return {"message": f"Withdrawal from account {account_id} successful!"}


@bank.get("/transfer/{from_account_id}/{to_account_id}")
async def transfer(from_account_id: int, to_account_id: int, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 1 (teller) or higher to transfer between bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to transfer between bank accounts")
    
    # Logic to transfer between bank accounts would go here
    return {"message": f"Transfer from account {from_account_id} to account {to_account_id} successful!"}


@bank.get("/view_transaction_history/{account_id}")
async def view_transaction_history(account_id: int, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 0 (customer) or higher to view transaction history
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to view transaction history")
    
    # Logic to view transaction history would go here
    return {"message": f"Transaction history for account {account_id} displayed successfully!"}


@bank.get("/close_bank_account/{account_id}")
async def close_bank_account(account_id: int, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 1 (teller) or higher to close bank accounts
    if current_user.get("permission", -1) < 1:
        raise HTTPException(status_code=403, detail="Must be a teller or higher to close a bank account")
    
    # Logic to close a bank account would go here
    return {"message": f"Bank account {account_id} closed successfully!"}


@bank.get("/account_info/{account_id}")
async def account_info(account_id: int, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 0 (customer) or higher to view account info
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to view account information")
    
    # Logic to view account information would go here
    return {"message": f"Information for account {account_id} displayed successfully!"}