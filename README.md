# BI Health Insurance - Portfolio Project

## Project Overview
An end-to-end Business Intelligence project analysing health insurance charges across 1,338 customers. 
The goal is to identify key cost drivers such as smoking status, age, BMI, and region to support 
insurance pricing decisions.

The dataset was sourced from Kaggle and contains individual-level insurance records including 
demographic and lifestyle attributes.

---

## Repository Structure

### Dashboard/
Interactive Power BI dashboard built to visualise health insurance charges.
- Smoker vs Non-Smoker analysis
- Charges by age group and region
- BMI vs charges scatter plot
- Gender breakdown
- Interactive slicers for smoker status and region

### SQL_Analysis/
SQL-based exploratory data analysis on the insurance dataset.
- 8 analytical queries covering key business questions
- Jupyter Notebook with full analysis walkthrough
- Query outputs exported to Excel

### Python_Report/
Automated PDF report generator built with Python.
- Reads insurance.csv and generates a professional multi-page BI report
- Covers all key findings: smoking, age, region, BMI, gender
- Built with pandas, matplotlib and reportlab

---

## Tools & Technologies
- **Power BI** — Dashboard and visualisations
- **SQL / SQLite** — Data querying and analysis
- **Python** — Automated report generation
- **Libraries** — pandas, matplotlib, reportlab