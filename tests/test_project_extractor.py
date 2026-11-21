
from src.project_extractor import extract_projects


def test_extracts_single_project():
    cv_text = """
    PROJECTS

    Student Management System
    Developed a student management application using Python and MySQL.
    """

    result = extract_projects(cv_text)

    assert len(result) == 1
    assert result[0]["name"] == "Student Management System"
    assert "Python" in result[0]["technologies"]
    assert "MySQL" in result[0]["technologies"]


def test_extracts_multiple_projects():
    cv_text = """
    PROJECTS

    Student Management System
    Built using Python and MySQL.

    Portfolio Website
    Developed using HTML, CSS and JavaScript.
    """

    result = extract_projects(cv_text)

    assert len(result) == 2


def test_extracts_project_description():
    cv_text = """
    PROJECTS

    Internship Recommendation System
    Built a system that analyses CVs and recommends internships.
    """

    result = extract_projects(cv_text)

    assert (
        "analyses CVs and recommends internships"
        in result[0]["description"]
    )


def test_extracts_technologies():
    cv_text = """
    PROJECTS

    Mobile Application
    Developed using Kotlin, Android Studio and Firebase.
    """

    result = extract_projects(cv_text)

    assert set(result[0]["technologies"]) == {
        "Kotlin",
        "Android Studio",
        "Firebase",
    }


def test_stops_at_next_section():
    cv_text = """
    PROJECTS

    Portfolio Website
    Built using HTML and CSS.

    EDUCATION

    Bachelor of Science in Computer Science
    """

    result = extract_projects(cv_text)

    assert len(result) == 1
    assert result[0]["name"] == "Portfolio Website"


def test_returns_empty_list_when_no_projects():
    assert extract_projects("No projects available.") == []


def test_rejects_non_string_input():
    import pytest

    with pytest.raises(TypeError):
        extract_projects(None)


def test_preserves_project_evidence():
    cv_text = """
    PROJECTS

    E-commerce Application
    Created an online shopping platform using Python.
    """

    result = extract_projects(cv_text)

    assert result[0]["evidence"]
    assert any(
        "online shopping platform" in line.lower()
        for line in result[0]["evidence"]
    )
