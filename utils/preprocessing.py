import re
from typing import Optional

# Common OCR confusion map
CONFUSIONS = {
    "0": "O",
    "O": "0",
    "1": "I",
    "I": "1",
    "5": "S",
    "S": "5",
    "8": "B",
    "B": "8",
    "4": "A",
    "6": "G",
    "9": "G",
}

def correct_confusions(text: str) -> str:
    """Fix common OCR character confusions."""
    return "".join(CONFUSIONS.get(c, c) for c in text)

def preprocess_text(raw_text: str) -> Optional[str]:
    """
    Extract valid Indian license plate from OCR text.
    Handles common OCR mistakes and flexible plate patterns.
    """
    if not raw_text:
        return None

    # Step 1: clean and uppercase
    cleaned = re.sub(r"[^A-Z0-9]", "", raw_text.upper())

    # Step 2: correct OCR confusions
    corrected = correct_confusions(cleaned)

    # Step 3: define flexible regex patterns
    patterns = [
        r"[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}",  # Typical plates like MH43O9740
        r"[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}",      # MH12EM8473
        r"[A-Z]{2}[0-9]{2}[A-Z]{1}[0-9]{4}",      # HR26U5478
    ]

    # Step 4: check all substrings of plausible plate lengths
    for length in range(9, 11):  # Indian plates are usually 9–10 chars without spaces
        for i in range(len(corrected) - length + 1):
            candidate = corrected[i:i+length]
            for pattern in patterns:
                if re.fullmatch(pattern, candidate):
                    return candidate

    return None

# ✅ Example usage
ocr_text = "MH.43.0.9740 Global Gallarie Group 00c9 121244"
plate = preprocess_text(ocr_text)
print("Processed Plate:", plate)
