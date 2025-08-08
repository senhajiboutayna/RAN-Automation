import json
import os

import pandas as pd
import numpy as np

# ----------- Threshold detection -----------

THRESHOLD_FILE = "threshold_config.json"
def load_threshold_config(path=THRESHOLD_FILE):
    """Loads thresholds and directions from a JSON file."""
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        return {}

def save_threshold_config(config, path=THRESHOLD_FILE):
    """Saves thresholds and directions to a JSON file."""
    with open(path, "w") as f:
        json.dump(config, f, indent=4)


# ----------- Statistical detection -----------

def detect_zscore_anomalies(series, threshold):
    """
    Detects anomalies using the Z-score method.

    Args :
        series (pandas.Series): The time series data.
        threshold (float): The threshold value for anomaly detection.
    
    Returns:
        bool: True if an anomaly is detected, False otherwise.
    """
    mean = series.mean()
    std = series.std()

    if std == 0 :
        return pd.Series([False] * len(series), index=series.index)

    z_scores = (series - mean) / std
    anomalies = z_scores.abs() > threshold
    return anomalies
