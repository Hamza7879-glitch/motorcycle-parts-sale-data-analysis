import pandas as pd
import numpy as np

# Load data
df = pd.read_excel("Motorcycle_Parts_Sales_RAW_Unclean.xlsx")

# Remove completely blank rows
df = df.dropna(how="all")

# Remove duplicate rows
df = df.drop_duplicates()

# Clean column names
df.columns = df.columns.str.strip()
df.columns = df.columns.str.replace(" ", "_")

# Text columns
text_columns = [
    "Customer_Name",
    "City",
    "Province",
    "Motorcycle_Model",
    "Brand",
    "Part_Name",
    "Category",
    "Supplier",
    "Payment_Mode",
    "Sales_Channel",
    "Order_Status"
]

for col in text_columns:
    df[col] = df[col].astype("string").str.strip()

# Standardize text
df["Customer_Name"] = df["Customer_Name"].str.title()
df["City"] = df["City"].str.title()
df["Supplier"] = df["Supplier"].str.title()
df["Part_Name"] = df["Part_Name"].str.title()

# Fix cities
city_mapping = {
    "Lahor": "Lahore",
    "Islamabd": "Islamabad",
    "Rawal Pindi": "Rawalpindi",
    "Faislabad": "Faisalabad",
    "Gujranwla": "Gujranwala"
}

df["City"] = df["City"].replace(city_mapping)

# Clean phone
df["Phone"] = (
    df["Phone"]
    .astype("string")
    .str.replace(r"[\s\-\+]", "", regex=True)
)

# Dates
df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce",
    dayfirst=True
)

df["Delivery_Date"] = pd.to_datetime(
    df["Delivery_Date"],
    errors="coerce",
    dayfirst=True
)

# Quantity
df["Quantity"] = (
    df["Quantity"]
    .astype("string")
    .str.extract(r"(\d+\.?\d*)")[0]
)

df["Quantity"] = pd.to_numeric(
    df["Quantity"],
    errors="coerce"
)

# Remove invalid quantities
df.loc[df["Quantity"] < 0, "Quantity"] = np.nan
df["Quantity"] = df["Quantity"].fillna(
    df["Quantity"].median()
)

# Prices
for col in ["Unit_Price_PKR", "Unit_Cost_PKR"]:
    df[col] = (
        df[col]
        .astype("string")
        .str.replace("PKR", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# Fix zero prices
df.loc[df["Unit_Price_PKR"] <= 0, "Unit_Price_PKR"] = np.nan

df["Unit_Price_PKR"] = df["Unit_Price_PKR"].fillna(
    df["Unit_Price_PKR"].median()
)

# Discount
df["Discount_Percent"] = (
    df["Discount_Percent"]
    .astype("string")
    .str.replace("%", "", regex=False)
    .str.strip()
)

df["Discount_Percent"] = pd.to_numeric(
    df["Discount_Percent"],
    errors="coerce"
)

# Invalid discount
df.loc[
    (df["Discount_Percent"] < 0) |
    (df["Discount_Percent"] > 100),
    "Discount_Percent"
] = np.nan

df["Discount_Percent"] = df["Discount_Percent"].fillna(0)

# Status
status_mapping = {
    "delivered": "Delivered",
    "DELIVERED": "Delivered",
    "Deliverd": "Delivered",
    "Pending ": "Pending",
    "Cancelled ": "Cancelled",
    "Return": "Returned"
}

df["Order_Status"] = df["Order_Status"].replace(status_mapping)

# Sales channel
channel_mapping = {
    "online": "Online",
    "ONLINE": "Online",
    "Retail": "Retail Store",
    "Retail Store ": "Retail Store",
    "Wholesale ": "Wholesale"
}

df["Sales_Channel"] = df["Sales_Channel"].replace(channel_mapping)

# Missing categorical values
df["Payment_Mode"] = df["Payment_Mode"].fillna("Unknown")
df["Supplier"] = df["Supplier"].fillna("Unknown")
df["Customer_Name"] = df["Customer_Name"].fillna("Unknown")

# Recalculate sales
df["Gross_Sales_PKR"] = (
    df["Quantity"] *
    df["Unit_Price_PKR"]
)

df["Discount_Amount_PKR"] = (
    df["Gross_Sales_PKR"] *
    df["Discount_Percent"] / 100
)

df["Net_Sales_PKR"] = (
    df["Gross_Sales_PKR"] -
    df["Discount_Amount_PKR"]
)

# Recalculate cost
df["Total_Cost_PKR"] = (
    df["Quantity"] *
    df["Unit_Cost_PKR"]
)

# Recalculate profit
df["Profit_PKR"] = (
    df["Net_Sales_PKR"] -
    df["Total_Cost_PKR"]
)

# Date features
df["Month"] = df["Order_Date"].dt.month_name()
df["Month_Number"] = df["Order_Date"].dt.month
df["Year_Month"] = df["Order_Date"].dt.to_period("M").astype(str)
df["Quarter"] = "Q" + df["Order_Date"].dt.quarter.astype(str)
df["Day_Name"] = df["Order_Date"].dt.day_name()

# Final checks
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Duplicate Rows:", df.duplicated().sum())
print("\nMissing Values:")
print(df.isnull().sum())

# Save
df.to_excel(
    "Motorcycle_Parts_Sales_Cleaned.xlsx",
    index=False
)

print("\nCleaning completed successfully!")
print("File saved as: Motorcycle_Parts_Sales_Cleaned.xlsx")