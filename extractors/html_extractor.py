
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag
import re

# =========================================================
# Configuration
# =========================================================

IGNORED_TAGS = {
    "script",
    "style",
    "noscript",
    "template",
    "link",
}

IGNORED_INPUT_TYPES = {
    "hidden",
    "button",
    "submit",
    "reset",
    "checkbox",
    "radio",
}

# =========================================================
# Text helpers
# =========================================================

def clean_text(text: str) -> str:
    """
    Normalize whitespace without destroying meaningful text.
    """

    text = text.replace("\xa0", " ")

    # Normalize spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces at the beginning of lines
    text = re.sub(r"\n[ \t]+", "\n", text)

    # Avoid excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# =========================================================
# Attribute handling
# =========================================================

def extract_attributes(element: Tag) -> dict:
    """
    Preserve all HTML attributes.
    """

    attributes = {}

    for key, value in element.attrs.items():

        if isinstance(value, list):
            attributes[key] = value
        else:
            attributes[key] = value

    return attributes


# =========================================================
# Hidden element detection
# =========================================================

def is_hidden_element(element: Tag) -> bool:
    """
    Detect elements that are explicitly hidden using
    standard HTML/CSS mechanisms.
    """

    if not isinstance(element, Tag):
        return False

    # HTML hidden attribute
    if element.has_attr("hidden"):
        return True

    # Inline CSS
    style = element.get("style", "").lower()

    if re.search(r"display\s*:\s*none", style):
        return True

    if re.search(r"visibility\s*:\s*hidden", style):
        return True

    return False


# =========================================================
# UI / technical element detection
# =========================================================

def is_ui_element(element: Tag) -> bool:
    """
    Detect elements that are clearly technical page
    infrastructure or UI controls rather than document content.

    No Codal-specific IDs or class names are used.
    """

    if not isinstance(element, Tag):
        return False

    tag = element.name.lower()

    # Technical HTML elements
    if tag in IGNORED_TAGS:
        return True

    # Explicitly hidden elements
    if is_hidden_element(element):
        return True

    # SELECT elements with onchange are usually
    # page/navigation controls.
    if tag == "select" and element.get("onchange"):
        return True

    return False


# =========================================================
# Text node
# =========================================================

def extract_text_node(node: NavigableString):
    """
    Convert a text node into JSON.
    """

    text = clean_text(str(node))

    if not text:
        return None

    return {
        "type": "text",
        "text": text
    }


# =========================================================
# Generic element
# =========================================================

def extract_element(element: Tag):
    """
    Recursively convert an HTML element into JSON.

    No semantic interpretation is performed.
    """

    if not isinstance(element, Tag):
        return None

    tag = element.name.lower()

    # -----------------------------------------------------
    # DIV
    # -----------------------------------------------------

    if tag == "div":
        return extract_children(element)

    # -----------------------------------------------------
    #SPAN
    # -----------------------------------------------------

    if tag == "span":
        return extract_children(element)

    # -----------------------------------------------------
    # FORM
    # -----------------------------------------------------

    if tag == "form":
        return extract_children(element)

    # -----------------------------------------------------
    # Ignore technical/UI elements
    # -----------------------------------------------------

    if is_ui_element(element):
        return None

    # -----------------------------------------------------
    # BR
    # -----------------------------------------------------

    if tag == "br":
        return {
            "type": "br"
        }

    # -----------------------------------------------------
    # INPUT
    # -----------------------------------------------------

    if tag == "input":

        input_type = element.get(
            "type",
            ""
        ).lower()

        if input_type in IGNORED_INPUT_TYPES:
            return None

        result = {
            "type": "input"
        }

        attributes = extract_attributes(element)

        if attributes:
            result["attributes"] = attributes

        value = element.get("value")

        if value is not None:

            value = clean_text(str(value))

            if value:
                result["value"] = value

        return result

    # -----------------------------------------------------
    # TEXTAREA
    # -----------------------------------------------------

    if tag == "textarea":

        result = {
            "type": "textarea"
        }

        attributes = extract_attributes(element)

        if attributes:
            result["attributes"] = attributes

        text = clean_text(
            element.get_text()
        )

        if text:
            result["text"] = text

        return result

    # -----------------------------------------------------
    # SELECT
    # -----------------------------------------------------

    if tag == "select":

        result = {
            "type": "select"
        }

        attributes = extract_attributes(element)

        if attributes:
            result["attributes"] = attributes

        children = extract_children(element)

        if children:
            result["children"] = children

        return result

    # -----------------------------------------------------
    # TABLE
    # -----------------------------------------------------

    if tag == "table":
        return extract_table(element)

    # -----------------------------------------------------
    # TR
    # -----------------------------------------------------

    if tag == "tr":

        result = {
            "type": "row"
        }

        attributes = extract_attributes(element)

        if attributes:
            result["attributes"] = attributes

        children = extract_children(element)

        if children:
            result["children"] = children

        return result

    # -----------------------------------------------------
    # TD / TH
    # -----------------------------------------------------

    if tag in {"td", "th"}:

        result = {
            "type": (
                "header_cell"
                if tag == "th"
                else "cell"
            )
        }

        attributes = extract_attributes(element)

        if attributes:
            result["attributes"] = attributes

        children = extract_children(element)

        if children:
            result["children"] = children

        return result

    # -----------------------------------------------------
    # Generic HTML element
    # -----------------------------------------------------

    result = {
        "type": tag
    }

    attributes = extract_attributes(element)

    if attributes:
        result["attributes"] = attributes

    children = extract_children(element)

    if children:
        result["children"] = children

    return result


# =========================================================
# Children
# =========================================================

def extract_children(element: Tag):
    """
    Extract children in exact document order.
    """

    children = []

    for child in element.children:

        # -------------------------------------------------
        # Text node
        # -------------------------------------------------

        if isinstance(child, NavigableString):

            extracted = extract_text_node(child)

            if extracted is not None:
                children.append(extracted)

            continue

        # -------------------------------------------------
        # HTML element
        # -------------------------------------------------

        if isinstance(child, Tag):

            extracted = extract_element(child)

            if extracted is not None:
                children.append(extracted)

    return children


# =========================================================
# Table
# =========================================================

def extract_table(table: Tag):
    """
    Extract a table while preserving nested tables.

    Nested tables are processed only when encountered
    naturally inside their parent cells.

    This prevents duplicate extraction of nested tables.
    """

    result = {
        "type": "table"
    }

    attributes = extract_attributes(table)

    if attributes:
        result["attributes"] = attributes

    children = []

    for child in table.children:

        # -------------------------------------------------
        # Text node
        # -------------------------------------------------

        if isinstance(child, NavigableString):

            extracted = extract_text_node(child)

            if extracted is not None:
                children.append(extracted)

            continue

        if not isinstance(child, Tag):
            continue

        tag = child.name.lower()

        # -------------------------------------------------
        # THEAD / TBODY / TFOOT
        # -------------------------------------------------

        if tag in {"thead", "tbody", "tfoot"}:

            group = {
                "type": tag
            }

            group_attributes = extract_attributes(child)

            if group_attributes:
                group["attributes"] = group_attributes

            group_children = extract_children(child)

            if group_children:
                group["children"] = group_children

            children.append(group)

        # -------------------------------------------------
        # Direct row
        # -------------------------------------------------

        elif tag == "tr":

            row = extract_element(child)

            if row is not None:
                children.append(row)

        # -------------------------------------------------
        # Other table-level elements
        # -------------------------------------------------

        else:

            extracted = extract_element(child)

            if extracted is not None:
                children.append(extracted)

    if children:
        result["children"] = children

    return result


# =========================================================
# Root detection
# =========================================================

def find_report_root(soup: BeautifulSoup):
    """
    Use the document body as the extraction root.

    Root detection should not rely on heuristic scoring.
    Technical elements are filtered during recursive extraction.
    """

    return soup.body or soup


# =========================================================
# Main extractor
# =========================================================

def extract_html(file_path: Path):
    """
    Structural HTML -> JSON parser.

    No semantic interpretation is performed.
    """

    # -----------------------------------------------------
    # Read HTML
    # -----------------------------------------------------

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        html_content = file.read()

    # -----------------------------------------------------
    # Parse HTML
    # -----------------------------------------------------

    soup = BeautifulSoup(
        html_content,
        "html.parser"
    )

    # -----------------------------------------------------
    # Find report root
    # -----------------------------------------------------

    root = find_report_root(soup)

    # -----------------------------------------------------
    # Document title
    # -----------------------------------------------------

    title = ""

    title_tag = soup.find("title")

    if title_tag:

        title = clean_text(
            title_tag.get_text()
        )

    # Prefer visible H1
    h1 = soup.find("h1")

    if h1:

        h1_text = clean_text(
            h1.get_text()
        )

        if h1_text:
            title = h1_text

    # -----------------------------------------------------
    # Structural extraction
    # -----------------------------------------------------

    children = extract_children(root)

    # -----------------------------------------------------
    # Final JSON object
    # -----------------------------------------------------

    document = {
        "document": {
            "title": title,
            "type": "html_document",
            "children": children
        }
    }

    return document