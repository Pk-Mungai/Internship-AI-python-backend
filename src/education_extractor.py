
import re


# --------------------------------------------------
# PATTERNS AND CONSTANTS
# --------------------------------------------------

QUALIFICATION_PATTERN = re.compile(
    r"\b("
    r"Doctor of Philosophy|"
    r"Higher National Diploma|"
    r"Bachelor of Business Administration|"
    r"Bachelor of Engineering|"
    r"Bachelor of Agriculture|"
    r"Bachelor of Technology|"
    r"Bachelor of Education|"
    r"Bachelor of Commerce|"
    r"Bachelor of Science|"
    r"Bachelor of Arts|"
    r"Master of Business Administration|"
    r"Master of Engineering|"
    r"Master of Education|"
    r"Master of Commerce|"
    r"Master of Science|"
    r"Master of Arts|"
    r"Associate Degree|"
    r"B\.?\s?Com\.?|"
    r"B\.?\s?Sc\.?|"
    r"B\.?\s?A\.?|"
    r"M\.?\s?Sc\.?|"
    r"M\.?\s?A\.?|"
    r"Ph\.?\s?D\.?|"
    r"Bachelor(?:'s)?|"
    r"Master(?:'s)?|"
    r"Diploma|"
    r"Certificate"
    r")\b",
    re.IGNORECASE,
)

YEAR_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")

DATE_RANGE_PATTERN = re.compile(
    r"\b((?:19|20)\d{2})\s*[-–—]\s*"
    r"((?:19|20)\d{2}|present|current|ongoing)\b",
    re.IGNORECASE,
)

INSTITUTION_PATTERN = re.compile(
    r"\b(?:university|college|institute|polytechnic|academy|school)\b",
    re.IGNORECASE,
)

EDUCATION_HEADINGS = {
    "education",
    "educational background",
    "academic background",
    "academic qualifications",
    "educational qualifications",
    "academic history",
}

END_HEADINGS = {
    "work experience",
    "professional experience",
    "employment history",
    "work history",
    "experience",
    "technical skills",
    "skills",
    "projects",
    "certifications",
    "references",
    "career objective",
    "professional summary",
    "profile",
    "leadership professional experience",
    "volunteer experience",
    "achievements awards",
    "awards",
    "leadership",
}


# --------------------------------------------------
# NORMALIZATION
# --------------------------------------------------

def _normalize_heading(line: str) -> str:
    """Normalize a heading for comparison."""
    normalized = re.sub(r"[^a-z ]", "", line.lower())
    return re.sub(r"\s+", " ", normalized).strip()


def _normalize_value(value: str | None) -> str:
    """Normalize a value for duplicate comparisons."""
    if not value:
        return ""

    return re.sub(r"\s+", " ", value.lower().strip())


def _clean_value(value: str) -> str:
    """Clean surrounding punctuation and whitespace."""
    value = re.sub(r"\s+", " ", value)
    return value.strip(" \t,;:-–—.")


# --------------------------------------------------
# EDUCATION SECTION
# --------------------------------------------------

def _extract_education_section(text: str) -> list[str]:
    """
    Extract the education section.

    If no recognized education heading exists,
    search the entire document.
    """
    lines = text.splitlines()
    start_index = None

    for index, line in enumerate(lines):
        if _normalize_heading(line) in EDUCATION_HEADINGS:
            start_index = index + 1
            break

    if start_index is None:
        return lines

    education_lines = []

    for line in lines[start_index:]:
        if _normalize_heading(line) in END_HEADINGS:
            break

        education_lines.append(line)

    return education_lines


# --------------------------------------------------
# RECORD IDENTIFICATION
# --------------------------------------------------

def _is_excluded_certificate(line: str) -> bool:
    """Exclude common non-academic certificates."""
    normalized = line.lower()

    excluded_phrases = (
        "certificate of achievement",
        "certificate of participation",
        "certificate of appreciation",
        "certificate of recognition",
    )

    return any(
        phrase in normalized
        for phrase in excluded_phrases
    )

def _is_education_record_start(line: str) -> bool:
    """Determine whether a line starts an education record."""
    stripped = line.strip()

    if not stripped:
        return False

    if _is_excluded_certificate(stripped):
        return False

    if QUALIFICATION_PATTERN.search(stripped):
        return True

    # Kenyan secondary-school qualification.
    if re.search(r"\bKCSE\b", stripped, re.IGNORECASE):
        return True

    # Programs that may not use a conventional degree title.
    if re.search(r"\bprogram\b", stripped, re.IGNORECASE):
        return bool(INSTITUTION_PATTERN.search(stripped))

    return False


# --------------------------------------------------
# INSTITUTION EXTRACTION
# --------------------------------------------------

def _extract_institution_from_line(line: str) -> str | None:
    """Extract an institution or awarding organization from a line."""
    line = line.strip()

    if not line:
        return None

    # Handle institutions inside parentheses.
    parenthesized_parts = re.findall(r"\(([^)]*)\)", line)

    for part in parenthesized_parts:
        if INSTITUTION_PATTERN.search(part):
            institution = YEAR_PATTERN.sub("", part)
            institution = _clean_value(institution)

            if institution:
                return institution

    # Handle institutions and awarding organizations.
    organization_pattern = re.compile(
        r"\b(?:university|college|institute|polytechnic|"
        r"academy|school|ambulance)\b",
        re.IGNORECASE,
    )

    match = organization_pattern.search(line)

    if not match:
        return None

    qualification_match = QUALIFICATION_PATTERN.search(line)

    if qualification_match and match.start() < qualification_match.start():
        institution = line[:qualification_match.start()]
    else:
        institution = line

    institution = re.sub(
        r"\b(?:19|20)\d{2}\b",
        "",
        institution,
    )

    institution = _clean_value(institution)

    return institution or None

def _find_institution(
    lines: list[str],
    index: int,
) -> str | None:
    """Find an institution near a qualification."""
    institution = _extract_institution_from_line(lines[index])

    if institution:
        return institution

    for distance in (1, 2):
        for candidate_index in (
            index + distance,
            index - distance,
        ):
            if not 0 <= candidate_index < len(lines):
                continue

            candidate_line = lines[candidate_index].strip()

            if not candidate_line:
                continue

            if _is_education_record_start(candidate_line):
                continue

            if YEAR_PATTERN.search(candidate_line):
                continue

            institution = _extract_institution_from_line(
                candidate_line
            )

            if institution:
                return institution

            # Support organization names without conventional
            # institution keywords, e.g. Aggrandize Africa.
            if (
                distance == 1
                and candidate_index == index + 1
                and re.fullmatch(
                    r"[A-Z][A-Za-z'.& ]{2,}",
                    candidate_line,
                )
            ):
                return _clean_value(candidate_line)

    return None

# --------------------------------------------------
# FIELD EXTRACTION
# --------------------------------------------------

def _extract_field(
    line: str,
    qualification_match,
) -> str | None:
    """
    Extract the subject or field associated with a qualification.
    """
    before = line[:qualification_match.start()].strip()
    after = line[qualification_match.end():].strip()

    # A preceding institution is not the field of study.
    if INSTITUTION_PATTERN.search(before):
        before = ""

    # Prefer a subject introduced by "in".
    in_match = re.search(
        r"\bin\s+(.+?)(?=\s*\(|$)",
        after,
        re.IGNORECASE,
    )

    if in_match:
        candidate = in_match.group(1)

    else:
        parenthesis = re.search(r"\(([^)]+)\)", after)

        if parenthesis:
            candidate = parenthesis.group(1)

            if INSTITUTION_PATTERN.search(candidate):
                candidate = ""

        else:
            candidate = after

            candidate = re.split(
                r"\s+[–—-]\s+",
                candidate,
                maxsplit=1,
            )[0]

            candidate = re.sub(
                r"^\s*(?:of|in)\s+",
                "",
                candidate,
                flags=re.IGNORECASE,
            )

    candidate = YEAR_PATTERN.sub("", candidate)
    candidate = _clean_value(candidate)

    if not candidate:
        return None

    if INSTITUTION_PATTERN.search(candidate):
        return None

    return candidate


def _extract_program_field(line: str) -> str | None:
    """Extract the name of a program without a degree keyword."""
    institution_match = INSTITUTION_PATTERN.search(line)

    if not institution_match:
        return None

    # Find the descriptive text after the institution.
    remainder = line[institution_match.end():]

    separator_match = re.search(r"\s*[-–—]\s*", remainder)

    if not separator_match:
        return None

    candidate = remainder[separator_match.end():]
    candidate = YEAR_PATTERN.sub("", candidate)
    candidate = _clean_value(candidate)

    return candidate or None


# --------------------------------------------------
# DATES
# --------------------------------------------------

def _find_graduation_year(
    lines: list[str],
    index: int,
) -> int | None:
    """
    Find a completed graduation year.

    A date range ending in Present, Current or Ongoing
    is not treated as a completed graduation.
    """
    relevant_lines = [lines[index]]

    for distance in (1, 2, 3):
        candidate_index = index + distance

        if candidate_index >= len(lines):
            break

        candidate_line = lines[candidate_index]

        if _is_education_record_start(candidate_line):
            break

        relevant_lines.append(candidate_line)

    for line in relevant_lines:
        if re.search(
            r"\b(?:in progress|ongoing|currently enrolled|present)\b",
            line,
            re.IGNORECASE,
        ):
            return None

        date_range = DATE_RANGE_PATTERN.search(line)

        if date_range:
            end_value = date_range.group(2).lower()

            if end_value in {"present", "current", "ongoing"}:
                return None

            return int(end_value)

    for line in relevant_lines:
        years = YEAR_PATTERN.findall(line)

        if years:
            return int(years[-1])

    return None


# --------------------------------------------------
# EVIDENCE
# --------------------------------------------------

def _collect_evidence(
    lines: list[str],
    index: int,
) -> list[str]:
    """
    Collect source lines belonging to one education record.

    Stop before the next record starts.
    """
    evidence = []

    for candidate_index in range(index, min(index + 4, len(lines))):
        line = lines[candidate_index].strip()

        if not line:
            continue

        if candidate_index > index and _is_education_record_start(line):
            break

        if _normalize_heading(line) in END_HEADINGS:
            break

        evidence.append(line)

    return evidence


# --------------------------------------------------
# DUPLICATE DETECTION
# --------------------------------------------------

def _is_duplicate(
    record: dict,
    existing_records: list[dict],
) -> bool:
    """Check whether an education record already exists."""
    for existing in existing_records:
        if (
            _normalize_value(record["qualification"])
            == _normalize_value(existing["qualification"])
            and _normalize_value(record["field"])
            == _normalize_value(existing["field"])
            and _normalize_value(record["institution"])
            == _normalize_value(existing["institution"])
            and record["graduation_year"]
            == existing["graduation_year"]
        ):
            return True

    return False


# --------------------------------------------------
# MAIN EXTRACTION FUNCTION
# --------------------------------------------------

def extract_education(text: str) -> list[dict]:
    """
    Extract education records from CV text.

    Each record contains:
        qualification
        field
        institution
        graduation_year
        evidence
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    if not text.strip():
        return []

    lines = _extract_education_section(text)
    education_records = []

    for index, line in enumerate(lines):
        stripped = line.strip()

        if not stripped or _is_excluded_certificate(stripped):
            continue

        # Handle Kenyan Certificate of Secondary Education.
        kcse_match = re.search(
            r"\bKCSE\b",
            stripped,
            re.IGNORECASE,
        )

        if kcse_match:
            institution = _find_institution(lines, index)

            grade_match = re.search(
                r"\bGrade\s+([A-F][+-]?)\b",
                stripped,
                re.IGNORECASE,
            )

            field = (
                f"Grade {grade_match.group(1)}"
                if grade_match
                else None
            )

            record = {
                "qualification": "KCSE",
                "field": field,
                "institution": institution,
                "graduation_year": _find_graduation_year(
                    lines,
                    index,
                ),
                "evidence": _collect_evidence(lines, index),
            }

            if not _is_duplicate(record, education_records):
                education_records.append(record)

            continue

        matches = list(QUALIFICATION_PATTERN.finditer(stripped))

        if matches:
            # Use the first qualification match on a line.
            match = matches[0]

            qualification = match.group(0).strip()
            field = _extract_field(stripped, match)

        elif re.search(r"\bprogram\b", stripped, re.IGNORECASE):
            qualification = "Program"
            field = _extract_program_field(stripped)

        else:
            continue

        institution = _find_institution(lines, index)

        evidence = _collect_evidence(lines, index)

        # Include nearby continuation text in the field when
        # a qualification's subject wraps onto the next line.
        if (
                qualification.lower() == "certificate"
                and field
                and len(evidence) > 1
        ):
            continuation = evidence[1]

            if (
                    continuation != institution
                    and not YEAR_PATTERN.search(continuation)
                    and not _extract_institution_from_line(continuation)
            ):
                field = _clean_value(
                    f"{field} {continuation}"
                )

        record = {
            "qualification": qualification,
            "field": field,
            "institution": institution,
            "graduation_year": _find_graduation_year(
                lines,
                index,
            ),
            "evidence": evidence,
        }

        if not _is_duplicate(record, education_records):
            education_records.append(record)

    return education_records
