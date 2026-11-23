
import re


# Skills our application can recognize
SKILL_DATABASE = {
    "Programming": [
        "python", "java", "kotlin", "javascript",
        "c++", "c#", "php", "dart", "ruby"
    ],

    "Web Development": [
        "html", "css", "react", "angular",
        "node.js", "laravel", "django", "fastapi"
    ],

    "Database Management": [
        "mysql", "postgresql", "sql", "mongodb",
        "sqlite", "oracle"
    ],

    "Data Science and AI": [
        "machine learning", "artificial intelligence",
        "data analysis", "pandas", "numpy",
        "tensorflow", "power bi"
    ],

    "Cybersecurity": [
        "network security", "cybersecurity",
        "ethical hacking", "penetration testing",
        "firewalls", "cryptography"
    ],

    "Mobile Development": [
        "android", "android studio", "jetpack compose",
        "flutter", "kotlin"
    ],

    "Networking": [
        "computer networks", "network administration",
        "cisco", "routing", "switching"
    ]
}


def extract_skills(cv_text: str) -> dict:
    """
    Identify skills mentioned in the student's CV.
    """

    text = cv_text.lower()

    identified_skills = {}

    for category, skills in SKILL_DATABASE.items():

        matched_skills = []

        for skill in skills:

            # Match complete terms rather than partial words
            pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

            if re.search(pattern, text):
                matched_skills.append(skill)

        if matched_skills:
            identified_skills[category] = matched_skills

    return identified_skills


def extract_education(cv_text: str) -> list:
    """
    Identify lines that may contain education information.
    """

    education_keywords = [
        "university",
        "college",
        "bachelor",
        "degree",
        "diploma",
        "education",
        "graduation",
        "student"
    ]

    education = []

    for line in cv_text.splitlines():

        cleaned_line = line.strip()

        if cleaned_line and any(
            keyword in cleaned_line.lower()
            for keyword in education_keywords
        ):
            education.append(cleaned_line)

    return education


def analyze_cv(cv_text: str) -> dict:
    """
    Generate a structured profile from extracted CV text.
    """

    if not cv_text or not cv_text.strip():
        raise ValueError("CV text cannot be empty.")

    skills = extract_skills(cv_text)
    education = extract_education(cv_text)

    total_skills = sum(
        len(skill_list)
        for skill_list in skills.values()
    )

    return {
        "skills": skills,
        "education": education,
        "total_skills_identified": total_skills
    }
