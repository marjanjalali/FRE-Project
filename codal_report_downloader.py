import os
import requests
import pandas as pd

def download_reports(company, DOWNLOAD_DIR):


    # =====================================================
    # Configuration
    # =====================================================

    # Persian fiscal year range
    START_YEAR = 1400
    END_YEAR = 1404

    # Create Directory where downloaded reports will be stored
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Codal search API endpoint
    SEARCH_URL = "https://search.codal.ir/api/search/v2/q"

    # HTTP request headers
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # =====================================================
    # Download reports
    # =====================================================

    def download_file(url, filename):
        # Minimum file size (20 KB) required to save a downloaded file
        MIN_FILE_SIZE = 20 * 1024
        try:
            response = requests.get(url, headers=headers, allow_redirects=True)

            if response.status_code != 200:
                return False

            # Save the downloaded file
            with open(filename, "wb") as f:
                f.write(response.content)

            # Remove very small files (likely blank/placeholder files)
            if os.path.getsize(filename) < MIN_FILE_SIZE:
                os.remove(filename)
                print(f"Deleted small file: {filename}")
                return False

            print(f"Saved: {filename}")
            return True

        except Exception as e:
            print(e)
            return False
            
    print(f"\nSearching reports for {company}")

    params = {
        "Symbol": company,
        "PageNumber": 1,
        "PageSize": 200,

        # Audited reports only
        "Audited": "true",
        "NotAudited": "false",

        # Do not restrict by category or letter type
        "Category": "-1",
        "LetterType": "-1",

        # Annual financial statements
        "ReportingType": "1000005",

        # Other filters used by Codal
        #"Childs": "true",
        # Search reports of the main listed company
        "Mains": "true",

        # Include consolidated reports in the search results
        "Consolidatable": "true",

        # Include separate financial statements in the search results
        "NotConsolidatable": "true",
    }

    # Send search request
    r = requests.get(SEARCH_URL, params=params, headers=headers)

    # Skip company if request failed
    if r.status_code != 200:
        print("Search failed")
        return

    # Parse JSON response
    data = r.json()

    # Retrieve list of reports
    letters = data.get("Letters", [])

    # Process each report
    for report in letters:

        # Report title and publication date
        title = report.get("Title", "")
        publish_date = report.get("PublishDateTime", "")

        # Extract Persian year from publication date
        try:
            year = int(publish_date[:4])
        except:
            continue

        # Filter reports by year
        if year < START_YEAR or year > END_YEAR:
            continue

        # Keep only audited financial statements
        if (
            "صورت‌های مالی" not in title or
            "حسابرسی شده" not in title
        ):
            continue

        # Skip consolidated financial statements
        if "تلفیقی" in title:
            continue

    # Retrieve report identifiers
        tracing_no = report.get("TracingNo")
        pdf_path = report.get("PdfUrl")
        html_path = report.get("Url")
        excel_url = report.get("ExcelUrl")
        attachment_path = report.get("AttachmentUrl")
        xbrl_url = report.get("XbrlUrl")
        # Retrieve report resources


        # Skip reports without a valid PDF or path
        if not tracing_no or not (pdf_path or html_path or excel_url or attachment_path or xbrl_url):
            continue

        # Download PDF
        if pdf_path:
            download_file(
                "https://www.codal.ir/" + pdf_path,
                os.path.join(DOWNLOAD_DIR, f"{company}_{tracing_no}.pdf")
            )

        # Download HTML page
        if html_path:
            download_file(
                "https://www.codal.ir" + html_path,
                os.path.join(DOWNLOAD_DIR, f"{company}_{tracing_no}.html")
            )

        # # Download attachments
        # if attachment_path:
        #     download_file(
        #         "https://www.codal.ir" + attachment_path,
        #         os.path.join(DOWNLOAD_DIR, f"{company}_{tracing_no}_attachment")
        #     ) 


        # # Download Excel
        # if excel_url:
        #     download_file(
        #         excel_url,
        #         os.path.join(DOWNLOAD_DIR, f"{company}_{tracing_no}.xlsx")
        #     )

        # # Download XBRL
        # if xbrl_url:
        #     download_file(
        #         "https://www.codal.ir" + xbrl_url,
        #         os.path.join(DOWNLOAD_DIR, f"{company}_{tracing_no}.xbrl")
        #     )




        # try:
        #     # Download PDF
        #     pdf = requests.get(pdf_url, headers=headers)

        #     # Save only valid PDF files
        #     if (
        #         pdf.status_code == 200 and
        #         pdf.headers.get("Content-Type", "").startswith("application/pdf")
        #     ):
        #         with open(filename, "wb") as f:
        #             f.write(pdf.content)
        #     else:
        #         print("Not a valid PDF:", pdf_url)

        # except Exception as e:
        #     print(e)




    print("\nFinished.")