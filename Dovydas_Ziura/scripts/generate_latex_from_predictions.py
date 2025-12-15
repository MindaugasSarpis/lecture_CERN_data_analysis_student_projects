import csv
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# Standardize outputs under personal folder
OUTPUT_TEX = PROJECT_ROOT / "Dovydas_Ziura" / "output" / "predictions_report.tex"
CSV_PATH = PROJECT_ROOT / "Dovydas_Ziura" / "output" / "predictions.csv"
# Dataset lives under personal folder
DATASET_ROOT = PROJECT_ROOT / "dataset"
PERSONAL_DATASET_ROOT = PROJECT_ROOT / "Dovydas_Ziura" / "dataset"


def escape_for_table_cell(s: str, mathlike: bool) -> str:
    # Prevent LaTeX from swallowing content: escape % & # in math;
    # escape more specials in text mode.
    if not s:
        return s
    if mathlike:
        return (
            s.replace('%', r'\%')
             .replace('&', r'\&')
             .replace('#', r'\#')
        )
    return (
        s.replace('\\', r'\textbackslash ')
         .replace('{', r'\{')
         .replace('}', r'\}')
         .replace('%', r'\%')
         .replace('&', r'\&')
         .replace('#', r'\#')
         .replace('_', r'\_')
    )


def normalize_image_path(path_str: str) -> str:
    # Produce a path relative to the output .tex directory, so pdflatex works from any CWD
    raw = path_str.replace("\\", "/")
    name = Path(raw).name
    # Prefer personal dataset location
    candidate = (PERSONAL_DATASET_ROOT / "hand_data" / name)
    if candidate.exists():
        p = candidate.resolve()
    else:
        # Fallback: try project-level dataset
        p = (DATASET_ROOT / "hand_data" / name)
        if not p.exists():
            # Last resort: interpret raw relative to project
            p = (PROJECT_ROOT / raw)
        p = p.resolve()
    rel = os.path.relpath(p, OUTPUT_TEX.parent)
    return rel.replace("\\", "/")


def read_rows(csv_path: Path):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            filename = r.get('filename', '').strip()
            pred = r.get('prediction', '').strip()
            gt = r.get('ground_truth', '').strip()
            rows.append({
                'filename': normalize_image_path(filename),
                'prediction': pred,
                'ground_truth': gt,
            })
        return rows


def build_tex(rows):
    lines = []
    # Larger base font
    lines.append(r"\documentclass[12pt]{article}")
    lines.append(r"\usepackage{graphicx}")
    lines.append(r"\usepackage{booktabs}")
    lines.append(r"\usepackage{longtable}")
    # Slightly smaller margins to give table more space
    lines.append(r"\usepackage[margin=0.7in]{geometry}")
    lines.append(r"\usepackage{amsmath, amssymb}")
    # Ensure images resolve whether compiling from project root or output folder
    lines.append(r"\graphicspath{{./}{Dovydas_Ziura/}{Dovydas_Ziura/dataset/hand_data/}{dataset/hand_data/}}")
    lines.append("")
    lines.append(r"\begin{document}")
    lines.append(r"\section*{Prediction Report}")
    lines.append(r"This report lists images, model predictions, and ground-truth LaTeX.")
    lines.append("")
    # Bigger spacing in table
    lines.append(r"\setlength{\tabcolsep}{12pt}")
    lines.append(r"\renewcommand{\arraystretch}{1.4}")
    # Wider columns to reduce wrapping; first column grows for images
    lines.append(r"\begin{longtable}{p{0.30\linewidth} p{0.33\linewidth} p{0.33\linewidth}}")
    lines.append(r"\toprule")
    lines.append(r"Image & Prediction & Ground Truth \\")
    lines.append(r"\midrule")
    lines.append(r"\endhead")

    for i, r in enumerate(rows, 1):
        # Force image path to personal dataset/hand_data using the filename basename
        name_only = Path(r['filename']).name
        # Use original relative path expected when compiling from output folder
        img = f"../dataset/hand_data/{name_only}"
        pred = r['prediction']
        gt = r['ground_truth']
        # Wrap math in $...$ if it looks mathy (heuristic: contains backslash or ^ or _)
        def wrap_math(s: str) -> str:
            s = s.strip()
            if not s:
                return s
            if any(ch in s for ch in ['\\', '^', '_', '{', '}', '∑', '√']):
                s2 = escape_for_table_cell(s, mathlike=True)
                return f"$ {s2} $"
            return escape_for_table_cell(s, mathlike=False)
        pred_tex = wrap_math(pred)
        gt_tex = wrap_math(gt)
        # Make images a bit larger
        lines.append(rf"\includegraphics[width=\linewidth]{{{img}}} & {pred_tex} & {gt_tex} \\")
        lines.append(r"\addlinespace")
        lines.append(r"\midrule")
    lines.append(r"\bottomrule")
    lines.append(r"\end{longtable}")
    lines.append(r"\end{document}")
    return "\n".join(lines)


def main():
    rows = read_rows(CSV_PATH)
    tex = build_tex(rows)
    OUTPUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_TEX.write_text(tex, encoding='utf-8')
    print(f"Wrote LaTeX report to: {OUTPUT_TEX}")


if __name__ == "__main__":
    main()
