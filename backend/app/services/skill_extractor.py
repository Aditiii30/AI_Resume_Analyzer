import os

# Fix path for deployment (works locally + Render)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILLS_FILE = os.path.join(BASE_DIR, "data", "skills.txt")


def load_skills():

    try:
        with open(SKILLS_FILE, "r") as file:
            skills = file.read().splitlines()
        return skills
    except Exception as e:
        print("Error loading skills file:", e)
        return []


def extract_skills(text):

    if not text:
        return []

    skills_list = load_skills()

    found_skills = []

    text = text.lower()

    for skill in skills_list:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))