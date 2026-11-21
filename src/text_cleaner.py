
import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Clean extracted CV text while preserving meaningful line breaks.

    Args:
        text: Raw text extracted from a PDF.

    Returns:
        Normalized CV text.
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    if not text.strip():
        return ""

    # 1. Normalize Unicode characters
    text = unicodedata.normalize("NFKC", text)

    # 2. Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # 3. Replace non-breaking spaces and tabs
    text = text.replace("\u00a0", " ")
    text = text.replace("\t", " ")

    # 4. Remove invisible zero-width characters
    text = re.sub(r"[\u200b-\u200d\ufeff]", "", text)

    # 5. Remove unwanted control characters,
    # while preserving line breaks
    text = "".join(
        char for char in text
        if char == "\n" or not unicodedata.category(char).startswith("C")
    )

    # 6. Remove unnecessary spaces within each line
    lines = []

    for line in text.split("\n"):
        line = re.sub(r"[ ]+", " ", line)
        line = line.strip()
        lines.append(line)

    # 7. Remove leading and trailing blank lines
    while lines and not lines[0]:
        lines.pop(0)

    while lines and not lines[-1]:
        lines.pop()

    # 8. Limit consecutive blank lines to one
    cleaned_lines = []
    previous_was_blank = False

    for line in lines:
        is_blank = not line

        if is_blank and previous_was_blank:
            continue

        cleaned_lines.append(line)
        previous_was_blank = is_blank

    return "\n".join(cleaned_lines)
