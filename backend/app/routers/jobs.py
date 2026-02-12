from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, deps

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/recommendations", response_model=List[schemas.JobResponse])
def get_recommendations(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # Fetch all jobs (In a real app, you'd filter via SQL)
    jobs = db.query(models.Job).all()
    
    # Simple Mock Matching Algorithm
    # 1. Get user skill names
    user_skill_names = {s.name.lower() for s in current_user.skills}
    
    results = []
    for job in jobs:
        req_skills = job.required_skills.split(",") if job.required_skills else []
        match_count = sum(1 for s in req_skills if s.strip().lower() in user_skill_names)
        
        # Calculate Mock Score
        total_req = len(req_skills) if len(req_skills) > 0 else 1
        score = int((match_count / total_req) * 100)
        
        # Create response object
        job_resp = schemas.JobResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            type=job.type,
            salary_range=job.salary_range,
            requiredSkills=req_skills,
            description=job.description,
            postedDate=job.posted_date,
            matchScore=score
        )
        results.append(job_resp)
        
    # Sort by match score
    results.sort(key=lambda x: x.matchScore, reverse=True)
    return results