import argparse, pathlib, pandas as pd
from glob import glob

p = argparse.ArgumentParser()
p.add_argument("--baseline", required=True)
p.add_argument("--latest-folder", required=True)
p.add_argument("--threshold", type=float, required=True)
p.add_argument("--out", required=True)
args = p.parse_args()

# Read baseline (single file data asset)
b = pd.read_csv(args.baseline)

# Read latest: support MLTable/partitioned folders with multiple CSVs
latest_root = pathlib.Path(args.latest_folder)
csvs = sorted(glob(str(latest_root / "**/*.csv"), recursive=True))
if not csvs:
    raise SystemExit("No CSVs found under latest folder.")
l = pd.concat((pd.read_csv(p) for p in csvs), ignore_index=True)

# Toy drift metric: size delta ratio
if len(b) == 0:
    sig = "DRIFT"
else:
    delta = abs(len(l) - len(b)) / max(len(b), 1)
    sig = "DRIFT" if delta > args.threshold else "NO_DRIFT"

out = pathlib.Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(sig)
print("drift_signal=", sig)
