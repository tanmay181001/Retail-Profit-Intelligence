
import pandas as pd
from pathlib import Path

# Locate the main project folder
project_folder = Path(__file__).resolve().parent.parent

# Locate the Excel dataset
file_path = project_folder / "data" / "raw" / "superstore raw data.xlsx"

# Read the Orders worksheet
df = pd.read_excel(file_path, sheet_name="Orders")

# Display the first five rows
print(df.head())

# Display the dataset dimensions
print("Dataset shape:", df.shape)

# Check missing values in every column
print("\nMissing values:")
print(df.isnull().sum())

# Check duplicate rows
print("\nDuplicate rows:", df.duplicated().sum())

# Check column data types
print("\nColumn data types:")
print(df.dtypes)

# Check invalid sales and quantities
print("\nSales less than or equal to zero:",
      (df["Sales"] <= 0).sum())

print("Quantity less than or equal to zero:",
      (df["Quantity"] <= 0).sum())

# Check invalid discounts
print("Discounts outside 0 to 1:",
      ((df["Discount"] < 0) | (df["Discount"] > 1)).sum())

# Check shipping date errors
print("Shipping before order date:",
      (df["Ship Date"] < df["Order Date"]).sum())

# Identify loss-making transactions
print("Transactions with negative profit:",
      (df["Profit"] < 0).sum())

# Calculate overall business performance
print("\nTotal Sales:", round(df["Sales"].sum(), 2))
print("Total Profit:", round(df["Profit"].sum(), 2))

profit_margin = (
    df["Profit"].sum() / df["Sales"].sum()
) * 100

print("Overall Profit Margin:", round(profit_margin, 2), "%")

# Analyze sales and profit by product category
category_analysis = df.groupby("Category").agg(
    Total_Sales=("Sales", "sum"),
    Total_Profit=("Profit", "sum"),
    Transactions=("Row ID", "count")
)

# Calculate profit margin for each category
category_analysis["Profit_Margin"] = (
    category_analysis["Total_Profit"]
    / category_analysis["Total_Sales"]
) * 100

# Round results to two decimal places
category_analysis = category_analysis.round(2)

print("\nCATEGORY PROFITABILITY ANALYSIS")
print(category_analysis.to_string())

# Analyze profitability by subcategory
subcategory_analysis = df.groupby(
    ["Category", "Sub-Category"]
).agg(
    Total_Sales=("Sales", "sum"),
    Total_Profit=("Profit", "sum"),
    Transactions=("Row ID", "count")
)

# Calculate profit margin
subcategory_analysis["Profit_Margin"] = (
    subcategory_analysis["Total_Profit"]
    / subcategory_analysis["Total_Sales"]
) * 100

# Sort from lowest to highest profit
subcategory_analysis = subcategory_analysis.sort_values(
    by="Total_Profit",
    ascending=True
)

print("\nSUBCATEGORY PROFITABILITY ANALYSIS")
print(subcategory_analysis.round(2).to_string())

# Create discount groups for analysis
df["Discount_Group"] = pd.cut(
    df["Discount"],
    bins=[-0.01, 0, 0.2, 0.4, 0.6, 1.0],
    labels=[
        "No Discount",
        "1-20%",
        "21-40%",
        "41-60%",
        "Above 60%"
    ]
)

# Analyze sales and profit by discount group
discount_analysis = df.groupby(
    "Discount_Group", observed=True
).agg(
    Total_Sales=("Sales", "sum"),
    Total_Profit=("Profit", "sum"),
    Transactions=("Row ID", "count"),
    Average_Discount=("Discount", "mean")
)

# Calculate profit margin
discount_analysis["Profit_Margin"] = (
    discount_analysis["Total_Profit"]
    / discount_analysis["Total_Sales"]
) * 100

# Calculate percentage of loss-making transactions
loss_rate = df.groupby(
    "Discount_Group", observed=True
)["Profit"].apply(
    lambda x: (x < 0).mean() * 100
)

discount_analysis["Loss_Rate"] = loss_rate

print("\nDISCOUNT PROFITABILITY ANALYSIS")
print(discount_analysis.round(2).to_string())

# Focus on the two loss-making Furniture subcategories
furniture_losses = df[
    df["Sub-Category"].isin(["Tables", "Bookcases"])
].copy()

# Compare discount groups within each subcategory
furniture_discount_analysis = furniture_losses.groupby(
    ["Sub-Category", "Discount_Group"],
    observed=True
).agg(
    Total_Sales=("Sales", "sum"),
    Total_Profit=("Profit", "sum"),
    Transactions=("Row ID", "count")
)

# Calculate profitability
furniture_discount_analysis["Profit_Margin"] = (
    furniture_discount_analysis["Total_Profit"]
    / furniture_discount_analysis["Total_Sales"]
) * 100

# Calculate loss-making order-line rate
furniture_discount_analysis["Loss_Rate"] = (
    furniture_losses.groupby(
        ["Sub-Category", "Discount_Group"],
        observed=True
    )["Profit"].apply(
        lambda x: (x < 0).mean() * 100
    )
)

print("\nFURNITURE DISCOUNT ANALYSIS")
print(furniture_discount_analysis.round(2).to_string())

# STEP 17: Export validated data for Power BI

# Create a copy to preserve the original dataset
clean_df = df.copy()

# Add useful business reporting columns
clean_df["Order_Year"] = clean_df["Order Date"].dt.year
clean_df["Order_Month"] = clean_df["Order Date"].dt.month
clean_df["Order_YearMonth"] = (
    clean_df["Order Date"].dt.strftime("%Y-%m")
)

# Calculate shipping duration in days
clean_df["Shipping_Days"] = (
    clean_df["Ship Date"] - clean_df["Order Date"]
).dt.days

# Flag loss-making transaction lines
clean_df["Loss_Flag"] = (
    clean_df["Profit"] < 0
).astype(int)

# Create output directory
output_folder = project_folder / "data" / "processed"
output_folder.mkdir(parents=True, exist_ok=True)

# Export data
output_file = output_folder / "superstore_clean.csv"
clean_df.to_csv(output_file, index=False)

print("\nPOWER BI DATA EXPORT COMPLETE")
print("File saved to:", output_file)
print("Rows exported:", len(clean_df))
print("Columns exported:", len(clean_df.columns))

