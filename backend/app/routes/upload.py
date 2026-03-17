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

    try:
        # ---------------- SAVE RESUME ----------------
        resume_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ---------------- EXTRACT RESUME TEXT ----------------
        try:
            resume_text = extract_text_from_pdf(resume_path)
        except Exception as e:
            raise Exception(f"Resume PDF error: {str(e)}")

        # ---------------- HANDLE JOB DESCRIPTION ----------------
        if job_file:
            job_path = os.path.join(UPLOAD_FOLDER, job_file.filename)

            with open(job_path, "wb") as buffer:
                shutil.copyfileobj(job_file.file, buffer)

            try:
                job_description = extract_text_from_pdf(job_path)
            except Exception as e:
                raise Exception(f"Job PDF error: {str(e)}")

        # ---------------- EXTRACT SKILLS ----------------
        resume_skills = extract_skills(resume_text) if resume_text else []
        job_skills = extract_skills(job_description) if job_description else []

        # ---------------- MATCHING ----------------
        matched_skills = list(set(resume_skills) & set(job_skills))
        missing_skills = list(set(job_skills) - set(resume_skills))

        # ---------------- SCORE ----------------
        score = 0
        if job_skills:
            score = (len(matched_skills) / len(job_skills)) * 100

        # ---------------- SEMANTIC ----------------
        if job_skills:
            semantic_score = calculate_similarity(resume_skills, job_skills) * 100
        else:
            semantic_score = 0

        resume_score = (score * 0.7) + (semantic_score * 0.3)

        # ---------------- SUGGESTIONS ----------------
        try:
            suggestions = generate_suggestions(
                resume_skills,
                job_skills,
                missing_skills,
                round(resume_score, 2)
            )
        except Exception:
            suggestions = []

            if missing_skills:
                suggestions.append(
                    f"Missing skills: {', '.join(missing_skills)}"
                )

            if resume_score < 50:
                suggestions.append("Improve alignment with job description.")

            suggestions.append("Add measurable achievements.")

        # ---------------- FINAL RESPONSE ----------------
        return {
            "resume_score": round(resume_score, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "suggestions": suggestions
        }

    except Exception as e:
        return {
            "resume_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": [f"Error: {str(e)}"]
        }