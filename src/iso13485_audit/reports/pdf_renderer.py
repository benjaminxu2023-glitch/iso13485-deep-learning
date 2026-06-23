"""Optional PDF rendering via WeasyPrint."""

from __future__ import annotations


def html_to_pdf(html: str, output_path: str) -> str:
    """Render an HTML string to a PDF file. Requires the optional [pdf] extra."""
    try:
        from weasyprint import HTML
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "PDF rendering requires the optional 'pdf' extra: "
            "pip install 'iso13485-audit[pdf]'"
        ) from exc
    HTML(string=html).write_pdf(output_path)
    return output_path
