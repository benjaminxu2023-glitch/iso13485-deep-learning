"""AI/ML (SaMD) audit CLI commands."""

from __future__ import annotations

import csv
import uuid

import typer
from rich.console import Console
from rich.table import Table

from ..database import session_scope
from ..schemas.ml_audit import BiasCheckRequest, DatasetCreate, MLModelCreate, ValidationCreate
from ..services import ml_audit_service
from ..services.ml_audit_service import MLAuditServiceError

app = typer.Typer(help="Audit AI/ML-based medical device software (SaMD).")
console = Console()


@app.command()
def register(
    name: str = typer.Option(..., "--name", "-n"),
    model_type: str = typer.Option("classification", "--type"),
    framework: str | None = typer.Option(None, "--framework"),
    algorithm: str | None = typer.Option(None, "--algorithm"),
    intended_use: str | None = typer.Option(None, "--intended-use"),
) -> None:
    """Register an ML model for audit."""
    with session_scope() as session:
        model = ml_audit_service.register_model(
            session,
            MLModelCreate(
                name=name,
                model_type=model_type,
                framework=framework,
                algorithm=algorithm,
                intended_use=intended_use,
            ),
        )
        session.flush()
        console.print(f"[green]Registered model[/green] {model.id} — {name}")


@app.command(name="list")
def list_models() -> None:
    """List registered ML models."""
    with session_scope() as session:
        models = ml_audit_service.list_models(session)
        table = Table("ID", "Name", "Version", "Stage", "SaMD")
        for m in models:
            table.add_row(
                str(m.id), m.name, m.version, m.lifecycle_stage.value,
                m.samd_risk_category.value if m.samd_risk_category else "—",
            )
    console.print(table)


@app.command(name="add-dataset")
def add_dataset(
    model_id: str,
    name: str = typer.Option(..., "--name"),
    purpose: str = typer.Option("training", "--purpose"),
    size: int | None = typer.Option(None, "--size"),
) -> None:
    """Register a dataset for a model and score its integrity."""
    with session_scope() as session:
        try:
            ds = ml_audit_service.add_dataset(
                session, uuid.UUID(model_id),
                DatasetCreate(name=name, purpose=purpose, size=size),
            )
            session.flush()
            score = ds.data_quality_score
        except MLAuditServiceError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
    console.print(f"[green]Dataset added.[/green] Data quality score: {score:.2f}")


@app.command()
def validate(
    model_id: str,
    validation_type: str = typer.Option("analytical", "--type"),
    passed: bool = typer.Option(True, "--passed/--failed"),
    summary: str | None = typer.Option(None, "--summary"),
) -> None:
    """Record a validation result for a model."""
    with session_scope() as session:
        try:
            ml_audit_service.record_validation(
                session, uuid.UUID(model_id),
                ValidationCreate(
                    validation_type=validation_type, pass_fail=passed, results_summary=summary
                ),
            )
        except MLAuditServiceError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
    console.print("[green]Validation recorded.[/green]")


@app.command(name="classify-samd")
def classify_samd(
    significance: str = typer.Option(..., "--significance", help="treat_diagnose|drive|inform"),
    situation: str = typer.Option(..., "--situation", help="critical|serious|non_serious"),
) -> None:
    """Classify SaMD risk category per the IMDRF framework."""
    with session_scope() as session:
        try:
            result = ml_audit_service.classify_samd(session, significance, situation)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
    console.print(
        f"[bold]SaMD Risk Category: [cyan]{result.risk_category.value}[/cyan][/bold] "
        f"({result.level})"
    )
    console.print(f"  {result.description}")
    console.print("  Requirements:")
    for req in result.requirements:
        console.print(f"    • {req}")


@app.command(name="bias-check")
def bias_check(
    model_id: str,
    predictions: str = typer.Option(..., "--predictions", help="CSV: one prediction (0/1) per row"),
    protected: str = typer.Option(..., "--protected", help="CSV: attr columns, one row per sample"),
    labels: str | None = typer.Option(None, "--labels", help="CSV: one true label (0/1) per row"),
) -> None:
    """Run an automated fairness/bias audit from CSV inputs."""
    preds = _read_numeric_column(predictions)
    label_vals = _read_numeric_column(labels) if labels else None
    protected_attrs = _read_protected(protected)

    with session_scope() as session:
        try:
            result = ml_audit_service.run_bias_check(
                session, uuid.UUID(model_id),
                BiasCheckRequest(
                    predictions=preds, labels=label_vals, protected_attributes=protected_attrs
                ),
            )
        except MLAuditServiceError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        table = Table("Attribute", "Metric", "Disparity", "Pass")
        for r in result.results:
            table.add_row(
                r.protected_attribute, r.metric_name, f"{r.metric_value:.3f}",
                "✓" if r.passes_threshold else "✗",
            )
    console.print(table)
    verdict = "[green]PASSED[/green]" if result.overall_passed else "[red]FAILED[/red]"
    console.print(f"Overall: {verdict}")


@app.command()
def lifecycle(model_id: str) -> None:
    """Show lifecycle stage and required-artifact readiness."""
    with session_scope() as session:
        try:
            status = ml_audit_service.get_lifecycle_status(session, uuid.UUID(model_id))
        except MLAuditServiceError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
    console.print(f"[bold]Current stage:[/bold] {status.current_stage.value}")
    if status.next_stage:
        console.print(f"[bold]Next stage:[/bold] {status.next_stage}")
    console.print("[bold]Readiness notes:[/bold]")
    for note in status.readiness_notes:
        console.print(f"  • {note}")


def _read_numeric_column(path: str) -> list[float]:
    values: list[float] = []
    with open(path, newline="") as fh:
        for row in csv.reader(fh):
            if row and row[0].strip():
                try:
                    values.append(float(row[0]))
                except ValueError:
                    continue  # skip header
    return values


def _read_protected(path: str) -> dict[str, list[str]]:
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        columns: dict[str, list[str]] = {name: [] for name in (reader.fieldnames or [])}
        for row in reader:
            for name in columns:
                columns[name].append(row[name])
    return columns
