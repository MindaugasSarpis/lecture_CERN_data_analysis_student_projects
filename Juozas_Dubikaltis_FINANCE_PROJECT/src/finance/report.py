from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re

from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound


def _get_env() -> Environment:
    this_file = Path(__file__).resolve()
    finance_dir = this_file.parent
    project_root = this_file.parents[2]
    template_dirs = [finance_dir / "templates", project_root / "templates"]
    return Environment(
        loader=FileSystemLoader([str(p) for p in template_dirs]),
        autoescape=select_autoescape(["html", "xml"]),
    )


def _load_template(env: Environment):
    for name in ("report.html.j2", "report.html"):
        try:
            return env.get_template(name)
        except TemplateNotFound:
            continue
    raise FileNotFoundError("Neither 'report.html.j2' nor 'report.html' found in templates.")


def _mask_numeric_strings(html: str) -> str:
    """Mask most numbers and money-like strings to X while preserving layout."""
    def repl(m: re.Match) -> str:
        s = m.group(0)
        return "".join("X" if ch.isdigit() else ch for ch in s)

    patterns = [
        r"(?:€\s*|\bEUR\s*)\d[\d,]*[.]\d{1,2}",
        r"\d[\d,]*[.]\d{1,2}\s*(?:€|\bEUR\b)",
        r"(?:€\s*|\bEUR\s*)\d[\d,]*\b",
        r"\b\d[\d,]*\s*(?:€|\bEUR\b)",
        r"\b\d[\d,]*[.]?\d*\s*%",  # percentages
    ]
    for pat in patterns:
        html = re.sub(pat, repl, html)
    return html


def render_report(
    *,
    month: str,
    kpis: dict,
    charts: dict,
    top_merchants: list[dict],
    income_sources: list[dict],
    source_summary: str,
    out_html: Path,
    out_pdf: Path,
    cat_summary: list[dict],
    inc_summary: list[dict],
    misc_rows: list[dict],
    cat_details: list[dict] | None = None,
    presentation: bool = False,   # NEW
) -> None:
    env = _get_env()
    template = _load_template(env)

    html_str = template.render(
        month=month,
        kpis=kpis,
        charts=charts,
        top_merchants=top_merchants,
        income_sources=income_sources,
        source_summary=source_summary,
        cat_summary=cat_summary,
        inc_summary=inc_summary,
        misc_rows=misc_rows,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        presentation=presentation,
    )

    if presentation:
        html_str = _mask_numeric_strings(html_str)

    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html_str, encoding="utf-8")

    try:
        from weasyprint import HTML  # type: ignore
    except Exception:
        return
    try:
        project_root = Path(__file__).resolve().parents[2]
        HTML(string=html_str, base_url=str(project_root)).write_pdf(str(out_pdf))
    except Exception:
        pass
