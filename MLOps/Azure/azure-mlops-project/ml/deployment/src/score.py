import json, numpy as np
import mlflow.pyfunc

# AML will set this env var; fallback for local
import os
MODEL_PATH = os.getenv("AZUREML_MODEL_DIR", ".")

model = mlflow.pyfunc.load_model(MODEL_PATH)

def init():
    pass  # model already loaded

def run(raw_data):
    data = json.loads(raw_data)
    X = np.array(data["inputs"])
    preds = model.predict(X)
    if isinstance(preds, np.ndarray):
        preds = preds.tolist()
    return {"predictions": preds}
