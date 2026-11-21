
import pymupdf
import pytest

from src.cv_parser import extract_text_from_pdf


def create_sample_pdf(path):
    """Create a sample PDF for testing."""

    document = pymupdf.open()

    page = document.new_page()

    page.insert_text(
        (72, 72),
        "John Doe\n"
        "Education: Bachelor of Science in Agriculture\n"
        "Skills: Python, Kotlin, SQL"
    )

    document.save(path)
    document.close()


def test_extract_text_from_pdf(tmp_path):

    pdf_path = tmp_path / "sample_cv.pdf"

    create_sample_pdf(pdf_path)

    text = extract_text_from_pdf(pdf_path)

    assert "John Doe" in text
    assert "Agriculture" in text
    assert "Python" in text


def test_missing_pdf():

    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("missing_cv.pdf")


def test_invalid_file_format(tmp_path):

    file_path = tmp_path / "sample.txt"

    file_path.write_text("This is not a PDF.")

    with pytest.raises(ValueError):
        extract_text_from_pdf(file_path)


def test_empty_pdf(tmp_path):

    pdf_path = tmp_path / "empty.pdf"

    document = pymupdf.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    with pytest.raises(ValueError, match="No extractable text"):
        extract_text_from_pdf(pdf_path)
