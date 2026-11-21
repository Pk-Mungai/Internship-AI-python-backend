import tempfile
from pathlib import Path

from fastapi import UploadFile, File

from config import (
    INTERNSHIP_DATABASE,
    APPLICATION_DATABASE,
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    MAX_CV_SIZE,
)
from src.cv_parser import extract_text_from_pdf
from src.text_cleaner import clean_text
from src.profile_builder import build_candidate_profile
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.internship_repository import InternshipRepository
from src.application_tracker import ApplicationTracker
from src.recommendation_service import recommend_internships
from pydantic import BaseModel, Field
from typing import Literal

from src.cover_letter_generator import generate_cover_letter


# --------------------------------------------------
# APPLICATION INITIALIZATION
# --------------------------------------------------

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

internship_repository = InternshipRepository(
    INTERNSHIP_DATABASE
)

application_tracker = ApplicationTracker(
    APPLICATION_DATABASE
)

# --------------------------------------------------
# API REQUEST MODELS
# --------------------------------------------------

ApplicationStatus = Literal[
    "saved",
    "applied",
    "shortlisted",
    "rejected",
    "accepted",
]


class CreateApplicationRequest(BaseModel):
    internship_id: str = Field(min_length=1)
    status: ApplicationStatus = "saved"
    notes: str = ""


class UpdateApplicationStatusRequest(BaseModel):
    status: ApplicationStatus


class UpdateApplicationNotesRequest(BaseModel):
    notes: str


class CoverLetterRequest(BaseModel):
    candidate_profile: dict
    internship_id: str = Field(min_length=1)
    applicant_name: str = "[Your Name]"
    contact_details: str = "[Your Email] | [Your Phone Number]"

# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/", tags=["System"])
def health_check():
    return {
        "status": "success",
        "message": "AI Internship Recommendation API is running.",
        "version": app.version,
    }


# --------------------------------------------------
# HEALTH ENDPOINT
# --------------------------------------------------

@app.get("/api/v1/health", tags=["System"])
def api_health():
    return {
        "status": "healthy",
        "service": "AI Internship Recommendation System",
    }


# --------------------------------------------------
# INTERNSHIP ENDPOINTS
# --------------------------------------------------

@app.get("/api/v1/internships", tags=["Internships"])
def get_internships():
    """
    Retrieve all active internships.
    """
    try:
        internships = internship_repository.load_all()

        active_internships = [
            internship.model_dump(mode="json")
            for internship in internships
            if internship.is_active
        ]

        return {
            "status": "success",
            "count": len(active_internships),
            "internships": active_internships,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve internships.",
        ) from error


@app.get(
    "/api/v1/internships/{internship_id}",
    tags=["Internships"],
)
def get_internship(internship_id: str):
    """
    Retrieve a specific active internship.
    """
    try:
        internship = internship_repository.get_by_id(
            internship_id
        )

        if internship is None or not internship.is_active:
            raise HTTPException(
                status_code=404,
                detail="Internship not found.",
            )

        return {
            "status": "success",
            "internship": internship.model_dump(mode="json"),
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve internship.",
        ) from error


# --------------------------------------------------
# APPLICATION TRACKING ENDPOINTS
# --------------------------------------------------

@app.get(
    "/api/v1/applications",
    tags=["Applications"],
)
def get_applications(status: str | None = None):
    """
    Retrieve tracked applications.
    Optionally filter by application status.
    """
    try:
        applications = application_tracker.list_applications(
            status=status
        )

        return {
            "status": "success",
            "count": len(applications),
            "applications": applications,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve applications.",
        ) from error


@app.get(
    "/api/v1/applications/{internship_id}",
    tags=["Applications"],
)
def get_application(internship_id: str):
    """
    Retrieve a tracked application by internship ID.
    """
    try:
        application = application_tracker.get_application(
            internship_id
        )

        if application is None:
            raise HTTPException(
                status_code=404,
                detail="Application not found.",
            )

        return {
            "status": "success",
            "application": application,
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve application.",
        ) from error


# --------------------------------------------------
# CV UPLOAD AND CANDIDATE PROFILE ENDPOINT
# --------------------------------------------------

@app.post(
    "/api/v1/candidates/analyze-cv",
    tags=["Candidates"],
)
async def analyze_cv(file: UploadFile = File(...)):
    """
    Upload a PDF CV, extract its text, clean it,
    and generate a structured candidate profile.

    The uploaded CV is processed temporarily and is
    not permanently stored by this endpoint.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename was provided.",
        )

    if Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a PDF.",
        )

    temporary_path = None

    try:
        # Read at most 1 byte beyond the configured limit.
        file_content = await file.read(MAX_CV_SIZE + 1)

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        if len(file_content) > MAX_CV_SIZE:
            raise HTTPException(
                status_code=413,
                detail="CV file exceeds the maximum allowed size of 5 MB.",
            )

        # Save temporarily because the PDF parser accepts a file path.
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temporary_file:
            temporary_file.write(file_content)
            temporary_path = Path(temporary_file.name)

        # Extract and clean CV text.
        extracted_text = extract_text_from_pdf(temporary_path)
        cleaned_text = clean_text(extracted_text)

        if not cleaned_text:
            raise HTTPException(
                status_code=422,
                detail="No usable text could be extracted from the CV.",
            )

        # Build the structured candidate profile.
        candidate_profile = build_candidate_profile(cleaned_text)

        return {
            "status": "success",
            "message": "CV analyzed successfully.",
            "filename": Path(file.filename).name,
            "profile": candidate_profile,
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while analyzing the CV.",
        ) from error

    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()

        await file.close()

# --------------------------------------------------
# INTERNSHIP RECOMMENDATION ENDPOINT
# --------------------------------------------------

@app.post(
    "/api/v1/recommendations",
    tags=["Recommendations"],
)
def get_recommendations(
    candidate_profile: dict,
    top_n: int = 10,
):
    """
    Generate ranked internship recommendations
    using the candidate's structured profile.
    """

    if top_n < 1 or top_n > 50:
        raise HTTPException(
            status_code=400,
            detail="top_n must be between 1 and 50.",
        )

    try:
        internships = internship_repository.load_all()

        active_internships = [
            internship
            for internship in internships
            if internship.is_active
        ]

        recommendations = recommend_internships(
            candidate_profile=candidate_profile,
            internships=active_internships,
            top_n=top_n,
        )

        return {
            "status": "success",
            "count": len(recommendations),
            "recommendations": recommendations,
        }

    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate internship recommendations.",
        ) from error

# --------------------------------------------------
# COVER LETTER GENERATION ENDPOINT
# --------------------------------------------------

@app.post(
    "/api/v1/cover-letters/generate",
    tags=["Applications"],
)
def create_cover_letter(request: CoverLetterRequest):
    """
    Generate a tailored cover letter for an internship.
    """

    try:
        internship = internship_repository.get_by_id(
            request.internship_id
        )

        if internship is None or not internship.is_active:
            raise HTTPException(
                status_code=404,
                detail="Internship not found.",
            )

        cover_letter = generate_cover_letter(
            candidate_profile=request.candidate_profile,
            internship=internship,
            applicant_name=request.applicant_name,
            contact_details=request.contact_details,
        )

        return {
            "status": "success",
            "cover_letter": cover_letter,
            "internship_id": request.internship_id,
        }

    except HTTPException:
        raise

    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate cover letter.",
        ) from error

# --------------------------------------------------
# CREATE APPLICATION
# --------------------------------------------------

@app.post(
    "/api/v1/applications",
    tags=["Applications"],
)
def create_application(request: CreateApplicationRequest):
    """
    Save an internship to the candidate's application tracker.
    """

    try:
        internship = internship_repository.get_by_id(
            request.internship_id
        )

        if internship is None or not internship.is_active:
            raise HTTPException(
                status_code=404,
                detail="Internship not found.",
            )

        application = application_tracker.add_application(
            internship_id=request.internship_id,
            status=request.status,
            notes=request.notes,
        )

        return {
            "status": "success",
            "message": "Application saved successfully.",
            "application": application,
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to save application.",
        ) from error


# --------------------------------------------------
# UPDATE APPLICATION STATUS
# --------------------------------------------------

@app.patch(
    "/api/v1/applications/{internship_id}/status",
    tags=["Applications"],
)
def update_application_status(
    internship_id: str,
    request: UpdateApplicationStatusRequest,
):
    """
    Update the status of a tracked application.
    """

    try:
        application = application_tracker.update_status(
            internship_id=internship_id,
            status=request.status,
        )

        return {
            "status": "success",
            "message": "Application status updated.",
            "application": application,
        }

    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to update application status.",
        ) from error


# --------------------------------------------------
# UPDATE APPLICATION NOTES
# --------------------------------------------------

@app.patch(
    "/api/v1/applications/{internship_id}/notes",
    tags=["Applications"],
)
def update_application_notes(
    internship_id: str,
    request: UpdateApplicationNotesRequest,
):
    """
    Update notes associated with a tracked application.
    """

    try:
        application = application_tracker.update_notes(
            internship_id=internship_id,
            notes=request.notes,
        )

        return {
            "status": "success",
            "message": "Application notes updated.",
            "application": application,
        }

    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to update application notes.",
        ) from error


# --------------------------------------------------
# DELETE APPLICATION
# --------------------------------------------------

@app.delete(
    "/api/v1/applications/{internship_id}",
    tags=["Applications"],
)
def delete_application(internship_id: str):
    """
    Delete a tracked application.
    """

    try:
        deleted = application_tracker.delete_application(
            internship_id
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Application not found.",
            )

        return {
            "status": "success",
            "message": "Application deleted successfully.",
            "internship_id": internship_id,
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete application.",
        ) from error