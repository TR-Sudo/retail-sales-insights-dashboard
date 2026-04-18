from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.data_processing import (  # noqa: E402
    calculate_kpis,
    filter_data,
    generate_insights,
    get_filter_options,
    load_data,
    sales_by_payment,
    sales_by_product,
    sales_over_time,
)


st.set_page_config(
    page_title="Retail KPI Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def draw_bar_chart(data: pd.DataFrame, x_col: str, y_col: str, title: str, color: str):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(data[x_col], data[y_col], color=color)
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel(y_col)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    st.pyplot(fig)


def draw_line_chart(data: pd.DataFrame, x_col: str, y_col: str, title: str, color: str):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(data[x_col], data[y_col], color=color, linewidth=2.5)
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel(y_col)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    st.pyplot(fig)


st.title("Retail Sales KPI Dashboard")
st.caption(
    "Interactive business dashboard for tracking revenue trends, customer behavior, and product performance."
)

try:
    df = load_data()
except FileNotFoundError as error:
    st.error(str(error))
    st.info(
        "Place the Kaggle supermarket sales CSV in `data/SuperMarket Analysis.csv` or `data/supermarket_sales.csv` and rerun the app."
    )
    st.stop()

filter_options = get_filter_options(df)

st.sidebar.header("Filters")

city = st.sidebar.multiselect("City", filter_options.get("City", []))
branch = st.sidebar.multiselect("Branch", filter_options.get("Branch", []))
product_line = st.sidebar.multiselect("Product Line", filter_options.get("Product line", []))
payment = st.sidebar.multiselect("Payment Method", filter_options.get("Payment", []))
customer_type = st.sidebar.multiselect(
    "Customer Type", filter_options.get("Customer type", [])
)

date_range = None
if "Date" in df.columns and not df["Date"].dropna().empty:
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    selected_dates = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        date_range = (
            pd.to_datetime(selected_dates[0]),
            pd.to_datetime(selected_dates[1]),
        )

filtered_df = filter_data(
    df,
    city=city,
    branch=branch,
    product_line=product_line,
    payment=payment,
    customer_type=customer_type,
    date_range=date_range,
)

kpis = calculate_kpis(filtered_df)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Revenue", format_currency(kpis["Revenue"]))
col2.metric("Transactions", f"{kpis['Transactions']:,}")
col3.metric("Avg Rating", f"{kpis['Avg Rating']:.2f}")
col4.metric("Avg Basket Size", f"{kpis['Avg Basket Size']:.2f}")
col5.metric("Gross Income", format_currency(kpis["Gross Income"]))

st.divider()

chart_col1, chart_col2 = st.columns(2)

product_sales = sales_by_product(filtered_df)
with chart_col1:
    st.subheader("Sales by Product Line")
    if not product_sales.empty:
        draw_bar_chart(
            product_sales,
            "Product line",
            "Total",
            "Revenue by Product Line",
            "#2A9D8F",
        )
    else:
        st.warning("No product sales data available for the selected filters.")

payment_sales = sales_by_payment(filtered_df)
with chart_col2:
    st.subheader("Sales by Payment Method")
    if not payment_sales.empty:
        draw_bar_chart(
            payment_sales,
            "Payment",
            "Total",
            "Revenue by Payment Method",
            "#E76F51",
        )
    else:
        st.warning("No payment data available for the selected filters.")

time_sales = sales_over_time(filtered_df)
st.subheader("Sales Over Time")
if not time_sales.empty:
    draw_line_chart(time_sales, "Date", "Total", "Daily Revenue Trend", "#264653")
else:
    st.warning("No time-series sales data available for the selected filters.")

st.subheader("Business Insights")
for insight in generate_insights(filtered_df):
    st.write(f"- {insight}")

st.subheader("Filtered Data Preview")
st.dataframe(filtered_df, use_container_width=True)
