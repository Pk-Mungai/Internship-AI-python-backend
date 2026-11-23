import uuid

from fastapi import UploadFile, HTTPException
from pypdf import PdfReader

from config import CV_DIRECTORY, MAX_CV_SIZE


# Ensure the configured CV directory exists
CV_DIRECTORY.mkdir(parents=True, exist_ok=True)


async def save_and_extract_cv(file: UploadFile, user_id: int):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are currently supported."
        )

    # Read at most 1 byte over the limit to detect oversized files
    contents = await file.read(MAX_CV_SIZE + 1)

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(contents) > MAX_CV_SIZE:
        raise HTTPException(
            status_code=413,
            detail="CV must not exceed 5MB."
        )

    # Basic check that the uploaded content is a PDF
    if not contents.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file does not appear to be a valid PDF."
        )

    filename = f"user_{user_id}_{uuid.uuid4().hex}.pdf"

    file_path = CV_DIRECTORY / filename

    try:
        with open(file_path, "wb") as f:
            f.write(contents)

        reader = PdfReader(str(file_path))

        if reader.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail="Encrypted PDFs are not supported."
            )

        extracted_text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in this PDF."
            )

        return {
            "filename": filename,
            "file_path": str(file_path),
            "extracted_text": extracted_text
        }

    except HTTPException:
        if file_path.exists():
            file_path.unlink()
        raise

    except Exception as error:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail="Could not process this PDF."
        ) from error

    finally:
        await file.close()