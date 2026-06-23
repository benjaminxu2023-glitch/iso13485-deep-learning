# ISO 13485 Audit System

A working **ISO 13485:2016 audit management system** with a built-in module for
**auditing AI/ML-based medical device software** (Software as a Medical Device,
SaMD), aligned with FDA's AI/ML Action Plan, Good Machine Learning Practice
(GMLP) principles, and the IMDRF SaMD risk-categorization framework.

It combines a traditional Quality Management System (QMS) audit toolset —
clause modeling, audit checklists, findings and CAPA tracking, NLP-based
document gap detection, and report generation — with specialized AI/ML auditing
(SaMD risk classification, fairness/bias metrics, dataset integrity, and model
lifecycle stage-gates).

> ⚕️ This is a software tool to *assist* qualified auditors. Its generated work
> products must be reviewed by competent personnel; it is not a substitute for a
> certified QMS or regulatory submission.

## Features

- **ISO 13485:2016 clause engine** — the full normative hierarchy for clauses
  4–8 (85 clauses, 90+ "shall" requirements) seeded from JSON, each
  cross-referenced to the corresponding **FDA 21 CFR Part 820** section.
- **Audit & checklist engine** — create audits, auto-generate checklists from
  templates or arbitrary clauses, assess conformity, and compute summary stats.
- **Findings & CAPA** — finding tracking with an **enforced CAPA state machine**
  (initiated → root-cause → planned → in-progress → verification → effectiveness
  → closed) and auto-numbering (`CAPA-YYYY-NNN`).
- **NLP compliance gap detection** — analyzes uploaded QMS documents against the
  ISO requirement set using a deterministic, offline **TF-IDF** similarity engine
  (an optional transformer backend is available).
- **AI/ML (SaMD) audit module**
  - IMDRF SaMD risk classification (Categories I–IV)
  - Group-fairness/bias metrics (demographic parity, equalized odds, predictive
    parity)
  - Dataset integrity scoring (completeness, lineage) and PSI drift
  - GMLP model-lifecycle stage-gate readiness
- **Reports** — HTML reports for audits, CAPAs, gap analyses and ML validation
  (optional PDF export).
- **Two interfaces** — a REST API (FastAPI, OpenAPI docs at `/docs`) and a
  `iso13485` CLI.

## Installation

```bash
pip install -e .

# Optional extras:
pip install -e '.[docs]'   # PDF/DOCX document parsing
pip install -e '.[pdf]'    # PDF report rendering (WeasyPrint)
pip install -e '.[nlp]'    # transformer embeddings (torch + sentence-transformers)
pip install -e '.[dev]'    # pytest, ruff
```

Requires Python 3.10+. The core install is fully self-contained and runs
offline — no model downloads or network access required.

## Quickstart (CLI)

```bash
# 1. Initialise and seed the database (ISO clauses + checklist templates)
iso13485 db seed

# 2. Browse the standard
iso13485 clause list
iso13485 clause show 7.3

# 3. Run an audit
iso13485 audit create --title "Q2 Internal Audit" --type internal
iso13485 audit generate-checklist <AUDIT_ID> --clauses 7.3,7.5
iso13485 audit show <AUDIT_ID>
iso13485 audit close <AUDIT_ID>

# 4. Analyze a QMS document for compliance gaps
iso13485 document upload ./my_sop.txt --title "Design Control SOP" --type sop
iso13485 document analyze <DOC_ID>
iso13485 document gaps <DOC_ID>

# 5. Audit an AI/ML device
iso13485 ml-audit register --name "Lesion Classifier" --framework pytorch
iso13485 ml-audit classify-samd --significance treat_diagnose --situation critical
iso13485 ml-audit bias-check <MODEL_ID> --predictions preds.csv \
    --labels labels.csv --protected demographics.csv
iso13485 ml-audit lifecycle <MODEL_ID>

# 6. Generate a report
iso13485 report generate audit <AUDIT_ID> --format html
```

## Quickstart (API)

```bash
iso13485 db seed
iso13485 serve --port 8000        # then open http://127.0.0.1:8000/docs
```

```bash
curl -X POST localhost:8000/api/v1/ml-audit/samd-classify \
  -H 'content-type: application/json' \
  -d '{"significance":"drive","healthcare_situation":"serious"}'
# => {"risk_category":"II", ...}
```

## Architecture

A clean three-layer design keeps business logic testable and transport-agnostic:

```
 CLI (Typer)  ┐
              ├─►  services/   ─►  models/ (SQLAlchemy ORM)  ─►  SQLite / Postgres
 API (FastAPI)┘        │
                       ├─►  nlp/            (TF-IDF gap detection)
                       └─►  ml_validation/  (SaMD, bias, lifecycle, data integrity)
                              │
                            reports/  (Jinja2 HTML, optional WeasyPrint PDF)
```

- `services/` contain all business logic, take a SQLAlchemy `Session`, and never
  import FastAPI or Typer.
- `seed_data/` holds the ISO 13485 clause hierarchy, FDA 820 mapping, checklist
  templates and the IMDRF SaMD matrix as JSON.
- The NLP gap detector defaults to TF-IDF for deterministic, auditable,
  network-free behavior.

| Area | Path |
|------|------|
| Models | `src/iso13485_audit/models/` |
| Services | `src/iso13485_audit/services/` |
| NLP | `src/iso13485_audit/nlp/` |
| AI/ML audit | `src/iso13485_audit/ml_validation/` |
| API | `src/iso13485_audit/api/` |
| CLI | `src/iso13485_audit/cli/` |
| Reference data | `src/iso13485_audit/seed_data/` |

## Configuration

All settings have defaults and can be overridden via environment variables
(prefix `ISO13485_`) or a `.env` file (see `.env.example`). Key options:
`ISO13485_DATABASE_URL`, `ISO13485_NLP_BACKEND` (`tfidf` | `transformer`),
`ISO13485_GAP_SIMILARITY_THRESHOLD`.

## Testing

```bash
pytest          # 49 unit + integration + e2e tests
```

## Roadmap / not in the MVP

- Alembic migrations (the MVP creates tables via `create_all`)
- Authentication/authorization enforcement (user roles are recorded only)
- Native JSONB columns and full-text search on PostgreSQL
- Fine-tuned domain NLP models

## Disclaimer

This project is an engineering tool and educational reference. It does not
constitute regulatory advice and does not by itself establish ISO 13485
certification or FDA compliance.
