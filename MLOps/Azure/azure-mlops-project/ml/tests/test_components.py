import subprocess
import pandas as pd
import numpy as np
import os
from pathlib import Path


def run_script(script_path, args):
    """Helper to run a CLI script with arguments."""
    result = subprocess.run(
        ["python", script_path] + args,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0
    return result


def test_prep_creates_csv(tmp_path):
    outdir = tmp_path / "prep_out"
    run_script("ml/components/prep/prep.py", [
        "--raw_path", "dummy",  # unused in script
        "--output_path", str(outdir)
    ])
    csv_file = outdir / "train.csv"
    assert csv_file.exists()
    df = pd.read_csv(csv_file)
    assert "target" in df.columns
    assert len(df) > 0


def test_train_creates_model_and_metrics(tmp_path):
    # Create dummy training CSV from iris
    from sklearn.datasets import load_iris
    X, y = load_iris(return_X_y=True, as_frame=True)
    df = X.copy()
    df["target"] = y
    train_csv = tmp_path / "train.csv"
    df.to_csv(train_csv, index=False)

    model_dir = tmp_path / "model_dir"
    run_script("ml/components/train/train.py", [
        "--train_csv", str(train_csv),
        "--model_dir", str(model_dir)
    ])

    assert (model_dir / "model.pkl").exists()
    metrics_file = model_dir / "metrics.txt"
    assert metrics_file.exists()
    acc = float(metrics_file.read_text())
    assert 0 <= acc <= 1


def test_evaluate_passes_with_high_acc(tmp_path):
    # Prepare model_dir with high accuracy
    model_dir = tmp_path / "model_dir"
    model_dir.mkdir()
    (model_dir / "metrics.txt").write_text("0.99")

    approved_dir = tmp_path / "approved"
    run_script("ml/components/evaluate/evaluate.py", [
        "--model_dir", str(model_dir),
        "--min_acc", "0.8",
        "--approved", str(approved_dir)
    ])

    assert (approved_dir / "ok").exists()


def test_drift_check_detects_no_drift(tmp_path):
    base = pd.DataFrame({"a": np.random.randn(10)})
    latest = base.copy()
    baseline_csv = tmp_path / "baseline.csv"
    latest_csv = tmp_path / "latest.csv"
    base.to_csv(baseline_csv, index=False)
    latest.to_csv(latest_csv, index=False)

    outdir = tmp_path / "drift_out"
    run_script("ml/components/drift_check/drift_check.py", [
        "--baseline", str(baseline_csv),
        "--latest", str(latest_csv),
        "--threshold", "0.5",
        "--out", str(outdir)
    ])

    assert (outdir / "avg_ks.txt").exists()
    drift_file = outdir / "DRIFT"
    assert not drift_file.exists()
