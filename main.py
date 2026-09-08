
from pathlib import Path
import json

from company_list import COMPANIES
from codal_report_downloader import download_reports
from codal_report_extractor import get_all_downloaded_reports

from extractors.html_extractor import extract_html
from extractors.pdf_extractor import extract_pdf
from extractors.json_to_text import save_json_as_text

from normalizer import normalize


# ============================================================
# CONFIGURATION
# ============================================================

# Download reports before processing
DOWNLOAD_REPORTS = False

# Directory containing downloaded reports
DOWNLOAD_DIR = "temp_dir"

# Output directories
RAW_OUTPUT_DIR = Path("json_output/raw")
NORMALIZED_OUTPUT_DIR = Path("json_output/normalized")

# Debug text output
DEBUG_OUTPUT = Path("debug_output.txt")


# ============================================================
# DOWNLOAD REPORTS
# ============================================================

if DOWNLOAD_REPORTS:
    for company in COMPANIES:
        download_reports(company, DOWNLOAD_DIR)


# ============================================================
# PREPARE OUTPUT DIRECTORIES
# ============================================================

RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
NORMALIZED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# GET REPORT FILES
# ============================================================

report_files = get_all_downloaded_reports(DOWNLOAD_DIR)


# ============================================================
# PROCESS REPORTS
# ============================================================

for report_file in report_files:

    report_file = Path(report_file)

    print("=" * 80)
    print(f"PROCESSING: {report_file.name}")

    # --------------------------------------------------------
    # 1. EXTRACTION
    # --------------------------------------------------------

    if report_file.suffix.lower() == ".html":

        raw_report = extract_html(report_file)

    elif report_file.suffix.lower() == ".pdf":

        raw_report = extract_pdf(report_file)

    else:

        print(f"SKIPPED: unsupported file type: {report_file.suffix}")
        continue


    # --------------------------------------------------------
    # 2. BASIC VALIDATION
    # --------------------------------------------------------

    print("RAW TYPE:", type(raw_report))
    print("RAW EMPTY:", not raw_report)

    if isinstance(raw_report, dict):
        print("RAW KEYS:", list(raw_report.keys()))

    if (
        isinstance(raw_report, dict)
        and "document" in raw_report
        and isinstance(raw_report["document"], dict)
    ):
        document = raw_report["document"]

        print("DOCUMENT KEYS:", list(document.keys()))

        if "pages" in document and isinstance(document["pages"], list):
            print("PAGES COUNT:", len(document["pages"]))


    # --------------------------------------------------------
    # 3. SAVE RAW JSON
    # --------------------------------------------------------

    raw_output_file = RAW_OUTPUT_DIR / f"{report_file.stem}.json"

    with raw_output_file.open("w", encoding="utf-8") as f:
        json.dump(
            raw_report,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"RAW JSON SAVED: {raw_output_file}")


    # --------------------------------------------------------
    # 4. NORMALIZATION
    # --------------------------------------------------------

    normalized_report = normalize(raw_report)

    print("NORMALIZED TYPE:", type(normalized_report))
    print("NORMALIZED EMPTY:", not normalized_report)


    # --------------------------------------------------------
    # 5. SAVE NORMALIZED JSON
    # --------------------------------------------------------

    normalized_output_file = (
        NORMALIZED_OUTPUT_DIR / f"{report_file.stem}.json"
    )

    with normalized_output_file.open("w", encoding="utf-8") as f:
        json.dump(
            normalized_report,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"NORMALIZED JSON SAVED: {normalized_output_file}")


    # --------------------------------------------------------
    # 6. DEBUG TEXT
    # --------------------------------------------------------

    save_json_as_text(
        normalized_report,
        DEBUG_OUTPUT
    )

    print(f"DEBUG TEXT SAVED: {DEBUG_OUTPUT}")


print("=" * 80)
print("PROCESSING COMPLETE")

