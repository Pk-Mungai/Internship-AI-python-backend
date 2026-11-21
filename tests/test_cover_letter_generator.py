
import pytest

from src.cover_letter_generator import generate_cover_letter


@pytest.fixture
def candidate_profile():
    return {
        "education": [
            {
                "qualification": "Bachelor of Science",
                "field": "Computer Science",
                "institution": "Example University",
            }
        ],
        "experience": [
            {
                "role": "IT Support Intern",
                "employer": "Example Technologies",
            }
        ],
        "skills_by_category": {
            "technical": ["Python", "SQL"],
            "tools": ["Git"],
        },
    }


@pytest.fixture
def internship():
    return {
        "id": "INT001",
        "title": "Software Developer Intern",
        "organization": "Tech Solutions",
        "description": "Assist with software development.",
        "required_skills": ["Python", "Java"],
    }


def test_generates_cover_letter(candidate_profile, internship):
    letter = generate_cover_letter(candidate_profile, internship)

    assert isinstance(letter, str)
    assert len(letter) > 100
    assert "Software Developer Intern" in letter
    assert "Tech Solutions" in letter


def test_includes_candidate_education(candidate_profile, internship):
    letter = generate_cover_letter(candidate_profile, internship)

    assert "Computer Science" in letter
    assert "Example University" in letter


def test_includes_candidate_experience(candidate_profile, internship):
    letter = generate_cover_letter(candidate_profile, internship)

    assert "IT Support Intern" in letter
    assert "Example Technologies" in letter


def test_includes_documented_skills(candidate_profile, internship):
    letter = generate_cover_letter(candidate_profile, internship)

    assert "Python" in letter
    assert "SQL" in letter
    assert "Git" in letter


def test_does_not_claim_unlisted_skills(candidate_profile, internship):
    letter = generate_cover_letter(candidate_profile, internship)

    assert "Java" not in letter


def test_uses_custom_applicant_details(candidate_profile, internship):
    letter = generate_cover_letter(
        candidate_profile,
        internship,
        applicant_name="Jane Doe",
        contact_details="jane@example.com | 0712345678",
    )

    assert "Jane Doe" in letter
    assert "jane@example.com" in letter
    assert "0712345678" in letter


def test_handles_profile_without_education_or_experience(internship):
    profile = {
        "education": [],
        "experience": [],
        "skills_by_category": {},
    }

    letter = generate_cover_letter(profile, internship)

    assert "Software Developer Intern" in letter
    assert "practical experience" in letter


def test_rejects_non_dictionary_profile(internship):
    with pytest.raises(TypeError):
        generate_cover_letter("invalid profile", internship)


def test_rejects_missing_internship_title(candidate_profile):
    invalid_internship = {
        "organization": "Tech Solutions",
    }

    with pytest.raises(ValueError, match="title"):
        generate_cover_letter(candidate_profile, invalid_internship)


def test_rejects_missing_organization(candidate_profile):
    invalid_internship = {
        "title": "Software Developer Intern",
    }

    with pytest.raises(ValueError, match="organization"):
        generate_cover_letter(candidate_profile, invalid_internship)
