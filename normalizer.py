
# lib/normalizer.py

import unicodedata


def normalize_text(text):
    """
    Normalize extracted Persian/Arabic text
    while preserving the original content structure.
    """

    if not isinstance(text, str):
        return text

    # Normalize Unicode and Arabic presentation forms
    text = unicodedata.normalize("NFKC", text)

    replacements = {
        # Arabic/Persian letters
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",
        "ھ": "ه",

        # Invisible / directional characters
        "\u200c": " ",
        "\u200e": " ",
        "\u200f": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Arabic/Persian digits → English digits
    digits = {
        "٠": "0",
        "١": "1",
        "٢": "2",
        "٣": "3",
        "٤": "4",
        "٥": "5",
        "٦": "6",
        "٧": "7",
        "٨": "8",
        "٩": "9",

        "۰": "0",
        "۱": "1",
        "۲": "2",
        "۳": "3",
        "۴": "4",
        "۵": "5",
        "۶": "6",
        "۷": "7",
        "۸": "8",
        "۹": "9",
    }

    for old, new in digits.items():
        text = text.replace(old, new)

    # Normalize whitespace
    text = " ".join(text.split())

    return text


def normalize(data):
    """
    Recursively normalize textual content while
    preserving the original data structure.
    """

    if isinstance(data, list):
        return [normalize(item) for item in data]

    if isinstance(data, dict):
        result = {}

        for key, value in data.items():

            # Normalize actual text content
            if key == "text" and isinstance(value, str):
                result[key] = normalize_text(value)

            else:
                result[key] = normalize(value)

        return result

    # Fallback for standalone strings
    if isinstance(data, str):
        return normalize_text(data)

    return data

