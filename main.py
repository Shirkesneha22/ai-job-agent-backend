from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import os

# Local imports
import scraper
import ai
import db
from pydantic import BaseModel

app = FastAPI(
    title="AI Job Agent API",
    description="API for scraping jobs, matching with resume, and optimizing resume using AI.",
    version="1.0.0"
)

# Initialize database
db.init_db()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class OptimizeRequest(BaseModel):
    job_description: str

class OptimizeResponse(BaseModel):
    updated_resume: str
    changes_made: List[str]

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    description: str
    link: str
    match_score: float

    class Config:
        from_attributes = True

class ScrapeResponse(BaseModel):
    message: str
    count: int
    jobs: List[JobResponse]

# --- Dependencies ---

get_db = db.get_db

# --- Helper Functions ---

def read_resume() -> str:
    """Reads the resume content from the local resume.txt file."""
    file_path = os.path.join(os.path.dirname(__file__), "resume.txt")
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading resume: {e}")
        return ""

# --- Endpoints ---

@app.get("/", tags=["General"])
async def root():
    """Welcome endpoint."""
    return {"message": "Welcome to AI Job Agent API", "docs": "/docs"}

@app.get("/health", tags=["General"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/jobs", response_model=List[JobResponse], tags=["Jobs"])
async def get_jobs(database: Session = Depends(get_db)):
    """Fetches all jobs from the database."""
    return database.query(db.Job).all()

@app.post("/scrape", response_model=ScrapeResponse, tags=["Jobs"])
async def scrape_jobs(database: Session = Depends(get_db)):
    """
    Scrapes job boards (Lever/Greenhouse), calculates match scores, 
    and saves new/updated jobs to the database.
    """
    try:
        # 1. Scrape jobs using Playwright
        lever_jobs = await scraper.scrape_lever()
        greenhouse_jobs = await scraper.scrape_greenhouse()
        all_scraped_jobs = lever_jobs + greenhouse_jobs
        
        # 2. Read resume for matching
        resume = read_resume()
        
        saved_jobs = []
        
        # 3. Process and save jobs
        for job_data in all_scraped_jobs:
            # Calculate AI match score if resume is available
            match_score = 0.0
            if resume:
                match_score = ai.match_job(resume, job_data.get("description", ""))
            
            job_data["match_score"] = float(match_score)
            
            # Save safely with duplicate checking (handled in db.py)
            job = db.save_job(database, job_data)
            if job:
                saved_jobs.append(job)
        
        return {
            "message": f"Successfully processed {len(all_scraped_jobs)} jobs. Total unique jobs in database: {len(saved_jobs)}",
            "count": len(saved_jobs),
            "jobs": saved_jobs
        }
        
    except Exception as e:
        database.rollback()
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")
        
    except Exception as e:
        database.rollback()
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.post("/optimize", response_model=OptimizeResponse, tags=["AI"])
async def optimize(request: OptimizeRequest):
    """
    Uses AI to optimize the current resume for a specific job description.
    """
    resume = read_resume()
    if not resume:
        raise HTTPException(
            status_code=400, 
            detail="Resume not found. Please create a 'resume.txt' file in the backend directory."
        )
    
    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
    
    try:
        optimization_results = ai.optimize_resume(resume, request.job_description)
        # Ensure the response matches our OptimizeResponse model
        return {
            "updated_resume": optimization_results.get("updated_resume", resume),
            "changes_made": optimization_results.get("changes_made", ["AI failed to provide a summary of changes."])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI optimization failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
