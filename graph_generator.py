import os
import matplotlib.pyplot as plt
import pandas as pd

def plot_kpi_time_series(df, site_name, kpi, threshold=None, save_path='plots/timeseries'):
    """
    Generate and save a time graph for a given KPI and a given site.
    
    Args:
        df: DataFrame containing all data (unfiltered)
        site_name: name of site to filter
        kpi: KPI to plot
        threshold: critical threshold to be displayed (optional)
        save_path: root folder to save plots
    
    Returns:
        fig: Matplotlib figure
    """
    # Data filtering for the site
    site_df = df[df['eNodeB Name'] == site_name].copy()
    if site_df.empty:
        print(f"[!] Aucune donnée trouvée pour le site: {site_name}")
        return
    
    # Date Conversion
    site_df['Date'] = pd.to_datetime(site_df['Date'])
    site_df.sort_values('Date', inplace=True)

    # Verification that the KPI exists
    if kpi not in site_df.columns:
        print(f"[!] KPI non trouvé: {kpi}")
        return

    # Plot
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(site_df['Date'], site_df[kpi], linestyle='-', label=kpi)

    if threshold is not None:
        ax.axhline(y=threshold, color='r', linestyle='--', label='Seuil critique')

    ax.set_title(f"{kpi} - {site_name}", fontsize=10)
    ax.set_xlabel("Date", fontsize=8)
    ax.set_ylabel(kpi, fontsize=8)
    ax.grid(True)
    ax.legend()
    fig.autofmt_xdate()
    plt.tight_layout()

    # Saving
    site_safe = site_name.replace(" ", "_").replace("/", "_")
    kpi_safe = kpi.replace(" ", "_").replace("/", "_").replace("%", "pct")
    save_folder = os.path.join(save_path, site_safe)
    os.makedirs(save_folder, exist_ok=True)
    save_path = os.path.join(save_folder, f"{kpi_safe}.png")
    plt.savefig(save_path)

    return fig

def generate_all_kpi_time_series(df, kpi_list, save_path='plots/timeseries', threshold_dict=None):
    """
    Generates time series graphs for all sites and KPIs.
    
    Args:
        df: Global DataFrame
        kpi_list: List of KPIs to plot
        save_path: Output folder
        threshold_dict: Dictionary {kpi_name: seuil} (optional)
    """
    all_sites = df['eNodeB Name'].unique()
    for site in all_sites:
        for kpi in kpi_list:
            threshold = None
            if threshold_dict and kpi in threshold_dict:
                threshold = threshold_dict[kpi]
            plot_kpi_time_series(df, site, kpi, threshold, save_path)

"""
df = pd.read_excel('data/cleaned_kpis.xlsx', sheet_name='4G_KPIs')

# Date Cleaning
df['Date'] = pd.to_datetime(df['Date'])

# List of KPIs
kpi_list = [
    'RRC Setup Fail', 'RRC_Succes_Rate', 'VoLTE Traffic', '4G PS Traffic(GB)',
    'Erab_Succes_Rate', '4G_Cell_Availability(%)', 'CSSR 4G', '4G_CSR_(HM)',
    'DL User throughput', 'UL User throughput', 'DL PRB Usage(%)', 'CDR_DDRX (%) LH',
    '4G_CSFB Success Rate(%)(%)', 'S1_Succes_Rate', 'Handover success rate of CA UEs',
    'UL interference', 'Average RSRP Reported(dBm)'
]

generate_all_kpi_time_series(df, kpi_list)
"""

def plot_kpi_histogram(df, site_name, kpi, save_path='plots/histograms'):
    """
    Generate and save the histogram of values for a given KPI.
    
    Args:
        df: Cleaned DataFrame
        site_name: name of site to filter
        kpi: KPI to plot
    """

    df = df[df["eNodeB Name"] == site_name] if "eNodeB Name" in df.columns else df
    values = df[kpi]

    # Verification that the KPI exists
    if kpi not in df.columns:
        print(f"[!] KPI non trouvé: {kpi}")
        return
    
    # Plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(values, bins=30, color='steelblue', edgecolor='black', alpha=0.7)

    ax.set_title(f"{kpi} - {site_name}", fontsize=10)
    ax.set_xlabel(kpi, fontsize=8)
    ax.set_ylabel("Fréquence", fontsize=8)
    ax.grid(True)
    ax.legend()

    # Saving
    site_safe = site_name.replace(" ", "_").replace("/", "_")
    kpi_safe = kpi.replace(" ", "_").replace("/", "_").replace("%", "pct")
    save_folder = os.path.join(save_path, site_safe)
    os.makedirs(save_folder, exist_ok=True)
    save_path = os.path.join(save_folder, f"{kpi_safe}.png")
    plt.savefig(save_path)

    return fig

def plot_all_kpis_histogram(df, site_name, save_path=None):
    """
    Generates histogram graphs for all sites and KPIs.

    - df : cleaned DataFrame
    - site_name : name of site to filter
    - save_path : path to save figures (optional)
    """
    df_site = df[df["eNodeB Name"] == site_name] if "eNodeB Name" in df.columns else df

    # Exclude non-numeric and non-KPI columns
    exclude_cols = ['Date', 'eNodeB Name', 'eNodeB Function Name', 'Cell Name', 'LocalCell Id', 'Cell FDD TDD Indication', 'Integrity', 'Average Nb of Users', 'Active User']
    numeric_kpis = [col for col in df_site.columns if col not in exclude_cols and pd.api.types.is_numeric_dtype(df_site[col])]

    for kpi in numeric_kpis:
        values = df_site[kpi].dropna()

        if values.empty:
            continue

        all_sites = df['eNodeB Name'].unique()
        for site in all_sites:
                threshold = None
                plot_kpi_histogram(df, site, kpi, save_path)

"""
df = pd.read_excel('data/cleaned_kpis.xlsx', sheet_name='4G_KPIs')
plot_kpi_histogram(df, 'CoMPT_AGA1114_999_Stade', 'DL User throughput')
plt.show()
"""