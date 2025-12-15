import sys
from pathlib import Path

print(">>> starting FINANCE_PROJECT")

# make src/ importable
sys.path.append(str(Path(__file__).parent / "src"))

from finance.cli import app  # import CLI

if __name__ == "__main__":
    print(">>> running Typer app")
    app()
    print(">>> finished")
