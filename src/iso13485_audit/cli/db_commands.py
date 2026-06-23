"""Database management CLI commands."""

from __future__ import annotations

import typer
from rich.console import Console

from ..database import drop_db, init_db, session_scope
from ..seed_data import seed_all

app = typer.Typer(help="Database management commands.")
console = Console()


@app.command()
def init() -> None:
    """Create all database tables."""
    init_db()
    console.print("[green]Database initialised.[/green]")


@app.command()
def seed() -> None:
    """Load ISO 13485 clauses and default checklist templates."""
    init_db()
    with session_scope() as session:
        counts = seed_all(session)
    console.print(
        f"[green]Seeded[/green] {counts['clauses']} clauses and "
        f"{counts['templates']} templates."
    )


@app.command()
def reset(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
) -> None:
    """Drop all tables, recreate and re-seed."""
    if not yes:
        typer.confirm("This will DROP ALL DATA. Continue?", abort=True)
    drop_db()
    init_db()
    with session_scope() as session:
        counts = seed_all(session)
    console.print(
        f"[yellow]Database reset.[/yellow] Seeded {counts['clauses']} clauses, "
        f"{counts['templates']} templates."
    )
