# KPI Dashboard Project

An interactive Streamlit dashboard for analyzing retail sales data and generating business insights for decision-making.

## Problem Statement

Retail teams need a simple way to monitor performance, compare product categories, and spot customer behavior patterns without manually digging through raw CSV files. This project turns supermarket transaction data into a dashboard that supports faster, data-driven decisions.

## Project Structure

```text
kpi-dashboard-project/
+-- data/
|   +-- SuperMarket Analysis.csv
+-- app/
|   +-- app.py
+-- notebooks/
|   +-- exploration.ipynb
+-- src/
|   +-- data_processing.py
+-- requirements.txt
+-- README.md
+-- .gitignore
```

## Dataset Source

Use the Kaggle supermarket sales dataset and save it as `data/SuperMarket Analysis.csv` or `data/supermarket_sales.csv`.

Suggested source:
- https://www.kaggle.com/datasets/aungpyaeap/supermarket-sales

## KPIs Defined

- Revenue: Sum of the `Total` column
- Transactions: Number of rows in the filtered dataset
- Avg Rating: Mean customer rating
- Avg Basket Size: Mean quantity purchased per transaction
- Gross Income: Sum of gross income

## Features

- Sidebar filters for city, branch, product line, customer type, payment method, and date range
- KPI summary cards
- Revenue by product line chart
- Revenue by payment method chart
- Sales over time chart
- Auto-generated business insights
- Filtered data preview table

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Add the dataset to `data/SuperMarket Analysis.csv` or `data/supermarket_sales.csv`.

4. Run the app:

```powershell
streamlit run app/app.py
```

## Notebook Workflow

Use `notebooks/exploration.ipynb` to:

- Inspect null values
- Review data types
- Analyze distributions
- Validate the chosen KPIs before building visuals

## Example Resume Bullet

Designed and developed a KPI dashboard using Streamlit and Python, implementing a modular data processing pipeline and delivering insights on revenue trends, customer behavior, and product performance.

## Next Upgrades

- Add SQL integration with SQLite or PostgreSQL
- Add forecasting or trend analysis
- Add profit margin analysis
- Deploy on Streamlit Cloud
