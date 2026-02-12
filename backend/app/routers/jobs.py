from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, deps

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# --- CREATE (POST) ---
@router.post("/", response_model=schemas.JobResponse)
def create_job(
    job: schemas.JobCreate,
    db: Session = Depends(deps.get_db)
):
    db_job = models.Job(
        title=job.title,
        company=job.company,
        location=job.location,
        type=job.type,
        salary_range=job.salary_range,
        description=job.description,
        required_skills=job.required_skills,
        posted_date=job.posted_date
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return schemas.JobResponse(
        id=db_job.id,
        title=db_job.title,
        company=db_job.company,
        location=db_job.location,
        type=db_job.type,
        salary_range=db_job.salary_range,
        requiredSkills=db_job.required_skills.split(",") if db_job.required_skills else [],
        description=db_job.description,
        postedDate=db_job.posted_date,
        matchScore=0
    )

# --- READ ALL (GET) ---
# MOVED UP: Must be before /{job_id}
@router.get("/all", response_model=List[schemas.JobResponse])
def read_all_jobs(db: Session = Depends(deps.get_db)):
    jobs = db.query(models.Job).all()
    results = []
    for job in jobs:
        results.append(schemas.JobResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            type=job.type,
            salary_range=job.salary_range,
            requiredSkills=job.required_skills.split(",") if job.required_skills else [],
            description=job.description,
            postedDate=job.posted_date,
            matchScore=0
        ))
    return results

# --- RECOMMENDATIONS (GET) ---
# MOVED UP: Must be before /{job_id}
@router.get("/recommendations", response_model=List[schemas.JobResponse])
def get_recommendations(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    jobs = db.query(models.Job).all()
    
    user_skill_names = {s.name.lower().strip() for s in current_user.skills}
    
    results = []
    for job in jobs:
        req_skills_list = [s.strip() for s in job.required_skills.split(",")] if job.required_skills else []
        
        if not req_skills_list:
            score = 0
        else:
            match_count = sum(1 for s in req_skills_list if s.lower() in user_skill_names)
            total_req = len(req_skills_list)
            score = int((match_count / total_req) * 100)
        
        # FILTER: Only show jobs with score >= 50
        if score >= 50:
            job_resp = schemas.JobResponse(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location,
                type=job.type,
                salary_range=job.salary_range,
                requiredSkills=req_skills_list,
                description=job.description,
                postedDate=job.posted_date,
                matchScore=score
            )
            results.append(job_resp)
        
    results.sort(key=lambda x: x.matchScore, reverse=True)
    return results

# --- READ ONE (GET) ---
# This catches everything else, so it must be last among GET requests
@router.get("/{job_id}", response_model=schemas.JobResponse)
def read_job(job_id: int, db: Session = Depends(deps.get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return schemas.JobResponse(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        type=job.type,
        salary_range=job.salary_range,
        requiredSkills=job.required_skills.split(",") if job.required_skills else [],
        description=job.description,
        postedDate=job.posted_date,
        matchScore=0
    )

# --- UPDATE (PUT) ---
@router.put("/{job_id}", response_model=schemas.JobResponse)
def update_job(
    job_id: int, 
    job_update: schemas.JobCreate, 
    db: Session = Depends(deps.get_db)
):
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db_job.title = job_update.title
    db_job.company = job_update.company
    db_job.location = job_update.location
    db_job.type = job_update.type
    db_job.salary_range = job_update.salary_range
    db_job.description = job_update.description
    db_job.required_skills = job_update.required_skills
    db_job.posted_date = job_update.posted_date

    db.commit()
    db.refresh(db_job)
    
    return schemas.JobResponse(
        id=db_job.id,
        title=db_job.title,
        company=db_job.company,
        location=db_job.location,
        type=db_job.type,
        salary_range=db_job.salary_range,
        requiredSkills=db_job.required_skills.split(",") if db_job.required_skills else [],
        description=db_job.description,
        postedDate=db_job.posted_date,
        matchScore=0
    )

# --- DELETE (DELETE) ---
@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(deps.get_db)):
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(db_job)
    db.commit()
    return {"message": "Job deleted successfully"}