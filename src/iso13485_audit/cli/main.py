"""Top-level Typer application for the ISO 13485 audit system."""

from __future__ import annotations

import typer

from .. import __version__
from . import (
    audit_commands,
    clause_commands,
    db_commands,
    document_commands,
    ml_commands,
    report_commands,
)

app = typer.Typer(
    name="iso13485",
    help="ISO 13485:2016 audit management system with an AI/ML (SaMD) audit module.",
    no_args_is_help=True,
)

app.add_typer(db_commands.app, name="db")
app.add_typer(clause_commands.app, name="clause")
app.add_typer(audit_commands.app, name="audit")
app.add_typer(document_commands.app, name="document")
app.add_typer(ml_commands.app, name="ml-audit")
app.add_typer(report_commands.app, name="report")


@app.command()
def version() -> None:
    """Print the application version."""
    typer.echo(f"iso13485-audit {__version__}")


@app.command()
def serve(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
) -> None:
    """Start the FastAPI server."""
    import uvicorn

    uvicorn.run(
        "iso13485_audit.api.app:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


if __name__ == "__main__":
    app()
