import math
import random
from typing import Dict, Optional

import numpy as np


class EcuSimulator:
    """
    Dummy ECU generator for intermittent sampling (mode B).
    It injects slow drift so you can demonstrate "impending issues".
    """
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.sim_t = 0.0

        self.engine_temp = 82.0
        self.rpm = 1100.0

        self.oil_age_days = 20.0
        self.coolant_age_days = 200.0
        self.mileage_since_service = 3000.0

        self.overheat_drift = 0.0
        self.eff_drop_drift = 0.0

    def step(self, sim_dt_sec: float) -> Dict[str, float]:
        self.sim_t += sim_dt_sec

        cycle = 0.5 + 0.5 * math.sin(self.sim_t / 120.0)
        bursts = 0.25 * max(0.0, math.sin(self.sim_t / 30.0))
        drive = min(1.0, max(0.0, cycle + bursts))

        target_rpm = 900 + 4200 * drive
        self.rpm += (target_rpm - self.rpm) * 0.35 + self.rng.uniform(-60, 60)
        self.rpm = float(np.clip(self.rpm, 700, 6000))

        if self.sim_t > 10 * 60:
            self.overheat_drift += 0.0008 * sim_dt_sec
            self.eff_drop_drift += 0.0005 * sim_dt_sec

        target_temp = 70 + (self.rpm / 6000.0) * 50 + 18 * self.overheat_drift
        self.engine_temp += (target_temp - self.engine_temp) * 0.18 + self.rng.uniform(-0.6, 0.6)
        self.engine_temp = float(np.clip(self.engine_temp, 50, 125))

        # higher is better
        eff = 18.0
        eff -= (self.rpm / 6000.0) * 7.5
        eff -= max(0.0, self.engine_temp - 85.0) * 0.07
        eff -= self.eff_drop_drift * 2.0
        eff -= (self.oil_age_days / 365.0) * 2.0
        eff -= (self.mileage_since_service / 10000.0) * 2.0
        eff += self.rng.uniform(-0.25, 0.25)
        eff = float(np.clip(eff, 5, 20))

        # accelerated aging for demo
        self.oil_age_days += sim_dt_sec / 900.0
        self.coolant_age_days += sim_dt_sec / 600.0

        km_per_sec = (self.rpm / 6000.0) * 0.03
        self.mileage_since_service += km_per_sec * sim_dt_sec

        return {
            "temp_engine": self.engine_temp,
            "rpm": self.rpm,
            "mileage_since_service": self.mileage_since_service,
            "fuel_efficiency": eff,
            "oil_age_days": self.oil_age_days,
            "coolant_age_days": self.coolant_age_days,
        }