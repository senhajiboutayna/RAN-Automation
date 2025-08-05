import json
import os

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
