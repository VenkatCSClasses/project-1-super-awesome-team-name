from fastapi import APIRouter, Depends, HTTPException
from server_utils import verify_token
from dotenv import load_dotenv
from app_state import bank
from transaction_type import TransactionType
load_dotenv()

_SUSPICIOUS_TRANSACTION_TYPES = {
    TransactionType.DEPOSIT,
    TransactionType.WITHDRAW,
    TransactionType.TRANSFER_DEPOSIT,
    TransactionType.TRANSFER_WITHDRAW,
}

# Everything starts at "/bank" for these routes, 
# so the full path for creating a bank account would be "/bank/create_bank_account"
bank_routes = APIRouter()


@bank_routes.post("/create_bank_account", response_model=dict)
async def create_bank_account(form_data: dict, current_user: dict = Depends(verify_token)):
    """Create a new bank account for the current user"""
    # Only allow users with permission level 1 (teller) or higher to create bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to create a bank account")
    
    # Logic to create a bank account would go here
    user = bank.get_user_by_id(current_user["user_id"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    account = bank.create_account_for_user(user, form_data["bank_account_type"], balance=form_data.get("initial_deposit", 0.00))

    return {"message": f"Bank account of type {form_data['bank_account_type']} created successfully!", "account_id": account.get_account_id()}

    
@bank_routes.get("/view_bank_account", response_model=dict)
async def view_bank_account(form_data: dict, current_user: dict = Depends(verify_token)):
    """View details about a specific bank account"""
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
        "account_id": account.get_account_id(),
        "account_type": account.get_account_type(),
        "balance": account.get_balance(),
        "is_frozen": account.is_frozen()
    }


    # Logic to view a bank account would go here
    return {"message": "Bank account details displayed successfully!"}


@bank_routes.get("/get_all_bank_accounts", response_model=dict)
async def view_all_bank_accounts(current_user: dict = Depends(verify_token)):
    """View all bank accounts within the bank. 
    Only tellers and admins can view all accounts, customers can only view their own accounts"""
    # Need to be logged in. 
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to view bank accounts")

    user = bank.get_user_by_id(current_user["user_id"])
    user_accounts = bank.get_accounts_for_user(user)
    if not user_accounts:
        return {"message": "No bank accounts found for this user", "accounts": []}

    accounts = []
    for account in user_accounts.values():
        accounts.append({
            "account_id": account.get_account_id(),
            "account_type": account.get_account_type(),
            "balance": account.get_balance(),
            "is_frozen": account.is_frozen()
        })
    return {"message": "All bank accounts displayed successfully!", "accounts": accounts}


@bank_routes.get("/get_all_bank_account_ids", response_model=dict)
async def get_all_bank_account_ids(current_user: dict = Depends(verify_token)):
    """Return all account ids so users can choose transfer destinations."""
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to view bank account ids")

    user = bank.get_user_by_id(current_user["user_id"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    account_ids = [account.get_account_id() for account in bank.get_all_accounts().values()]
    return {"message": "All bank account ids displayed successfully!", "account_ids": account_ids}


@bank_routes.post("/deposit", response_model=dict)
async def deposit(form_data: dict, current_user: dict = Depends(verify_token)):
    """Deposit money into a bank account"""
    # Only allow users with permission level 1 (teller) or higher to deposit into bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to deposit into a bank account")
    

    user = bank.get_user_by_id(current_user["user_id"])
    accounts = bank.get_accounts_for_user(user)
    if form_data["account_id"] not in [account.get_account_id() for account in accounts.values()] and current_user.get("permission", -1) == 0:
        raise HTTPException(status_code=403, detail="Customers can only deposit into their own accounts")

    account = bank.get_account_by_id(form_data["account_id"])
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.is_frozen():
        raise HTTPException(status_code=403, detail="Cannot deposit into a frozen account")

    account.deposit(form_data["amount"])
    return {
        "message": f"Deposit into account {form_data['account_id']} successful!",
        "balance": account.get_balance()
    }


@bank_routes.post("/withdraw", response_model=dict)
async def withdraw(form_data: dict, current_user: dict = Depends(verify_token)):
    """Withdraw money from a bank account"""
    # Only allow users with permission level 1 (teller) or higher to withdraw from bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to withdraw from a bank account")
    

    user = bank.get_user_by_id(current_user["user_id"])
    accounts = bank.get_accounts_for_user(user)
    if form_data["account_id"] not in [account.get_account_id() for account in accounts.values()] and current_user.get("permission", -1) == 0:
        raise HTTPException(status_code=403, detail="Customers can only withdraw from their own accounts")

    account = bank.get_account_by_id(form_data["account_id"])
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.is_frozen():
        raise HTTPException(status_code=403, detail="Cannot withdraw from a frozen account")

    account.withdraw(form_data["amount"])
    return {
        "message": f"Withdrawal from account {form_data['account_id']} successful!", 
        "balance": account.get_balance()
    }


@bank_routes.post("/transfer", response_model=dict)
async def transfer(form_data: dict, current_user: dict = Depends(verify_token)):
    """Transfer money from one account to another"""
    # Only allow users with permission level 1 (teller) or higher to transfer between bank accounts
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to transfer between bank accounts")
    
    user = bank.get_user_by_id(current_user["user_id"])
    accounts = bank.get_accounts_for_user(user)
    if form_data["from_account_id"] not in [account.get_account_id() for account in accounts.values()] and current_user.get("permission", -1) == 0:
        raise HTTPException(status_code=403, detail="Customers can only transfer from their own accounts")
    if form_data["from_account_id"] == form_data["to_account_id"]:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")
    
    from_account = bank.get_account_by_id(form_data["from_account_id"])
    to_account = bank.get_account_by_id(form_data["to_account_id"])
    if from_account is None or to_account is None:
        raise HTTPException(status_code=404, detail="One or both accounts not found")
    if from_account.is_frozen() or to_account.is_frozen():
        raise HTTPException(status_code=403, detail="Cannot transfer from or to a frozen account")
    
    from_account.transfer(form_data["amount"], to_account)

    return {
        "message": f"Transfer from account {form_data['from_account_id']} to account {form_data['to_account_id']} successful!",
        "from_account_balance": from_account.get_balance()
    }

@bank_routes.get("/view_transaction_history/{account_id}", response_model=dict)
async def view_transaction_history(account_id: int, current_user: dict = Depends(verify_token)):
    """View the transaction history for a specific bank account"""
    # Only allow users with permission level 0 (customer) or higher to view transaction history
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to view transaction history")
    
    if current_user.get("permission", -1) == 0:
        # If the user is a customer, only allow them to view their own accounts
        user = bank.get_user_by_id(current_user["user_id"])
        accounts = bank.get_accounts_for_user(user)
        if account_id not in [account.get_account_id() for account in accounts.values()]:
            raise HTTPException(status_code=403, detail="Customers can only view transaction history for their own accounts")
    # If the user is a teller or admin, they can view transaction history for any account
    account = bank.get_account_by_id(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    transactions = []
    for transaction in account.get_all_transactions().values():
        transactions.append(
            {
                "absolute_transaction_id": transaction.get_absolute_id(),
                "relative_transaction_id": transaction.get_relative_id(),
                "account_id": transaction.get_account_id(),
                "amount": transaction.get_amount(),
                "balance": transaction.get_post_balance(),
                "type": transaction.get_type().name,
                "description": transaction.get_description(),
                "transfer_account_id": transaction.get_transfer_account_id(),
                "datetime_str": transaction.get_time().isoformat(),
            }
        )

    return {
        "message": f"Transaction history for account {account_id} displayed successfully!",
        "transactions": transactions
    }


@bank_routes.get("/close_bank_account/{account_id}", response_model=dict)
async def close_bank_account(account_id: int, current_user: dict = Depends(verify_token)):
    """Close a bank account"""
    # Only allow users with permission level 1 (teller) or higher to close bank accounts
    if current_user.get("permission", -1) < 1:
        raise HTTPException(status_code=403, detail="Must be a teller or higher to close a bank account")
    
    account = bank.get_account_by_id(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    owner = None
    for user in bank.get_all_users().values():
        if account_id in user.get_owned_accounts():
            owner = user
            break
    if owner is None:
        raise HTTPException(status_code=404, detail="Account owner not found")

    owner.get_owned_accounts().pop(account_id, None)
    bank.remove_account(account_id)
    return {"message": f"Bank account {account_id} closed successfully!"}


@bank_routes.get("/account_info/{account_id}", response_model=dict)
async def account_info(account_id: int, current_user: dict = Depends(verify_token)):
    """Get information about a specific bank account"""
    # Only allow users with permission level 0 (customer) or higher to view account info
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be logged in to view account information")
    
    try: 
        account = bank.get_account_by_id(account_id)
        account_info = {
            "message": f"Account information for account {account_id} displayed successfully!",
            "account_id": account.get_account_id(),
            "account_type": account.get_account_type(),
            "balance": account.get_balance(),
            "is_frozen": account.is_frozen()
        }
        return account_info
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))



@bank_routes.get("/get-suspicious-accounts")
async def get_suspicious_accounts(current_user: dict = Depends(verify_token)):
    """Get a list of all accounts with suspicious activity"""
    # Only allow users with permission level 2 (admin) to view suspicious accounts
    if current_user.get("permission", -1) < 2:
        raise HTTPException(status_code=403, detail="Must be an admin to view suspicious accounts")

    suspicious_accounts = []
    for account in bank.get_all_accounts().values():
        matching_transaction = None
        for transaction in account.get_all_transactions().values():
            if transaction.get_type() not in _SUSPICIOUS_TRANSACTION_TYPES:
                continue
            if abs(float(transaction.get_amount())) >= 10000:
                matching_transaction = transaction
                break
        if matching_transaction is None:
            continue

        owner = None
        for user in bank.get_all_users().values():
            if account.get_account_id() in user.get_owned_accounts():
                owner = user
                break

        transactions = list(account.get_all_transactions().values())
        suspicious_accounts.append(
            {
                "account_id": account.get_account_id(),
                "user_id": owner.get_id() if owner is not None else None,
                "owner": owner.get_name() if owner is not None else "unknown",
                "account_type": account.get_account_type().upper(),
                "balance": account.get_balance(),
                "status": "FROZEN" if account.is_frozen() else "ACTIVE",
                "is_frozen": account.is_frozen(),
                "is_suspicious": True,
                "suspicious_reason": matching_transaction.get_description(),
                "last_activity": max(transactions, key=lambda tx: tx.get_time()).get_time().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return {
        "message": "Suspicious accounts retrieved successfully!",
        "suspicious_accounts": suspicious_accounts
    }



@bank_routes.get("/toggle-freeze/{account_id}")
async def toggle_freeze(account_id: int, current_user: dict = Depends(verify_token)):
    """Freeze or unfreeze an account based on its current status"""
    # Only allow users with permission level 2 (admin) or higher to freeze/unfreeze accounts
    if current_user.get("permission", -1) < 2:
        raise HTTPException(status_code=403, detail="Must be an admin or higher to freeze/unfreeze accounts")
    

    account = bank.get_account_by_id(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    account.toggle_frozen()
    return {
        "message": f"Freeze status for account {account_id} toggled successfully!",
        "is_frozen": account.is_frozen()
    }


@bank_routes.get("/isfrozen/{account_id}")
async def is_frozen(account_id: int, current_user: dict = Depends(verify_token)):
    """Check if an account is frozen"""

    # Only allow users with permission level 2 (admin) or higher to check freeze status
    if current_user.get("permission", -1) < 0:
        raise HTTPException(status_code=403, detail="Must be an loggeded in to check if an account is frozen")

    # Logic to check if an account is frozen would go here
    account = bank.get_account_by_id(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return {
        "message": f"Freeze status for account {account_id} retrieved successfully!",
        "is_frozen": account.is_frozen()
    }
