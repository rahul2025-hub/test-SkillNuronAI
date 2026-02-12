from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from .models import UserRole

# --- Auth Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    user_name: str
    role: str

# --- Skill Schemas ---
class SkillBase(BaseModel):
    name: str
    level: int = Field(..., ge=0, le=100)
    category: str

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# --- Job Schemas ---
class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    type: str
    salary: str = Field(alias="salary_range")
    requiredSkills: List[str]
    description: str
    postedDate: str
    matchScore: Optional[int] = 0

    class Config:
        from_attributes = True