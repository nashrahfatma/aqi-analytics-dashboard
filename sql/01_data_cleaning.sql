-- ============================================================
-- 01_data_cleaning.sql
-- Purpose: Clean raw AQI sensor readings
-- Issues handled: duplicate readings, missing sensor values
-- ============================================================

-- Step 1: Remove duplicate (city, date) readings — keep first occurrence
DROP TABLE IF EXISTS aqi_dedup;
CREATE TABLE aqi_dedup AS
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY city, date ORDER BY reading_id) AS rn
    FROM aqi_raw
)
WHERE rn = 1;

-- Step 2: Handle missing sensor values
-- A missing AQI/PM reading is a sensor outage, not a "zero pollution" day —
-- we drop these rows rather than impute, since faking a pollution reading
-- would distort the health-risk analysis.
DROP TABLE IF EXISTS aqi_clean;
CREATE TABLE aqi_clean AS
SELECT reading_id, city, region, date, aqi, pm25, pm10
FROM aqi_dedup
WHERE aqi IS NOT NULL AND pm25 IS NOT NULL AND pm10 IS NOT NULL;

-- Step 3: Sanity check
SELECT 'aqi_raw' AS stage, COUNT(*) AS row_count FROM aqi_raw
UNION ALL
SELECT 'aqi_dedup', COUNT(*) FROM aqi_dedup
UNION ALL
SELECT 'aqi_clean', COUNT(*) FROM aqi_clean;
