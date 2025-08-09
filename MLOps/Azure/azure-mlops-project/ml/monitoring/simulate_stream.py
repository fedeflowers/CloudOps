import time
import argparse
from azure.storage.blob import BlobServiceClient
from sklearn.datasets import load_iris

p = argparse.ArgumentParser()
p.add_argument('--conn', required=True)
p.add_argument('--container', default='data')
p.add_argument('--path', default='incoming/latest.csv')
p.add_argument('--period', type=int, default=300)
p.add_argument('--drift_after', type=int, default=3, help='cycles before drift')
args = p.parse_args()

svc = BlobServiceClient.from_connection_string(args.conn)
container = svc.get_container_client(args.container)
container.create_container(exist_ok=True)

X, y = load_iris(return_X_y=True, as_frame=True)

cycle = 0
while True:
    df = X.copy()
    if cycle >= args.drift_after:
        # induce drift: add offset to a feature and scale variance
        df[df.columns[0]] = df[df.columns[0]] + 2.0
        df[df.columns[1]] = df[df.columns[1]] * 1.5
    # write to blob
    csv = df.to_csv(index=False).encode()
    container.upload_blob(args.path, csv, overwrite=True)
    print(f"Uploaded latest.csv (cycle {cycle})")
    cycle += 1
    time.sleep(args.period)