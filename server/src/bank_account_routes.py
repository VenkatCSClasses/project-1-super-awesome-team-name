from fastapi import APIRouter, Depends, HTTPException
from server_utils import verify_token
from dotenv import load_dotenv
from app_state import bank
load_dotenv()

# Everything starts at "/bank" for these routes, 
# so the full path for creating a bank account would be "/bank/create_bank_account"
bank_routes = APIRouter()


@bank_routes.post("/create_bank_account", response_model=dict)
async def create_bank_account(form_data: dict, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 1 (teller) or higher to create bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to create a bank account")
    
    # Logic to create a bank account would go here
    user = bank.get_user_by_id(current_user["user_id"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    account = bank.create_account_for_user(user, form_data["bank_account_type"])

    return {"message": f"Bank account of type {form_data['bank_account_type']} created successfully!", "account_id": account.get_id()}

    
@bank_routes.get("/view_bank_account", response_model=dict)
async def view_bank_account(form_data: dict, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 0 (customer) or higher to view bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to view bank account details")
    
    bank.get_user_by_id(current_user["user_id"])
    bank.get_accounts_for_user(bank.get_user_by_id(current_user["user_id"]))

    if current_user.get("permission", -1) == 0:
        # If the user is a customer, only allow them to view their own accounts
        accounts = bank.get_accounts_ids_for_user(bank.get_user_by_id(current_user["user_id"]))
        if form_data["account_id"] not in accounts:
            raise HTTPException(status_code=403, detail="Customers can only view their own accounts")
    # If the user is a teller or admin, they can view any account
    account = bank.get_account_by_id(form_data["account_id"])

    return {
        "message": f"Bank account {form_data['account_id']} details displayed successfully!",
        "account_id": account.get_id(),
        "account_type": account.get_account_type(),
        "balance": account.get_balance(),
        "is_frozen": account.is_frozen()
    }


    # Logic to view a bank account would go here
    return {"message": "Bank account details displayed successfully!"}


@bank_routes.get("/delete_bank_account", response_model=dict)
async def delete_bank_account(current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 1 (teller) or higher to delete bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to delete a bank account")
    
    # Logic to delete a bank account would go here
    return {"message": "Bank account deleted successfully!"}


@bank_routes.get("/get_all_bank_accounts", response_model=dict)
async def view_all_bank_accounts(current_user: dict = Depends(verify_token)):
    # Need to be logged in. 
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to view bank accounts")

    user = bank.get_user_by_id(current_user["user_id"])
    user_accounts = bank.get_accounts_for_user(user)
    if not user_accounts:
        return {"message": "No bank accounts found for this user", "accounts": []}

    accounts = []
    for account in user_accounts:
        accounts.append({
            "account_id": account.get_id(),
            "account_type": account.get_account_type(),
            "balance": account.get_balance(),
            "is_frozen": account.is_frozen()
        })
    return {"message": "All bank accounts displayed successfully!", "accounts": accounts}


@bank_routes.post("/deposit", response_model=dict)
async def deposit(form_data: dict, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 1 (teller) or higher to deposit into bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to deposit into a bank account")
    

    user = bank.get_user_by_id(current_user["user_id"])
    accounts = bank.get_accounts_for_user(user)
    if form_data["account_id"] not in [account.get_id() for account in accounts] and current_user.get("permission", -1) == 0:
        raise HTTPException(status_code=403, detail="Customers can only deposit into their own accounts")

    account = bank.get_account_by_id(form_data["account_id"])
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.is_frozen:
        raise HTTPException(status_code=403, detail="Cannot deposit into a frozen account")

    account.deposit(form_data["amount"])
    return {
        "message": f"Deposit into account {form_data['account_id']} successful!",
        "balance": account.get_balance()
    }


@bank_routes.post("/withdraw", response_model=dict)
async def withdraw(form_data: dict, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 1 (teller) or higher to withdraw from bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to withdraw from a bank account")
    

    user = bank.get_user_by_id(current_user["user_id"])
    accounts = bank.get_accounts_for_user(user)
    if form_data["account_id"] not in [account.get_id() for account in accounts] and current_user.get("permission", -1) == 0:
        raise HTTPException(status_code=403, detail="Customers can only withdraw from their own accounts")

    account = bank.get_account_by_id(form_data["account_id"])
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.is_frozen:
        raise HTTPException(status_code=403, detail="Cannot withdraw from a frozen account")

    account.withdraw(form_data["amount"])
    return {
        "message": f"Withdrawal from account {form_data['account_id']} successful!", 
        "balance": account.get_balance()
    }


@bank_routes.post("/transfer", response_model=dict)
async def transfer(form_data: dict, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 1 (teller) or higher to transfer between bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to transfer between bank accounts")
    
    user = bank.get_user_by_id(current_user["user_id"])
    accounts = bank.get_accounts_for_user(user)
    if form_data["from_account_id"] not in [account.get_id() for account in accounts] and current_user.get("permission", -1) == 0:
        raise HTTPException(status_code=403, detail="Customers can only transfer from their own accounts")
    
    from_account = bank.get_account_by_id(form_data["from_account_id"])
    to_account = bank.get_account_by_id(form_data["to_account_id"])
    if from_account is None or to_account is None:
        raise HTTPException(status_code=404, detail="One or both accounts not found")
    if from_account.is_frozen or to_account.is_frozen:
        raise HTTPException(status_code=403, detail="Cannot transfer from or to a frozen account")
    
    from_account.transfer(to_account, form_data["amount"])

    return {
        "message": f"Transfer from account {form_data['from_account_id']} to account {form_data['to_account_id']} successful!",
        "from_account_balance": from_account.get_balance()
    }

@bank_routes.get("/view_transaction_history/{account_id}", response_model=dict)
async def view_transaction_history(account_id: int, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 0 (customer) or higher to view transaction history
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to view transaction history")
    
    # Logic to view transaction history would go here
    return {"message": f"Transaction history for account {account_id} displayed successfully!"}


@bank_routes.get("/close_bank_account/{account_id}", response_model=dict)
async def close_bank_account(account_id: int, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 1 (teller) or higher to close bank accounts
    if current_user.get("permission", -1) < 1:
        raise HTTPException(status_code=403, detail="Must be a teller or higher to close a bank account")
    
    # Logic to close a bank account would go here
    return {"message": f"Bank account {account_id} closed successfully!"}


@bank_routes.get("/account_info/{account_id}", response_model=dict)
async def account_info(account_id: int, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 0 (customer) or higher to view account info
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to view account information")
    
    # Logic to view account information would go here
    return {"message": f"Information for account {account_id} displayed successfully!"}


@bank_routes.get("/get-suspicious-accounts")
async def get_suspicious_accounts(current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 2 (admin) to view suspicious accounts
    if current_user.get("permission", -1) < 2:
        raise HTTPException(status_code=403, detail="Must be an admin to view suspicious accounts")

    # Logic to get suspicious accounts would go here
    return {"message": "List of suspicious accounts displayed successfully!"}


@bank_routes.get("/toggle-freeze/{account_id}")
async def toggle_freeze(account_id: int, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 2 (admin) or higher to freeze/unfreeze accounts
    if current_user.get("permission", -1) < 2:
        raise HTTPException(status_code=403, detail="Must be an admin or higher to freeze/unfreeze accounts")
    
    # Logic to toggle freeze status of a bank account would go here
    return {"message": f"Freeze status for account {account_id} toggled successfully!"}


@bank_routes.get("/view-frozen-accounts")
async def view_frozen_accounts(current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 2 (admin) or higher to view frozen accounts
    if current_user.get("permission", -1) < 2:
        raise HTTPException(status_code=403, detail="Must be an admin or higher to view frozen accounts")
    
    # Logic to view frozen accounts would go here
    return {"message": "List of frozen accounts displayed successfully!"}


@bank_routes.get("/isfrozen/{account_id}")
async def is_frozen(account_id: int, current_user: dict = Depends(verify_token)):
    # Only allow users with permission level 2 (admin) or higher to check freeze status
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be an loggeded in to check if an account is frozen")

    # Logic to check if an account is frozen would go here
    return {"message": f"Check completed for account {account_id}!"}
