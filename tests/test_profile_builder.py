
import pytest

from src.profile_builder import build_candidate_profile


SAMPLE_CV = """
EDUCATION
Bachelor of Science in Computer Science
University of Nairobi
2022 - 2026

WORK EXPERIENCE
Software Developer Intern
ABC Technologies
May 2024 - Aug 2024
Developed Python applications and SQL databases.

SKILLS
Python, Java, SQL, Git, Communication, Teamwork

PROJECTS
Developed a machine learning application using Python.
"""


def test_builds_complete_candidate_profile():
    profile = build_candidate_profile(SAMPLE_CV)

    assert "education" in profile
    assert "experience" in profile
    assert "skills" in profile
    assert "skills_by_category" in profile
    assert "summary" in profile


def test_extracts_education():
    profile = build_candidate_profile(SAMPLE_CV)

    assert profile["summary"]["education_count"] == 1
    assert profile["education"][0]["qualification"] == (
        "Bachelor of Science"
    )


def test_extracts_experience():
    profile = build_candidate_profile(SAMPLE_CV)

    assert profile["summary"]["experience_count"] == 1
    assert profile["experience"][0]["role"] == (
        "Software Developer Intern"
    )


def test_extracts_skills():
    profile = build_candidate_profile(SAMPLE_CV)

    skill_names = [
        item["skill"] for item in profile["skills"]
    ]

    assert "python" in skill_names
    assert "java" in skill_names
    assert "sql" in skill_names


def test_groups_skills_by_category():
    profile = build_candidate_profile(SAMPLE_CV)

    assert "python" in profile["skills_by_category"]["technical"]
    assert "git" in profile["skills_by_category"]["tools"]
    assert "communication" in profile["skills_by_category"]["soft"]


def test_summary_counts_match_extracted_records():
    profile = build_candidate_profile(SAMPLE_CV)

    assert profile["summary"]["education_count"] == len(
        profile["education"]
    )
    assert profile["summary"]["experience_count"] == len(
        profile["experience"]
    )
    assert profile["summary"]["skill_count"] == len(
        profile["skills"]
    )



def test_empty_cv_returns_empty_profile():
    profile = build_candidate_profile("")

    assert profile["education"] == []
    assert profile["experience"] == []
    assert profile["skills"] == []
    assert profile["technical_skills"] == []
    assert profile["projects"] == []
    assert profile["career_interests"] == []

    assert profile["skills_by_category"] == {
        "technical": [],
        "tools": [],
        "soft": [],
        "professional": [],
    }

    assert profile["summary"] == {
        "education_count": 0,
        "experience_count": 0,
        "skill_count": 0,
        "technical_skill_count": 0,
        "project_count": 0,
        "career_interest_count": 0,
    }


def test_rejects_non_string_input():
    with pytest.raises(TypeError):
        build_candidate_profile(None)
