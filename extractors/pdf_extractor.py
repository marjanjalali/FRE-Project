
from pathlib import Path
import pymupdf

def extract_pdf(file_path: Path):
    """
    Extract raw PDF structure while preserving
    text, page information, and spatial coordinates.
    """

    document = {
        "document": {
            "title": file_path.stem,
            "type": "pdf_document",
            "pages": []
        }
    }

    pdf = pymupdf.open(file_path)

    try:
        for page_number, page in enumerate(pdf, start=1):

            page_data = {
                "type": "page",
                "page_number": page_number,
                "width": page.rect.width,
                "height": page.rect.height,
                "blocks": []
            }

            blocks = page.get_text("dict")["blocks"]

            for block in blocks:

                # Ignore non-text blocks for now
                if block.get("type") != 0:
                    continue

                block_data = {
                    "type": "text_block",
                    "bbox": block["bbox"],
                    "lines": []
                }

                for line in block.get("lines", []):

                    line_data = {
                        "type": "line",
                        "bbox": line["bbox"],
                        "spans": []
                    }

                    for span in line.get("spans", []):

                        text = span.get("text", "")

                        if not text.strip():
                            continue

                        span_data = {
                            "type": "text",
                            "text": text,
                            "bbox": span["bbox"],
                            "font": span.get("font"),
                            "size": span.get("size"),
                            "flags": span.get("flags")
                        }

                        line_data["spans"].append(span_data)

                    if line_data["spans"]:
                        block_data["lines"].append(line_data)

                if block_data["lines"]:
                    page_data["blocks"].append(block_data)

            document["document"]["pages"].append(page_data)
            # print(document)

    finally:
        pdf.close()

    return document


def debug_spans(document, page_number=1):
    """
    Display extracted spans of one PDF page
    together with their coordinates.
    """

    pages = document["document"]["pages"]

    page = next(
        (
            page
            for page in pages
            if page["page_number"] == page_number
        ),
        None
    )

    if page is None:
        print(f"Page {page_number} not found.")
        return

    print("=" * 100)
    print(f"PAGE {page_number}")
    print("=" * 100)

    for block_index, block in enumerate(page["blocks"]):

        print(f"\nBLOCK {block_index}")
        print(f"BLOCK BBOX: {block['bbox']}")

        for line_index, line in enumerate(block["lines"]):

            print(f"\n  LINE {line_index}")
            print(f"  LINE BBOX: {line['bbox']}")

            for span_index, span in enumerate(line["spans"]):

                x0, y0, x1, y1 = span["bbox"]

                print(
                    f"    SPAN {span_index} | "
                    f"x0={x0:.1f} | "
                    f"y0={y0:.1f} | "
                    f"x1={x1:.1f} | "
                    f"y1={y1:.1f} | "
                    f"size={span['size']:.1f} | "
                    f"text={span['text']!r}"
                )



def debug_blocks_and_lines(document):
    """
    Display PDF content at block/line level
    for all pages.
    """

    pages = document["document"]["pages"]

    for page in pages:

        page_number = page["page_number"]

        print("=" * 100)
        print(f"PAGE {page_number}")
        print("=" * 100)

        for block_index, block in enumerate(page["blocks"]):

            print(f"\nBLOCK {block_index}")
            print("-" * 80)

            for line_index, line in enumerate(block["lines"]):

                text = "".join(
                    span["text"]
                    for span in line["spans"]
                )

                print(
                    f"  LINE {line_index}: {text}"
                )


def debug_pdf_coordinates(report):
    pages = report["document"]["pages"]

    for page in pages[:1]:  # فعلاً فقط صفحه اول
        print("\n" + "=" * 80)
        print(f"PAGE {page['page_number']}")
        print("=" * 80)

        for block_index, block in enumerate(page["blocks"], start=1):

            print(f"\n--- BLOCK {block_index} ---")

            for line_index, line in enumerate(
                block["lines"],
                start=1
            ):

                print(f"\nLINE {line_index}")

                for span_index, span in enumerate(
                    line["spans"],
                    start=1
                ):

                    x0, y0, x1, y1 = span["bbox"]

                    print(
                        f"  SPAN {span_index}: "
                        f"x0={x0:.1f}, "
                        f"y0={y0:.1f}, "
                        f"x1={x1:.1f}, "
                        f"y1={y1:.1f} | "
                        f"size={span.get('size')} | "
                        f"text={span['text']!r}"
                    )


def debug_block_positions(report):
    page = report["document"]["pages"][0]

    blocks = []

    for index, block in enumerate(page["blocks"], start=1):

        if not block["lines"]:
            continue

        first_line = block["lines"][0]

        x0, y0, x1, y1 = first_line["bbox"]

        text = " ".join(
            span["text"]
            for line in block["lines"]
            for span in line["spans"]
        )

        blocks.append({
            "index": index,
            "x0": x0,
            "y0": y0,
            "x1": x1,
            "y1": y1,
            "text": text
        })

    blocks.sort(key=lambda block: block["y0"])

    print("\n" + "=" * 100)
    print("BLOCKS SORTED BY Y")
    print("=" * 100)

    for block in blocks:

        print(
            f"BLOCK {block['index']:02d} | "
            f"y={block['y0']:.1f}-{block['y1']:.1f} | "
            f"x={block['x0']:.1f}-{block['x1']:.1f} | "
            f"{block['text']}"
        )

def debug_line_order(report):
    page = report["document"]["pages"][0]

    block = page["blocks"][3]  # BLOCK 4
    line = block["lines"][1]   # LINE 2

    spans = line["spans"]

    print("\n" + "=" * 100)
    print("ORIGINAL SPAN ORDER")
    print("=" * 100)

    for span in spans:
        x0, y0, x1, y1 = span["bbox"]

        print(
            f"x0={x0:.1f} | "
            f"x1={x1:.1f} | "
            f"text={span['text']!r}"
        )

    print("\n" + "=" * 100)
    print("SORTED RIGHT → LEFT")
    print("=" * 100)

    sorted_spans = sorted(
        spans,
        key=lambda span: span["bbox"][0],
        reverse=True
    )

    for span in sorted_spans:
        x0, y0, x1, y1 = span["bbox"]

        print(
            f"x0={x0:.1f} | "
            f"x1={x1:.1f} | "
            f"text={span['text']!r}"
        )