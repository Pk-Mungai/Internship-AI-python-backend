def generate_cv_recommendations(missing_skills: list) -> list:
    """
    Generate honest, actionable CV improvement suggestions
    based on skills missing from an internship's requirements.
    """

    recommendations = []

    for skill in missing_skills:
        skill_name = skill.strip().title()

        recommendations.append({
            "skill": skill_name,
            "recommendation": (
                f"If you have experience with {skill_name}, "
                f"make sure it is clearly mentioned in your CV. "
                f"If you are still learning it, consider completing "
                f"a project or course to develop this skill."
            )
        })

    if not recommendations:
        recommendations.append({
            "skill": None,
            "recommendation": (
                "Your CV matches the listed skills for this internship. "
                "Review your project descriptions and make sure they "
                "clearly demonstrate your relevant experience."
            )
        })

    return recommendations