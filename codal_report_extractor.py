import os
#import fitz  # PyMuPDF pip3 install pymupdf
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import unicodedata
import re

DOWNLOAD_DIR = "codal_reports"

def get_all_downloaded_reports(DOWNLOAD_DIR):
    """
    Return all files saved inside DOWNLOAD_DIR and its subdirectories.
    """

    if not os.path.exists(DOWNLOAD_DIR):
        return []

    reports = []

    for root, dirs, files in os.walk(DOWNLOAD_DIR):
        for filename in files:
            filepath = os.path.join(root, filename)
            reports.append(filepath)

    return reports

def normalize_text(text):
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)

    replacements = {
        # Arabic/Persian letters
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",
        "ھ": "ه",

        # Invisible characters
        "\u200c": " ",
        "\u200e": " ",
        "\u200f": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize Persian/Arabic digits (optional)
    digits = {
        "٠": "0", "١": "1", "٢": "2",
        "٣": "3", "٤": "4", "٥": "5",
        "٦": "6", "٧": "7",
        "٨": "8", "٩": "9",

        "۰": "0", "۱": "1", "۲": "2",
        "۳": "3", "۴": "4", "۵": "5",
        "۶": "6", "۷": "7",
        "۸": "8", "۹": "9",
    }

    for old, new in digits.items():
        text = text.replace(old, new)

    # Remove extra spaces
    text = " ".join(text.split())

    return text

def extract_text(report_file):
    """
    Extract text from PDF or HTML report.        if extension == ".pdf":
            reader = PdfReader(report_file)

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"
    """

    text = ""
    soup = None

    try:
        extension = os.path.splitext(report_file)[1].lower()

        # PDF
        if extension == ".pdf":
            reader = PdfReader(report_file)

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        # HTML
        elif extension in [".html", ".htm"]:
            with open(report_file, "r", encoding="utf-8") as f:
                html = f.read()

            soup = BeautifulSoup(html, "html.parser")

            # Keep the original DOM structure intact.
            # A separate copy is used only for text extraction.
            text_soup = BeautifulSoup(html, "html.parser")

            # BeautifulSoup.get_text() does not include input[value].
            # Replace input elements with their value so section headings
            # such as "نتیجه گیری مشروط" become part of the extracted text.
            for tag in text_soup.find_all("input"):
                value = tag.get("value")

                if value:
                    tag.replace_with(value)

            # Extract text AFTER processing all input elements
            text = text_soup.get_text(separator="\n")

        else:
            print(f"Unsupported format: {report_file}")
            return ""

    except Exception as e:
        print(f"Cannot read {report_file}: {e}")
        return ""

    text = normalize_text(text)

    # Debug: find and print context around "اظهار"
    idx = text.find("اظهار")

    return text, soup

