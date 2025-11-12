from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"
SQL_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(SQL_URL, connect_args={"check_same_thread": False})


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
