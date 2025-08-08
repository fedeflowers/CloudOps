import argparse, joblib, os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

parser = argparse.ArgumentParser()
parser.add_argument('--train_csv')
parser.add_argument('--model_dir')
args = parser.parse_args()

df = pd.read_csv(args.train_csv)
X = df.drop('target', axis=1)
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

pred = clf.predict(X_test)
acc = accuracy_score(y_test, pred)
print(f"ACC={acc:.4f}")

os.makedirs(args.model_dir, exist_ok=True)
joblib.dump(clf, os.path.join(args.model_dir, 'model.pkl'))
# save simple metadata for evaluation gate
with open(os.path.join(args.model_dir, 'metrics.txt'), 'w') as f:
    f.write(str(acc))