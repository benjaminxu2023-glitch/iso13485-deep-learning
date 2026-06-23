"""Audit CLI commands."""

from __future__ import annotations

import uuid

import typer
from rich.console import Console
from rich.table import Table

from ..database import session_scope
from ..models.audits import AuditType
from ..schemas.audits import AuditCreate
from ..services import audit_service
from ..services.audit_service import AuditServiceError

app = typer.Typer(help="Manage audits and checklists.")
console = Console()


@app.command()
def create(
    title: str = typer.Option(..., "--title", "-t"),
    audit_type: AuditType = typer.Option(AuditType.INTERNAL, "--type"),
    scope: str | None = typer.Option(None, "--scope"),
) -> None:
    """Create a new audit."""
    with session_scope() as session:
        audit = audit_service.create_audit(
            session, AuditCreate(title=title, audit_type=audit_type, scope_description=scope)
        )
        session.flush()
        console.print(f"[green]Created audit[/green] {audit.id} — {audit.title}")


@app.command(name="list")
def list_audits() -> None:
    """List all audits."""
    with session_scope() as session:
        audits = audit_service.list_audits(session)
        table = Table("ID", "Title", "Type", "Status")
        for a in audits:
            table.add_row(str(a.id), a.title, a.audit_type.value, a.status.value)
    console.print(table)


@app.command()
def show(audit_id: str) -> None:
    """Show an audit and its conformity summary."""
    with session_scope() as session:
        aid = uuid.UUID(audit_id)
        audit = audit_service.get_audit(session, aid)
        if audit is None:
            console.print("[red]Audit not found.[/red]")
            raise typer.Exit(1)
        summary = audit_service.compute_audit_summary(session, aid)
        console.print(
            f"[bold]{audit.title}[/bold] "
            f"({audit.audit_type.value}) — {audit.status.value}"
        )
        console.print(
            f"  Items: {summary.total_items} | Conforming: {summary.conforming} | "
            f"Nonconforming: {summary.nonconforming} | Observations: {summary.observations}"
        )
        console.print(
            f"  Conformity rate: {summary.conformity_rate:.0%} | "
            f"Findings: {summary.findings_count}"
        )


@app.command(name="generate-checklist")
def generate_checklist(
    audit_id: str,
    clauses: str | None = typer.Option(None, "--clauses", help="Comma-separated, e.g. 7.3,7.5"),
    template: str | None = typer.Option(None, "--template", help="Template name"),
) -> None:
    """Generate a checklist for an audit from clauses or a template."""
    clause_list = [c.strip() for c in clauses.split(",")] if clauses else None
    with session_scope() as session:
        try:
            checklist = audit_service.generate_checklist(
                session,
                uuid.UUID(audit_id),
                template_name=template,
                clause_numbers=clause_list,
            )
            session.flush()
            n_items = len(checklist.items)
            cid = checklist.id
        except AuditServiceError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
    console.print(f"[green]Generated checklist[/green] {cid} with {n_items} items.")


@app.command()
def close(audit_id: str) -> None:
    """Close an audit."""
    with session_scope() as session:
        try:
            audit = audit_service.close_audit(session, uuid.UUID(audit_id))
            status = audit.status.value
        except AuditServiceError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
    console.print(f"[green]Audit closed.[/green] Status: {status}")
