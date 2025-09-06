import re
from typing import Optional

def preprocess_text(raw_text: str) -> Optional[str]:
    """Extracts valid Indian license plate number using regex patterns."""
    cleaned = re.sub(r"[^A-Z0-9]", "", raw_text.upper())

    patterns = [
        r"([A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4})",  # MH12EM8473
        r"([A-Z]{2}[0-9]{2}[A-Z]{1}[0-9]{4})",  # HR26U5478
        r"([A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4})"  # DL5C1234
    ]

    for pattern in patterns:
        match = re.search(pattern, cleaned)
        if match:
            return match.group(1)
    return None
