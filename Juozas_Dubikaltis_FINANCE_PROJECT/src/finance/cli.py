import typer
from pathlib import Path
from .pipeline import run_monthly_report

app = typer.Typer(help="FINANCE_PROJECT CLI")

@app.command()
def report(
    month: str = typer.Option(..., help="Month in YYYY-MM, e.g., 2025-10"),
    csv: list[Path] = typer.Option(None, "--csv", help="One or more CSV files to read"),
    config_path: Path = typer.Option(Path("config.yaml"), help="Path to config.yaml"),
    presentation: bool = typer.Option(
        False, "--presentation/--no-presentation",
        help="Hide numeric values in report and charts (presentation mode)",
    ),
):
    print(">>> CLI reached successfully")
    print("Month:", month)
    print("CSV files:", csv)
    print("Config path:", config_path)
    print("Presentation mode:", presentation)

    run_monthly_report(month, csv, config_path, presentation=presentation)
    print(">>> Report generated successfully.")

if __name__ == "__main__":
    app()
