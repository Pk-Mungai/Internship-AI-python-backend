
from ai_analyzer import analyze_cv


def get_flat_skills(analysis: dict) -> set:
    """Convert categorized skills into a lowercase set."""
    skills = set()

    for skill_list in analysis.get("skills", {}).values():
        for skill in skill_list:
            skills.add(skill.lower().strip())

    return skills


def calculate_match(cv_text: str, requirements) -> dict:
    """Compare CV skills with an internship's required skills."""

    analysis = analyze_cv(cv_text)
    student_skills = get_flat_skills(analysis)

    matched_skills = []
    missing_skills = []

    total_weight = 0
    matched_weight = 0

    for requirement in requirements or []:
        if not isinstance(requirement, dict):
            continue

        skill = requirement.get("skill", "").strip().lower()
        importance = requirement.get("importance", "preferred").lower()

        if not skill:
            continue

        weight = 2 if importance == "mandatory" else 1

        total_weight += weight

        if skill in student_skills:
            matched_skills.append(skill)
            matched_weight += weight
        else:
            missing_skills.append(skill)

    if total_weight == 0:
        match_score = 0
    else:
        match_score = round(
            (matched_weight / total_weight) * 100
        )

    return {
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }
