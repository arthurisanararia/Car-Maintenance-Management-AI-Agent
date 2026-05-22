from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np


def trapmf(x, a, b, c, d):
    if x <= a:
        return 0.0
    if a < x < b:
        return (x - a) / (b - a) if b != a else 1.0
    if b <= x <= c:
        return 1.0
    if c < x < d:
        return (d - x) / (d - c) if d != c else 1.0
    return 0.0


def trimf(x, a, b, c):
    if x <= a or x >= c:
        return 0.0
    if a < x < b:
        return (x - a) / (b - a) if b != a else 1.0
    if x == b:
        return 1.0
    if b < x < c:
        return (c - x) / (c - b) if c != b else 1.0
    return 0.0


@dataclass
class FuzzyVar:
    name: str
    sets: Dict[str, Tuple[str, Tuple[float, ...]]]  # set_name -> (mf_type, params)

    def fuzzify(self, x: float) -> Dict[str, float]:
        out = {}
        for set_name, (mf_type, params) in self.sets.items():
            if mf_type == "trap":
                out[set_name] = trapmf(x, *params)
            elif mf_type == "tri":
                out[set_name] = trimf(x, *params)
            else:
                raise ValueError(f"Unknown mf_type: {mf_type}")
        return out


@dataclass
class Antecedent:
    var: str
    set_name: str


@dataclass
class Rule:
    antecedents: List[Antecedent]  # AND via min
    consequent: str                # output set name
    weight: float = 1.0


class MamdaniFIS:
    """
    Mamdani inference:
    - AND: min
    - implication: clip consequent MF by alpha
    - aggregation: max
    - defuzzification: centroid
    """
    def __init__(self, input_vars: Dict[str, FuzzyVar], output_var: FuzzyVar,
                 rules: List[Rule], output_universe: np.ndarray):
        self.input_vars = input_vars
        self.output_var = output_var
        self.rules = rules
        self.U = output_universe

    def _output_mf(self, set_name: str) -> np.ndarray:
        mf_type, params = self.output_var.sets[set_name]
        if mf_type == "trap":
            return np.array([trapmf(x, *params) for x in self.U])
        if mf_type == "tri":
            return np.array([trimf(x, *params) for x in self.U])
        raise ValueError(f"Unknown output mf_type: {mf_type}")

    def infer(self, crisp_inputs: Dict[str, float]) -> float:
        fuzz = {vn: self.input_vars[vn].fuzzify(crisp_inputs[vn]) for vn in self.input_vars}

        agg = np.zeros_like(self.U, dtype=float)

        for rule in self.rules:
            strengths = []
            for ant in rule.antecedents:
                strengths.append(fuzz[ant.var].get(ant.set_name, 0.0))
            alpha = (min(strengths) if strengths else 0.0) * rule.weight

            cons_mf = self._output_mf(rule.consequent)
            clipped = np.minimum(cons_mf, alpha)
            agg = np.maximum(agg, clipped)

        den = np.sum(agg)
        if den <= 1e-9:
            return 0.0
        return float(np.sum(self.U * agg) / den)


def urgency_label(score: float) -> str:
    if score < 35:
        return "Rendah"
    if score < 70:
        return "Sedang"
    return "Tinggi"