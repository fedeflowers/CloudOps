import joblib
from sklearn.ensemble import RandomForestClassifier


def build_model(random_state=42):
    return RandomForestClassifier(n_estimators=100, random_state=random_state)


def save_model(clf, path):
    joblib.dump(clf, path)


def load_model(path):
    return joblib.load(path)