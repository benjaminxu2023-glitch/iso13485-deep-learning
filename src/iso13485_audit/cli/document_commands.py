"""Document CLI commands."""

from __future__ import annotations

import uuid

import typer
from rich.console import Console
from rich.table import Table

from ..database import session_scope
from ..models.documents import DocumentType
from ..services import document_service
from ..services.document_service import DocumentServiceError

app = typer.Typer(help="Upload and analyze QMS documents.")
console = Console()


@app.command()
def upload(
    file_path: str,
    title: str = typer.Option(..., "--title", "-t"),
    doc_type: DocumentType = typer.Option(DocumentType.SOP, "--type"),
) -> None:
    """Register a document from a local file."""
    with session_scope() as session:
        try:
            document = document_service.create_document(
                session, title=title, file_path=file_path, document_type=doc_type
            )
            session.flush()
            did = document.id
        except DocumentServiceError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
    console.print(f"[green]Uploaded document[/green] {did} — {title}")


@app.command(name="list")
def list_documents() -> None:
    """List registered documents."""
    with session_scope() as session:
        docs = document_service.list_documents(session)
        table = Table("ID", "Title", "Type")
        for d in docs:
            table.add_row(str(d.id), d.title, d.document_type.value)
    console.print(table)


@app.command()
def analyze(document_id: str) -> None:
    """Run NLP compliance-gap analysis on a document."""
    with session_scope() as session:
        try:
            analysis = document_service.analyze_document(session, uuid.UUID(document_id))
            session.flush()
            console.print(f"[green]{analysis.summary}[/green]")
        except DocumentServiceError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc


@app.command()
def gaps(document_id: str, limit: int = typer.Option(20, "--limit")) -> None:
    """Show compliance gaps from the latest analysis."""
    with session_scope() as session:
        analysis = document_service.get_latest_analysis(session, uuid.UUID(document_id))
        if analysis is None:
            console.print("[yellow]No analysis found. Run 'analyze' first.[/yellow]")
            raise typer.Exit(1)
        table = Table("Clause", "Severity", "Confidence", "Recommendation")
        for gap in sorted(analysis.gaps, key=lambda g: g.confidence, reverse=True)[:limit]:
            table.add_row(
                gap.clause_number or "—",
                gap.severity,
                f"{gap.confidence:.2f}",
                (gap.recommendation or "")[:80],
            )
    console.print(table)
