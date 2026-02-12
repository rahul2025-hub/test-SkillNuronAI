from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, skills, jobs
from . import models

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SkillNuron AI Backend")

# CORS Setup
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed Mock Jobs (Optional Helper)
@app.on_event("startup")
def seed_db():
    from .database import SessionLocal
    db = SessionLocal()
    if db.query(models.Job).count() == 0:
        mock_jobs = [
            models.Job(
                title="Senior Full Stack Developer",
                company="TechCorp Inc.",
                location="Remote",
                type="Full-time",
                salary_range="$120k - $160k",
                description="We are looking for an experienced Full Stack Developer...",
                required_skills="React,Node.js,TypeScript,MongoDB,AWS",
                posted_date="2025-11-20"
            ),
             models.Job(
                title="Frontend Developer (React)",
                company="StartupXYZ",
                location="San Francisco, CA",
                type="Full-time",
                salary_range="$100k - $140k",
                description="Join our fast-growing startup...",
                required_skills="React,JavaScript,HTML/CSS,Git",
                posted_date="2025-11-22"
            )
        ]
        db.add_all(mock_jobs)
        db.commit()
    db.close()

# Include Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(skills.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to SkillNuron AI API"}