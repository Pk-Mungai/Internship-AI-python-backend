
import pytest

from src.skill_extractor import extract_skills


def test_extracts_technical_skills():
    text = """
    TECHNICAL SKILLS
    Python, Java, SQL, Machine Learning
    """

    result = extract_skills(text)
    skills = [item["skill"] for item in result]

    assert "python" in skills
    assert "java" in skills
    assert "sql" in skills
    assert "machine learning" in skills


def test_extracts_tools():
    text = """
    SKILLS
    Git, Docker, Excel, Android Studio
    """

    result = extract_skills(text)
    skills = [item["skill"] for item in result]

    assert "git" in skills
    assert "docker" in skills
    assert "excel" in skills
    assert "android studio" in skills


def test_extracts_soft_skills():
    text = """
    CORE COMPETENCIES
    Communication, teamwork, leadership
    """

    result = extract_skills(text)
    skills = [item["skill"] for item in result]

    assert "communication" in skills
    assert "teamwork" in skills
    assert "leadership" in skills


def test_extracts_professional_skills():
    text = """
    SKILLS
    Research, project management, technical writing
    """

    result = extract_skills(text)
    skills = [item["skill"] for item in result]

    assert "research" in skills
    assert "project management" in skills
    assert "technical writing" in skills


def test_preserves_project_evidence():
    text = """
    PROJECTS
    Developed a Python application using SQL.
    """

    result = extract_skills(text)

    python_skill = next(
        item for item in result if item["skill"] == "python"
    )

    assert python_skill["sources"] == ["projects"]
    assert "Developed a Python application using SQL." in (
        python_skill["evidence"]
    )


def test_does_not_duplicate_skills():
    text = """
    SKILLS
    Python, Java

    PROJECTS
    Developed a Python application.
    """

    result = extract_skills(text)

    python_records = [
        item for item in result if item["skill"] == "python"
    ]

    assert len(python_records) == 1
    assert len(python_records[0]["evidence"]) == 2


def test_ignores_partial_word_matches():
    text = """
    SKILLS
    Pythonista and JavaScript frameworks.
    """

    result = extract_skills(text)
    skills = [item["skill"] for item in result]

    assert "python" not in skills
    assert "java" not in skills


def test_returns_empty_for_empty_input():
    assert extract_skills("") == []
    assert extract_skills("   ") == []


def test_rejects_non_string_input():
    with pytest.raises(TypeError):
        extract_skills(None)


def test_preserves_original_source_section_heading():
    text = """
    PERSONAL PROJECTS
    Developed a Python application.
    """

    result = extract_skills(text)

    python_skill = next(
        item for item in result if item["skill"] == "python"
    )

    assert python_skill["source_sections"] == ["PERSONAL PROJECTS"]


def test_recognizes_additional_skill_section_headings():
    text = """
    TECHNICAL COMPETENCIES
    Python, SQL, Docker
    """

    result = extract_skills(text)
    skills = [item["skill"] for item in result]

    assert "python" in skills
    assert "sql" in skills
    assert "docker" in skills


def test_tracks_multiple_source_sections():
    text = """
    SKILLS
    Python, Java

    PROJECTS
    Developed an application using Python.

    WORK EXPERIENCE
    Used Java to develop software.
    """

    result = extract_skills(text)

    python_skill = next(
        item for item in result if item["skill"] == "python"
    )

    java_skill = next(
        item for item in result if item["skill"] == "java"
    )

    assert python_skill["source_sections"] == [
        "SKILLS",
        "PROJECTS"
    ]

    assert java_skill["source_sections"] == [
        "SKILLS",
        "WORK EXPERIENCE"
    ]


def test_does_not_carry_skills_section_into_education():
    text = """
    SKILLS
    Python, Java

    EDUCATION
    Bachelor of Science in Computer Science
    """

    result = extract_skills(text)
    skills = [item["skill"] for item in result]

    assert "python" in skills
    assert "java" in skills


def test_preserves_original_evidence_without_case_duplicates():
    text = """
    SKILLS
    Python, Java

    PROJECTS
    python application development.
    """

    result = extract_skills(text)

    python_skill = next(
        item for item in result if item["skill"] == "python"
    )

    assert len(python_skill["evidence"]) == 2
