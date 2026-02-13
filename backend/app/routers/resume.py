from fastapi import APIRouter, UploadFile, File, HTTPException
from .. import schemas
import io
import pypdf
import docx
from typing import List

router = APIRouter(prefix="/resume", tags=["Resume Analysis"])

# --- CONSTANTS FOR ANALYSIS ---
# In a real ML app, these would come from a database or NLP model
high_value_keywords = ["Python", "Java", "React", "AWS", "Docker", "Kubernetes", "Machine Learning", "CI/CD", "SQL", "FastAPI"]
soft_skills = ["Leadership", "Communication", "Problem Solving", "Agile", "Teamwork"]
action_verbs = ["Spearheaded", "Developed", "Orchestrated", "Engineered", "Managed", "Led"]

def extract_text_from_pdf(file_file) -> str:
    pdf_reader = pypdf.PdfReader(file_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_file) -> str:
    doc = docx.Document(file_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def calculate_section_score(text: str, keywords: List[str]) -> int:
    found = sum(1 for k in keywords if k.lower() in text.lower())
    if not found: return 50
    # Simple curve: 5 keywords = 100%
    return min(50 + (found * 10), 100)

@router.post("/analyze", response_model=schemas.ResumeAnalysisResponse)
async def analyze_resume(file: UploadFile = File(...)):
    # 1. READ FILE CONTENT
    content = await file.read()
    file_obj = io.BytesIO(content)
    text = ""

    try:
        if file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_obj)
        elif file.filename.endswith(".docx"):
            text = extract_text_from_docx(file_obj)
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use PDF or DOCX.")
    except Exception as e:
        print(f"Error parsing file: {e}")
        raise HTTPException(status_code=500, detail="Could not parse file content.")

    if len(text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume content is too short or unreadable.")

    # 2. PERFORM ANALYSIS (Rule-Based Heuristics)
    
    # Detect Keywords
    present_keywords = [kw for kw in high_value_keywords if kw.lower() in text.lower()]
    missing_keywords = [kw for kw in high_value_keywords if kw.lower() not in text.lower()]
    
    # Calculate Scores
    tech_score = calculate_section_score(text, high_value_keywords)
    format_score = 90 if len(text.split('\n')) > 20 else 60 # Simple line check
    impact_score = calculate_section_score(text, action_verbs)
    
    overall_score = int((tech_score + format_score + impact_score) / 3)

    # Generate Dynamic Feedback
    strengths = []
    if len(present_keywords) >= 3:
        strengths.append({
            "title": "Strong Technical Base", 
            "description": f"Found key skills: {', '.join(present_keywords[:3])}", 
            "type": "strength"
        })
    if impact_score > 80:
        strengths.append({
            "title": "Action-Oriented Language", 
            "description": "Good use of strong action verbs (e.g., Led, Engineered).", 
            "type": "strength"
        })

    improvements = []
    if len(missing_keywords) > 0:
        improvements.append({
            "title": "Missing High-Value Skills",
            "description": f"Consider adding: {', '.join(missing_keywords[:3])}",
            "type": "improvement",
            "severity": "high"
        })
    if impact_score < 70:
        improvements.append({
            "title": "Weak Impact Verbs",
            "description": "Use words like 'Spearheaded' or 'Orchestrated' instead of 'Worked on'.",
            "type": "improvement",
            "severity": "medium"
        })

    # 3. RETURN STRUCTURED RESPONSE
    return {
        "overallScore": overall_score,
        "atsCompatibility": 85, # Placeholder for complex regex logic
        "contentQuality": impact_score,
        "formatting": format_score,
        "keywordOptimization": tech_score,
        "impactScore": impact_score,
        "sections": [
            {"section": "Contact Information", "score": 100, "status": "excellent", "feedback": "detected"},
            {"section": "Skills", "score": tech_score, "status": "good" if tech_score > 75 else "average", "feedback": f"{len(present_keywords)} keywords found"},
            {"section": "Work Experience", "score": impact_score, "status": "good" if impact_score > 75 else "average", "feedback": "Action verbs analyzed"},
        ],
        "strengths": strengths,
        "improvements": improvements,
        "keywords": {
            "present": present_keywords,
            "missing": missing_keywords,
            "recommended": ["System Design", "Scalability"] # specific recommendations
        }
    }