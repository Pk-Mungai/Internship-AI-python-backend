
from src.education_extractor import extract_education
from src.experience_extractor import extract_experience
from src.skill_extractor import extract_skills
from src.project_extractor import extract_projects
from src.interest_extractor import extract_interests


SKILL_CATEGORIES = (
    "technical",
    "tools",
    "soft",
    "professional",
)


def build_candidate_profile(cv_text: str) -> dict:
    """
    Build a structured candidate profile from extracted CV text.

    Extracts education, experience, skills, projects, and career
    interests while preserving evidence from the original CV.
    """
    if not isinstance(cv_text, str):
        raise TypeError("CV text must be a string.")

    if not cv_text.strip():
        return {
            "education": [],
            "experience": [],
            "skills": [],
            "technical_skills": [],
            "projects": [],
            "career_interests": [],
            "skills_by_category": {
                category: [] for category in SKILL_CATEGORIES
            },
            "summary": {
                "education_count": 0,
                "experience_count": 0,
                "skill_count": 0,
                "technical_skill_count": 0,
                "project_count": 0,
                "career_interest_count": 0,
            },
        }

    education = extract_education(cv_text)
    experience = extract_experience(cv_text)
    skills = extract_skills(cv_text)
    projects = extract_projects(cv_text)
    career_interests = extract_interests(cv_text)

    skills_by_category = {
        category: [
            skill["skill"]
            for skill in skills
            if skill["category"] == category
        ]
        for category in SKILL_CATEGORIES
    }

    technical_skills = skills_by_category["technical"]

    return {
        "education": education,
        "experience": experience,
        "skills": skills,
        "technical_skills": technical_skills,
        "projects": projects,
        "career_interests": career_interests,
        "skills_by_category": skills_by_category,
        "summary": {
            "education_count": len(education),
            "experience_count": len(experience),
            "skill_count": len(skills),
            "technical_skill_count": len(technical_skills),
            "project_count": len(projects),
            "career_interest_count": len(career_interests),
        },
    }
