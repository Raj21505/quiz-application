from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Quiz(SQLModel, table=True):
    # __tablename__ = "quiz1" # Renamed table for a fresh start
    
    id: Optional[int] = Field(default=None, primary_key=True)
    Que: str
    A: str
    B: str
    C: str
    D: str
    Ans: str


# Use Postgres in Docker when DATABASE_URL is set, otherwise fall back to local SQLite.
raw_database_url = os.getenv("DATABASE_URL", "sqlite:///./quiz.db")

# Render and similar platforms may provide postgres URLs without explicit driver.
if raw_database_url.startswith("postgres://"):
    DATABASE_URL = "postgresql+psycopg2://" + raw_database_url[len("postgres://"):]
elif raw_database_url.startswith("postgresql://") and "+psycopg2" not in raw_database_url:
    DATABASE_URL = "postgresql+psycopg2://" + raw_database_url[len("postgresql://"):]
else:
    DATABASE_URL = raw_database_url

engine_kwargs = {"echo": False}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)