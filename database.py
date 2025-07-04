from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
LocalSession = sessionmaker(bind=engine,autoflush=False,autocommit= False)
Base = declarative_base()



def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()