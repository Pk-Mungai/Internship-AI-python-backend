
import pytest

from src.education_extractor import extract_education


def test_extracts_single_qualification():
    cv_text = """
    EDUCATION

    Bachelor of Science in Agriculture
    University of Nairobi
    2022 - 2026
    """

    result = extract_education(cv_text)

    assert len(result) == 1
    assert result[0]["qualification"] == "Bachelor of Science"
    assert result[0]["field"] == "Agriculture"
    assert result[0]["institution"] == "University of Nairobi"
    assert result[0]["graduation_year"] == 2026


def test_extracts_multiple_qualifications():
    cv_text = """
    EDUCATION

    Bachelor of Science in Agriculture
    University of Nairobi
    2022 - 2026

    Diploma in Information Technology
    Kenya Institute of Technology
    2019 - 2021
    """

    result = extract_education(cv_text)

    assert len(result) == 2
    assert result[0]["field"] == "Agriculture"
    assert result[1]["field"] == "Information Technology"


def test_stops_at_next_section():
    cv_text = """
    EDUCATION

    Bachelor of Science in Agriculture
    University of Nairobi
    2022 - 2026

    WORK EXPERIENCE

    Diploma in Business Administration
    """

    result = extract_education(cv_text)

    assert len(result) == 1


def test_extracts_qualification_without_institution():
    cv_text = """
    EDUCATION

    Diploma in Information Technology
    """

    result = extract_education(cv_text)

    assert len(result) == 1
    assert result[0]["qualification"] == "Diploma"
    assert result[0]["field"] == "Information Technology"
    assert result[0]["institution"] is None


def test_handles_missing_year():
    cv_text = """
    EDUCATION

    Bachelor of Science in Agriculture
    University of Nairobi
    """

    result = extract_education(cv_text)

    assert len(result) == 1
    assert result[0]["graduation_year"] is None


def test_extracts_parenthesized_field():
    cv_text = """
    EDUCATION

    Bachelor of Science (Agriculture)
    University of Nairobi
    """

    result = extract_education(cv_text)

    assert result[0]["field"] == "Agriculture"


def test_returns_empty_list_for_empty_text():
    assert extract_education("") == []
    assert extract_education("   ") == []


def test_rejects_non_string_input():
    with pytest.raises(TypeError):
        extract_education(123)


def test_preserves_evidence():
    cv_text = """
    EDUCATION

    Bachelor of Science in Agriculture
    University of Nairobi
    """

    result = extract_education(cv_text)

    assert "Bachelor of Science in Agriculture" in result[0]["evidence"]
    assert "University of Nairobi" in result[0]["evidence"]


# --------------------------------------------------
# ADDITIONAL REGRESSION TESTS
# --------------------------------------------------

def test_extracts_field_when_institution_precedes_qualification():
    cv_text = """
    EDUCATION

    Strathmore University - BSc. Informatics & Computer Science
    2020 - 2024
    """

    result = extract_education(cv_text)

    assert len(result) == 1
    assert result[0]["qualification"].replace(".", "") == "BSc"
    assert result[0]["field"] == "Informatics & Computer Science"
    assert result[0]["institution"] == "Strathmore University"
    assert result[0]["graduation_year"] == 2024


def test_extracts_certificate_subject():
    cv_text = """
    EDUCATION

    Aggrandize Africa - Certificate in Digital Sales & Online
    2024
    """

    result = extract_education(cv_text)

    assert len(result) == 1
    assert result[0]["qualification"] == "Certificate"
    assert result[0]["field"] == "Digital Sales & Online"


def test_extracts_certificate_subject_with_institution_in_parentheses():
    cv_text = """
    EDUCATION

    Certificate of Excellence in leadership (Mt. Kenya Academy, 2022)
    """

    result = extract_education(cv_text)

    assert len(result) == 1
    assert result[0]["field"] == "leadership"
    assert result[0]["institution"] == "Mt. Kenya Academy"
    assert result[0]["graduation_year"] == 2022


def test_does_not_assign_previous_qualification_year_to_next_record():
    cv_text = """
    EDUCATION

    Bachelor of Science in Agriculture
    University of Nairobi
    2022 - 2026

    Diploma in Information Technology
    Kenya Institute of Technology
    """

    result = extract_education(cv_text)

    assert len(result) == 2
    assert result[0]["graduation_year"] == 2026
    assert result[1]["graduation_year"] is None


def test_does_not_duplicate_identical_education_records():
    cv_text = """
    EDUCATION

    Bachelor of Science in Agriculture
    University of Nairobi
    2022 - 2026

    Bachelor of Science in Agriculture
    University of Nairobi
    2022 - 2026
    """

    result = extract_education(cv_text)

    assert len(result) == 1


def test_does_not_treat_institution_as_field():
    cv_text = """
    EDUCATION

    University of Nairobi
    Bachelor of Science
    2022 - 2026
    """

    result = extract_education(cv_text)

    assert len(result) == 1
    assert result[0]["field"] is None
    assert result[0]["institution"] == "University of Nairobi"


def test_stops_at_leadership_and_professional_experience():
    cv_text = """
    EDUCATION

    Bachelor of Science in Informatics
    Strathmore University
    2020 - 2024

    LEADERSHIP & PROFESSIONAL EXPERIENCE

    Certificate in Leadership
    """

    result = extract_education(cv_text)

    assert len(result) == 1


def test_handles_multiple_certificates():
    cv_text = """
    EDUCATION

    Certificate in Digital Sales
    Aggrandize Africa
    2024

    Certificate in First Aid
    St. John's Ambulance
    2022
    """

    result = extract_education(cv_text)

    assert len(result) == 2
    assert result[0]["field"] == "Digital Sales"
    assert result[1]["field"] == "First Aid"
