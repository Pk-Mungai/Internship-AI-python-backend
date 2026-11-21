
import pytest

from src.interest_extractor import extract_interests


def test_extracts_single_career_interest():
    cv_text = """
    CAREER INTERESTS

    Software Development
    """

    result = extract_interests(cv_text)

    assert "Software Development" in result


def test_extracts_multiple_career_interests():
    cv_text = """
    CAREER INTERESTS

    Artificial Intelligence
    Data Science
    Cybersecurity
    """

    result = extract_interests(cv_text)

    assert len(result) == 3
    assert "Artificial Intelligence" in result
    assert "Data Science" in result
    assert "Cybersecurity" in result


def test_extracts_interests_from_career_objective():
    cv_text = """
    CAREER OBJECTIVE

    Seeking opportunities in software development
    and artificial intelligence.
    """

    result = extract_interests(cv_text)

    assert "Software Development" in result
    assert "Artificial Intelligence" in result


def test_extracts_interests_from_professional_summary():
    cv_text = """
    PROFESSIONAL SUMMARY

    Aspiring data scientist interested in machine learning
    and data analytics.
    """

    result = extract_interests(cv_text)

    assert "Data Science" in result
    assert "Machine Learning" in result
    assert "Data Analytics" in result


def test_does_not_infer_interests_from_skills_alone():
    cv_text = """
    SKILLS

    Python, JavaScript, HTML, CSS, MySQL
    """

    result = extract_interests(cv_text)

    assert result == []


def test_does_not_extract_unrelated_sections():
    cv_text = """
    EDUCATION

    Bachelor of Science in Computer Science

    EXPERIENCE

    Software Developer

    SKILLS

    Python, JavaScript
    """

    result = extract_interests(cv_text)

    assert result == []


def test_stops_at_next_section():
    cv_text = """
    CAREER INTERESTS

    Software Development
    Artificial Intelligence

    EDUCATION

    Bachelor of Science in Computer Science
    """

    result = extract_interests(cv_text)

    assert len(result) == 2


def test_removes_duplicate_interests():
    cv_text = """
    CAREER INTERESTS

    Software Development
    Artificial Intelligence
    Software Development
    """

    result = extract_interests(cv_text)

    assert result.count("Software Development") == 1


def test_returns_empty_list_when_no_interests_exist():
    assert extract_interests("No career information available.") == []


def test_rejects_non_string_input():
    with pytest.raises(TypeError):
        extract_interests(None)


def test_preserves_explicit_career_interest_evidence():
    cv_text = """
    CAREER INTERESTS

    Interested in cloud computing and cybersecurity.
    """

    result = extract_interests(cv_text)

    assert "Cloud Computing" in result
    assert "Cybersecurity" in result
