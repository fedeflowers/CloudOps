import argparse, sys, pathlib, pandas as pd
from glob import glob

p = argparse.ArgumentParser()
p.add_argument("--latest-folder", required=True)
p.add_argument("--signal", required=True)
p.add_argument("--out", required=True)
args = p.parse_args()

sig = pathlib.Path(args.signal).read_text().strip() if pathlib.Path(args.signal).exists() else "NO_DRIFT"
print("drift_signal=", sig)
if sig != "DRIFT":
    print("No drift detected; stopping retrain path.", file=sys.stderr)
    sys.exit(2)

root = pathlib.Path(args.latest_folder)
csvs = sorted(glob(str(root / "**/*.csv"), recursive=True))
if not csvs:
    raise SystemExit("No CSVs found for prep.")
df = pd.concat((pd.read_csv(p) for p in csvs), ignore_index=True).dropna()

out = pathlib.Path(args.out)
out.mkdir(parents=True, exist_ok=True)
df.to_csv(out / "train.csv", index=False)
print("Prepared rows:", len(df))
