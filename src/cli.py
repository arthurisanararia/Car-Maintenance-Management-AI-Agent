import argparse
import time
from datetime import datetime, timedelta
from typing import Optional

from .fuzzy import urgency_label
from .forecast import Forecaster
from .logger import append_csv, ensure_dirs
from .simulator import EcuSimulator
from .systems import build_systems
from .plotting import plot_from_csv, DT_FORMAT


def run(csv_path: str,
        sample_sec: float,
        print_every: int,
        steps: Optional[int],
        seed: Optional[int],
        start_dt: str,
        clock_step_sec: float):
    """
    sample_sec: delta for ECU simulation dynamics (mode B)
    clock_step_sec: how much the logged timestamp advances per sample (demo "hours" with few rows)
    """
    ensure_dirs()
    oil_fis, coolant_fis, service_fis = build_systems()
    ecu = EcuSimulator(seed=seed)
    forecaster = Forecaster(window=10)

    current_dt = datetime.strptime(start_dt, DT_FORMAT)

    step = 0
    while True:
        step += 1

        ts_iso = current_dt.strftime(DT_FORMAT)
        ts_epoch = current_dt.timestamp()

        data = ecu.step(sample_sec)
        row_base = {"ts_iso": ts_iso, "ts_epoch": ts_epoch, **data}

        forecaster.update(row_base)
        bonus = forecaster.risk_bonus()

        oil_score = oil_fis.infer({
            "oil_age_days": data["oil_age_days"],
            "mileage_since_service": data["mileage_since_service"],
            "temp_engine": data["temp_engine"],
            "rpm": data["rpm"],
        })
        coolant_score = coolant_fis.infer({
            "coolant_age_days": data["coolant_age_days"],
            "temp_engine": data["temp_engine"],
            "rpm": data["rpm"],
        })
        service_score = service_fis.infer({
            "fuel_efficiency": data["fuel_efficiency"],
            "temp_engine": data["temp_engine"],
            "rpm": data["rpm"],
        })

        coolant_total = max(0.0, min(100.0, coolant_score + bonus["bonus_coolant"]))
        service_total = max(0.0, min(100.0, service_score + bonus["bonus_service"]))

        row = dict(row_base)
        row.update({
            "oil_score": oil_score,
            "coolant_score": coolant_score,
            "service_score": service_score,
            "coolant_bonus": bonus["bonus_coolant"],
            "service_bonus": bonus["bonus_service"],
            "coolant_score_total": coolant_total,
            "service_score_total": service_total,
        })
        append_csv(csv_path, row)

        if step % print_every == 0:
            recs = [
                ("Ganti Oli", oil_score),
                ("Ganti Coolant", coolant_total),
                ("Servis Mesin", service_total),
            ]
            top = max(recs, key=lambda x: x[1])

            print("\n" + "=" * 92)
            print(f"time={ts_iso} | Temp={data['temp_engine']:5.1f}°C | RPM={data['rpm']:6.0f} | FuelEffIdx={data['fuel_efficiency']:4.1f}")
            print(f"OilAge={data['oil_age_days']:6.1f} d | CoolantAge={data['coolant_age_days']:6.1f} d | MileageSinceService={data['mileage_since_service']:7.1f} km")
            print(f"[GANTI OLI]     score={oil_score:5.1f} ({urgency_label(oil_score)})")
            print(f"[GANTI COOLANT] score={coolant_total:5.1f} ({urgency_label(coolant_total)}) (fuzzy={coolant_score:4.1f} + bonus={bonus['bonus_coolant']:4.1f})")
            print(f"[SERVIS MESIN]  score={service_total:5.1f} ({urgency_label(service_total)}) (fuzzy={service_score:4.1f} + bonus={bonus['bonus_service']:4.1f})")
            print(f">> REKOMENDASI TERATAS: {top[0]} (score={top[1]:.1f})")

        if steps is not None and step >= steps:
            break

        current_dt = current_dt + timedelta(seconds=clock_step_sec)
        time.sleep(0.05)


def main():
    p = argparse.ArgumentParser(description="Car Maintenance Management AI Agent (Mamdani FIS)")

    sub = p.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run simulation + fuzzy inference, append to CSV (timestamp-based).")
    p_run.add_argument("--csv", default="data/telemetry.csv")
    p_run.add_argument("--sample-sec", type=float, default=10.0)
    p_run.add_argument("--print-every", type=int, default=1)
    p_run.add_argument("--steps", type=int, default=120, help="Total samples; set -1 for infinite.")
    p_run.add_argument("--seed", type=int, default=42)
    p_run.add_argument("--start", default="2026-05-22 08:00:00", help=f'Start time format "{DT_FORMAT}"')
    p_run.add_argument("--clock-step-sec", type=float, default=600.0, help="Advance logged time per sample (default 10 min).")

    p_plot = sub.add_parser("plot", help="Plot by request from CSV using datetime range.")
    p_plot.add_argument("--csv", default="data/telemetry.csv")
    p_plot.add_argument("--from", dest="dt_from", type=str, default=None, help=f'From "{DT_FORMAT}"')
    p_plot.add_argument("--to", dest="dt_to", type=str, default=None, help=f'To "{DT_FORMAT}"')
    p_plot.add_argument("--show", action="store_true")
    p_plot.add_argument("--save", action="store_true")
    p_plot.add_argument("--out", default=None)

    args = p.parse_args()

    if args.cmd == "run":
        steps = None if args.steps == -1 else args.steps
        run(args.csv, args.sample_sec, args.print_every, steps, args.seed, args.start, args.clock_step_sec)
        print(f"\nDone. Data appended to: {args.csv}")

    elif args.cmd == "plot":
        plot_from_csv(args.csv, args.dt_from, args.dt_to, show=args.show, save=args.save, out_path=args.out)


if __name__ == "__main__":
    main()