import argparse, pandas as pd, numpy as np, os
from scipy.stats import ks_2samp

p = argparse.ArgumentParser()
p.add_argument('--baseline')
p.add_argument('--latest')
p.add_argument('--threshold', type=float)
p.add_argument('--out')
args = p.parse_args()

base = pd.read_csv(args.baseline)
latest = pd.read_csv(args.latest)

# Compute average KS statistic across numeric columns as a simple drift proxy
ks_vals = []
for c in base.columns:
    if base[c].dtype.kind in 'ifu' and c in latest.columns:
        stat, pval = ks_2samp(base[c], latest[c])
        ks_vals.append(stat)

avg_ks = float(np.mean(ks_vals)) if ks_vals else 0.0
print(f"AVG_KS={avg_ks:.4f}")

os.makedirs(args.out, exist_ok=True)
with open(os.path.join(args.out, 'avg_ks.txt'), 'w') as f:
    f.write(str(avg_ks))

if avg_ks >= args.threshold:
    # non-empty marker file indicates drift
    with open(os.path.join(args.out, 'DRIFT'), 'w') as f:
        f.write('drift')