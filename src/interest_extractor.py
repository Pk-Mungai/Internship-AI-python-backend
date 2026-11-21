
import re


INTEREST_KEYWORDS = {
    "Software Development": [
        "software development",
        "software engineering",
        "software developer",
    ],
    "Web Development": [
        "web development",
        "web developer",
    ],
    "Mobile Application Development": [
        "mobile application development",
        "mobile app development",
        "android development",
        "ios development",
    ],
    "Artificial Intelligence": [
        "artificial intelligence",
        "ai development",
    ],
    "Machine Learning": [
        "machine learning",
    ],
    "Data Science": [
        "data science",
        "data scientist",
    ],
    "Data Analytics": [
        "data analytics",
        "data analysis",
        "data analyst",
    ],
    "Cybersecurity": [
        "cybersecurity",
        "cyber security",
    ],
    "Cloud Computing": [
        "cloud computing",
        "cloud engineering",
    ],
    "Agricultural Technology": [
        "agricultural technology",
        "agritech",
        "agricultural innovation",
    ],
    "Digital Marketing": [
        "digital marketing",
        "online marketing",
    ],
    "Networking": [
        "computer networking",
        "network engineering",
    ],
    "Database Administration": [
        "database administration",
        "database management",
    ],
    "UI/UX Design": [
        "ui/ux design",
        "ui design",
        "ux design",
        "user interface design",
        "user experience design",
    ],
    "Game Development": [
        "game development",
        "game developer",
    ],
    "Internet of Things": [
        "internet of things",
        "iot development",
    ],
    "Robotics": [
        "robotics",
        "robotic engineering",
    ],
    "Entrepreneurship": [
        "entrepreneurship",
        "business development",
    ],
}


INTEREST_HEADINGS = {
    "career interests",
    "interests",
    "areas of interest",
    "professional interests",
}

OBJECTIVE_HEADINGS = {
    "career objective",
    "professional objective",
    "career profile",
    "professional summary",
    "summary",
}

END_HEADINGS = {
    "education",
    "educational background",
    "academic background",
    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "leadership professional experience",
    "skills",
    "technical skills",
    "core competencies",
    "projects",
    "personal projects",
    "certifications",
    "achievements awards",
    "awards",
    "volunteer experience",
    "references",
}


def _normalize_heading(line: str) -> str:
    line = line.strip().lower()
    line = re.sub(r"[^a-z0-9\s]", "", line)
    return re.sub(r"\s+", " ", line).strip()


def _is_heading(line: str) -> bool:
    normalized = _normalize_heading(line)

    return normalized in (
        INTEREST_HEADINGS
        | OBJECTIVE_HEADINGS
        | END_HEADINGS
    )


def _extract_relevant_sections(cv_text: str) -> list[str]:
    lines = cv_text.splitlines()
    relevant_sections = []

    current_heading = None
    current_content = []

    for line in lines:
        normalized = _normalize_heading(line)

        if normalized in (
            INTEREST_HEADINGS
            | OBJECTIVE_HEADINGS
            | END_HEADINGS
        ):
            if current_heading is not None:
                relevant_sections.append(
                    "\n".join(current_content)
                )

            if normalized in INTEREST_HEADINGS:
                current_heading = "interests"
            elif normalized in OBJECTIVE_HEADINGS:
                current_heading = "objective"
            else:
                current_heading = None

            current_content = []
            continue

        if current_heading is not None:
            current_content.append(line)

    if current_heading is not None:
        relevant_sections.append("\n".join(current_content))

    return relevant_sections


def _find_interests(text: str) -> list[str]:
    normalized_text = text.lower()
    found_interests = []

    for interest, keywords in INTEREST_KEYWORDS.items():
        for keyword in keywords:
            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(keyword)
                + r"(?![a-z0-9])"
            )

            if re.search(pattern, normalized_text):
                found_interests.append(interest)
                break

    return found_interests


def extract_interests(cv_text: str) -> list[str]:
    """
    Extract explicitly stated career interests from CV sections.

    The extractor examines career-interest sections, career objectives,
    and professional summaries. It does not infer career interests
    merely from technical skills.
    """
    if not isinstance(cv_text, str):
        raise TypeError("CV text must be a string.")

    if not cv_text.strip():
        return []

    relevant_sections = _extract_relevant_sections(cv_text)

    if not relevant_sections:
        return []

    interests = []
    seen = set()

    for section in relevant_sections:
        for interest in _find_interests(section):
            if interest not in seen:
                interests.append(interest)
                seen.add(interest)

    return interests
