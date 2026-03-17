from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()



client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_suggestions(resume_skills, job_skills, missing_skills, score):

    prompt = f"""
You are an expert resume reviewer.

Resume skills:
{resume_skills}

Job description skills:
{job_skills}

Missing skills:
{missing_skills}

Match score: {score}

Provide 2–3 professional suggestions to improve the resume.
"""

    try:
        print("Calling LLM...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional career advisor."},
                {"role": "user", "content": prompt}
            ]
        )

        result = response.choices[0].message.content.strip()

        print("LLM RESPONSE:", result)

        return result

    except Exception as e:

        print("LLM ERROR:", e)

        # fallback suggestions if LLM fails
        suggestions = []

        if missing_skills:
            skill_list = ", ".join(missing_skills)
            suggestions.append(
                f"Your resume is missing some important skills such as {skill_list}. Adding projects or experience related to these skills could improve your match."
            )

        if score < 50:
            suggestions.append(
                "Your resume has a relatively low match with the job description. Consider tailoring your resume to highlight relevant technologies."
            )

        suggestions.append(
            "Consider adding measurable achievements in your projects such as accuracy improvements or performance gains."
        )

        return " ".join(suggestions)
