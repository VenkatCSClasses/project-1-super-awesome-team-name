from argon2 import PasswordHasher
from fastapi import APIRouter, Depends, HTTPException

from admin import Admin
from app_state import bank
from customer import Customer
from server_utils import verify_token
from teller import Teller
from transaction_type import TransactionType

admin = APIRouter()
_PASSWORD_HASHER = PasswordHasher()
_SUSPICIOUS_TRANSACTION_TYPES = {
    TransactionType.DEPOSIT,
    TransactionType.WITHDRAW,
    TransactionType.TRANSFER_DEPOSIT,
    TransactionType.TRANSFER_WITHDRAW,
}


def _require_staff(current_user: dict) -> None:
    if current_user.get("permission", -1) < 1:
        raise HTTPException(status_code=403, detail="Must be a teller or admin to access staff data")


def _require_admin(current_user: dict) -> None:
    if current_user.get("permission", -1) < 2:
        raise HTTPException(status_code=403, detail="Must be an admin to perform this action")


def _account_owner(account_id: int) -> Customer | Teller | Admin | None:
    for user in bank.get_all_users().values():
        if account_id in user.get_owned_accounts():
            return user
    return None


def _is_suspicious(account) -> bool:
    for transaction in account.get_all_transactions().values():
        if transaction.get_type() not in _SUSPICIOUS_TRANSACTION_TYPES:
            continue
        if abs(float(transaction.get_amount())) >= 10000:
            return True
    return False


def _suspicious_reason(account) -> str:
    for transaction in sorted(
        account.get_all_transactions().values(),
        key=lambda tx: tx.get_time(),
        reverse=True,
    ):
        if transaction.get_type() not in _SUSPICIOUS_TRANSACTION_TYPES:
            continue
        if abs(float(transaction.get_amount())) >= 10000:
            return transaction.get_description()
    return ""


def _serialize_account(account) -> dict:
    owner = _account_owner(account.get_account_id())
    is_suspicious = _is_suspicious(account)
    transactions = list(account.get_all_transactions().values())
    last_activity = (
        max(transactions, key=lambda tx: tx.get_time()).get_time().strftime("%Y-%m-%d %H:%M:%S")
        if transactions
        else "N/A"
    )
    return {
        "account_id": account.get_account_id(),
        "user_id": owner.get_id() if owner is not None else None,
        "owner": owner.get_name() if owner is not None else "unknown",
        "account_type": account.get_account_type().upper(),
        "balance": account.get_balance(),
        "status": "FROZEN" if account.is_frozen() else "ACTIVE",
        "is_frozen": account.is_frozen(),
        "is_suspicious": is_suspicious,
        "suspicious_reason": _suspicious_reason(account) if is_suspicious else "",
        "last_activity": last_activity,
    }


def _serialize_user(user) -> dict:
    return {
        "user_id": user.get_id(),
        "username": user.get_name(),
        "permission": user.get_permissions(),
        "status": "ACTIVE",
        "account_count": len(user.get_owned_accounts()),
    }


@admin.get("/users", response_model=dict)
async def list_users(current_user: dict = Depends(verify_token)):
    _require_staff(current_user)
    users = [_serialize_user(user) for user in bank.get_all_users().values()]
    users.sort(key=lambda user: user["user_id"])
    return {"users": users}


@admin.get("/accounts", response_model=dict)
async def list_accounts(current_user: dict = Depends(verify_token)):
    _require_staff(current_user)
    accounts = [_serialize_account(account) for account in bank.get_all_accounts().values()]
    accounts.sort(key=lambda account: account["account_id"])
    return {"accounts": accounts}


@admin.get("/users/{user_id}/accounts", response_model=dict)
async def list_accounts_for_user(user_id: int, current_user: dict = Depends(verify_token)):
    _require_staff(current_user)
    user = bank.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    accounts = [_serialize_account(account) for account in user.get_owned_accounts().values()]
    accounts.sort(key=lambda account: account["account_id"])
    return {"accounts": accounts}


@admin.post("/users", response_model=dict)
async def create_user(payload: dict, current_user: dict = Depends(verify_token)):
    _require_admin(current_user)

    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    permission = int(payload.get("permission", 0))

    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    if permission not in {0, 1, 2}:
        raise HTTPException(status_code=400, detail="Permission must be 0, 1, or 2")
    if bank.get_user_by_name(username) is not None:
        raise HTTPException(status_code=400, detail=f"User @{username} already exists")

    hashed_password = _PASSWORD_HASHER.hash(password)
    if permission == 2:
        user = Admin(username, bank._next_user_id, hashed_password, bank, permissions=permission)
    elif permission == 1:
        user = Teller(username, bank._next_user_id, hashed_password, bank, permissions=permission)
    else:
        user = Customer(username, bank._next_user_id, hashed_password, bank, permissions=permission)

    bank.add_user(user)
    return {"message": f"User @{username} created successfully", "user": _serialize_user(user)}


@admin.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: int, current_user: dict = Depends(verify_token)):
    _require_admin(current_user)

    user = bank.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get_owned_accounts():
        raise HTTPException(status_code=400, detail="Delete or close this user's accounts first")

    username = user.get_name()
    bank.remove_user_by_id(user_id)
    return {"message": f"User @{username} deleted successfully", "user": _serialize_user(user)}


@admin.post("/accounts", response_model=dict)
async def create_account(payload: dict, current_user: dict = Depends(verify_token)):
    _require_staff(current_user)

    user_id = payload.get("user_id")
    account_type = str(payload.get("account_type", "CHECKING")).strip().upper()
    opening_balance = float(payload.get("opening_balance", 0.0))

    if user_id is None:
        raise HTTPException(status_code=400, detail="User id is required")
    if account_type not in {"CHECKING", "SAVINGS"}:
        raise HTTPException(status_code=400, detail="Account type must be CHECKING or SAVINGS")
    if opening_balance < 0:
        raise HTTPException(status_code=400, detail="Opening balance cannot be negative")

    user = bank.get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        account = bank.create_account_for_user(user, account_type, balance=opening_balance)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {
        "message": f"Account {account.get_account_id()} created successfully",
        "account": _serialize_account(account),
    }


@admin.delete("/accounts/{account_id}", response_model=dict)
async def delete_account(account_id: int, current_user: dict = Depends(verify_token)):
    _require_staff(current_user)

    account = bank.get_account_by_id(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    owner = _account_owner(account_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Account owner not found")

    removed = _serialize_account(account)
    owner.get_owned_accounts().pop(account_id, None)
    bank.remove_account(account_id)
    return {"message": f"Account ACC-{account_id} closed successfully", "account": removed}
