import os 
from sqlmodel import create_engine, Session
from dotenv import load_dotenv
load_dotenv()

sqlite_url = os.getenv("DATABASE_URL", "sqlite:///./database.sqlite")
engine = create_engine(
    sqlite_url, 
    connect_args={"check_same_thread": False} 
)

def get_session():
    with Session(engine) as session:
        yield session