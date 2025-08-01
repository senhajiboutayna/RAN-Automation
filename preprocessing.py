import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Dataset Load
df = pd.read_excel('data/4G_KPI.xlsx')
print(df.head())

# Generate statistical summary
summary = df.describe(include=[np.number]).transpose().round(2)
print(summary)

# Columns
colonnes = df.columns.tolist()
print(colonnes)

def clean_data(df):
    """
    Route to the correct cleaning function based on the detected columns.
    """
    columns = df.columns

    if 'eNodeB Name' in columns and 'Cell Name' in columns and 'LocalCell Id' in columns:
        return clean_data1(df)  # Nettoyage classique
    elif 'Time' in columns and 'Game time' in columns and 'Sector' in columns:
        return clean_data2(df)  # Nouveau format détecté (ex: Stade)
    else:
        raise ValueError("Structure du fichier non reconnue. Ajoutez une nouvelle fonction de nettoyage.")

# ----------- Data cleaning 1-----------

def clean_data1(df):
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


def clean_data2(df):
    df_clean = df.copy()

    df_clean = df_clean.drop_duplicates()
    df_clean = df_clean.dropna(axis='columns', how='all')

    # First identify which columns should be numeric (exclude obvious non-numeric columns)
    non_numeric_cols = ['Time', 'Game time', 'eNodeB Name', 'Cell Name', 'Cell FDD TDD Indication', 'Cell Name', 'sector', 'Beam', 'LocalCell Id', 'eNodeB Function Name', 'Frequency band', 'LTECell Tx and Rx Mode', 'eNodeB identity']
    numeric_cols = [col for col in df_clean.columns if col not in non_numeric_cols]

    # Remove rows with "/0" in numeric columns before conversion
    for col in numeric_cols:
        if df_clean[col].dtype == 'object':
            # Remove rows with "/0"
            mask = df_clean[col].astype(str).str.contains('/0', regex=False)
            df_clean = df_clean[~mask]

    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            df_clean[col] = (
                df_clean[col]
                .astype(str)
                .str.replace(',', '.', regex=False)
                .str.replace('%', '', regex=False)
                .str.replace(' ', '', regex=False)
                .replace('', np.nan)
            )
            try:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='raise')
            except ValueError:
                pass  # Keep as-is if not convertible

    # Standardiser les noms de colonnes si nécessaire
    if 'Time' in df_clean.columns:
        df_clean = df_clean.rename(columns={'Time': 'Date'})

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

# ----------- Time aggregation : daily average KPIs -----------
def aggregate_by_day(df, date_column='Date', exclude_columns=None):
    """
    Aggregates KPIs numerically by day.

    Args:
        df (pd.DataFrame)
        date_column (str): name of the date column
        exclude_columns (list): columns to be excluded

    Returns:
        df_daily (pd.DataFrame) : daily average KPIs
    """
    if exclude_columns is None:
        exclude_columns = []

    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    df = df.dropna(subset=[date_column])  # supprime les dates invalides

    numeric_cols = df.select_dtypes(include=['float', 'int']).columns
    numeric_cols = [col for col in numeric_cols if col not in exclude_columns]

    df_daily = df.groupby(df[date_column].dt.date)[numeric_cols].mean()
    df_daily.index = pd.to_datetime(df_daily.index)

    return df_daily


# ----------- Daily average by site -----------
def aggregate_by_site_and_day(df, site_col='eNodeB Name', date_col='Date', exclude_columns=None):
    """
    Aggregates data by site and day

    Args:
        df (pd.DataFrame)
        site_col (str): name of the site column
        date_col (str): name of the date column
        exclude_columns (list): columns to be excluded

    Returns:
        df_site_day (pd.DataFrame): Multi-indexed DataFrame (site, day) with KPI averages
    """
    if exclude_columns is None:
        exclude_columns = []

    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col, site_col])

    numeric_cols = df.select_dtypes(include=['float', 'int']).columns
    numeric_cols = [col for col in numeric_cols if col not in exclude_columns]

    df_grouped = df.groupby([site_col, df[date_col].dt.date])[numeric_cols].mean()
    df_grouped.index.set_names(['Site', 'Date'], inplace=True)
    
    return df_grouped

def plot_kpi_trend(df_grouped, site, kpi):
    """
    Traces the evolution of a KPI for a given site.

    Args:
        df_grouped (pd.DataFrame): Output of `aggregate_by_site_and_day`
        site (str): name of the site
        kpi (str): name of the KPI to plot
    """
    df_site = df_grouped.loc[site]
    df_site[kpi].plot(figsize=(10, 4), title=f"{kpi} trend - Site: {site}")
    plt.ylabel(kpi)
    plt.xlabel("Date")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# Cleaning
df_clean = clean_data1(df)
# Columns to be excluded
exclude_columns = ['Date', 'eNodeB Name', 'eNodeB Function Name', 'Cell Name', 'LocalCell Id', 'Cell FDD TDD Indication', 'Integrity', 'Average Nb of Users', 'Active User']
# Statistical summary of KPIs
summary_df = summarize_kpis(df_clean, exclude_columns)
print(summary_df)

daily_agg = aggregate_by_day(df_clean, date_column='Date', exclude_columns=exclude_columns)
print(daily_agg)

# Save cleaned data
with pd.ExcelWriter("data/cleaned_kpis.xlsx") as writer:
    df_clean.to_excel(writer, sheet_name="4G_KPIs", index=False)

df_grouped = aggregate_by_site_and_day(df_clean, exclude_columns=exclude_columns)
plot_kpi_trend(df_grouped, site='CoMPT_AGA1114_999_Stade', kpi='RRC_Succes_Rate')
