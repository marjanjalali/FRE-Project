
from pathlib import Path

def save_pdf_as_text(data, output_path):

    text = pdf_json_to_text(data)

    # print("PDF TEXT LENGTH:", len(text))

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(text)

def pdf_json_to_text(data):
    lines = []

    pages = data.get("document", {}).get("pages", [])

    for page in pages:

        lines.append(f"===== PAGE {page['page_number']} =====")

        for block in page.get("blocks", []):

            for line in block.get("lines", []):

                # Sort spans from right to left
                spans = sorted(
                    line.get("spans", []),
                    key=lambda span: span["bbox"][0],
                    reverse=True
                )

                line_text = " ".join(
                    span["text"].strip()
                    for span in spans
                    if span.get("text", "").strip()
                )

                if line_text:
                    lines.append(line_text)

        lines.append("")

    return "\n".join(lines)


def json_to_text(data):
    lines = []

    def walk(node):

        if isinstance(node, dict):

            node_type = node.get("type")

            if node_type == "text":
                text = node.get("text")

                if text:
                    lines.append(text)

            elif node_type == "input":
                value = node.get("value")

                if value:
                    lines.append(value)

            for key, value in node.items():

                if key in {"text", "value"}:
                    continue

                walk(value)

        elif isinstance(node, list):

            for item in node:
                walk(item)

    walk(data)

    return "\n".join(lines)


def save_json_as_text(data, output_path):

    text = json_to_text(data)

    # print("TEXT LENGTH:", len(text))

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(text)