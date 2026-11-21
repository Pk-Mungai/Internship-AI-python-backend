
import re


EXPERIENCE_HEADINGS = {
    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "work history",
    "career history",
    "internship experience",
    "professional background",
    "leadership professional experience",
    "leadership experience",
    "volunteer experience",
    "volunteering experience",
}

END_HEADINGS = {
    "education",
    "educational background",
    "academic background",
    "academic qualifications",
    "technical skills",
    "skills",
    "skiils",
    "projects",
    "certifications",
    "achievements awards",
    "awards",
    "references",
    "referees",
    "career objective",
    "professional summary",
    "profile",
    "interests",
    "languages",
}

MONTH = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
    r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|"
    r"Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)

DATE = rf"(?:{MONTH}\s+)?(?:19|20)\d{{2}}|Present|Current|Ongoing"

DATE_RANGE_PATTERN = re.compile(
    rf"(?P<start>{DATE})\s*(?:-|–|—|to)\s*(?P<end>{DATE})",
    re.IGNORECASE,
)

DATE_ONLY_PATTERN = re.compile(
    rf"^\s*(?:{DATE})\s*$",
    re.IGNORECASE,
)


def _normalize_heading(line: str) -> str:
    normalized = re.sub(r"[^a-z ]", "", line.lower())
    return re.sub(r"\s+", " ", normalized).strip()


def _extract_experience_sections(text: str) -> list[tuple[str, list[str]]]:
    """
    Extract professional and volunteer experience sections.
    """
    sections = []
    current_type = None
    current_lines = []

    for line in text.splitlines():
        heading = _normalize_heading(line)

        if heading in EXPERIENCE_HEADINGS:
            if current_type and current_lines:
                sections.append((current_type, current_lines))

            current_type = (
                "volunteer"
                if "volunteer" in heading
                else "professional"
            )
            current_lines = []
            continue

        if heading in END_HEADINGS:
            if current_type and current_lines:
                sections.append((current_type, current_lines))

            current_type = None
            current_lines = []
            continue

        if current_type:
            current_lines.append(line)

    if current_type and current_lines:
        sections.append((current_type, current_lines))

    return sections




def _split_into_entries(lines: list[str]) -> list[list[str]]:
    """
    Split experience sections into individual entries.

    Supports:
    1. Role - Employer - Date on separate or combined lines.
    2. Blank lines between dates and responsibilities.
    3. Multiple experience records in one section.
    """
    non_empty = [
        line.strip()
        for line in lines
        if line.strip()
    ]

    if not non_empty:
        return []

    start_indexes = []

    for index, line in enumerate(non_empty):
        if not DATE_RANGE_PATTERN.search(line):
            continue

        # Date is on its own line, so include the role
        # and employer lines immediately before it.
        if DATE_RANGE_PATTERN.fullmatch(line):
            previous = index - 1

            if previous < 0:
                start = index

            elif any(
                separator in non_empty[previous]
                for separator in (" - ", " – ", " — ")
            ):
                # Combined role and employer on one line.
                start = previous

            elif previous >= 1:
                # Role and employer on separate lines.
                start = previous - 1

            else:
                start = previous

        else:
            # Date is embedded in the role/employer line.
            start = index

        if start not in start_indexes:
            start_indexes.append(start)

    if not start_indexes:
        return [non_empty]

    start_indexes.sort()

    entries = []

    for position, start in enumerate(start_indexes):
        end = (
            start_indexes[position + 1]
            if position + 1 < len(start_indexes)
            else len(non_empty)
        )

        entry = non_empty[start:end]

        if entry:
            entries.append(entry)

    return entries


def _clean_responsibility(line: str) -> str:
    return re.sub(r"^[\s•●▪◦\-\*]+", "", line).strip()


def _extract_dates(entry_lines: list[str]) -> tuple[str | None, str | None]:
    for line in entry_lines:
        match = DATE_RANGE_PATTERN.search(line)

        if match:
            return (
                match.group("start").strip(),
                match.group("end").strip(),
            )

    return None, None


def _remove_dates(line: str) -> str:
    return DATE_RANGE_PATTERN.sub("", line).strip(" |,–—-")


def _split_role_and_employer(line: str) -> tuple[str | None, str | None]:
    """
    Split a combined heading such as:
    Project Manager - Katolikey Solutions
    """
    separators = [" - ", " – ", " — "]

    for separator in separators:
        if separator in line:
            role, employer = line.split(separator, 1)
            return role.strip() or None, employer.strip() or None

    return line.strip() or None, None


def _classify_experience(
    role: str | None,
    section_type: str,
) -> str:
    if section_type == "volunteer":
        return "volunteer"

    role_lower = (role or "").lower()

    if any(
        word in role_lower
        for word in ("founder", "reseller", "entrepreneur", "business owner")
    ):
        return "entrepreneurial"

    if any(
        word in role_lower
        for word in (
            "prefect",
            "president",
            "chairperson",
            "chairman",
            "captain",
            "student leader",
            "representative",
        )
    ):
        return "leadership"

    return "professional"



def _extract_entry(
    entry_lines: list[str],
    section_type: str,
) -> dict:
    start_date, end_date = _extract_dates(entry_lines)

    descriptive_lines = []

    for line in entry_lines:
        cleaned = _remove_dates(line)

        if cleaned:
            descriptive_lines.append(cleaned)

    if not descriptive_lines:
        return {}

    # Support both:
    # Role - Employer
    # Role
    # Employer

    role, employer = _split_role_and_employer(descriptive_lines[0])

    if employer:
        responsibility_start = 1
    else:
        employer = (
            descriptive_lines[1]
            if len(descriptive_lines) > 1
            else None
        )
        responsibility_start = 2

    responsibilities = []

    for line in descriptive_lines[responsibility_start:]:
        responsibility = _clean_responsibility(line)

        if responsibility:
            responsibilities.append(responsibility)

    experience_type = _classify_experience(role, section_type)

    return {
        "role": role,
        "employer": employer,
        "experience_type": experience_type,
        "start_date": start_date,
        "end_date": end_date,
        "responsibilities": responsibilities,
        "evidence": entry_lines.copy(),
    }


def extract_experience(text: str) -> list[dict]:
    """
    Extract professional, leadership, entrepreneurial,
    and volunteer experience from CV text.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    if not text.strip():
        return []

    sections = _extract_experience_sections(text)

    experiences = []

    for section_type, lines in sections:
        entries = _split_into_entries(lines)

        for entry in entries:
            record = _extract_entry(entry, section_type)

            if record and record["role"]:
                experiences.append(record)

    return experiences
