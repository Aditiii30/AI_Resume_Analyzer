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
        # -------------------------------
        # Save resume safely
        # -------------------------------
        resume_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract resume text
        try:
            resume_text = extract_text_from_pdf(resume_path)
        except Exception as e:
            return {"error": f"Error reading resume PDF: {str(e)}"}

        # -------------------------------
        # Handle job description
        # -------------------------------
        if job_file:
            job_path = os.path.join(UPLOAD_FOLDER, job_file.filename)

            with open(job_path, "wb") as buffer:
                shutil.copyfileobj(job_file.file, buffer)

            try:
                job_description = extract_text_from_pdf(job_path)
            except Exception as e:
                return {"error": f"Error reading job PDF: {str(e)}"}

        # -------------------------------
        # Extract skills safely
        # -------------------------------
        resume_skills = extract_skills(resume_text) if resume_text else []
        job_skills = extract_skills(job_description) if job_description else []

        # -------------------------------
        # Skill comparison
        # -------------------------------
        matched_skills = list(set(resume_skills) & set(job_skills))
        missing_skills = list(set(job_skills) - set(resume_skills))

        # -------------------------------
        # Skill score
        # -------------------------------
        score = 0
        if len(job_skills) > 0:
            score = (len(matched_skills) / len(job_skills)) * 100

        # -------------------------------
        # Semantic similarity (SAFE)
        # -------------------------------
        if job_skills:
            semantic_score = calculate_similarity(resume_skills, job_skills) * 100
        else:
            semantic_score = 0

        # Final score
        resume_score = (score * 0.7) + (semantic_score * 0.3)

        # -------------------------------
        # Suggestions (SAFE)
        # -------------------------------
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
                skill_list = ", ".join(missing_skills)
                suggestions.append(
                    f"Your resume is missing important skills such as {skill_list}. Add projects or experience for better matching."
                )

            if resume_score < 50:
                suggestions.append(
                    "Your resume has a low match score. Try aligning it more with the job description."
                )

            suggestions.append(
                "Include measurable achievements (accuracy, performance, impact) in your projects."
            )

        # -------------------------------
        # Final response
        # -------------------------------
        return {
            "resume_score": round(resume_score, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "suggestions": suggestions
        }

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}