"""Jinja2 HTML rendering for reports."""

from __future__ import annotations

from importlib import resources

from jinja2 import Environment, FileSystemLoader, select_autoescape

_TEMPLATE_DIR = resources.files("iso13485_audit.reports").joinpath("templates")


def _build_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )


_env: Environment | None = None


def render(template_name: str, context: dict) -> str:
    global _env
    if _env is None:
        _env = _build_env()
    template = _env.get_template(template_name)
    return template.render(**context)
