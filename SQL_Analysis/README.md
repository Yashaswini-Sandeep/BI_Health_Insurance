# Insurance Data - SQL Analysis

## Project Overview
Health insurance companies face a core business challenge: accurately predicting 
how much a customer is likely to cost them in medical expenses. Charge too little 
in premiums and the company loses money. Charge too much and customers leave.

This project uses SQL to analyse a real-world health insurance dataset of 1,338 
customers to uncover which factors — age, BMI, smoking status, region, and family 
size — have the strongest influence on annual medical charges.

The analysis simulates the kind of exploratory data work a Business Intelligence 
team at an insurance company would perform to support pricing decisions, risk 
segmentation, and regional strategy.

## Business Questions Answered
1. Which region generates the highest insurance charges?
2. How much does smoking impact the cost of insurance?
3. Do older customers cost significantly more than younger ones?
4. Who are the highest-risk customers in each region?
5. Does having children or being a certain gender affect charges?

## Project Structure

SQL_Analysis/
├── data/                          # Raw dataset (not uploaded to GitHub)
├── outputs/
│   └── sql_analysis_results.xlsx  # All query results exported to Excel
├── queries/
│   └── analysis.sql               # All SQL queries in plain .sql file
├── insurance_analysis.ipynb       # Main Jupyter Notebook
└── README.md                      # Project documentation


## Dataset
- Source: Kaggle - Medical Cost Personal Dataset
- Link: https://www.kaggle.com/datasets/mirichoi0218/insurance
- Size: 1,338 records
- Columns: age, sex, bmi, children, smoker, region, charges

## Analysis Performed

| Query | Analysis | SQL Concepts Used |
|-------|----------|-------------------|
| 1 | Total and Average Charges by Region | GROUP BY, SUM, AVG, COUNT, ROUND |
| 2 | Smokers vs Non-Smokers Comparison | GROUP BY, MIN, MAX |
| 3 | Top 10 Highest Claims | ORDER BY, LIMIT |
| 4 | Charges by Age Group | CASE WHEN |
| 5 | Top 3 Customers per Region | Window Functions, RANK(), Subquery |
| 6 | Impact of Number of Children | GROUP BY on numerical variable |
| 7 | Gender Based Analysis | Multi-metric comparison |
| 8 | Combined Risk Profile | Multi-dimensional GROUP BY |

## Key Insights
1. Smoking is the single biggest cost driver - smokers pay nearly 4x more ($32,050 vs $8,434)
2. Southeast is the most expensive region - highest total and average charges
3. Age increases charges steadily - seniors pay 2x more than young customers
4. Every single top 10 highest claim belongs to a smoker, without exception
5. Males pay slightly more than females ($13,956 vs $12,569)

## Tools Used
- Python 3
- Pandas
- SQLite3
- Jupyter Notebook

## How to Run
1. Clone this repository
2. Download the dataset from Kaggle and place it in the data/ folder
3. Open insurance_analysis.ipynb in Jupyter Notebook
4. Run all cells from top to bottom

## Author
Yashaswini Sandeep
