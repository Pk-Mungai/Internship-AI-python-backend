
from datetime import date
import re


def _to_dict(value) -> dict:
    """Convert supported model objects or dictionaries into dictionaries."""
    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    return {}


def _clean_text(value) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _get_candidate_skills(profile: dict) -> list[str]:
    """Collect distinct skills explicitly present in the candidate profile."""
    skills = []
    categories = profile.get("skills_by_category", {})

    if isinstance(categories, dict):
        for category_skills in categories.values():
            if isinstance(category_skills, list):
                for item in category_skills:
                    if isinstance(item, dict):
                        skill = item.get("name") or item.get("skill")
                    else:
                        skill = item
                    skill = _clean_text(skill)
                    if skill:
                        skills.append(skill)

    # Also support profiles that store skills in a flat list.
    for item in profile.get("skills", []):
        if isinstance(item, dict):
            skill = item.get("name") or item.get("skill")
        else:
            skill = item
        skill = _clean_text(skill)
        if skill:
            skills.append(skill)

    return list(dict.fromkeys(skills))


def _get_education_summary(profile: dict) -> str:
    education = profile.get("education", [])

    if isinstance(education, dict):
        education = [education]

    summaries = []

    for item in education:
        record = _to_dict(item)
        qualification = _clean_text(record.get("qualification"))
        field = _clean_text(record.get("field"))
        institution = _clean_text(record.get("institution"))

        description = " ".join(
            part for part in [qualification, f"in {field}" if field else "", f"at {institution}" if institution else ""]
            if part
        )

        if description:
            summaries.append(description)

    return "; ".join(dict.fromkeys(summaries))


def _get_experience_summary(profile: dict) -> str:
    experience = profile.get("experience", [])

    if isinstance(experience, dict):
        experience = [experience]

    summaries = []

    for item in experience:
        record = _to_dict(item)
        role = _clean_text(record.get("role"))
        employer = _clean_text(record.get("employer"))

        if role and employer:
            summaries.append(f"{role} at {employer}")
        elif role:
            summaries.append(role)
        elif employer:
            summaries.append(employer)

    return "; ".join(dict.fromkeys(summaries))


def generate_cover_letter(
    candidate_profile: dict,
    internship,
    applicant_name: str = "[Your Name]",
    contact_details: str = "[Your Email] | [Your Phone Number]",
) -> str:
    """
    Generate a tailored cover letter using only information in the profile
    and internship record.
    """
    if not isinstance(candidate_profile, dict):
        raise TypeError("candidate_profile must be a dictionary.")

    internship_data = _to_dict(internship)

    if not internship_data:
        raise TypeError("internship must be a dictionary or supported model.")

    title = _clean_text(internship_data.get("title"))
    organization = _clean_text(internship_data.get("organization"))

    if not title:
        raise ValueError("Internship title is required.")

    if not organization:
        raise ValueError("Internship organization is required.")

    applicant_name = _clean_text(applicant_name) or "[Your Name]"
    contact_details = _clean_text(contact_details)

    education = _get_education_summary(candidate_profile)
    experience = _get_experience_summary(candidate_profile)
    skills = _get_candidate_skills(candidate_profile)

    paragraphs = [
        f"Dear Hiring Team at {organization},",
        (
            f"I am writing to express my interest in the {title} "
            f"opportunity at {organization}."
        ),
    ]

    if education:
        paragraphs.append(
            f"My educational background includes {education}. "
            "This has contributed to my academic foundation and interest "
            "in developing practical skills in a professional environment."
        )

    if experience:
        paragraphs.append(
            f"My experience includes {experience}. "
            "These experiences have given me opportunities to develop "
            "and apply practical workplace skills."
        )

    if skills:
        paragraphs.append(
            f"My documented skills include {', '.join(skills)}. "
            "I would welcome the opportunity to apply these skills, "
            "learn from your team, and contribute to its work."
        )
    else:
        paragraphs.append(
            "I am interested in gaining practical experience, learning "
            "from your team, and contributing positively to its work."
        )

    paragraphs.extend([
        (
            "Thank you for considering my application. I would appreciate "
            "the opportunity to discuss how my background and interests "
            "align with this internship."
        ),
        "Yours faithfully,",
        applicant_name,
    ])

    if contact_details:
        paragraphs.append(contact_details)

    return "\n\n".join(paragraphs)
