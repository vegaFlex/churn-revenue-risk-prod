from __future__ import annotations

import html
from pathlib import Path


DOCS_DIR = Path("docs")

DOCS_REGISTRY = {
    "user-guide": {
        "title": "Revenue Risk and Customer Churn Intelligence Platform - User Guide",
        "subtitle": (
            "Browser-friendly product documentation for analysts, reviewers, and business users "
            "working with churn intelligence, role-based access, revenue exposure, monitoring workflows, "
            "and protected admin operations."
        ),
        "path": DOCS_DIR / "user_guide.md",
    },
    "manual-testing-guide": {
        "title": "Revenue Risk and Customer Churn Intelligence Platform - Manual Testing Guide",
        "subtitle": (
            "Step-by-step validation guide for browser pages, auth flows, upload mapping, admin actions, "
            "monitoring, and realtime API behaviour."
        ),
        "path": DOCS_DIR / "manual_testing_guide.md",
    },
    "buyer-guide": {
        "title": "Revenue Risk and Customer Churn Intelligence Platform - Buyer Guide",
        "subtitle": (
            "Buyer-facing overview of the product value, differentiators, and real-world use "
            "cases for churn, revenue-risk operations, and internal operational control workflows."
        ),
        "path": DOCS_DIR / "buyer_guide.md",
    },
    "upload-schema-guide": {
        "title": "Revenue Risk and Customer Churn Intelligence Platform - Upload Schema Guide",
        "subtitle": (
            "Validation rules, required fields, mapping behaviour, and practical guidance for "
            "uploading datasets into the churn scoring workflow."
        ),
        "path": DOCS_DIR / "upload_schema_guide.md",
    },
}

DOCS_NAV = [
    {"label": "User Guide", "href": "/docs/user-guide/"},
    {"label": "Manual Testing Guide", "href": "/docs/manual-testing-guide/"},
    {"label": "Buyer Guide", "href": "/docs/buyer-guide/"},
    {"label": "Upload Schema Guide", "href": "/docs/upload-schema-guide/"},
    {"label": "API Docs", "href": "/docs"},
    {"label": "Open App", "href": "/"},
]


def render_inline(text: str) -> str:
    escaped = html.escape(text)
    rendered: list[str] = []
    open_code = False
    buffer: list[str] = []

    for char in escaped:
        if char == "`":
            if open_code:
                rendered.append("<code>" + "".join(buffer) + "</code>")
                buffer = []
                open_code = False
            else:
                if buffer:
                    rendered.append("".join(buffer))
                    buffer = []
                open_code = True
        else:
            buffer.append(char)

    if buffer:
        rendered.append("".join(buffer))

    return "".join(rendered)


def render_markdown_like(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    parts: list[str] = []
    in_ul = False
    in_ol = False

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            parts.append("</ul>")
            in_ul = False
        if in_ol:
            parts.append("</ol>")
            in_ol = False

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            close_lists()
            continue

        if stripped.startswith("# "):
            close_lists()
            parts.append(f"<h2>{render_inline(stripped[2:])}</h2>")
        elif stripped.startswith("## "):
            close_lists()
            parts.append(f"<h2>{render_inline(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            close_lists()
            parts.append(f"<h3>{render_inline(stripped[4:])}</h3>")
        elif stripped.startswith("#### "):
            close_lists()
            parts.append(f"<h4>{render_inline(stripped[5:])}</h4>")
        elif stripped.startswith("- "):
            if not in_ul:
                close_lists()
                parts.append("<ul>")
                in_ul = True
            parts.append(f"<li>{render_inline(stripped[2:])}</li>")
        elif stripped[:2].isdigit() and stripped[1:3] == ". ":
            if not in_ol:
                close_lists()
                parts.append("<ol>")
                in_ol = True
            parts.append(f"<li>{render_inline(stripped[3:])}</li>")
        else:
            close_lists()
            parts.append(f"<p>{render_inline(stripped)}</p>")

    close_lists()
    return "".join(parts)


def build_docs_hub_context() -> dict:
    return {
        "page_title": "Documentation Center",
        "docs_title": "Revenue Risk and Customer Churn Intelligence Platform - Documentation Center",
        "docs_subtitle": (
            "Browser-friendly documentation for users, reviewers, and buyers, including product "
            "guides, auth-aware usage instructions, upload mapping guidance, admin operation notes, "
            "manual testing instructions, and buyer-facing positioning."
        ),
        "docs_nav": DOCS_NAV,
    }


def build_doc_page_context(slug: str) -> dict:
    doc_entry = DOCS_REGISTRY.get(slug)
    if doc_entry is None:
        raise FileNotFoundError(f"Unknown document slug: {slug}")

    doc_path = doc_entry["path"]
    if not doc_path.exists():
        raise FileNotFoundError(f"Documentation file not found: {doc_path}")

    markdown_text = doc_path.read_text(encoding="utf-8")
    return {
        "page_title": doc_entry["title"],
        "docs_title": doc_entry["title"],
        "docs_subtitle": doc_entry["subtitle"],
        "docs_nav": DOCS_NAV,
        "document_body": render_markdown_like(markdown_text),
    }
