from typing import Dict, List

import numpy as np


class Forecaster:
    """
    Simple early warning using slope (linear trend) over last N samples.
    Output is a bonus (0..20) added to fuzzy urgency for certain actions.
    """
    def __init__(self, window: int = 10):
        self.window = window
        self.buffer: List[Dict[str, float]] = []

    def update(self, row: Dict[str, float]):
        self.buffer.append(row)
        if len(self.buffer) > self.window:
            self.buffer.pop(0)

    def _slope(self, key: str) -> float:
        if len(self.buffer) < 3:
            return 0.0
        t = np.array([r["ts_epoch"] for r in self.buffer], dtype=float)
        y = np.array([r[key] for r in self.buffer], dtype=float)
        t = t - t[0]
        if np.std(t) < 1e-9:
            return 0.0
        return float(np.polyfit(t, y, 1)[0])  # unit/sec

    def risk_bonus(self) -> Dict[str, float]:
        temp_slope = self._slope("temp_engine")
        eff_slope = self._slope("fuel_efficiency")

        bonus_coolant = 0.0
        bonus_service = 0.0

        # tuned for timestamp-based (epoch seconds)
        if temp_slope > 0.002:  # ~0.12°C/min
            bonus_coolant += min(12.0, (temp_slope / 0.004) * 8.0)
            bonus_service += min(6.0, (temp_slope / 0.004) * 4.0)

        if eff_slope < -0.001:  # ~-0.06 index/min
            bonus_service += min(12.0, (-eff_slope / 0.002) * 8.0)

        return {
            "bonus_coolant": float(np.clip(bonus_coolant, 0, 20)),
            "bonus_service": float(np.clip(bonus_service, 0, 20)),
        }