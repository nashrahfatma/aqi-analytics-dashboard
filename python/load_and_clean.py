"""
Loads the generated AQI CSV into a SQLite database and runs the cleaning script.
Run from repo root: python python/load_and_clean.py
"""
import sqlite3
import pandas as pd

DB_PATH = "sql/aqi_analytics.db"

conn = sqlite3.connect(DB_PATH)

df = pd.read_csv("data/aqi_readings.csv")
df.to_sql("aqi_raw", conn, if_exists="replace", index=False)
print("Loaded aqi_raw:", conn.execute("SELECT COUNT(*) FROM aqi_raw").fetchone()[0], "rows")

with open("sql/01_data_cleaning.sql") as f:
    cleaning_script = f.read()

cur = conn.cursor()
cur.executescript(cleaning_script.rsplit("-- Step 3", 1)[0])
conn.commit()

for t in ["aqi_dedup", "aqi_clean"]:
    cnt = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"{t}: {cnt} rows")

# Create the categorized view used by all analysis queries
with open("sql/02_analysis.sql") as f:
    analysis_script = f.read()
view_sql = analysis_script.split("-- Q1:")[0]
cur.executescript(view_sql)
conn.commit()

print("\nDatabase ready at", DB_PATH)
conn.close()
