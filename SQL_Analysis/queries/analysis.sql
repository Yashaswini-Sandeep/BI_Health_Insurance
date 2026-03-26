
-- Query 1: Total and Average Charges by Region
SELECT 
    region,
    COUNT(*) AS total_customers,
    ROUND(AVG(charges), 2) AS avg_charge,
    ROUND(SUM(charges), 2) AS total_charges
FROM insurance
GROUP BY region
ORDER BY total_charges DESC;

-- Query 2: Smokers vs Non-Smokers
SELECT
    smoker,
    COUNT(*) AS total_customers,
    ROUND(AVG(bmi), 2) AS avg_bmi,
    ROUND(AVG(charges), 2) AS avg_charges,
    ROUND(MIN(charges), 2) AS min_charges,
    ROUND(MAX(charges), 2) AS max_charges
FROM insurance
GROUP BY smoker
ORDER BY avg_charges DESC;

-- Query 3: Top 10 Highest Claims
SELECT
    age, sex, bmi, smoker, region,
    ROUND(charges, 2) AS charges
FROM insurance
ORDER BY charges DESC
LIMIT 10;

-- Query 4: Charges by Age Group
SELECT
    CASE 
        WHEN age < 25 THEN 'Young (Under 25)'
        WHEN age BETWEEN 25 AND 40 THEN 'Adult (25-40)'
        WHEN age BETWEEN 41 AND 55 THEN 'Middle Aged (41-55)'
        ELSE 'Senior (55+)'
    END AS age_group,
    COUNT(*) AS total_customers,
    ROUND(AVG(charges), 2) AS avg_charges,
    ROUND(SUM(charges), 2) AS total_charges
FROM insurance
GROUP BY age_group
ORDER BY avg_charges DESC;

-- Query 5: Top 3 Customers per Region (Window Function)
SELECT * FROM (
    SELECT
        age, sex, region,
        ROUND(charges, 2) AS charges,
        RANK() OVER (
            PARTITION BY region 
            ORDER BY charges DESC
        ) AS rank_in_region
    FROM insurance
)
WHERE rank_in_region <= 3
ORDER BY region, rank_in_region;

-- Query 6: Impact of Number of Children
SELECT
    children,
    COUNT(*) AS total_customers,
    ROUND(AVG(charges), 2) AS avg_charges,
    ROUND(AVG(bmi), 2) AS avg_bmi
FROM insurance
GROUP BY children
ORDER BY children ASC;

-- Query 7: Gender Analysis
SELECT
    sex,
    COUNT(*) AS total_customers,
    ROUND(AVG(charges), 2) AS avg_charges,
    ROUND(AVG(bmi), 2) AS avg_bmi,
    ROUND(AVG(age), 2) AS avg_age
FROM insurance
GROUP BY sex
ORDER BY avg_charges DESC;

-- Query 8: Combined Risk Profile
SELECT
    region,
    smoker,
    CASE 
        WHEN age < 25 THEN 'Young'
        WHEN age BETWEEN 25 AND 40 THEN 'Adult'
        WHEN age BETWEEN 41 AND 55 THEN 'Middle Aged'
        ELSE 'Senior'
    END AS age_group,
    COUNT(*) AS total_customers,
    ROUND(AVG(charges), 2) AS avg_charges
FROM insurance
GROUP BY region, smoker, age_group
ORDER BY avg_charges DESC
LIMIT 10;
