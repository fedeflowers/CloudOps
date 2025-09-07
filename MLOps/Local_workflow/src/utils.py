import pandas as pd
from sklearn.model_selection import train_test_split


def load_example_dataset():
# small reproducible dataset using iris
    from sklearn.datasets import load_iris
    data = load_iris(as_frame=True)
    df = data.frame.copy()
    df['target'] = data.target
    return df


def split(df, target='target', test_size=0.2, random_state=42):
    X = df.drop(columns=[target])
    y = df[target]
    return train_test_split(X, y, test_size=test_size, random_state=random_state)