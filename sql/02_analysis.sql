-- ============================================================
-- 02_analysis.sql
-- Purpose: Core analysis queries on cleaned AQI data
-- Techniques: CTEs, window functions (RANK, LAG, AVG OVER), CASE-based classification
-- ============================================================

-- Convenience view: adds AQI health category to every clean reading
DROP VIEW IF EXISTS aqi_categorized;
CREATE VIEW aqi_categorized AS
SELECT
    reading_id, city, region, date, aqi, pm25, pm10,
    CASE
        WHEN aqi <= 50  THEN 'Good'
        WHEN aqi <= 100 THEN 'Satisfactory'
        WHEN aqi <= 200 THEN 'Moderate'
        WHEN aqi <= 300 THEN 'Poor'
        WHEN aqi <= 400 THEN 'Very Poor'
        ELSE 'Severe'
    END AS category
FROM aqi_clean;


-- Q1: Average AQI by city, ranked worst to best
SELECT
    city,
    region,
    ROUND(AVG(aqi), 1) AS avg_aqi,
    ROUND(MAX(aqi), 1) AS worst_day_aqi,
    ROUND(MIN(aqi), 1) AS best_day_aqi
FROM aqi_categorized
GROUP BY city, region
ORDER BY avg_aqi DESC;


-- Q2: Monthly AQI trend per city with month-over-month change (window function: LAG)
WITH monthly AS (
    SELECT
        city,
        strftime('%Y-%m', date) AS month,
        ROUND(AVG(aqi), 1) AS avg_aqi
    FROM aqi_categorized
    GROUP BY city, month
)
SELECT
    city,
    month,
    avg_aqi,
    ROUND(avg_aqi - LAG(avg_aqi) OVER (PARTITION BY city ORDER BY month), 1) AS mom_change
FROM monthly
ORDER BY city, month;


-- Q3: Number of "Severe"/"Very Poor" days per city (health-risk exposure)
SELECT
    city,
    COUNT(*) AS total_days,
    SUM(CASE WHEN category IN ('Severe','Very Poor') THEN 1 ELSE 0 END) AS hazardous_days,
    ROUND(100.0 * SUM(CASE WHEN category IN ('Severe','Very Poor') THEN 1 ELSE 0 END) / COUNT(*), 1) AS hazardous_pct
FROM aqi_categorized
GROUP BY city
ORDER BY hazardous_pct DESC;


-- Q4: Region-wise ranking — which city is worst/best within each region (window function: RANK)
WITH region_avg AS (
    SELECT region, city, ROUND(AVG(aqi), 1) AS avg_aqi
    FROM aqi_categorized
    GROUP BY region, city
),
ranked AS (
    SELECT
        region, city, avg_aqi,
        RANK() OVER (PARTITION BY region ORDER BY avg_aqi DESC) AS rnk_worst
    FROM region_avg
)
SELECT * FROM ranked ORDER BY region, rnk_worst;


-- Q5: Winter vs Monsoon comparison (seasonal impact)
SELECT
    city,
    ROUND(AVG(CASE WHEN CAST(strftime('%m', date) AS INTEGER) IN (11,12,1) THEN aqi END), 1) AS winter_avg_aqi,
    ROUND(AVG(CASE WHEN CAST(strftime('%m', date) AS INTEGER) IN (6,7,8,9) THEN aqi END), 1) AS monsoon_avg_aqi
FROM aqi_categorized
GROUP BY city
ORDER BY winter_avg_aqi DESC;


-- Q6: 7-day rolling average AQI for Delhi (smoothing noisy daily readings — window function)
SELECT
    date,
    aqi,
    ROUND(AVG(aqi) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS rolling_7day_avg
FROM aqi_categorized
WHERE city = 'Delhi'
ORDER BY date;
