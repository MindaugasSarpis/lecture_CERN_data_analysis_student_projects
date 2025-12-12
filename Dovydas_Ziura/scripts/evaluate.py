import csv
import argparse

def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    dp = list(range(lb + 1))
    for i in range(1, la + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, lb + 1):
            temp = dp[j]
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[j] = min(
                dp[j] + 1,      # deletion
                dp[j - 1] + 1,  # insertion
                prev + cost     # substitution
            )
            prev = temp
    return dp[lb]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', type=str, default='../output/predictions.csv', help='Path to predictions CSV with filename,prediction,ground_truth')
    args = parser.parse_args()

    rows = []
    with open(args.csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    total = len(rows)
    if total == 0:
        print('[WARN] No rows found in CSV.')
        return

    exact = 0
    dists = []
    for r in rows:
        pred = (r.get('prediction') or '').strip()
        gt = (r.get('ground_truth') or '').strip()
        if gt == '':
            # skip missing ground truth from aggregate metrics, but report separately
            continue
        if pred == gt:
            exact += 1
        dists.append(levenshtein(pred, gt))

    labeled = len(dists)
    exact_acc = (exact / labeled) * 100 if labeled > 0 else 0.0
    avg_edit = (sum(dists) / labeled) if labeled > 0 else 0.0

    print('[RESULTS] Evaluation Summary')
    print(f'- Rows: {total}')
    print(f'- Labeled: {labeled}')
    print(f'- Exact-match accuracy: {exact_acc:.2f}%')
    print(f'- Average Levenshtein distance: {avg_edit:.2f}')

    # Optional: print top-5 hardest examples by edit distance
    examples = []
    for r in rows:
        pred = (r.get('prediction') or '').strip()
        gt = (r.get('ground_truth') or '').strip()
        if gt == '':
            continue
        examples.append((levenshtein(pred, gt), r.get('filename',''), pred, gt))
    examples.sort(key=lambda x: -x[0])
    print('\n[DETAIL] Hardest examples (top 5):')
    for d, fn, pred, gt in examples[:5]:
        print(f'- {fn} | dist={d} | pred={pred} | gt={gt}')

if __name__ == '__main__':
    main()
