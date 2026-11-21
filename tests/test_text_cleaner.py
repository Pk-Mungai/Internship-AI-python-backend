
import pytest

from src.text_cleaner import clean_text


def test_removes_extra_spaces():

    raw_text = "John     Doe     Python"

    result = clean_text(raw_text)

    assert result == "John Doe Python"


def test_preserves_meaningful_line_breaks():

    raw_text = "EDUCATION\nBachelor of Science\nAgriculture"

    result = clean_text(raw_text)

    assert result == raw_text


def test_removes_excessive_blank_lines():

    raw_text = "John Doe\n\n\n\nEducation\n\n\nAgriculture"

    result = clean_text(raw_text)

    assert result == "John Doe\n\nEducation\n\nAgriculture"


def test_removes_leading_and_trailing_whitespace():

    raw_text = "\n\n  John Doe  \n\n"

    result = clean_text(raw_text)

    assert result == "John Doe"


def test_normalizes_tabs_and_line_endings():

    raw_text = "John\tDoe\r\nPython\rSQL"

    result = clean_text(raw_text)

    assert result == "John Doe\nPython\nSQL"


def test_handles_empty_text():

    assert clean_text("") == ""
    assert clean_text("   \n\n  ") == ""


def test_rejects_non_string_input():

    with pytest.raises(TypeError):
        clean_text(123)


def test_removes_zero_width_characters():

    raw_text = "Py\u200bthon"

    result = clean_text(raw_text)

    assert result == "Python"
