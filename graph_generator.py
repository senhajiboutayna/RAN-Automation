import os
import matplotlib.pyplot as plt
import pandas as pd

def plot_kpi_time_series(df, site_name, kpi, threshold=None, output_dir='plots'):
    """
    Generate and save a time graph for a given KPI and a given site.
    
    Args:
        df: DataFrame containing all data (unfiltered)
        site_name: name of site to filter
        kpi: KPI to plot
        threshold: critical threshold to be displayed (optional)
        output_dir: root folder to save plots
    
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
    save_folder = os.path.join(output_dir, site_safe)
    os.makedirs(save_folder, exist_ok=True)
    save_path = os.path.join(save_folder, f"{kpi_safe}.png")
    plt.savefig(save_path)

    return fig

def generate_all_kpi_graphs(df, kpi_list, output_dir='plots', threshold_dict=None):
    """
    Génère les graphiques temporels pour tous les sites et KPIs.
    
    Args:
        df: Global DataFrame
        kpi_list: List of KPIs to plot
        output_dir: Output folder
        threshold_dict: Dictionary {kpi_name: seuil} (optional)
    """
    all_sites = df['eNodeB Name'].unique()
    for site in all_sites:
        for kpi in kpi_list:
            threshold = None
            if threshold_dict and kpi in threshold_dict:
                threshold = threshold_dict[kpi]
            plot_kpi_time_series(df, site, kpi, threshold, output_dir)

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

generate_all_kpi_graphs(df, kpi_list)
"""
