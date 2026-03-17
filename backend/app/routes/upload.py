from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import shutil
import os

from backend.app.services.resume_parser import extract_text_from_pdf
from backend.app.services.skill_extractor import extract_skills
from backend.app.services.semantic_matcher import calculate_similarity
from backend.app.services.llm_suggester import generate_suggestions

router = APIRouter()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_file: Optional[UploadFile] = File(None)
):

    # Save resume
    resume_path = f"{UPLOAD_FOLDER}/{file.filename}"

    with open(resume_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_text = extract_text_from_pdf(resume_path)

    # If job description PDF uploaded
    if job_file:

        job_path = f"{UPLOAD_FOLDER}/{job_file.filename}"

        with open(job_path, "wb") as buffer:
            shutil.copyfileobj(job_file.file, buffer)

        job_description = extract_text_from_pdf(job_path)

    # Extract skills
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description) if job_description else []
    

    # Matched skills
    matched_skills = list(set(resume_skills) & set(job_skills))

    # Missing skills
    missing_skills = list(set(job_skills) - set(resume_skills))

    # Skill match score
    score = 0
    if len(job_skills) > 0:
        score = (len(matched_skills) / len(job_skills)) * 100

    # Semantic similarity
    semantic_score = calculate_similarity(resume_skills, job_skills) * 100

    # Final resume score
    resume_score = (score * 0.7) + (semantic_score * 0.3)

    # Try LLM suggestions
    try:

        suggestions = generate_suggestions(
            resume_skills,
            job_skills,
            missing_skills,
            round(resume_score, 2)
        )

    except:

        # Fallback rule-based suggestions
        suggestions = []

        if missing_skills:
            skill_list = ", ".join(missing_skills)

            suggestions.append(
                f"Your resume is missing some important skills such as {skill_list}. Adding projects or experience related to these skills could improve your match."
            )

        if resume_score < 50:
            suggestions.append(
                "Your resume currently has a low match score. Consider tailoring your resume to highlight technologies mentioned in the job description."
            )

        suggestions.append(
            "Consider including measurable achievements in your projects such as performance improvements or model accuracy gains."
        )

    return {
        "resume_score": round(resume_score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions
    }