from sqlmodel import SQLModel, Field




class User(SQLModel):
    id: int = Field(primary_key=True)
    name: str
    hashed_password: str