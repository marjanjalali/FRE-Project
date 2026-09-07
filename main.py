
from company_list import COMPANIES
from codal_report_downloader import download_reports
from extractors.html_extractor import extract_html
from codal_report_extractor import get_all_downloaded_reports
from pathlib import Path
from pathlib import Path
import json
from extractors.html_extractor import extract_html
import json
from extractors.json_to_text import save_json_as_text, pdf_json_to_text, save_pdf_as_text
from extractors.pdf_extractor import extract_pdf, debug_spans, debug_blocks_and_lines, debug_pdf_coordinates, debug_block_positions, debug_line_order

# HTML
#  ↓
# RAW STRUCTURAL JSON      
#  ↓
# Clean / Normalize
#  ↓
# Semantic Processing
#  ↓
# Financial / Audit Analysis

# from extractors.pdf_extractor import extract_pdf


# Expected output structure:
#
# {
#     "document": {
#         "title": "...",
#         "metadata": {
#             "...": "..."
#         },
#         "content": {
#             "title": "...",
#             "recipient": "...",
#             "company": "...",
#             "sections": [
#                 {
#                     "title": "...",
#                     "number": "...",
#                     "content": [
#                         {
#                             "type": "paragraph",
#                             "text": "..."
#                         }
#                     ]
#                 }
#             ],
#             "date": "...",
#             "auditor": "...",
#             "signatures": [
#                 {
#                     "position": "...",
#                     "name": "...",
#                     "membership_number": "...",
#                     "time": "..."
#                 }
#             ]
#         }
#     }
# }

# ============================================================
# DOWNLOAD CONFIGURATION
# ============================================================
# Controls whether reports should be downloaded before processing.
#
# False:
#   Use reports that already exist in DOWNLOAD_DIR.
#
# True:
#   Download reports for all companies in COMPANIES.
DOWNLOAD_REPORTS = False
# DOWNLOAD_REPORTS = True


# Directory where downloaded reports will be stored
# Different directories can be enabled for testing different
# datasets or error cases.
# DOWNLOAD_DIR = "codal_reports1"
# DOWNLOAD_DIR = "codal_reports"
DOWNLOAD_DIR = "temp_dir"

# ============================================================
# DOWNLOAD REPORTS
# ============================================================
# If downloading is enabled, retrieve reports for every company
# in the configured company list.
#
# Otherwise, the pipeline works directly with the reports that
# are already available in DOWNLOAD_DIR.
if DOWNLOAD_REPORTS:
    for company in COMPANIES:
        # Download Codal reports for the current company
        report_files = download_reports(company, DOWNLOAD_DIR)

# ============================================================
# EXTRACT REPORT CONTENT
# ============================================================
# Process each report according to its file type.
# HTML and PDF reports are handled by their respective extractors.
report_files = get_all_downloaded_reports(DOWNLOAD_DIR)

def find_top_level_tables(node):
    tables = []

    if isinstance(node, dict):

        if node.get("type") == "table":
            return [node]

        for value in node.values():

            if isinstance(value, dict) and value.get("type") == "table":
                tables.append(value)

            else:
                tables.extend(find_top_level_tables(value))

    elif isinstance(node, list):

        for item in node:
            tables.extend(find_top_level_tables(item))

    return tables


for report_file in report_files:

    report_file = Path(report_file)
    if report_file.suffix.lower() == ".html":

        report = extract_html(report_file)

        with open("debug_output.json", "w", encoding="utf-8") as f:
            json.dump(
                report,
                f,
                ensure_ascii=False,
                indent=2
            )

        print("REPORT TYPE:", type(report))

        output_path = "debug_output.txt"

        save_json_as_text(
            report,
            output_path
        )

        tables = find_top_level_tables(report)
        output_dir = Path(DOWNLOAD_DIR) / "extracted_tables"
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / f"{report_file.stem}.json"

        with output_file.open("w", encoding="utf-8") as f:
            json.dump(
                tables,
                f,
                ensure_ascii=False,
                indent=2
            )

    if report_file.suffix.lower() == ".pdf":
        report = extract_pdf(report_file)
        output_dir = Path("json_output")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{report_file.stem}.json"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(
                report,
                f,
                ensure_ascii=False,
                indent=2
            )

        print("REPORT TYPE:", type(report))

        output_path = "debug_output.txt"

        save_json_as_text(
            report,
            output_path
        )

        tables = find_top_level_tables(report)
        output_dir = Path(DOWNLOAD_DIR) / "extracted_tables"
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / f"{report_file.stem}.json"

        with output_file.open("w", encoding="utf-8") as f:
            json.dump(
                tables,
                f,
                ensure_ascii=False,
                indent=2
            )

        # save_json(report, output_path)

        # debug_spans(
        #     report,
        #     page_number=1
        # )

    #     debug_blocks_and_lines(
    #     report
    # )
        # debug_pdf_coordinates(report)
        # debug_block_positions(report)
        # debug_line_order(report)


    #     save_pdf_as_text(
    #     report,
    #     "debug_pdf.txt"
    # )
    # pdf_text = pdf_json_to_text(report)


    # print(pdf_text[:5000])

    # print(f"Saved: {output_file}")

    # print("TABLE COUNT:", len(tables))

    # print(
    #     json.dumps(
    #         tables,
    #         ensure_ascii=False,
    #         indent=2
    #     )
    # )

# print("REPORT TYPE:", type(report))
# print("REPORT:", report)
# print("=" * 80)
# ============================================================
# RUN / DEBUG COMMANDS
# ============================================================
# Run the main pipeline while suppressing stderr output:
#FRE
#python3 main.py 2>/dev/null

# Inspect running Python processes:
#ps aux | grep python

