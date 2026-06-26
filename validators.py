import re

QUESTION_MAX_LENGTH = 512
QUESTION_MIN_LENGTH = 5
URL_PATTERN = re.compile(r"https?://|www\.|mailto:|\.ru\b|\.com\b|telegram\.me|t\.me|vk\.com", re.IGNORECASE)
ALLOWED_COMMAND_PATTERN = re.compile(r"^/hack(?:@[\w_]+)?\s+([a-z0-9_]+)$", re.IGNORECASE)


def is_valid_question(question: str) -> bool:
    if not question:
        return False
    text = question.strip()
    if len(text) < QUESTION_MIN_LENGTH or len(text) > QUESTION_MAX_LENGTH:
        return False
    if URL_PATTERN.search(text):
        return False
    if re.search(r"[@#$%^&*_=+<>\[\]{}|\\]", text):
        return False
    return True


def extract_hackathon_slug(text: str) -> str | None:
    if not text:
        return None
    match = ALLOWED_COMMAND_PATTERN.match(text.strip())
    if not match:
        return None
    return match.group(1).lower()
