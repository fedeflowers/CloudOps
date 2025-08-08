import argparse, os

p = argparse.ArgumentParser()
p.add_argument('--model_dir')
p.add_argument('--min_acc', type=float)
p.add_argument('--approved')
args = p.parse_args()

with open(os.path.join(args.model_dir, 'metrics.txt')) as f:
    acc = float(f.read())
print(f"Model acc={acc} threshold={args.min_acc}")

if acc < args.min_acc:
    raise SystemExit("Model did not meet threshold")

os.makedirs(args.approved, exist_ok=True)
with open(os.path.join(args.approved, 'ok'), 'w') as f:
    f.write('approved')