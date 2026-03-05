from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    hashed_password: str
    permission: Optional[int] = Field(default=0, nullable=False, sa_column_kwargs={"server_default": "0"})