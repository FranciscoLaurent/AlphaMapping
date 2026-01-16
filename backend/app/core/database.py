from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
import os

# Ensure data directory exists
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),  "..", "data")
os.makedirs(data_dir, exist_ok=True)

# Create engine with proper SQLite URL
db_path = os.path.join(data_dir, "alpha_mapping.db")
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
