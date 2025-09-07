import mlflow
import mlflow.sklearn
import os
from model import build_model, save_model
from utils import load_example_dataset, split


import os

mlruns_path = os.path.join(os.getcwd(), "mlruns")  # absolute path to mlruns in current folder
MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI', f"file:///{mlruns_path.replace(os.sep, '/')}")



def train_and_log(run_name='local-run'):
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("local_experiment")  # create/get experiment
    df = load_example_dataset()
    X_train, X_test, y_train, y_test = split(df)
    input_example = X_train.head(5)

    clf = build_model()


    with mlflow.start_run(run_name=run_name) as run:
        clf.fit(X_train, y_train)
        # log model
        mlflow.sklearn.log_model(clf, name='model', input_example = input_example)
        # log params
        mlflow.log_param('model_type', 'RandomForest')
        mlflow.log_metric('train_samples', len(X_train))


        # evaluate on test
        from sklearn.metrics import accuracy_score
        preds = clf.predict(X_test)
        acc = accuracy_score(y_test, preds)
        mlflow.log_metric('test_accuracy', float(acc))


        # save a local copy too
        os.makedirs('artifacts', exist_ok=True)
        save_model(clf, 'artifacts/model.joblib')


    print(f"Run saved: {run.info.run_id}")


if __name__ == '__main__':
    train_and_log()