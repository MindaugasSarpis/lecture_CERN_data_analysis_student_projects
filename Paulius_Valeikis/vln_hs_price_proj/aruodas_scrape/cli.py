import argparse
from .pipeline_db import run_pipeline
from .export import export_all, export_latest

#CLI irankis visko naudojomuisi //leidzia paliesti scraperi, gauti visus sukauptus rezultatus, gauti paskutinio run rezultatus

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=["run", "export"],
        help="run scraper or export data"
    )
    #jei nori tik nauajausu
    parser.add_argument(
        "--latest",
        action="store_true",
        help="export only latest"
    )
    args = parser.parse_args()

    if args.command == "run":
        print("PIPELINE WAS STARTED") 
        run_pipeline()
    #exportuoti galima kartu su --latest
    elif args.command == "export":
        if args.latest:
            print("EXPORTING LATEST")
            export_latest()
        else:
            print("EXPORTING ALL")
            export_all()


if __name__ == "__main__":
    main()