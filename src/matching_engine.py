
from datetime import date, datetime
import re

from src.internship_model import Internship


WEIGHTS = {
    "required_skills": 0.50,
    "preferred_skills": 0.10,
    "education": 0.20,
    "experience": 0.20,
}

EDUCATION_STOP_WORDS = {
    "a", "an", "and", "or", "of", "in", "the", "to",
    "related", "qualification", "qualifications", "degree",
    "diploma", "certificate", "field", "study",
}


def _normalize_skill(skill: str) -> str:
    return re.sub(r"\s+", " ", skill.strip().lower())


def _calculate_skill_match(
    candidate_skills: list[dict],
    internship_skills: list[str],
) -> dict:
    candidate_names = {
        _normalize_skill(item["skill"])
        for item in candidate_skills
    }

    required = {
        _normalize_skill(skill)
        for skill in internship_skills
    }

    matched = sorted(candidate_names & required)
    missing = sorted(required - candidate_names)

    score = (
        len(matched) / len(required) * 100
        if required else 100.0
    )

    return {
        "score": round(score, 2),
        "matched": matched,
        "missing": missing,
    }



def _calculate_education_match(
    education_records: list[dict],
    requirements: list[str],
) -> float:
    if not requirements:
        return 100.0

    if not education_records:
        return 0.0

    qualification_terms = {
        "bachelor", "bachelors", "master", "masters",
        "degree", "diploma", "certificate", "phd",
        "doctor", "associate",
    }

    best_score = 0.0

    for requirement in requirements:
        requirement_words = set(
            re.findall(r"[a-z0-9]+", requirement.lower())
        )

        # Remove generic qualification and requirement wording.
        discipline_words = (
            requirement_words
            - EDUCATION_STOP_WORDS
            - qualification_terms
        )

        for record in education_records:
            candidate_field = str(
                record.get("field") or ""
            ).lower()

            candidate_qualification = str(
                record.get("qualification") or ""
            ).lower()

            if discipline_words:
                candidate_words = set(
                    re.findall(r"[a-z0-9]+", candidate_field)
                )
                overlap = discipline_words & candidate_words

                score = (
                    len(overlap) / len(discipline_words) * 100
                )
            else:
                # If no discipline is specified, compare qualification.
                requested_qualification = (
                    requirement_words & qualification_terms
                )

                candidate_words = set(
                    re.findall(
                        r"[a-z0-9]+",
                        candidate_qualification
                    )
                )

                score = (
                    100.0
                    if requested_qualification
                    & candidate_words
                    else 0.0
                )

            best_score = max(best_score, score)

    return round(best_score, 2)



def _parse_date(value: str | None, is_end_date: bool = False) -> date | None:
    if not value:
        return None

    value = value.strip()

    if value.lower() in {"present", "current"}:
        return date.today()

    for date_format in ("%b %Y", "%B %Y"):
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            pass

    if re.fullmatch(r"(?:19|20)\d{2}", value):
        year = int(value)
        return date(year, 12 if is_end_date else 1, 1)

    return None


def _calculate_experience_months(
    experience_records: list[dict],
) -> int:
    total_months = 0

    for record in experience_records:
        start = _parse_date(record.get("start_date"))
        end = _parse_date(record.get("end_date"), is_end_date=True)

        if not start or not end or end < start:
            continue

        months = (
            (end.year - start.year) * 12
            + end.month - start.month
        )

        total_months += max(0, months)

    return total_months


def match_internship(
    candidate_profile: dict,
    internship: Internship,
) -> dict:
    """
    Calculate an explainable compatibility score between
    a candidate profile and an internship.
    """
    if not isinstance(candidate_profile, dict):
        raise TypeError("Candidate profile must be a dictionary.")

    if not isinstance(internship, Internship):
        raise TypeError("Internship must be an Internship instance.")

    skills = candidate_profile.get("skills", [])
    education = candidate_profile.get("education", [])
    experience = candidate_profile.get("experience", [])

    required_match = _calculate_skill_match(
        skills,
        internship.required_skills,
    )

    preferred_match = _calculate_skill_match(
        skills,
        internship.preferred_skills,
    )

    education_score = _calculate_education_match(
        education,
        internship.education_requirements,
    )

    detected_months = _calculate_experience_months(experience)

    if internship.minimum_experience_months == 0:
        experience_score = 100.0
    else:
        experience_score = min(
            detected_months / internship.minimum_experience_months * 100,
            100.0,
        )
        experience_score = round(experience_score, 2)

    score = (
        required_match["score"] * WEIGHTS["required_skills"]
        + preferred_match["score"] * WEIGHTS["preferred_skills"]
        + education_score * WEIGHTS["education"]
        + experience_score * WEIGHTS["experience"]
    )

    return {
        "internship_id": internship.id,
        "internship_title": internship.title,
        "organization": internship.organization,
        "overall_score": round(score, 2),
        "score_breakdown": {
            "required_skills": required_match["score"],
            "preferred_skills": preferred_match["score"],
            "education": education_score,
            "experience": experience_score,
        },
        "matched_required_skills": required_match["matched"],
        "missing_required_skills": required_match["missing"],
        "matched_preferred_skills": preferred_match["matched"],
        "missing_preferred_skills": preferred_match["missing"],
        "detected_experience_months": detected_months,
        "eligibility": {
            "status": "requires_manual_review",
            "criteria": internship.eligibility_criteria,
        },
    }


def rank_internships(
    candidate_profile: dict,
    internships: list[Internship],
) -> list[dict]:
    """Rank active internships from highest to lowest score."""
    results = [
        match_internship(candidate_profile, internship)
        for internship in internships
        if internship.is_active
    ]

    return sorted(
        results,
        key=lambda result: result["overall_score"],
        reverse=True,
    )
