import os
import time
from datetime import datetime
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt

from .logger import load_csv

DT_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_dt(s: str) -> datetime:
    return datetime.strptime(s, DT_FORMAT)


def plot_from_csv(csv_path: str, dt_from: Optional[str], dt_to: Optional[str],
                  show: bool, save: bool, out_path: Optional[str]):
    rows = load_csv(csv_path)
    if not rows:
        raise ValueError("CSV has no data.")

    if dt_from is None:
        t_from = rows[0]["ts_epoch"]
    else:
        t_from = parse_dt(dt_from).timestamp()

    if dt_to is None:
        t_to = rows[-1]["ts_epoch"]
    else:
        t_to = parse_dt(dt_to).timestamp()

    sel = [r for r in rows if (r["ts_epoch"] >= t_from and r["ts_epoch"] <= t_to)]
    if not sel:
        raise ValueError("No data in selected time range.")

    x_dt = [datetime.fromtimestamp(r["ts_epoch"]) for r in sel]

    temp = np.array([r["temp_engine"] for r in sel])
    rpm = np.array([r["rpm"] for r in sel])

    oil = np.array([r["oil_score"] for r in sel])
    coolant = np.array([r["coolant_score_total"] for r in sel])
    service = np.array([r["service_score_total"] for r in sel])

    fig, axs = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    ax1, ax2 = axs

    ax1.plot(x_dt, temp, label="Temp Engine (°C)")
    ax1_t = ax1.twinx()
    ax1_t.plot(x_dt, rpm, color="orange", alpha=0.7, label="RPM")

    ax1.set_title("Telemetry (selected time range)")
    ax1.set_ylabel("Temp (°C)")
    ax1_t.set_ylabel("RPM")

    l1, lab1 = ax1.get_legend_handles_labels()
    l2, lab2 = ax1_t.get_legend_handles_labels()
    ax1.legend(l1 + l2, lab1 + lab2, loc="upper left")

    ax2.plot(x_dt, oil, label="Urgency Ganti Oli (Fuzzy)")
    ax2.plot(x_dt, coolant, label="Urgency Ganti Coolant (Fuzzy + Forecast bonus)")
    ax2.plot(x_dt, service, label="Urgency Servis Mesin (Fuzzy + Forecast bonus)")
    ax2.set_ylabel("Urgency (0-100)")
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper left")

    plt.tight_layout()

    if save:
        if out_path is None:
            os.makedirs("plots", exist_ok=True)
            out_path = os.path.join("plots", f"plot_{int(time.time())}.png")
        plt.savefig(out_path, dpi=150)
        print(f"Saved plot: {out_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)