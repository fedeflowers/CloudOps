import argparse, sys
import mlflow, mlflow.pyfunc
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
import numpy as np

p = argparse.ArgumentParser()
p.add_argument("--model", required=True)
p.add_argument("--min-acc", type=float, required=True)
args = p.parse_args()

iris = load_iris()
X, y = iris.data, iris.target

model = mlflow.pyfunc.load_model(args.model)
preds = model.predict(X)
if isinstance(preds, list): preds = np.asarray(preds)
if preds.ndim == 2: preds = preds.argmax(axis=1)
acc = float(accuracy_score(y, preds))
print("accuracy=", acc)

float_min_acc = float(args.min_acc)
if acc < float_min_acc:
    print(f"Accuracy {acc:.4f} below threshold {float_min_acc:.4f}", file=sys.stderr)
    sys.exit(3)
