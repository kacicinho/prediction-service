from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Declare global variables
engine = None
SessionLocal = None
Base = None

def init_db():
    """
    Initialize the database by loading environment variables and setting up the
    SQLAlchemy engine, session, and base.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get PostgreSQL credentials from environment variables
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    # Define the DATABASE_URL
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # SQLAlchemy setup
    global engine, SessionLocal, Base
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    # Initialize the tables (this could be handled separately if using migrations)
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Retrieve the session for the current request.
    Using Flask's g to store the session ensures it's reused during the same request.
    """
    if 'db' not in g:
        g.db = SessionLocal()  # Create a session for the request
    return g.db

# Define the Image model
class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

def get_image_by_id(image_id):
    """
    Fetch an image from the PostgreSQL database by its ID.
    :param image_id: ID of the image to fetch
    :return: Dictionary with image details or None if not found
    """
    db = get_db()
    image = db.query(Image).filter(Image.id == image_id).first()
    if image:
        return {
            "id": image.id,
            "url": image.url,
            "name": image.name,
            "description": image.description,
        }
    return None
