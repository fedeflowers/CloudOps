import argparse
from pathlib import Path
from sklearn.datasets import load_iris

parser = argparse.ArgumentParser()
parser.add_argument('--raw_path')
parser.add_argument('--output_path')
args = parser.parse_args()

X, y = load_iris(return_X_y=True, as_frame=True)
df = X.copy(); df['target'] = y

outdir = Path(args.output_path); outdir.mkdir(parents=True, exist_ok=True)
df.to_csv(outdir/"train.csv", index=False)