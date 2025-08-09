import argparse, pathlib, os
import numpy as np, pandas as pd
import mlflow, mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

p = argparse.ArgumentParser()
p.add_argument("--data", required=True)
p.add_argument("--out", required=True)
args = p.parse_args()

p_in = pathlib.Path(args.data) / "train.csv"
df = pd.read_csv(p_in)

if "label" in df.columns:
    y = df["label"].values
    X = df.drop(columns=["label"]).select_dtypes(include=[np.number]).fillna(0).values
else:
    X = df.select_dtypes(include=[np.number]).fillna(0).values
    y = (np.arange(len(X)) % 2).astype(int)

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)
clf = LogisticRegression(max_iter=500).fit(Xtr, ytr)
acc = float(accuracy_score(yte, clf.predict(Xte)))
print("eval_acc=", acc)

mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", ""))
with mlflow.start_run():
    mlflow.log_metric("eval_acc", acc)
    out_dir = pathlib.Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    mlflow.sklearn.save_model(clf, path=str(out_dir))
