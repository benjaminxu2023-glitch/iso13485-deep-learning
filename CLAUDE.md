# CLAUDE.md

Developer guidance for working in this repository.

## What this is

An ISO 13485:2016 audit management system with an AI/ML (SaMD) audit module.
Python 3.10+, FastAPI + Typer over SQLAlchemy 2.0, SQLite by default.

## Layout

- `src/iso13485_audit/models/` — SQLAlchemy 2.0 ORM (`Mapped`/`mapped_column`).
  All models use `UUIDMixin` + `TimestampMixin` from `models/base.py`. UUIDs use
  the custom `GUID` type (CHAR(32)) for SQLite/Postgres portability.
- `src/iso13485_audit/schemas/` — Pydantic v2 request/response models.
- `src/iso13485_audit/services/` — business logic. **Take a `Session`; never
  import FastAPI/Typer.** Services commit nothing — callers (API/CLI) commit.
- `src/iso13485_audit/api/` — FastAPI routers (thin: parse → call service →
  commit → return). App factory in `api/app.py`.
- `src/iso13485_audit/cli/` — Typer commands, registered in `cli/main.py`.
- `src/iso13485_audit/nlp/` — TF-IDF gap detection (`engine.py`, `gap_detector.py`,
  `document_analyzer.py`).
- `src/iso13485_audit/ml_validation/` — SaMD classifier, bias metrics, model
  lifecycle, data integrity.
- `src/iso13485_audit/reports/` — Jinja2 HTML templates + generator.
- `src/iso13485_audit/seed_data/` — JSON reference data + `seed_all()` loader.

## Common commands

```bash
pip install -e '.[dev]'   # install with test deps
pytest                    # run all tests
ruff check src tests      # lint
iso13485 db seed          # create + seed the database
iso13485 serve            # run the API (http://127.0.0.1:8000/docs)
```

## Conventions

- Add a new entity by following the existing slice: model → schema → service →
  API router → CLI command → test. Register new routers in `api/v1/__init__.py`
  and new CLI groups in `cli/main.py`.
- Keep the NLP path deterministic and offline by default (TF-IDF). Heavy deps
  (`torch`, `weasyprint`, `pypdf`) are optional extras — guard their imports.
- The CAPA status state machine lives in `services/capa_service.ALLOWED_TRANSITIONS`;
  update it (and its tests) when changing the workflow.
- Tests use an in-memory SQLite DB via fixtures in `tests/conftest.py`
  (`seeded_session` for service tests, `client` for API tests).
