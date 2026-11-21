
import pytest

from src.internship_model import Internship
from src.matching_engine import match_internship, rank_internships


@pytest.fixture
def candidate_profile():
    return {
        "education": [
            {
                "qualification": "Bachelor of Science",
                "field": "Computer Science",
                "institution": "University of Nairobi",
                "graduation_year": 2026,
            }
        ],
        "experience": [
            {
                "role": "Software Developer Intern",
                "employer": "ABC Technologies",
                "start_date": "Jan 2023",
                "end_date": "Jan 2024",
                "responsibilities": ["Developed Python applications"],
                "evidence": ["Developed Python applications"],
            }
        ],
        "skills": [
            {"skill": "python", "category": "technical"},
            {"skill": "sql", "category": "technical"},
            {"skill": "git", "category": "tools"},
        ],
    }


@pytest.fixture
def internship():
    return Internship(
        id="INT-001",
        title="Software Development Intern",
        organization="ABC Technologies",
        description="Assist with software development.",
        required_skills=["Python", "SQL", "Java"],
        preferred_skills=["Git", "Docker"],
        education_requirements=["Computer Science"],
        minimum_experience_months=12,
        eligibility_criteria=["Currently enrolled student"],
        location="Nairobi, Kenya",
        work_arrangement="hybrid",
        is_active=True,
    )


def test_calculates_overall_score(candidate_profile, internship):
    result = match_internship(candidate_profile, internship)

    assert 0 <= result["overall_score"] <= 100
    assert result["overall_score"] == 78.34

def test_identifies_matched_required_skills(
    candidate_profile, internship
):
    result = match_internship(candidate_profile, internship)

    assert result["matched_required_skills"] == ["python", "sql"]


def test_identifies_missing_required_skills(
    candidate_profile, internship
):
    result = match_internship(candidate_profile, internship)

    assert result["missing_required_skills"] == ["java"]


def test_identifies_preferred_skills(
    candidate_profile, internship
):
    result = match_internship(candidate_profile, internship)

    assert result["matched_preferred_skills"] == ["git"]
    assert result["missing_preferred_skills"] == ["docker"]


def test_matches_relevant_education(candidate_profile, internship):
    result = match_internship(candidate_profile, internship)

    assert result["score_breakdown"]["education"] == 100.0


def test_education_is_not_a_hard_filter(
    candidate_profile, internship
):
    candidate_profile["education"][0]["field"] = "Agriculture"

    result = match_internship(candidate_profile, internship)

    assert result["overall_score"] > 0
    assert result["score_breakdown"]["education"] == 0.0


def test_calculates_experience_months(candidate_profile, internship):
    result = match_internship(candidate_profile, internship)

    assert result["detected_experience_months"] == 12
    assert result["score_breakdown"]["experience"] == 100.0


def test_zero_experience_requirement_gets_full_score(
    candidate_profile, internship
):
    internship.minimum_experience_months = 0

    result = match_internship(candidate_profile, internship)

    assert result["score_breakdown"]["experience"] == 100.0


def test_no_education_requirement_gets_neutral_full_score(
    candidate_profile, internship
):
    internship.education_requirements = []

    result = match_internship(candidate_profile, internship)

    assert result["score_breakdown"]["education"] == 100.0


def test_eligibility_is_flagged_for_manual_review(
    candidate_profile, internship
):
    result = match_internship(candidate_profile, internship)

    assert result["eligibility"]["status"] == "requires_manual_review"
    assert result["eligibility"]["criteria"] == [
        "Currently enrolled student"
    ]


def test_rejects_invalid_candidate_profile(internship):
    with pytest.raises(TypeError):
        match_internship(None, internship)


def test_rejects_invalid_internship(candidate_profile):
    with pytest.raises(TypeError):
        match_internship(candidate_profile, {})


def test_ranks_internships_highest_score_first(candidate_profile):
    strong_match = Internship(
        id="INT-001",
        title="Python Developer Intern",
        organization="Company A",
        description="Python and SQL development.",
        required_skills=["Python", "SQL"],
        education_requirements=["Computer Science"],
    )

    weak_match = Internship(
        id="INT-002",
        title="Java Developer Intern",
        organization="Company B",
        description="Java development.",
        required_skills=["Java", "C++"],
        education_requirements=["Computer Science"],
    )

    results = rank_internships(
        candidate_profile,
        [weak_match, strong_match],
    )

    assert results[0]["internship_id"] == "INT-001"
    assert results[1]["internship_id"] == "INT-002"


def test_ranking_excludes_inactive_internships(candidate_profile):
    inactive = Internship(
        id="INT-003",
        title="Inactive Internship",
        organization="Company C",
        description="An expired opportunity.",
        is_active=False,
    )

    results = rank_internships(candidate_profile, [inactive])

    assert results == []


def test_empty_internship_list_returns_empty_results(candidate_profile):
    assert rank_internships(candidate_profile, []) == []
