"""Report generation CLI commands."""

from __future__ import annotations

import uuid

import typer
from rich.console import Console

from ..database import session_scope
from ..reports.generator import ReportError
from ..schemas.reports import ReportFormat, ReportType
from ..services import report_service

app = typer.Typer(help="Generate audit, CAPA, gap-analysis and ML validation reports.")
console = Console()


@app.command()
def generate(
    report_type: ReportType = typer.Argument(..., help="audit|capa|gap_analysis|ml_validation"),
    target_id: str = typer.Argument(..., help="UUID of the audit/capa/document/model"),
    fmt: ReportFormat = typer.Option(ReportFormat.HTML, "--format", "-f"),
) -> None:
    """Generate a report and write it to the report output directory."""
    with session_scope() as session:
        try:
            result = report_service.generate_report(
                session, report_type, uuid.UUID(target_id), fmt
            )
        except ReportError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        except ImportError as exc:
            console.print(f"[yellow]{exc}[/yellow]")
            raise typer.Exit(1) from exc
    console.print(f"[green]Report written:[/green] {result.file_path}")
