import os
import matplotlib.pyplot as plt
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

def plot_kpi_time_series(df, site_name, kpi, selected_cells=None, normalize=False, y_range=None):
    """
    Plot interactive time series of a KPI for each cell of a given site.

    Args:
        df: full cleaned dataframe
        site_name: selected eNodeB Name
        kpi: KPI to plot
        selected_cells: optional list of selected cell names

    Returns:
        fig: Plotly figure
    """
    site_df = df[df['eNodeB Name'] == site_name].copy()
    if site_df.empty:
        print(f"[!] Aucune donnée trouvée pour le site: {site_name}")
        return
    
    site_df['Date'] = pd.to_datetime(site_df['Date'])
    site_df.sort_values('Date', inplace=True)

    ### Case : Site average
    if selected_cells and "Moyenne du site" in selected_cells:
        mean_df = site_df.groupby("Date")[kpi].mean().reset_index()
        fig = px.line(mean_df, x="Date", y=kpi, title=f"Moyenne {kpi} - {site_name}", markers=True)
        fig.update_traces(line=dict(color='green'), name="Moyenne")
    
    else : 
        ### Case : normal or "Toutes les cellules"
        if selected_cells and "Toutes les cellules" not in selected_cells:
            site_df = site_df[site_df['Cell Name'].isin(selected_cells)]
    
        if normalize:
            site_df[kpi] = (site_df[kpi] - site_df[kpi].min()) / (site_df[kpi].max() - site_df[kpi].min())

        fig = px.line(
            site_df,
            x="Date",
            y=kpi,
            color="Cell Name",
            title=f"{kpi} - {site_name}",
            markers=True
    )
    fig.update_layout(
        height=500,
        margin=dict(l=30, r=30, t=40, b=30),
        xaxis_title="Date",
        yaxis_title=kpi,
        legend_title="Cellule",
        font=dict(size=12)
    )

    if y_range:
        fig.update_yaxes(range=[y_range[0], y_range[1]])

    return fig

def plot_dual_axis_kpi_time_series(df, site_name, kpi1, kpi2, selected_cells=None, normalize=False, y_range=None):
    """
    Plot two KPIs with two Y axes (left and right), with per-cell or average display.

    Args:
        df: full cleaned dataframe
        site_name: selected eNodeB Name
        kpi1: KPI to plot on the left Y axis
        kpi2: KPI to plot on the right Y axis
        selected_cells: optional list of selected cell names

    Returns:
        fig: Plotly figure
    """
    site_df = df[df['eNodeB Name'] == site_name].copy()
    if site_df.empty:
        print(f"[!] Aucune donnée trouvée pour le site: {site_name}")
        return
    
    site_df['Date'] = pd.to_datetime(site_df['Date'])
    site_df.sort_values('Date', inplace=True)

    fig = go.Figure()

    if selected_cells and "Moyenne du site" in selected_cells:
        mean_df = site_df.groupby("Date")[[kpi1, kpi2]].mean().reset_index()

        fig.add_trace(go.Scatter(
            x=mean_df["Date"],
            y=mean_df[kpi1],
            mode='lines+markers',
            name=f"Moyenne - {kpi1}",
            yaxis='y1',
            line=dict(color='blue')
        ))

        fig.add_trace(go.Scatter(
            x=mean_df["Date"],
            y=mean_df[kpi2],
            mode='lines+markers',
            name=f"Moyenne - {kpi2}",
            yaxis='y2',
            line=dict(color='red')
        ))
    
    else :
        if selected_cells and "Toutes les cellules" not in selected_cells:
            site_df = site_df[site_df['Cell Name'].isin(selected_cells)]


        for cell in site_df["Cell Name"].unique():
            cell_data = site_df[site_df["Cell Name"] == cell]

            fig.add_trace(
                go.Scatter(
                    x=cell_data["Date"],
                    y=cell_data[kpi1],
                    mode="lines",
                    name=f"{kpi1} - {cell}",
                    line=dict(color="blue"),
                    yaxis="y1"
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=cell_data["Date"],
                    y=cell_data[kpi2],
                    mode="lines",
                    name=f"{kpi2} - {cell}",
                    line=dict(color="red"),
                    yaxis="y2"
                )
            )
    
    fig.update_layout(
        title = f"{kpi1} et {kpi2} - {site_name}",
        xaxis_title="Date",
        yaxis=dict(title=kpi1, side='left'),
        yaxis2=dict(title=kpi2, overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99),
        height=500,
        margin=dict(l=30, r=30, t=40, b=30),
    )
    
    return fig

def plot_kpi_time_series1(df, site_name, kpi, threshold=None, save_path='plots/timeseries'):
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
    fig, ax = plt.subplots()
    
    cell_names = site_df['Cell Name'].unique()

    for cell in cell_names:
        cell_df = site_df[site_df['Cell Name'] == cell]
        ax.plot(cell_df['Date'], cell_df[kpi], linestyle='-', label=cell)

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
            plot_kpi_time_series1(df, site, kpi, threshold, save_path)

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