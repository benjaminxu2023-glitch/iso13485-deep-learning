"""Text extraction, section splitting and chunking utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Section:
    """A heading-delimited section of a document."""

    heading: str
    body: str

    @property
    def text(self) -> str:
        return f"{self.heading}\n{self.body}".strip()


def extract_text(file_path: str | Path) -> str:
    """Extract plain text from a TXT, Markdown, PDF or DOCX file.

    PDF/DOCX support requires the optional ``[docs]`` extra; if the relevant
    library is missing a clear ImportError is raised. Plain text always works.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in {".txt", ".md", ".csv", ""}:
        return path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "Reading PDF files requires the optional 'docs' extra: "
                "pip install 'iso13485-audit[docs]'"
            ) from exc
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if suffix in {".docx", ".doc"}:
        try:
            import docx
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "Reading DOCX files requires the optional 'docs' extra: "
                "pip install 'iso13485-audit[docs]'"
            ) from exc
        document = docx.Document(str(path))
        return "\n".join(p.text for p in document.paragraphs)

    # Fallback: best-effort plain-text read.
    return path.read_text(encoding="utf-8", errors="ignore")


_HEADING_RE = re.compile(
    r"^\s*(?:(?:\d+(?:\.\d+)*\.?)|#{1,6}|[A-Z][A-Z \-]{3,})\s*.*$"
)


def split_sections(text: str) -> list[Section]:
    """Split text into sections on numbered or capitalised headings.

    Falls back to a single section when no headings are detected.
    """
    lines = text.splitlines()
    sections: list[Section] = []
    current_heading = "Document"
    current_body: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped and _is_heading(stripped):
            if current_body or sections:
                sections.append(
                    Section(heading=current_heading, body="\n".join(current_body).strip())
                )
            current_heading = stripped
            current_body = []
        else:
            current_body.append(line)

    sections.append(Section(heading=current_heading, body="\n".join(current_body).strip()))
    # Drop empty sections.
    return [s for s in sections if s.text]


def _is_heading(line: str) -> bool:
    if len(line) > 120:
        return False
    if line.startswith("#"):
        return True
    # Numbered heading like "4.2 Documentation Requirements"
    if re.match(r"^\d+(?:\.\d+)*\.?\s+\S", line):
        return True
    # Short all-caps title
    letters = [c for c in line if c.isalpha()]
    if letters and len(line) < 80 and line.upper() == line and len(letters) >= 4:
        return True
    return False


def chunk_text(text: str, max_chars: int = 1000, overlap: int = 100) -> list[str]:
    """Split text into overlapping character chunks for embedding."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    start = 0
    step = max(1, max_chars - overlap)
    while start < len(text):
        chunks.append(text[start : start + max_chars])
        start += step
    return chunks
