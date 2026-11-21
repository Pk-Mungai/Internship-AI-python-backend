
import json

import pytest
from pydantic import ValidationError

from src.internship_model import Internship
from src.internship_repository import InternshipRepository


def make_internship(**overrides):
    data = {
        "id": "INT-001",
        "title": "Software Development Intern",
        "organization": "ABC Technologies",
        "description": "Assist with software development projects.",
        "required_skills": ["Python", "SQL"],
        "preferred_skills": ["Docker", "Git"],
        "education_requirements": [
            "Computer Science or a related qualification"
        ],
        "minimum_experience_months": 0,
        "eligibility_criteria": [
            "Currently enrolled student or recent graduate"
        ],
        "location": "Nairobi, Kenya",
        "work_arrangement": "hybrid",
        "application_deadline": "2026-12-15",
        "application_url": "https://example.com/apply",
        "is_active": True,
    }

    data.update(overrides)
    return Internship(**data)


def test_creates_valid_internship():
    internship = make_internship()

    assert internship.id == "INT-001"
    assert internship.title == "Software Development Intern"
    assert internship.required_skills == ["Python", "SQL"]


def test_rejects_missing_required_fields():
    with pytest.raises(ValidationError):
        Internship(
            id="INT-002",
            title="Data Intern"
        )


def test_rejects_negative_experience_requirement():
    with pytest.raises(ValidationError):
        make_internship(minimum_experience_months=-1)


def test_rejects_invalid_work_arrangement():
    with pytest.raises(ValidationError):
        make_internship(work_arrangement="flexible")


def test_load_returns_empty_list_when_database_is_missing(tmp_path):
    repository = InternshipRepository(
        tmp_path / "data" / "internships.json"
    )

    assert repository.load_all() == []


def test_saves_and_loads_internships(tmp_path):
    repository = InternshipRepository(
        tmp_path / "internships.json"
    )
    internship = make_internship()

    repository.save_all([internship])
    loaded = repository.load_all()

    assert len(loaded) == 1
    assert loaded[0].id == internship.id
    assert loaded[0].application_deadline.isoformat() == "2026-12-15"


def test_retrieves_internship_by_id(tmp_path):
    repository = InternshipRepository(
        tmp_path / "internships.json"
    )
    internship = make_internship()

    repository.save_all([internship])

    result = repository.get_by_id("INT-001")

    assert result is not None
    assert result.title == "Software Development Intern"


def test_returns_none_for_unknown_internship_id(tmp_path):
    repository = InternshipRepository(
        tmp_path / "internships.json"
    )

    assert repository.get_by_id("UNKNOWN") is None


def test_upsert_adds_and_updates_internship(tmp_path):
    repository = InternshipRepository(
        tmp_path / "internships.json"
    )

    original = make_internship()
    repository.upsert(original)

    updated = make_internship(
        title="Junior Software Engineering Intern"
    )
    repository.upsert(updated)

    loaded = repository.load_all()

    assert len(loaded) == 1
    assert loaded[0].title == "Junior Software Engineering Intern"


def test_rejects_duplicate_internship_ids(tmp_path):
    repository = InternshipRepository(
        tmp_path / "internships.json"
    )

    first = make_internship()
    second = make_internship(title="Another Internship")

    with pytest.raises(ValueError, match="unique"):
        repository.save_all([first, second])


def test_rejects_invalid_json_database(tmp_path):
    database = tmp_path / "internships.json"
    database.write_text("{invalid json", encoding="utf-8")

    repository = InternshipRepository(database)

    with pytest.raises(ValueError, match="invalid JSON"):
        repository.load_all()


def test_rejects_json_that_is_not_a_list(tmp_path):
    database = tmp_path / "internships.json"
    database.write_text(
        json.dumps({"id": "INT-001"}),
        encoding="utf-8"
    )

    repository = InternshipRepository(database)

    with pytest.raises(ValueError, match="JSON list"):
        repository.load_all()
