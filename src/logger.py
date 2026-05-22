import csv
import os
from typing import Dict, List

CSV_FIELDS = [
    "ts_iso",
    "ts_epoch",
    "temp_engine",
    "rpm",
    "mileage_since_service",
    "fuel_efficiency",
    "oil_age_days",
    "coolant_age_days",
    "oil_score",
    "coolant_score",
    "service_score",
    "coolant_bonus",
    "service_bonus",
    "coolant_score_total",
    "service_score_total",
]


def ensure_dirs():
    os.makedirs("data", exist_ok=True)
    os.makedirs("plots", exist_ok=True)


def append_csv(path: str, row: Dict[str, float]):
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in CSV_FIELDS})


def load_csv(path: str) -> List[Dict[str, float]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")
    rows = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            parsed = {}
            for k, v in row.items():
                if k == "ts_iso":
                    parsed[k] = v
                else:
                    try:
                        parsed[k] = float(v)
                    except (ValueError, TypeError):
                        parsed[k] = v
            rows.append(parsed)
    return rows