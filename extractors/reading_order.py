

def get_line_text(line):
    return "".join(
        span["text"]
        for span in line.get("spans", [])
    ).strip()


def get_block_text(block):
    return " ".join(
        get_line_text(line)
        for line in block.get("lines", [])
        if get_line_text(line)
    )


def build_reading_order(report):
    """
    Build a reading-order representation from the raw PDF structure.

    The raw extracted report is not modified.
    """

    ordered_report = {
        "document": {
            "title": report["document"]["title"],
            "type": report["document"]["type"],
            "pages": []
        }
    }

    for page in report["document"]["pages"]:

        blocks = []

        for block in page.get("blocks", []):

            if not block.get("lines"):
                continue

            x0, y0, x1, y1 = block["bbox"]

            blocks.append({
                "type": "text_block",
                "bbox": block["bbox"],
                "text": get_block_text(block),
                "original_block": block
            })

        # First approximation:
        # top → bottom
        blocks.sort(
            key=lambda block: (
                block["bbox"][1],
                block["bbox"][0]
            )
        )

        ordered_report["document"]["pages"].append({
            "type": "page",
            "page_number": page["page_number"],
            "width": page["width"],
            "height": page["height"],
            "blocks": blocks
        })

    return ordered_report