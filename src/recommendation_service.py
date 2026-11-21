
from src.matching_engine import rank_internships


def _get_recommendation_level(score: float) -> str:
    if score >= 80:
        return "Strong match"
    if score >= 60:
        return "Good match"
    return "Developing match"


def _build_explanation(result: dict) -> dict:
    breakdown = result["score_breakdown"]

    reasons = []
    improvement_areas = []

    matched_required = result["matched_required_skills"]
    missing_required = result["missing_required_skills"]
    matched_preferred = result["matched_preferred_skills"]
    missing_preferred = result["missing_preferred_skills"]

    if matched_required:
        reasons.append(
            "You demonstrate these required skills: "
            + ", ".join(matched_required) + "."
        )

    if not missing_required:
        reasons.append(
            "You have all the required skills listed for this internship."
        )
    else:
        improvement_areas.append(
            "Develop these missing required skills: "
            + ", ".join(missing_required) + "."
        )

    if matched_preferred:
        reasons.append(
            "Your profile also includes preferred skills: "
            + ", ".join(matched_preferred) + "."
        )

    if missing_preferred:
        improvement_areas.append(
            "Consider developing these additional preferred skills: "
            + ", ".join(missing_preferred) + "."
        )

    if breakdown["education"] >= 75:
        reasons.append(
            "Your educational background is relevant to the stated requirements."
        )
    elif breakdown["education"] > 0:
        reasons.append(
            "Your educational background has some overlap with the stated requirements."
        )
    else:
        improvement_areas.append(
            "Your CV does not currently demonstrate a clear match "
            "with the stated education requirements. Review the requirements "
            "and provide relevant evidence if applicable."
        )

    if breakdown["experience"] >= 75:
        reasons.append(
            "Your practical experience meets or closely matches the experience requirement."
        )
    elif breakdown["experience"] > 0:
        reasons.append(
            "Your practical experience partially meets the stated requirement."
        )
    else:
        improvement_areas.append(
            "Gain or document relevant practical experience where possible."
        )

    if not reasons:
        reasons.append(
            "This opportunity has been included based on the available profile information."
        )

    return {
        "recommendation_level": _get_recommendation_level(
            result["overall_score"]
        ),
        "reasons": reasons,
        "improvement_areas": improvement_areas,
        "eligibility_note": (
            "Review the internship eligibility criteria manually "
            "before applying."
        ),
    }


def recommend_internships(
    candidate_profile: dict,
    internships: list,
    top_n: int | None = None,
) -> list[dict]:
    """
    Rank internships and attach human-readable explanations.

    Only active internships are considered by the matching engine.
    """
    if top_n is not None:
        if isinstance(top_n, bool) or not isinstance(top_n, int):
            raise TypeError("top_n must be an integer or None.")
        if top_n < 0:
            raise ValueError("top_n cannot be negative.")

    results = rank_internships(candidate_profile, internships)

    if top_n is not None:
        results = results[:top_n]

    recommendations = []

    for result in results:
        explanation = _build_explanation(result)

        recommendations.append({
            **result,
            **explanation,
        })

    return recommendations
