import pandas as pd
import numpy as np


# Dataset Load
df = pd.read_excel('data/raw/4G_KPI.xlsx')
print(df.head())

# Generate statistical summary
summary = df.describe(include=[np.number]).transpose().round(2)
print(summary)

# Columns
colonnes = df.columns.tolist()
print(colonnes)


# ----------- Data cleaning -----------

def clean_data(df):
    """
    - Applies a basic cleanup to the DataFrame
    - Removes duplicates
    - Keeps rows and columns with at least 1 non-zero value
    - Replaces decimal commas with periods
    - Deletes % symbols
    - Converts object columns to float if possible
    - Removes rows with "/0" values in numeric columns

    Args:
        df (pd.DataFrame)

    Returns:
        df_clean (pd.DataFrame)
    """
    df_clean = df.copy()

    # Deleting duplicates
    df_clean.drop_duplicates()

    # Delete rows and columns if all values are missing
    df_clean = df_clean.dropna(axis='columns', how='all')

    # First identify which columns should be numeric (exclude obvious non-numeric columns)
    non_numeric_cols = ['Date', 'eNodeB Name', 'eNodeB Function Name', 'Cell Name', 'Cell FDD TDD Indication']
    numeric_cols = [col for col in df_clean.columns if col not in non_numeric_cols]

    # Remove rows with "/0" in numeric columns before conversion
    for col in numeric_cols:
        if df_clean[col].dtype == 'object':
            # Remove rows with "/0"
            mask = df_clean[col].astype(str).str.contains('/0', regex=False)
            df_clean = df_clean[~mask]

    for col in df_clean.columns :
        if df_clean[col].dtype == 'object':
            
            # Replacing decimal commas with periods and deleting %
            df_clean[col] = (
                df_clean[col]
                .astype(str)
                .str.replace(',', '.', regex=False)
                .str.replace('%', '', regex=False)
                .str.replace(' ', '', regex=False)
                .replace('', np.nan)
            )

            # Converting object columns to float
            try:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='raise')
            except ValueError as e:
                print(f"Could not convert column {col} to numeric: {e}")
                # Keep original if conversion fails
                df_clean[col] = df_clean[col]

    return df_clean

# ----------- KPIs in the dataset -----------

def summarize_kpis(df, exclude_columns=None):
    """
    Calculates descriptive statistics for numeric columns (KPIs) in DataFrame.

    Args:
        df (pd.DataFrame)
        exclude_columns (list) : columns not to be included (e.g. ['Date', 'Site'])

    Returns:
        summary_df (pd.DataFrame) : statistical summary (mean, std, min, max, NaN count, etc.).
    """
    if exclude_columns is None:
        exclude_columns = []

    # Numerical columns for analysis
    numeric_cols = df.select_dtypes(include=['float', 'int']).columns
    numeric_cols = [col for col in numeric_cols if col not in exclude_columns]

    summary_data = []
    for col in numeric_cols:
        summary_data.append({
            "KPI": col,
            "Mean": df[col].mean(),
            "Std": df[col].std(),
            "Min": df[col].min(),
            "Max": df[col].max(),
            "Missing Values": df[col].isna().sum(),
            "Count": df[col].count(),
            "Unique Values": df[col].nunique()
        })

    summary_df = pd.DataFrame(summary_data)
    summary_df.sort_values("Missing Values", ascending=False, inplace=True)

    return summary_df

# Cleaning
df_clean = clean_data(df)
# Columns not to be included
exclude_columns = ['Date', 'eNodeB Name', 'eNodeB Function Name', 'Cell Name', 'LocalCell Id', 'Cell FDD TDD Indication', 'Integrity', 'Average Nb of Users', 'Active User']
# Statistical summary of KPIs
summary_df = summarize_kpis(df_clean, exclude_columns)
print(summary_df)

# Save cleaned data
with pd.ExcelWriter("data/cleaned_kpis.xlsx") as writer:
    df_clean.to_excel(writer, sheet_name="4G_KPIs", index=False)
