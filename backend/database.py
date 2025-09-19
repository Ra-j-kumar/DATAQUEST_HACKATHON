from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import os

# Connection strings - without authentication for development
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/tickertracker"
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"

# Create SQLAlchemy engine and session for TimescaleDB
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create MongoDB client and database
mongodb_client = MongoClient(MONGODB_CONNECTION_STRING)
mongodb = mongodb_client["tickertracker"]
# Define collections (like tables)
news_collection = mongodb["news"]

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()