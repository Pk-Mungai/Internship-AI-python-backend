
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class Internship(BaseModel):
    """Validated representation of an internship opportunity."""

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    organization: str = Field(min_length=1)
    description: str = Field(min_length=1)

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)

    # These are stored as requirement descriptions, not used as
    # automatic academic-discipline filters.
    education_requirements: list[str] = Field(default_factory=list)

    minimum_experience_months: int = Field(default=0, ge=0)
    eligibility_criteria: list[str] = Field(default_factory=list)

    location: str | None = None
    work_arrangement: Literal["onsite", "hybrid", "remote"] = "onsite"

    application_deadline: date | None = None
    application_url: str | None = None

    is_active: bool = True
