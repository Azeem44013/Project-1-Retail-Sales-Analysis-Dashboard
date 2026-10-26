
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import re

# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "Superstore Sales Dataset.csv"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# 2. LOAD THE CSV
# This file uses semicolons and a non-UTF-8 encoding.
# --------------------------------------------------
df = pd.read_csv(
    INPUT_FILE,
    sep=";",
    encoding="latin1"
)

print("=" * 55)
print("RETAIL SALES PERFORMANCE ANALYSIS")
print("=" * 55)

print("\nOriginal dataset shape:", df.shape)
print("\nOriginal columns:")
print(df.columns.tolist())

# --------------------------------------------------
# 3. CLEAN COLUMN NAMES
# --------------------------------------------------
def clean_column_name(column):
    column = column.strip().lower()
    column = re.sub(r"[^a-z0-9]+", "_", column)
    return column.strip("_")

df.columns = [clean_column_name(c) for c in df.columns]

# --------------------------------------------------
# 4. CHECK DATA QUALITY
# --------------------------------------------------
missing_before = df.isnull().sum()
duplicates_before = df.duplicated().sum()

print("\nMissing values:")
print(missing_before[missing_before > 0])

print("\nExact duplicate rows:", duplicates_before)

# Remove exact duplicate records
df = df.drop_duplicates().copy()

# --------------------------------------------------
# 5. CLEAN TEXT FIELDS
# --------------------------------------------------
text_columns = df.select_dtypes(include="object").columns

for col in text_columns:
    df[col] = df[col].str.strip()

# --------------------------------------------------
# 6. CONVERT DATE COLUMNS
# Dates are in day/month/year format.
# --------------------------------------------------
for col in ["order_date", "ship_date"]:
    df[col] = pd.to_datetime(
        df[col],
        format="%d/%m/%Y",
        errors="coerce"
    )

# Convert postal code while preserving missing values
df["postal_code"] = pd.to_numeric(
    df["postal_code"],
    errors="coerce"
).astype("Int64")

# --------------------------------------------------
# 7. INSPECT SALES WITHOUT GUESSING ITS SCALE
# --------------------------------------------------
df["sales_raw"] = df["sales"]

# Remove currency symbols and commas for inspection only.
# Do NOT use this digit string as a valid sales amount.
df["sales_digits_unscaled"] = (
    df["sales_raw"]
    .astype("string")
    .str.replace(r"[$,\s]", "", regex=True)
)

sales_digits = df["sales_digits_unscaled"]

print("\nSales column sample:")
print(df[["sales_raw", "sales_digits_unscaled"]].head(10))

print("\nSales values that are not simple digit strings:",
      (~sales_digits.str.fullmatch(r"\d+", na=False)).sum())

print(
    "\nWARNING: Sales values appear to have lost decimal "
    "separators. Revenue totals are not calculated until "
    "the original numeric values are verified."
)

# --------------------------------------------------
# 8. REMOVE ROWS MISSING ESSENTIAL ANALYSIS FIELDS
# Postal code is not essential for overall analysis.
# --------------------------------------------------
required_columns = [
    "order_id",
    "order_date",
    "customer_id",
    "product_id",
    "category",
]

rows_before = len(df)

df = df.dropna(subset=required_columns).copy()

print("\nRows removed for missing essential fields:",
      rows_before - len(df))

# --------------------------------------------------
# 9. CREATE DATE ATTRIBUTES
# --------------------------------------------------
df["order_year"] = df["order_date"].dt.year
df["order_month"] = (
    df["order_date"].dt.to_period("M").astype(str)
)

# --------------------------------------------------
# 10. OVERALL BUSINESS COUNTS
# --------------------------------------------------
total_records = len(df)
total_orders = df["order_id"].nunique()
total_customers = df["customer_id"].nunique()
total_products = df["product_id"].nunique()
total_categories = df["category"].nunique()

print("\nOVERALL DATA SUMMARY")
print("-" * 40)
print("Order-line records:", f"{total_records:,}")
print("Unique orders:", f"{total_orders:,}")
print("Unique customers:", f"{total_customers:,}")
print("Unique products:", f"{total_products:,}")
print("Product categories:", total_categories)

# --------------------------------------------------
# 11. ORDER ACTIVITY BY CATEGORY
# --------------------------------------------------
category_activity = (
    df.groupby("category", as_index=False)
      .agg(
          order_lines=("order_id", "size"),
          unique_orders=("order_id", "nunique"),
          unique_products=("product_id", "nunique"),
          unique_customers=("customer_id", "nunique")
      )
      .sort_values("order_lines", ascending=False)
)

print("\nACTIVITY BY CATEGORY")
print(category_activity.to_string(index=False))

# --------------------------------------------------
# 12. ORDER ACTIVITY BY REGION
# --------------------------------------------------
region_activity = (
    df.groupby("region", as_index=False)
      .agg(
          order_lines=("order_id", "size"),
          unique_orders=("order_id", "nunique"),
          unique_customers=("customer_id", "nunique")
      )
      .sort_values("unique_orders", ascending=False)
)

print("\nACTIVITY BY REGION")
print(region_activity.to_string(index=False))

# --------------------------------------------------
# 13. MONTHLY ORDER TREND
# --------------------------------------------------
monthly_activity = (
    df.groupby("order_month", as_index=False)
      .agg(
          order_lines=("order_id", "size"),
          unique_orders=("order_id", "nunique"),
          unique_customers=("customer_id", "nunique")
      )
      .sort_values("order_month")
)

print("\nMONTHLY ORDER ACTIVITY")
print(monthly_activity.to_string(index=False))

# --------------------------------------------------
# 14. CUSTOMER SEGMENT ANALYSIS
# --------------------------------------------------
segment_activity = (
    df.groupby("segment", as_index=False)
      .agg(
          order_lines=("order_id", "size"),
          unique_orders=("order_id", "nunique"),
          unique_customers=("customer_id", "nunique")
      )
      .sort_values("unique_orders", ascending=False)
)

print("\nCUSTOMER SEGMENT ACTIVITY")
print(segment_activity.to_string(index=False))

# --------------------------------------------------
# 15. TOP PRODUCTS BY NUMBER OF ORDER LINES
# This is NOT a ranking by sales revenue.
# --------------------------------------------------
product_activity = (
    df.groupby(["product_id", "product_name"], as_index=False)
      .agg(
          order_lines=("order_id", "size"),
          unique_orders=("order_id", "nunique")
      )
      .sort_values("order_lines", ascending=False)
      .head(10)
)

print("\nTOP 10 PRODUCTS BY ORDER-LINE COUNT")
print(product_activity.to_string(index=False))

# --------------------------------------------------
# 16. EXPORT CLEANED DATA AND ANALYSIS TABLES
# --------------------------------------------------
df.to_csv(
    OUTPUT_DIR / "superstore_cleaned.csv",
    index=False
)

category_activity.to_csv(
    OUTPUT_DIR / "category_activity.csv", index=False
)

region_activity.to_csv(
    OUTPUT_DIR / "region_activity.csv", index=False
)

monthly_activity.to_csv(
    OUTPUT_DIR / "monthly_order_activity.csv", index=False
)

segment_activity.to_csv(
    OUTPUT_DIR / "segment_activity.csv", index=False
)

product_activity.to_csv(
    OUTPUT_DIR / "top_products_by_order_count.csv",
    index=False
)

# --------------------------------------------------
# 17. CHART: ORDER ACTIVITY BY CATEGORY
# --------------------------------------------------
plt.figure(figsize=(9, 5))
plt.bar(
    category_activity["category"],
    category_activity["unique_orders"]
)
plt.title("Unique Orders by Product Category")
plt.xlabel("Category")
plt.ylabel("Unique Orders")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "orders_by_category.png",
    dpi=300
)
plt.close()

# --------------------------------------------------
# 18. CHART: MONTHLY ORDER TREND
# --------------------------------------------------
plt.figure(figsize=(12, 5))
plt.plot(
    monthly_activity["order_month"],
    monthly_activity["unique_orders"],
    marker="o"
)
plt.title("Monthly Order Trend")
plt.xlabel("Order Month")
plt.ylabel("Unique Orders")
plt.xticks(rotation=60)
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "monthly_order_trend.png",
    dpi=300
)
plt.close()

# --------------------------------------------------
# 19. SAVE DATA-QUALITY REPORT
# --------------------------------------------------
quality_report = pd.DataFrame({
    "column": df.columns,
    "missing_values": [df[c].isna().sum() for c in df.columns],
    "data_type": [str(df[c].dtype) for c in df.columns]
})

quality_report.to_csv(
    OUTPUT_DIR / "data_quality_report.csv",
    index=False
)

print("\nAnalysis completed.")
print("Output folder:", OUTPUT_DIR)
print("Revenue analysis is pending Sales data validation.")
