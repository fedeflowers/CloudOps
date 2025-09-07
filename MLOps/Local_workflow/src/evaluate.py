import pandas as pd
import numpy as np
from model import load_model
from utils import load_example_dataset, split


MODEL_PATH = 'artifacts/model.joblib'


def compute_feature_stats(df):
    # returns mean/std/count per column
    return df.describe().T[['mean', 'std', 'count']]


if __name__ == '__main__':
    df = load_example_dataset()
    X_train, X_test, y_train, y_test = split(df)
    # compute baseline stats from train
    stats = compute_feature_stats(X_train)
    stats.to_csv('artifacts/baseline_feature_stats.csv')
    print('Saved baseline feature stats to artifacts/baseline_feature_stats.csv')


    # optional: load model and evaluate
    clf = load_model(MODEL_PATH)
    preds = clf.predict(X_test)
    from sklearn.metrics import accuracy_score
    print('Test accuracy:', accuracy_score(y_test, preds))