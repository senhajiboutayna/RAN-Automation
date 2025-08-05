# ----------- Thresholds -----------

kpi_thresholds = {
    'RRC Setup Fail': 10,
    'RRC_Succes_Rate': 95,
    'VoLTE Traffic': None,
    '4G PS Traffic(GB)': None,
    'Erab_Succes_Rate': 95,
    # Ajouter les autres seuils ici
}

import json
import os

THRESHOLD_FILE = "threshold_config.json"

def load_threshold_config(path=THRESHOLD_FILE):
    """Charge les seuils et directions depuis un fichier JSON."""
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        return {}

def save_threshold_config(config, path=THRESHOLD_FILE):
    """Sauvegarde les seuils et directions dans un fichier JSON."""
    with open(path, "w") as f:
        json.dump(config, f, indent=4)
