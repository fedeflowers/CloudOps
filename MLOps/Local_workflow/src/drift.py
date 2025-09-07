import numpy as np
import pandas as pd
from scipy import stats

def population_stability_index(expected, actual, buckets=10):
    expected = np.array(expected).astype(float)
    actual = np.array(actual).astype(float)

    try:
        quantiles = np.percentile(expected, np.linspace(0, 100, buckets + 1))
    except Exception:
        return np.nan

    eps = 1e-8
    expected_counts, _ = np.histogram(expected, bins=quantiles)
    actual_counts, _ = np.histogram(actual, bins=quantiles)
    expected_perc = expected_counts.astype(float) / (expected_counts.sum() + eps)
    actual_perc = actual_counts.astype(float) / (actual_counts.sum() + eps)

    def psi(e, a):
        return (e - a) * np.log((e + eps) / (a + eps))

    psi_values = psi(expected_perc, actual_perc)
    return np.sum(psi_values)

def ks_test(expected, actual):
    return stats.ks_2samp(expected, actual)

def check_drift(baseline_df, current_df, numeric_features=None, psi_threshold=0.1, ks_pvalue_threshold=0.05):
    numeric_features = numeric_features or baseline_df.select_dtypes(include=[np.number]).columns.tolist()
    drift_report = {}
    alerts = []
    for col in numeric_features:
        b = baseline_df[col].dropna()
        c = current_df[col].dropna()
        if len(b) < 10 or len(c) < 10:
            drift_report[col] = {'reason': 'not enough data'}
            continue
        psi = population_stability_index(b, c, buckets=10)
        ks_res = ks_test(b, c)
        drifted = (not np.isnan(psi) and psi > psi_threshold) or (ks_res.pvalue < ks_pvalue_threshold)
        drift_report[col] = {
            'psi': float(psi) if not np.isnan(psi) else None,
            'ks_stat': float(ks_res.statistic),
            'ks_pvalue': float(ks_res.pvalue),
            'drift': bool(drifted)
        }
        if drifted:
            alerts.append(col)
    return drift_report, alerts

if __name__ == '__main__':
    from utils import load_example_dataset, split
    df = load_example_dataset()
    X_train, X_test, y_train, y_test = split(df, test_size=0.5)
    report, alerts = check_drift(X_train, X_test)
    import json
    print(json.dumps(report, indent=2))
    if alerts:
        print('DRIFT ALERT:', alerts)
