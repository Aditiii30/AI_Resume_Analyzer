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

Provide 2–3 short professional suggestions.
Return each suggestion on a new line.
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

        # ✅ Convert string → list (IMPORTANT FIX)
        suggestions = [s.strip() for s in result.split("\n") if s.strip()]

        return suggestions

    except Exception as e:

        print("LLM ERROR:", e)

        # ✅ ALWAYS return LIST (IMPORTANT)
        suggestions = []

        if missing_skills:
            skill_list = ", ".join(missing_skills)
            suggestions.append(
                f"Your resume is missing important skills like {skill_list}. Add projects or experience related to these."
            )

        if score < 50:
            suggestions.append(
                "Your resume score is low. Tailor your resume based on the job description."
            )

        suggestions.append(
            "Include measurable achievements like accuracy, performance improvements, or impact."
        )

        return suggestions