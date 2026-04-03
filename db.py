from sqlalchemy import create_engine, Column, Integer, String, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

# Database configuration
DATABASE_URL = "sqlite:///./jobs.db"

# Create engine and session factory
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Job model
class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    description = Column(Text)
    link = Column(String, unique=True, index=True)
    match_score = Column(Float, default=0.0)

# Initialize database tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Safe job insertion with duplicate check
def save_job(db: Session, job_data: dict):
    """
    Saves a job to the database if it doesn't already exist.
    Duplicate check is performed on the 'link' field.
    """
    try:
        # Check if job with same link already exists
        existing_job = db.query(Job).filter(Job.link == job_data["link"]).first()
        
        if existing_job:
            # Update match score if it's different (optional, depends on use case)
            if existing_job.match_score != job_data.get("match_score", 0.0):
                existing_job.match_score = job_data.get("match_score", 0.0)
                db.commit()
            return existing_job
        
        # Create new job instance
        new_job = Job(
            title=job_data["title"],
            company=job_data["company"],
            description=job_data["description"],
            link=job_data["link"],
            match_score=job_data.get("match_score", 0.0)
        )
        
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return new_job
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error saving job: {str(e)}")
        return None
