
import pytest

from src.experience_extractor import extract_experience


def test_extract_single_work_experience():
    text = """
    WORK EXPERIENCE
    Software Developer
    ABC Technologies
    Jan 2022 - Dec 2023
    • Developed web applications
    • Maintained databases
    """

    result = extract_experience(text)

    assert len(result) == 1
    assert result[0]["role"] == "Software Developer"
    assert result[0]["employer"] == "ABC Technologies"
    assert result[0]["start_date"] == "Jan 2022"
    assert result[0]["end_date"] == "Dec 2023"
    assert len(result[0]["responsibilities"]) == 2


def test_extract_internship_experience():
    text = """
    EXPERIENCE
    IT Intern
    XYZ Company
    May 2024 - Aug 2024
    Assisted with network maintenance.
    """

    result = extract_experience(text)

    assert len(result) == 1
    assert result[0]["role"] == "IT Intern"
    assert result[0]["employer"] == "XYZ Company"


def test_extract_current_position():
    text = """
    PROFESSIONAL EXPERIENCE
    Data Analyst
    Data Solutions Ltd
    March 2023 - Present
    Prepared reports.
    """

    result = extract_experience(text)

    assert result[0]["start_date"] == "March 2023"
    assert result[0]["end_date"] == "Present"


def test_extract_multiple_experiences():
    text = """
    WORK EXPERIENCE
    Junior Developer
    Company A
    2022 - 2023
    Built websites.

    IT Support Intern
    Company B
    2021 - 2022
    Supported users.
    """

    result = extract_experience(text)

    assert len(result) == 2
    assert result[0]["role"] == "Junior Developer"
    assert result[1]["role"] == "IT Support Intern"


def test_stop_at_education_section():
    text = """
    EXPERIENCE
    Developer
    Company A
    2022 - 2023
    Built applications.

    EDUCATION
    Bachelor of Science
    University of Nairobi
    """

    result = extract_experience(text)

    assert len(result) == 1
    assert result[0]["role"] == "Developer"


def test_missing_dates():
    text = """
    WORK EXPERIENCE
    Volunteer
    Community Organization
    Helped organize community events.
    """

    result = extract_experience(text)

    assert len(result) == 1
    assert result[0]["start_date"] is None
    assert result[0]["end_date"] is None


def test_empty_input():
    assert extract_experience("") == []
    assert extract_experience("   ") == []


def test_non_string_input():
    with pytest.raises(TypeError):
        extract_experience(None)


def test_evidence_is_preserved():
    text = """
    EXPERIENCE
    Python Developer
    Example Ltd
    2023 - 2024
    Developed Python applications.
    """

    result = extract_experience(text)

    assert "Python Developer" in result[0]["evidence"]
    assert "Example Ltd" in result[0]["evidence"]
