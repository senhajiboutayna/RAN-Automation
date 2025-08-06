import os
import matplotlib.pyplot as plt
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

from anomaly_detector import detect_zscore_anomalies

def plot_kpi_time_series(df, site_name, kpi, selected_cells=None, y_range=None, threshold=None, threshold_direction=None, use_zscore=False, zscore_threshold=3.0):
    """
    Plot interactive time series of a KPI for each cell of a given site.

    Args:
        df: full cleaned dataframe
        site_name: selected eNodeB Name
        kpi: KPI to plot
        selected_cells: optional list of selected cell names
        thresholds: dict containing thresholds {kpi1: value, kpi2: value}
        threshold_directions: dict containing direction ("max" or "min") for each KPI

    Returns:
        fig: Plotly figure
    """
    site_df = df[df['eNodeB Name'] == site_name].copy()
    if site_df.empty:
        print(f"[!] Aucune donnée trouvée pour le site: {site_name}")
        return
    
    ### Key step: managing temporal column names 
    date_col = None
    if 'Date' in site_df.columns:
        date_col = 'Date'
        site_df[date_col] = pd.to_datetime(site_df[date_col])
    elif 'Time' in site_df.columns:
        date_col = 'Time'
        site_df[date_col] = site_df[date_col].astype(str)
        site_df[date_col] = site_df[date_col].str.replace(r'(\d{4}-\d{2}-\d{2})(\d{2}:\d{2})', r'\1 \2', regex=True)
        site_df[date_col] = pd.to_datetime(site_df[date_col], errors='coerce')
        site_df = site_df.dropna(subset=[date_col])
    else:
        raise KeyError("Aucune colonne de date trouvée (ni 'Date' ni 'Time').")
    
    site_df.sort_values(date_col, inplace=True)

    ### Case : Site average
    if selected_cells and "Moyenne du site" in selected_cells:
        mean_df = site_df.groupby(date_col)[kpi].mean().reset_index()
        fig = px.line(mean_df, x=date_col, y=kpi, title=f"Moyenne {kpi} - {site_name}", markers=True)
        fig.update_traces(line=dict(color='green'), name="Moyenne")
    
    else : 
        ### Case : normal or "Toutes les cellules"
        if selected_cells and "Toutes les cellules" not in selected_cells:
            site_df = site_df[site_df['Cell Name'].isin(selected_cells)]

        fig = px.line(
            site_df,
            x=date_col,
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

    else:
        min_val = site_df[kpi].min()
        max_val = site_df[kpi].max()
        padding = (max_val - min_val) * 0.1 if max_val != min_val else 1
        fig.update_yaxes(range=[min_val - padding, max_val + padding])
    
    if threshold and threshold_direction:
        if threshold_direction == "Maximum à ne pas dépasser":
            anomalies = site_df[site_df[kpi] > threshold]
        elif threshold_direction == "Minimum à respecter":
            anomalies = site_df[site_df[kpi] < threshold]
        fig.add_hline(y=threshold, line_dash="dash", line_color="red", annotation_text="Seuil", annotation_position="top left")
        fig.add_trace(
            go.Scatter(
                x = anomalies[date_col],
                y = anomalies[kpi],
                mode = "markers+text",
                name = "Anomalies",
                marker = dict(color = "red", size = 10, symbol = "x"),
                text = [f"⚠ {v:.2f}" for v in anomalies[kpi]],
                textposition='top center',
                showlegend=True
            )
        )
    
    if use_zscore :
        anomalies = detect_zscore_anomalies(site_df[kpi], zscore_threshold)
        site_df["Z_Anomaly"] = anomalies

        fig.add_trace(
            go.Scatter(
                x=site_df[date_col][anomalies],
                y=site_df[kpi][anomalies],
                mode='markers+text',
                name='Z-score Anomalie',
                marker=dict(color='orange', size=9, symbol='triangle-up'),
                text=[f"Z⚠ {v:.2f}" for v in site_df[kpi][anomalies]],
                textposition='top center',
                showlegend=True
            )
        )

    return fig

def plot_dual_axis_kpi_time_series(df, site_name, kpi1, kpi2, selected_cells=None, y_range=None, thresholds=None, threshold_directions=None):
    """
    Plot two KPIs with two Y axes (left and right), with per-cell or average display.

    Args:
        df: full cleaned dataframe
        site_name: selected eNodeB Name
        kpi1: KPI to plot on the left Y axis
        kpi2: KPI to plot on the right Y axis
        selected_cells: optional list of selected cell names
        thresholds: dict containing thresholds {kpi1: value, kpi2: value}
        threshold_directions: dict containing direction ("max" or "min") for each KPI

    Returns:
        fig: Plotly figure
    """
    site_df = df[df['eNodeB Name'] == site_name].copy()
    if site_df.empty:
        print(f"[!] Aucune donnée trouvée pour le site: {site_name}")
        return
    
    ### Key step: managing temporal column names 
    date_col = None
    if 'Date' in site_df.columns:
        date_col = 'Date'
    elif 'Time' in site_df.columns:
        date_col = 'Time'
    else:
        raise KeyError("Aucune colonne de date trouvée (ni 'Date' ni 'Time').")
    
    
    site_df[date_col] = pd.to_datetime(site_df[date_col])
    site_df.sort_values(date_col, inplace=True)

    fig = go.Figure()

    def add_anomalies(fig, x, y, kpi, axis):
        if thresholds and kpi in thresholds and threshold_directions:
            thresh = thresholds[kpi]
            direction = threshold_directions.get(kpi, "max")
            if direction == "max":
                anomalies = y > thresh
            else:
                anomalies = y < thresh

            fig.add_trace(go.Scatter(
                x=x[anomalies],
                y=y[anomalies],
                mode='markers+text',
                name=f"Anomalies {kpi}",
                yaxis=axis,
                marker=dict(color='blue' if axis == 'y1' else 'red', size=10, symbol='x'),
                text=[f"⚠ {val:.2f}" for val in y[anomalies]],
                textposition='top center',
                showlegend=True
            ))

    if selected_cells and "Moyenne du site" in selected_cells:
        mean_df = site_df.groupby(date_col)[[kpi1, kpi2]].mean().reset_index()

        fig.add_trace(go.Scatter(
            x=mean_df[date_col],
            y=mean_df[kpi1],
            mode='lines+markers',
            name=f"Moyenne - {kpi1}",
            yaxis='y1',
            line=dict(color='#355e3b')
        ))

        fig.add_trace(go.Scatter(
            x=mean_df[date_col],
            y=mean_df[kpi2],
            mode='lines+markers',
            name=f"Moyenne - {kpi2}",
            yaxis='y2',
            line=dict(color='#BAB86C')
        ))

        add_anomalies(fig, mean_df[date_col], mean_df[kpi1], kpi1, 'y1')
        add_anomalies(fig, mean_df[date_col], mean_df[kpi2], kpi2, 'y2')
    
    else :
        if selected_cells and "Toutes les cellules" not in selected_cells:
            site_df = site_df[site_df['Cell Name'].isin(selected_cells)]


        for cell in site_df["Cell Name"].unique():
            cell_data = site_df[site_df["Cell Name"] == cell]

            fig.add_trace(
                go.Scatter(
                    x=cell_data[date_col],
                    y=cell_data[kpi1],
                    mode="lines",
                    name=f"{kpi1} - {cell}",
                    line=dict(color="blue"),
                    yaxis="y1"
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=cell_data[date_col],
                    y=cell_data[kpi2],
                    mode="lines",
                    name=f"{kpi2} - {cell}",
                    line=dict(color="red"),
                    yaxis="y2"
                )
            )

            add_anomalies(fig, cell_data[date_col], cell_data[kpi1], kpi1, 'y1')
            add_anomalies(fig, cell_data[date_col], cell_data[kpi2], kpi2, 'y2')
    
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