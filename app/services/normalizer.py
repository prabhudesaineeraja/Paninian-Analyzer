import re


def normalize_text(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"[|।]+", "।", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned
