from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./orders.db"

# Create the SQLAlchemy engine (the “bridge” between Python and the DB)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session factory for managing database sessions
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base class for all models (tables will inherit from this)
Base = declarative_base()