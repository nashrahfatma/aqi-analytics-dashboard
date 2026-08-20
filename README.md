# India Air Quality (AQI) Analytics Dashboard

End-to-end data analytics project analyzing air pollution across 10 major Indian
cities — SQL data cleaning and analysis (window functions, seasonal comparison),
and a live interactive dashboard.

**🔗 Live dashboard:** `https://aqi-analytics-dashboard.github.io/<repo-name>/`
*(enable in Settings → Pages → deploy from `main` branch → root)*

> **Note on data:** This project uses a synthetically generated daily AQI dataset
> (10 cities, Jan 2024–Aug 2026) — not a live paid API feed. City baselines and
> seasonal swings are grounded in real, publicly reported figures (IQAir / CPCB /
> AQI.in, as of Aug 2026) — e.g. Delhi ~107–204 AQI depending on season, Bengaluru
> among the cleanest metros, India's 2025 national PM2.5 average equivalent to an
> AQI of ~134. Generated with `python/generate_data.py`.

## Why this problem
Air pollution is one of India's most urgent, current public-health issues —
especially across North India during winter (stubble burning, Diwali, temperature
inversion trapping pollutants). This project analyzes exactly how much worse it
gets, city by city and season by season.

## Tech Stack
- **SQL (SQLite)** — data cleaning, CTEs, window functions (`RANK`, `LAG`, rolling `AVG() OVER`)
- **Python (pandas, numpy)** — data generation and pipeline orchestration
- **HTML / CSS / JavaScript (Chart.js)** — live interactive dashboard, AQI-standard color coding

## Repo Structure
```
├── index.html                 # Live interactive dashboard (GitHub Pages entry point)
├── python/
│   ├── generate_data.py       # Generates data/aqi_readings.csv
│   ├── load_and_clean.py      # Loads into SQLite, runs cleaning
│   └── export_summaries.py    # Runs analysis queries, exports output/*.csv
├── sql/
│   ├── 01_data_cleaning.sql   # Dedup + missing-sensor-reading handling
│   └── 02_analysis.sql        # 6 analysis queries (CTEs/window functions/rolling avg)
└── data/                      # Generated input CSV (daily AQI readings)
```

## Data Cleaning
- Removed duplicate (city, date) sensor readings using `ROW_NUMBER() OVER (PARTITION BY ...)`
- Dropped rows with missing AQI/PM2.5/PM10 sensor readings (~184 rows) rather than
  imputing — a missing sensor reading is a monitoring gap, not a "zero pollution"
  day, so faking a value would distort the health-risk analysis

## Key SQL Techniques Demonstrated
- `ROW_NUMBER() OVER (PARTITION BY city, date ORDER BY reading_id)` for deduplication
- `LAG()` for month-over-month AQI change per city
- `RANK() OVER (PARTITION BY region ORDER BY avg_aqi DESC)` for within-region city ranking
- Rolling 7-day average: `AVG(aqi) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`
- `CASE`-based AQI health-category classification (Good → Severe, per India's National AQI standard)

## Key Insights
1. **Delhi and Lucknow spend ~25% of days in "Very Poor"/"Severe" AQI** — roughly
   1 in 4 days, a genuine public-health signal.
2. **North Indian cities see a 4× winter spike** — Delhi's winter average (360) is
   over 4× its monsoon average (85), driven by stubble burning, Diwali, and
   temperature inversion trapping pollutants near the ground.
3. **South Indian cities stay far more stable year-round** — Bengaluru, Hyderabad,
   and Chennai show much smaller seasonal swings.
4. **Patna sits in a high-risk middle tier** — 8% hazardous days, better than
   Delhi/Lucknow but well above southern cities, suggesting regional stubble-burning
   spillover into Bihar.

## How to Reproduce
```bash
pip install -r requirements.txt

python python/generate_data.py       # → data/aqi_readings.csv
python python/load_and_clean.py      # → sql/aqi_analytics.db (cleaned)
python python/export_summaries.py    # → output/*.csv
```

`index.html` needs no build step — open it directly in a browser, or serve it via
GitHub Pages.
