"""Clause CLI commands."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.tree import Tree

from ..database import session_scope
from ..services import clause_service

app = typer.Typer(help="Browse ISO 13485 clauses.")
console = Console()


@app.command(name="list")
def list_clauses() -> None:
    """Show the full clause hierarchy as a tree."""
    with session_scope() as session:
        clauses = clause_service.list_clauses(session)
        nodes: dict = {}
        root = Tree("[bold]ISO 13485:2016[/bold]")
        # Build in clause-number order so parents are added before their children.
        for clause in sorted(clauses, key=lambda c: _key(c.clause_number)):
            label = f"[cyan]{clause.clause_number}[/cyan] {clause.title}"
            parent_node = nodes.get(clause.parent_id, root)
            nodes[clause.id] = parent_node.add(label)
    console.print(root)


@app.command()
def show(clause_number: str) -> None:
    """Show a clause and its requirements."""
    with session_scope() as session:
        clause = clause_service.get_clause_by_number(session, clause_number)
        if clause is None:
            console.print(f"[red]Clause {clause_number} not found.[/red]")
            raise typer.Exit(1)
        console.print(f"[bold cyan]{clause.clause_number}[/bold cyan] {clause.title}")
        if clause.fda_820_reference:
            console.print(f"  FDA 21 CFR: [magenta]{clause.fda_820_reference}[/magenta]")
        if clause.description:
            console.print(f"  {clause.description}")
        if clause.requirements:
            console.print("\n[bold]Requirements:[/bold]")
            for req in clause.requirements:
                console.print(f"  • (risk {req.risk_weight}) {req.requirement_text}")
        if clause.children:
            console.print("\n[bold]Sub-clauses:[/bold]")
            for child in sorted(clause.children, key=lambda c: _key(c.clause_number)):
                console.print(f"  {child.clause_number} {child.title}")


@app.command()
def search(query: str) -> None:
    """Search clauses by text."""
    with session_scope() as session:
        results = clause_service.search_clauses(session, query)
        if not results:
            console.print("[yellow]No matching clauses.[/yellow]")
            return
        for clause in results:
            console.print(f"[cyan]{clause.clause_number}[/cyan] {clause.title}")


def _key(clause_number: str) -> tuple[int, ...]:
    return tuple(int(p) for p in clause_number.split(".") if p.isdigit())
