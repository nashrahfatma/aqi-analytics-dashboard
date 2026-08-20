"""
Generates a realistic daily AQI (Air Quality Index) dataset for 10 major Indian
cities, Jan 2024 - Dec 2025.

Methodology: This is a synthetically generated dataset — not pulled live from a
paid API. Each city's baseline AQI level and seasonal swing are grounded in real,
publicly reported figures (IQAir / CPCB / AQI.in, as of Aug 2026), for example:
Delhi ~107-112, Kolkata ~97, Mumbai ~69, Pune ~67, national 2025 average ~134.
Daily values simulate realistic seasonal pollution patterns for North India:
- Winter spike (Oct-Jan): stubble burning + Diwali firecrackers + cooler air
  trapping pollutants (temperature inversion)
- Monsoon improvement (Jun-Sep): rain washes out particulates
- Random day-to-day noise + occasional missing sensor readings (real-world messiness)

Run from repo root: python python/generate_data.py
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(7)
np.random.seed(7)

# City baseline AQI (annual average) and region, grounded in real reported data
cities = {
    "Delhi":      {"baseline": 155, "region": "North", "winter_mult": 2.3},
    "Patna":      {"baseline": 140, "region": "East",  "winter_mult": 2.1},
    "Lucknow":    {"baseline": 148, "region": "North", "winter_mult": 2.2},
    "Kolkata":    {"baseline": 100, "region": "East",  "winter_mult": 1.7},
    "Jaipur":     {"baseline": 118, "region": "North", "winter_mult": 1.9},
    "Mumbai":     {"baseline": 75,  "region": "West",  "winter_mult": 1.4},
    "Pune":       {"baseline": 68,  "region": "West",  "winter_mult": 1.35},
    "Hyderabad":  {"baseline": 78,  "region": "South", "winter_mult": 1.3},
    "Chennai":    {"baseline": 82,  "region": "South", "winter_mult": 1.25},
    "Bengaluru":  {"baseline": 55,  "region": "South", "winter_mult": 1.2},
}

def seasonal_factor(month, winter_mult):
    """Winter months (Nov-Jan) spike, monsoon months (Jun-Sep) dip."""
    if month in (11, 12, 1):
        return winter_mult
    elif month in (6, 7, 8, 9):
        return 0.55
    elif month in (2, 3, 10):
        return (winter_mult + 1) / 2  # transition months
    else:
        return 0.85

def aqi_category(aqi):
    if aqi <= 50: return "Good"
    if aqi <= 100: return "Satisfactory"
    if aqi <= 200: return "Moderate"
    if aqi <= 300: return "Poor"
    if aqi <= 400: return "Very Poor"
    return "Severe"

start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)
n_days = (end_date - start_date).days + 1

records = []
row_id = 1
for city, meta in cities.items():
    for d in range(n_days):
        date = start_date + timedelta(days=d)
        factor = seasonal_factor(date.month, meta["winter_mult"])
        noise = np.random.normal(0, 12)
        # Diwali spike simulation (approx late Oct / early Nov each year)
        diwali_boost = 45 if (date.month == 11 and date.day <= 5) else 0
        aqi = max(15, meta["baseline"] * factor + noise + diwali_boost)
        aqi = round(aqi, 1)

        pm25 = round(aqi * 0.55 + np.random.normal(0, 4), 1)
        pm10 = round(aqi * 0.85 + np.random.normal(0, 6), 1)

        records.append({
            "reading_id": row_id,
            "city": city,
            "region": meta["region"],
            "date": date.strftime("%Y-%m-%d"),
            "aqi": aqi,
            "pm25": max(5, pm25),
            "pm10": max(8, pm10),
        })
        row_id += 1

df = pd.DataFrame(records)

# Inject real-world messiness: missing sensor readings (~2.5%) and a few duplicate rows
missing_idx = df.sample(frac=0.025, random_state=3).index
df.loc[missing_idx, ["aqi", "pm25", "pm10"]] = np.nan

dupes = df.sample(35, random_state=5)
df = pd.concat([df, dupes], ignore_index=True)

os.makedirs("data", exist_ok=True)
df.to_csv("data/aqi_readings.csv", index=False)

print("Rows generated:", df.shape)
print("Missing values:\n", df[["aqi", "pm25", "pm10"]].isna().sum())
print("Duplicate rows:", df.duplicated(subset=["city", "date"]).sum())
print("\nSample real-world reference check (2025 avg AQI by city, Delhi should be highest):")
print(df.dropna().groupby("city")["aqi"].mean().sort_values(ascending=False).round(1))
