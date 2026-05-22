import numpy as np

from .fuzzy import Antecedent, FuzzyVar, MamdaniFIS, Rule


def build_systems():
    # Inputs
    temp_engine = FuzzyVar("temp_engine", {
        "rendah": ("trap", (50, 50, 65, 75)),
        "normal": ("tri", (70, 85, 95)),
        "tinggi": ("trap", (90, 100, 120, 120)),
    })

    rpm = FuzzyVar("rpm", {
        "rendah": ("trap", (0, 0, 1500, 2500)),
        "medium": ("tri", (2000, 3500, 5000)),
        "tinggi": ("trap", (4000, 5000, 6000, 6000)),
    })

    mileage = FuzzyVar("mileage_since_service", {
        "pendek": ("trap", (0, 0, 2000, 4000)),
        "sedang": ("tri", (3000, 5000, 7000)),
        "panjang": ("trap", (6000, 8000, 10000, 12000)),
    })

    fuel_eff = FuzzyVar("fuel_efficiency", {
        "buruk": ("trap", (0, 0, 8, 11)),
        "normal": ("tri", (10, 13, 16)),
        "bagus": ("trap", (15, 17, 20, 20)),
    })

    oil_age = FuzzyVar("oil_age_days", {
        "baru": ("trap", (0, 0, 30, 90)),
        "sedang": ("tri", (60, 150, 240)),
        "lama": ("trap", (200, 280, 365, 365)),
    })

    coolant_age = FuzzyVar("coolant_age_days", {
        "baru": ("trap", (0, 0, 90, 180)),
        "sedang": ("tri", (150, 365, 550)),
        "lama": ("trap", (500, 650, 730, 730)),
    })

    # Output
    urgency = FuzzyVar("urgency", {
        "rendah": ("trap", (0, 0, 20, 40)),
        "sedang": ("tri", (30, 55, 80)),
        "tinggi": ("trap", (70, 85, 100, 100)),
    })
    U = np.linspace(0, 100, 501)

    # Oil change rules
    oil_rules = [
        Rule([Antecedent("oil_age_days", "lama")], "tinggi"),
        Rule([Antecedent("oil_age_days", "sedang"), Antecedent("mileage_since_service", "panjang")], "tinggi"),
        Rule([Antecedent("oil_age_days", "sedang"), Antecedent("temp_engine", "tinggi")], "tinggi"),

        Rule([Antecedent("oil_age_days", "sedang")], "sedang"),
        Rule([Antecedent("mileage_since_service", "sedang")], "sedang"),
        Rule([Antecedent("temp_engine", "tinggi"), Antecedent("rpm", "medium")], "sedang"),

        Rule([Antecedent("oil_age_days", "baru"), Antecedent("mileage_since_service", "pendek")], "rendah"),
        Rule([Antecedent("temp_engine", "rendah"), Antecedent("rpm", "rendah")], "rendah"),
    ]

    # Coolant change rules
    coolant_rules = [
        Rule([Antecedent("coolant_age_days", "lama")], "tinggi"),
        Rule([Antecedent("coolant_age_days", "sedang"), Antecedent("temp_engine", "tinggi")], "tinggi"),
        Rule([Antecedent("rpm", "medium"), Antecedent("temp_engine", "tinggi")], "tinggi"),

        Rule([Antecedent("coolant_age_days", "sedang")], "sedang"),
        Rule([Antecedent("temp_engine", "tinggi")], "sedang"),
        Rule([Antecedent("temp_engine", "normal"), Antecedent("rpm", "tinggi")], "sedang"),

        Rule([Antecedent("coolant_age_days", "baru"), Antecedent("temp_engine", "normal")], "rendah"),
        Rule([Antecedent("rpm", "rendah"), Antecedent("temp_engine", "rendah")], "rendah"),
    ]

    # Service rules
    service_rules = [
        Rule([Antecedent("fuel_efficiency", "buruk"), Antecedent("rpm", "tinggi")], "tinggi"),
        Rule([Antecedent("fuel_efficiency", "buruk"), Antecedent("temp_engine", "tinggi")], "tinggi"),
        Rule([Antecedent("temp_engine", "tinggi"), Antecedent("rpm", "tinggi")], "tinggi"),

        Rule([Antecedent("fuel_efficiency", "buruk")], "sedang"),
        Rule([Antecedent("temp_engine", "tinggi")], "sedang"),
        Rule([Antecedent("fuel_efficiency", "normal"), Antecedent("rpm", "medium")], "sedang"),

        Rule([Antecedent("fuel_efficiency", "bagus"), Antecedent("temp_engine", "normal")], "rendah"),
        Rule([Antecedent("rpm", "rendah"), Antecedent("temp_engine", "normal")], "rendah"),
    ]

    oil_fis = MamdaniFIS(
        input_vars={"oil_age_days": oil_age, "mileage_since_service": mileage, "temp_engine": temp_engine, "rpm": rpm},
        output_var=urgency, rules=oil_rules, output_universe=U
    )
    coolant_fis = MamdaniFIS(
        input_vars={"coolant_age_days": coolant_age, "temp_engine": temp_engine, "rpm": rpm},
        output_var=urgency, rules=coolant_rules, output_universe=U
    )
    service_fis = MamdaniFIS(
        input_vars={"fuel_efficiency": fuel_eff, "temp_engine": temp_engine, "rpm": rpm},
        output_var=urgency, rules=service_rules, output_universe=U
    )

    return oil_fis, coolant_fis, service_fis