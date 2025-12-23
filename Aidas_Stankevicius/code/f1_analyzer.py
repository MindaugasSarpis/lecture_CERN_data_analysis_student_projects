try:
    from .cli import main
except Exception:
    import sys
    import os

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from Aidas_Stankevicius.code.cli import main


if __name__ == "__main__":
    main()
