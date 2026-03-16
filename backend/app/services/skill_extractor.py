SKILLS_FILE = "data/skills.txt"


def load_skills():

    with open(SKILLS_FILE, "r") as file:
        skills = file.read().splitlines()

    return skills


def extract_skills(text):

    skills_list = load_skills()

    found_skills = []

    text = text.lower()

    for skill in skills_list:
        if skill in text:
            found_skills.append(skill)

    return found_skills