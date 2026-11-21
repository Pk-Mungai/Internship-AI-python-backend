
from pathlib import Path
import pymupdf


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Extract readable text from all pages of a PDF CV.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text from the PDF.

    Raises:
        FileNotFoundError: If the PDF does not exist.
        ValueError: If the file is invalid or contains no extractable text.
    """

    pdf_path = Path(pdf_path)

    # 1. Check whether the file exists
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"CV file not found: {pdf_path}"
        )

    # 2. Check the file extension
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            "Invalid file format. Please provide a PDF file."
        )

    # 3. Open the PDF and extract text
    try:
        with pymupdf.open(pdf_path) as document:

            # Check for password protection
            if document.is_encrypted:
                raise ValueError(
                    "The PDF is password protected."
                )

            extracted_pages = []

            for page_number, page in enumerate(document, start=1):

                page_text = page.get_text("text").strip()

                if page_text:
                    extracted_pages.append(
                        f"--- Page {page_number} ---\n{page_text}"
                    )

    except pymupdf.FileDataError as error:
        raise ValueError(
            "The supplied file is not a valid PDF."
        ) from error

    # 4. Combine text from all pages
    extracted_text = "\n\n".join(extracted_pages)

    # 5. Check whether any text was extracted
    if not extracted_text:
        raise ValueError(
            "No extractable text found. "
            "This may be a scanned PDF requiring OCR."
        )

    return extracted_text
