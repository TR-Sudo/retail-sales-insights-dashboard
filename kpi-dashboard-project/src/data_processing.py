from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DEFAULT_DATA_FILES = [
    DATA_DIR / "SuperMarket Analysis.csv",
    DATA_DIR / "supermarket_sales.csv",
]


def resolve_data_path(file_path: str | Path | None = None) -> Path:
    """Find the dataset path, supporting the common project filenames."""
    if file_path is not None:
        path = Path(file_path)
        if path.exists():
            return path
        raise FileNotFoundError(f"Dataset not found at '{path}'.")

    for candidate in DEFAULT_DATA_FILES:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Dataset not found. Add `SuperMarket Analysis.csv` or `supermarket_sales.csv` to the data folder."
    )


def load_data(file_path: str | Path | None = None) -> pd.DataFrame:
    """Load and normalize the supermarket sales dataset."""
    path = resolve_data_path(file_path)

    df = pd.read_csv(path)
    df.columns = [column.strip() for column in df.columns]

    if "Sales" in df.columns and "Total" not in df.columns:
        df["Total"] = pd.to_numeric(df["Sales"], errors="coerce")

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    numeric_columns = [
        "Unit price",
        "Quantity",
        "Tax 5%",
        "Total",
        "cogs",
        "gross margin percentage",
        "gross income",
        "Rating",
    ]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    if "Month" not in df.columns and "Date" in df.columns:
        df["Month"] = df["Date"].dt.to_period("M").astype(str)

    if "Hour" not in df.columns and "Time" in df.columns:
        df["Hour"] = pd.to_datetime(
            df["Time"], format="%I:%M:%S %p", errors="coerce"
        ).dt.hour

    return df


def get_filter_options(df: pd.DataFrame) -> dict[str, list[Any]]:
    """Return sorted filter values for Streamlit controls."""
    options: dict[str, list[Any]] = {}
    filter_columns = ["Branch", "City", "Gender", "Customer type", "Product line", "Payment"]
    for column in filter_columns:
        if column in df.columns:
            values = sorted(value for value in df[column].dropna().unique().tolist())
            options[column] = values
    return options


def filter_data(
    df: pd.DataFrame,
    city: list[str] | None = None,
    branch: list[str] | None = None,
    product_line: list[str] | None = None,
    payment: list[str] | None = None,
    customer_type: list[str] | None = None,
    date_range: tuple[pd.Timestamp, pd.Timestamp] | None = None,
) -> pd.DataFrame:
    """Apply dashboard filters and return a filtered copy."""
    filtered_df = df.copy()

    mapping = {
        "City": city,
        "Branch": branch,
        "Product line": product_line,
        "Payment": payment,
        "Customer type": customer_type,
    }
    for column, selected_values in mapping.items():
        if column in filtered_df.columns and selected_values:
            filtered_df = filtered_df[filtered_df[column].isin(selected_values)]

    if date_range and "Date" in filtered_df.columns:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            filtered_df["Date"].between(
                pd.to_datetime(start_date), pd.to_datetime(end_date)
            )
        ]

    return filtered_df


def calculate_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Calculate summary metrics displayed in KPI cards."""
    revenue = float(df["Total"].sum()) if "Total" in df.columns else 0.0
    transactions = int(len(df))
    average_rating = float(df["Rating"].mean()) if "Rating" in df.columns else 0.0
    avg_basket_size = float(df["Quantity"].mean()) if "Quantity" in df.columns else 0.0
    gross_income = float(df["gross income"].sum()) if "gross income" in df.columns else 0.0

    return {
        "Revenue": revenue,
        "Transactions": transactions,
        "Avg Rating": average_rating,
        "Avg Basket Size": avg_basket_size,
        "Gross Income": gross_income,
    }


def sales_by_product(df: pd.DataFrame) -> pd.DataFrame:
    if {"Product line", "Total"}.issubset(df.columns):
        result = (
            df.groupby("Product line", as_index=False)["Total"]
            .sum()
            .sort_values("Total", ascending=False)
        )
        return result
    return pd.DataFrame(columns=["Product line", "Total"])


def sales_over_time(df: pd.DataFrame) -> pd.DataFrame:
    if {"Date", "Total"}.issubset(df.columns):
        result = (
            df.dropna(subset=["Date"])
            .groupby("Date", as_index=False)["Total"]
            .sum()
            .sort_values("Date")
        )
        return result
    return pd.DataFrame(columns=["Date", "Total"])


def sales_by_payment(df: pd.DataFrame) -> pd.DataFrame:
    if {"Payment", "Total"}.issubset(df.columns):
        result = (
            df.groupby("Payment", as_index=False)["Total"]
            .sum()
            .sort_values("Total", ascending=False)
        )
        return result
    return pd.DataFrame(columns=["Payment", "Total"])


def generate_insights(df: pd.DataFrame) -> list[str]:
    """Create lightweight business insights from the filtered dataset."""
    if df.empty:
        return ["No records match the current filters."]

    insights: list[str] = []

    if {"Product line", "Total"}.issubset(df.columns):
        top_product = (
            df.groupby("Product line")["Total"].sum().sort_values(ascending=False).head(1)
        )
        if not top_product.empty:
            insights.append(
                f"Top product line: {top_product.index[0]} generated ${top_product.iloc[0]:,.2f}."
            )

    if {"Payment", "Total"}.issubset(df.columns):
        top_payment = (
            df.groupby("Payment")["Total"].sum().sort_values(ascending=False).head(1)
        )
        if not top_payment.empty:
            insights.append(
                f"Most valuable payment method: {top_payment.index[0]} with ${top_payment.iloc[0]:,.2f} in sales."
            )

    if "Rating" in df.columns:
        insights.append(f"Average customer rating is {df['Rating'].mean():.2f}/10.")

    if {"Date", "Total"}.issubset(df.columns):
        daily_sales = df.groupby("Date")["Total"].sum()
        if not daily_sales.empty:
            best_day = daily_sales.sort_values(ascending=False).head(1)
            insights.append(
                f"Peak sales day: {best_day.index[0].strftime('%Y-%m-%d')} reached ${best_day.iloc[0]:,.2f}."
            )

    return insights
