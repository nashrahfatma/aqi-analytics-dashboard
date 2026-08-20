"""
Runs the core analysis queries and exports summary CSVs used by the dashboard.
Run from repo root: python python/export_summaries.py
"""
import sqlite3
import pandas as pd
import os

DB_PATH = "sql/aqi_analytics.db"
OUT_DIR = "output"
os.makedirs(OUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

city_avg = pd.read_sql_query("""
    SELECT city, region, ROUND(AVG(aqi),1) AS avg_aqi,
           ROUND(MAX(aqi),1) AS worst_day_aqi, ROUND(MIN(aqi),1) AS best_day_aqi
    FROM aqi_categorized GROUP BY city, region ORDER BY avg_aqi DESC
""", conn)

monthly = pd.read_sql_query("""
    SELECT city, strftime('%Y-%m', date) AS month, ROUND(AVG(aqi),1) AS avg_aqi
    FROM aqi_categorized GROUP BY city, month ORDER BY city, month
""", conn)

hazardous = pd.read_sql_query("""
    SELECT city, COUNT(*) AS total_days,
           SUM(CASE WHEN category IN ('Severe','Very Poor') THEN 1 ELSE 0 END) AS hazardous_days,
           ROUND(100.0*SUM(CASE WHEN category IN ('Severe','Very Poor') THEN 1 ELSE 0 END)/COUNT(*),1) AS hazardous_pct
    FROM aqi_categorized GROUP BY city ORDER BY hazardous_pct DESC
""", conn)

seasonal = pd.read_sql_query("""
    SELECT city,
    ROUND(AVG(CASE WHEN CAST(strftime('%m',date) AS INTEGER) IN (11,12,1) THEN aqi END),1) AS winter_avg_aqi,
    ROUND(AVG(CASE WHEN CAST(strftime('%m',date) AS INTEGER) IN (6,7,8,9) THEN aqi END),1) AS monsoon_avg_aqi
    FROM aqi_categorized GROUP BY city ORDER BY winter_avg_aqi DESC
""", conn)

city_avg.to_csv(f"{OUT_DIR}/city_avg_aqi.csv", index=False)
monthly.to_csv(f"{OUT_DIR}/monthly_trend.csv", index=False)
hazardous.to_csv(f"{OUT_DIR}/hazardous_days.csv", index=False)
seasonal.to_csv(f"{OUT_DIR}/seasonal_comparison.csv", index=False)

print("Summaries written to output/:")
print(city_avg)
print()
print(seasonal)

conn.close()
