
import re


# --------------------------------------------------
# PATTERNS AND CONSTANTS
# --------------------------------------------------

PROJECT_HEADINGS = {
    "projects",
    "personal projects",
    "academic projects",
    "professional projects",
    "selected projects",
    "relevant projects",
    "key projects",
    "project experience",
}

END_HEADINGS = {
    "education",
    "educational background",
    "academic background",
    "work experience",
    "professional experience",
    "employment history",
    "leadership professional experience",
    "volunteer experience",
    "skills",
    "technical skills",
    "certifications",
    "achievements awards",
    "awards",
    "interests",
    "career interests",
    "references",
}

TECHNOLOGIES = {
    "Android Studio": r"\bandroid studio\b",
    "JavaScript": r"\bjavascript\b",
    "TypeScript": r"\btypescript\b",
    "Python": r"\bpython\b",
    "Kotlin": r"\bkotlin\b",
    "Firebase": r"\bfirebase\b",
    "MySQL": r"\bmysql\b",
    "PostgreSQL": r"\bpostgresql\b",
    "MongoDB": r"\bmongodb\b",
    "SQLite": r"\bsqlite\b",
    "HTML": r"\bhtml\b",
    "CSS": r"\bcss\b",
    "React": r"\breact(?:\.js)?\b",
    "Node.js": r"\bnode\.?js\b",
    "Django": r"\bdjango\b",
    "Flask": r"\bflask\b",
    "FastAPI": r"\bfastapi\b",
    "Java": r"\bjava\b",
    "C++": r"\bc\+\+\b",
    "C#": r"\bc#\b",
    "PHP": r"\bphp\b",
    "SQL": r"\bsql\b",
    "Git": r"\bgit\b",
    "GitHub": r"\bgithub\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b",
    "AWS": r"\baws\b",
    "Azure": r"\bazure\b",
    "Figma": r"\bfigma\b",
    "WordPress": r"\bwordpress\b",
    "TensorFlow": r"\btensorflow\b",
    "PyTorch": r"\bpytorch\b",
    "Pandas": r"\bpandas\b",
    "NumPy": r"\bnumpy\b",
    "OpenCV": r"\bopencv\b",
    "Bootstrap": r"\bbootstrap\b",
}


# --------------------------------------------------
# NORMALIZATION
# --------------------------------------------------

def _normalize_heading(line: str) -> str:
    """Normalize section headings."""
    normalized = re.sub(r"[^a-z ]", "", line.lower())
    return re.sub(r"\s+", " ", normalized).strip()


def _clean_line(line: str) -> str:
    """Remove common bullets and surrounding whitespace."""
    line = line.strip()
    line = re.sub(r"^[•●▪◦\-*]\s*", "", line)
    return line.strip()


# --------------------------------------------------
# PROJECT SECTION EXTRACTION
# --------------------------------------------------

def _extract_project_section(text: str) -> list[str]:
    """
    Extract lines belonging to a recognized project section.

    Return an empty list when no project section exists.
    """
    lines = text.splitlines()
    start_index = None

    for index, line in enumerate(lines):
        if _normalize_heading(line) in PROJECT_HEADINGS:
            start_index = index + 1
            break

    if start_index is None:
        return []

    project_lines = []

    for line in lines[start_index:]:
        if _normalize_heading(line) in END_HEADINGS:
            break

        project_lines.append(line)

    return project_lines


# --------------------------------------------------
# PROJECT ENTRY SPLITTING
# --------------------------------------------------

def _split_project_entries(lines: list[str]) -> list[list[str]]:
    """Split a project section into individual project entries."""
    entries = []
    current_entry = []

    for line in lines:
        cleaned = _clean_line(line)

        if not cleaned:
            if current_entry:
                entries.append(current_entry)
                current_entry = []
            continue

        current_entry.append(cleaned)

    if current_entry:
        entries.append(current_entry)

    return entries


# --------------------------------------------------
# TECHNOLOGY EXTRACTION
# --------------------------------------------------

def _extract_technologies(text: str) -> list[str]:
    """Extract recognized technologies while avoiding duplicates."""
    technologies = []

    for technology, pattern in TECHNOLOGIES.items():
        if re.search(pattern, text, re.IGNORECASE):
            technologies.append(technology)

    return technologies


# --------------------------------------------------
# PROJECT EXTRACTION
# --------------------------------------------------

def _extract_project(entry_lines: list[str]) -> dict:
    """Extract structured information from one project entry."""
    if not entry_lines:
        return {}

    first_line = entry_lines[0]

    # Support labels such as "Project: Portfolio Website".
    name = re.sub(
        r"^project\s*:\s*",
        "",
        first_line,
        flags=re.IGNORECASE,
    ).strip()

    if not name:
        return {}

    description_lines = entry_lines[1:]

    description = " ".join(
        line.strip()
        for line in description_lines
        if line.strip()
    )

    technologies = _extract_technologies(
        " ".join(entry_lines)
    )

    return {
        "name": name,
        "description": description,
        "technologies": technologies,
        "evidence": entry_lines.copy(),
    }


# --------------------------------------------------
# MAIN EXTRACTION FUNCTION
# --------------------------------------------------

def extract_projects(text: str) -> list[dict]:
    """
    Extract projects from CV text.

    Each project contains:
        name
        description
        technologies
        evidence
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    if not text.strip():
        return []

    project_lines = _extract_project_section(text)

    if not project_lines:
        return []

    entries = _split_project_entries(project_lines)

    projects = []

    for entry in entries:
        project = _extract_project(entry)

        if project:
            projects.append(project)

    return projects
