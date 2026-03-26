# Health Insurance Charges Analysis - Power BI Dashboard

## Project Overview

This project presents an interactive Power BI dashboard analysing health insurance charges across 1,338 customers. The dashboard is designed to support insurance pricing decisions by surfacing key cost drivers such as smoking status, age, region, and BMI.

The dataset was sourced from Kaggle and contains individual-level insurance records including demographic and lifestyle attributes.

---

## Business Context

Insurance companies need to understand what factors drive higher claims in order to set accurate premiums and manage risk. This dashboard answers four core business questions:

- Do smokers incur significantly higher insurance charges than non-smokers?
- Which age groups represent the highest cost to insurers?
- Are there regional differences in average insurance charges?
- Does BMI correlate with higher charges, and does smoking amplify this effect?

---

## Dashboard Features

### Visuals
| Visual | Type | Key Insight |
|---|---|---|
| Smokers vs Non-Smokers | Horizontal bar chart | Smokers average 4x higher charges ($32K vs $8K) |
| Charges by Age Group | Column chart | Seniors (55+) have the highest average charges at $18.8K |
| Charges by Region | Horizontal bar chart | Southeast has the highest regional average at $15K |
| Charges by Gender | Pie chart | Males incur slightly higher charges (52.6% vs 47.4%) |
| BMI vs Charges | Scatter plot | Smokers form a distinct high-cost cluster regardless of BMI |

### Interactive Elements
- **Smoker slicer** - filters all visuals by smoking status
- **Region slicer** - filters all visuals by geographic region
- **KPI card** - displays the overall average insurance charge ($13.27K), fixed regardless of slicer selection

---

## Key Findings

1. **Smoking is the strongest cost driver.** Smokers pay on average $32K compared to $8K for non-smokers - a difference of 4x. This is the most significant predictor of high insurance charges in this dataset.

2. **Age has a clear positive relationship with charges.** Seniors (55+) average $18.8K, nearly double the charges of young customers (Under 25) at $9.1K.

3. **Regional variation exists but is moderate.** The Southeast has the highest average charges ($15K), while the Northwest and Southwest are lower at $12K each.

4. **Gender plays a minor role.** Males average slightly higher charges than females, but the difference is small compared to smoking status and age.

5. **BMI alone is not a reliable predictor.** The scatter plot reveals that non-smokers maintain relatively low charges across all BMI ranges, while smokers show high charges regardless of BMI - suggesting smoking status overrides the effect of BMI.

---

## Tools Used

- Power BI Desktop
- Data source: insurance.csv (Kaggle)
- Data transformation: Conditional column (age_group) created in Power Query

---

## Project Structure

```
BI_Health_Insurance/
├── Health Insurance Analysis.pbix
├── sql_analysis_results.xlsx
├── insurance.csv
└── README.md
```

---

## How to Use the Dashboard

1. Open `Health Insurance Analysis.pbix` in Power BI Desktop
2. Use the **smoker slicer** on the right to filter by smoking status
3. Use the **region slicer** to filter by geographic region
4. Both slicers can be combined to explore specific segments
5. The KPI card always displays the global average for reference