import joblib, json, numpy as np
from typing import List

def init():
    import os
    global model
    model = joblib.load(os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'model.pkl'))

def run(data):
    X = np.array(json.loads(data)["inputs"])  # [[...], [...]]
    preds = model.predict(X).tolist()
    return {"predictions": preds}