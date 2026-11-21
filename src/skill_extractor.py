
import re


SKILL_CATEGORIES = {
    "technical": [
        "python", "java", "javascript", "typescript", "c++", "c#",
        "php", "kotlin", "swift", "sql", "html", "css",
        "machine learning", "deep learning", "data analysis",
        "data science", "artificial intelligence", "networking",
        "cybersecurity", "software development", "web development",
        "mobile development", "database management", "cloud computing",
        "api development", "statistics", "data visualization",
        "natural language processing", "computer vision",
        "data engineering", "software testing",
    ],
    "tools": [
        "git", "github", "docker", "kubernetes", "excel",
        "power bi", "tableau", "android studio", "visual studio",
        "pycharm", "jupyter", "linux", "mysql", "postgresql",
        "mongodb", "firebase", "aws", "azure", "google cloud",
        "figma", "photoshop", "intellij idea", "vs code",
        "visual studio code", "postman", "jira", "trello",
    ],
    "soft": [
        "communication", "teamwork", "leadership",
        "problem solving", "critical thinking",
        "time management", "adaptability",
        "creativity", "collaboration", "attention to detail",
        "interpersonal skills", "decision making",
        "conflict resolution",
    ],
    "professional": [
        "research", "project management", "technical writing",
        "report writing", "presentation", "customer service",
        "requirements analysis", "quality assurance",
        "testing", "documentation", "data collection",
        "business analysis", "strategic planning",
        "stakeholder management",
    ],
}


SECTION_TYPES = {
    # Skills sections
    "skills": "skills",
    "technical skills": "skills",
    "technical competencies": "skills",
    "core competencies": "skills",
    "competencies": "skills",
    "professional skills": "skills",
    "key skills": "skills",
    "areas of expertise": "skills",

    # Project sections
    "projects": "projects",
    "personal projects": "projects",
    "academic projects": "projects",
    "professional projects": "projects",
    "project experience": "projects",
    "selected projects": "projects",
    "relevant projects": "projects",

    # Experience sections
    "work experience": "experience",
    "professional experience": "experience",
    "employment history": "experience",
    "experience": "experience",
    "internship experience": "experience",
    "leadership professional experience": "experience",
    "volunteer experience": "experience",
    "leadership experience": "experience",

    # Other sections that establish a new section boundary
    "education": "general",
    "educational background": "general",
    "academic background": "general",
    "academic qualifications": "general",
    "certifications": "general",
    "certificates": "general",
    "references": "general",
    "career objective": "general",
    "professional objective": "general",
    "professional summary": "general",
    "summary": "general",
    "profile": "general",
    "career interests": "general",
    "interests": "general",
    "achievements awards": "general",
    "awards": "general",
    "languages": "general",
    "publications": "general",
    "training": "general",
}


ALL_SKILLS = {
    skill: category
    for category, skills in SKILL_CATEGORIES.items()
    for skill in skills
}


def _normalize_heading(line: str) -> str:
    line = line.strip().lower()
    line = re.sub(r"[^a-z0-9\s]", "", line)
    return re.sub(r"\s+", " ", line).strip()


def _detect_section_types(
    text: str,
) -> list[tuple[str, str, str | None]]:
    """
    Return CV lines with their section type and original heading.

    Each tuple contains:
        (line, section_type, original_section_heading)
    """
    current_section = "general"
    current_heading = None
    result = []

    for line in text.splitlines():
        heading = _normalize_heading(line)

        if heading in SECTION_TYPES:
            current_section = SECTION_TYPES[heading]
            current_heading = line.strip()
            continue

        result.append((
            line,
            current_section,
            current_heading,
        ))

    return result


def _matches_skill(skill: str, line: str) -> bool:
    """
    Match a complete skill phrase without matching partial words.
    """
    pattern = re.compile(
        rf"(?<![a-z0-9]){re.escape(skill)}(?![a-z0-9])",
        re.IGNORECASE,
    )

    return bool(pattern.search(line))


def extract_skills(text: str) -> list[dict]:
    """
    Extract known skills from CV text.

    Preserves:
    - Skill name
    - Skill category
    - Original evidence lines
    - Normalized source types
    - Original CV section headings
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    if not text.strip():
        return []

    section_lines = _detect_section_types(text)
    extracted = {}

    for line, section, source_heading in section_lines:
        if not line.strip():
            continue

        for skill, category in ALL_SKILLS.items():
            if not _matches_skill(skill, line):
                continue

            if skill not in extracted:
                extracted[skill] = {
                    "skill": skill,
                    "category": category,
                    "evidence": [],
                    "sources": [],
                    "source_sections": [],
                }

            record = extracted[skill]

            # Preserve distinct evidence lines.
            normalized_evidence = re.sub(
                r"\s+", " ", line.strip()
            ).casefold()

            existing_evidence = {
                re.sub(r"\s+", " ", evidence.strip()).casefold()
                for evidence in record["evidence"]
            }

            if normalized_evidence not in existing_evidence:
                record["evidence"].append(line.strip())

            # Preserve the normalized section type.
            if section not in record["sources"]:
                record["sources"].append(section)

            # Preserve the original CV section heading.
            if (
                source_heading
                and source_heading not in record["source_sections"]
            ):
                record["source_sections"].append(source_heading)

    return list(extracted.values())
