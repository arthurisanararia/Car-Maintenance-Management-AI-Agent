# Car Maintenance Management AI Agent (Mamdani Fuzzy Inference System)

This project simulates a car ECU data stream (dummy telemetry) and performs maintenance analysis using a Mamdani Fuzzy Inference System (FIS) with centroid defuzzification.

## Features
- Intermittent ECU sampling (mode B) suitable for maintenance monitoring
- Mamdani Fuzzy Inference System (min-max) + centroid defuzzification
- Outputs:
  - Score (0-100) + category (Rendah/Sedang/Tinggi)
  - Recommended top maintenance action
- Early-warning forecasting (trend-based bonus) to predict issues "soon"
- CSV logging
- Plot generation by request with selectable time range
  - show in matplotlib window
  - save plot image to `plots/`

## Setup
```bash
pip install -r requirements.txt
```

## Run simulation (append to CSV)
Example: 1 sample advances timestamp by 10 minutes, so 120 samples represent 20 hours but only 120 rows.

```bash
python -m src.cli run --sample-sec 10 --clock-step-sec 600 --steps 120 --start "2026-05-22 08:00:00"
```

Output CSV:
- `data/telemetry.csv`

## Plot by request (time range)
```bash
python -m src.cli plot --from "2026-05-22 12:00:00" --to "2026-05-22 18:00:00" --show --save
```

Saved plots:
- `plots/plot_<timestamp>.png`

## Poster-friendly architecture
ECU (dummy stream) -> Fuzzification -> Rule evaluation (Mamdani) -> Defuzzification (Centroid)
-> Decision Layer (scores + categories) -> Early Warning (trend bonus) -> Display/Plot