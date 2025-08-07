import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from preprocessing import clean_data
from graph_generator import plot_kpi_time_series, plot_kpi_histogram, plot_dual_axis_kpi_time_series, plot_kpi_bar_chart, plot_kpi_anomaly_scatter
from anomaly_detector import load_threshold_config, save_threshold_config

threshold_config = load_threshold_config()

# ----------- Config -----------
def set_page_config():
    st.set_page_config(
        page_title="Analyse KPI 4G", 
        page_icon=":bar_chart:",
        layout="wide")
    
    st.markdown("<style> footer {visibility: hidden;} </style>", unsafe_allow_html=True)

set_page_config()
st.title("Analyse des Performances Radio 2G/3G/4G")

# Image of stadium
col_img = st.columns([2, 6, 1]) 
with col_img[1]: 
    st.image("img/Stade_MV_Casablanca.jpg", caption="Stade MV Casablanca")

# Layout principal
left_col, right_col = st.columns([1, 3])

df = None
df_site = None
site_col = None
selected_site = None
selected_kpis = []
normalize = True

# ----------- Left Side -----------
with left_col:
    st.markdown("### 📥 Chargement du rapport")
    uploaded_file = st.file_uploader("Charger le rapport contenant les KPIs", type=["xlsx"])

    graph_type = st.selectbox("📊 Type de graphique", 
        ["Graphique temporel", "Graphique 2 axes (double KPI)", "Graphique à barres", "Scatter Anomalies", "Histogramme"]
    )

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df = clean_data(df)

            site_column = ["eNodeB Name", "Cell Name", "LocalCell Id"]
            for col in site_column:
                if col in df.columns:
                    site_col = col
                    break

            if site_col:
                sites = df[site_col].dropna().unique()
                selected_site = st.selectbox("🏗️ Sélectionner un site", sites)
                df_site = df[df[site_col] == selected_site]
            else:
                st.warning("Aucune colonne de site reconnue.")
                df_site = df

            exclude_columns = ['Date', 'eNodeB Name', 'eNodeB Function Name', 
                               'Cell Name', 'LocalCell Id', 'Cell FDD TDD Indication', 'Integrity']
            numeric_cols = [col for col in df.columns if col not in exclude_columns]

            if graph_type != "Graphique 2 axes (double KPI)":
                selected_kpis = st.multiselect("📈 Sélectionner les KPIs", numeric_cols)
            else:
                selected_kpis = []

            if selected_site is not None:
                available_cells = df_site["Cell Name"].dropna().unique()
                cell_options = ["Toutes les cellules", "Moyenne du site"] + list(available_cells)
                default_selection = [available_cells[0]] if available_cells.size > 0 else []
                selected_cells = st.multiselect("📶 Cellules à afficher", cell_options, default=default_selection)
            else:
                selected_cells = []
            
            use_custom_y_range = st.checkbox("📏 Personnaliser l'échelle Y du KPI ?", value=False)

            custom_y_range = None
            if use_custom_y_range and selected_kpis:
                kpi_sample = selected_kpis[0]
                if kpi_sample in df_site.columns:
                    y_min_default = float(df_site[kpi_sample].min())
                    y_max_default = float(df_site[kpi_sample].max())
                else:
                    y_min_default = 0.0
                    y_max_default = 100.0
                
                y_min = st.number_input("🔽 Valeur minimale Y", value=y_min_default)
                y_max = st.number_input("🔼 Valeur maximale Y", value=y_max_default)
                custom_y_range = [y_min, y_max]

            threshold_input = st.checkbox("⚠️ Afficher les anomalies ?", value=False)
            thresholds = {}
            threshold_direction = {}

            if threshold_input:
                for kpi in selected_kpis:
                    existing = threshold_config.get(kpi, {})
                    default_thresh = existing.get("threshold", 0.0)
                    default_dir = existing.get("direction", "Maximum à ne pas dépasser")

                    col1, col2 = st.columns([2, 2])
                    with col1:
                        threshold_value = st.number_input(
                            f"Valeur à ne pas dépasser", 
                            key=f"thresh_{kpi}", 
                            value=float(default_thresh)
                        )
                    
                    with col2:
                        direction = st.selectbox(
                            f"Type de seuil", 
                            options = ["Maximum à ne pas dépasser", "Minimum à respecter"],
                            key=f"direction_{kpi}",
                            index=0 if default_dir == "Maximum à ne pas dépasser" else 1
                        )

                    thresholds[kpi] = threshold_value
                    threshold_direction[kpi] = direction

                    threshold_config[kpi] = {
                        "threshold": threshold_value,
                        "direction": direction
                    }
                
                save_threshold_config(threshold_config)
            
            use_zscore = st.checkbox("📉 Détection Z-score", value=False)
            zscore_threshold = None
            if use_zscore:
                zscore_threshold = st.slider("Seuil Z-score", min_value=1.0, max_value=5.0, value=3.0, step=0.1)

            use_moving_avg = st.checkbox("📈 Détection Moving Average", value=False)
            if use_moving_avg:
                moving_avg_window = st.slider("Fenêtre moyenne mobile", min_value=3, max_value=21, value=5, step=2)
                moving_avg_thresh = st.slider("Seuil d'écart (σ)", min_value=0.5, max_value=5.0, value=2.0, step=0.1)
            else:
                moving_avg_window = None
                moving_avg_thresh = None

        except Exception as e:
            st.error(f"Erreur lors du traitement du fichier : {e}")

# ----------- Right Side -----------
with right_col:
    if uploaded_file is not None and df is not None:
        st.subheader("Aperçu des données")
        st.dataframe(df.head())

        if selected_site and graph_type == "Graphique 2 axes (double KPI)":
            kpi_duo = st.multiselect("Sélectionner exactement 2 KPIs", numeric_cols, max_selections=2)
            if len(kpi_duo) == 2:
                fig = plot_dual_axis_kpi_time_series(df, selected_site, kpi_duo[0], kpi_duo[1], selected_cells, y_range=custom_y_range, thresholds=thresholds,threshold_directions=threshold_direction)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Veuillez sélectionner 2 KPIs pour le graphique à deux axes.")
        
        elif selected_kpis:
            for kpi in selected_kpis:
                st.markdown(f"### 📈 {kpi}")
                if graph_type == "Graphique temporel":
                    fig = plot_kpi_time_series(df, selected_site, kpi, selected_cells, y_range=custom_y_range, threshold=thresholds.get(kpi), threshold_direction=threshold_direction.get(kpi), use_zscore=use_zscore, zscore_threshold=zscore_threshold, use_moving_avg=use_moving_avg, moving_avg_window=moving_avg_window, moving_avg_thresh=moving_avg_thresh)
                    st.plotly_chart(fig, use_container_width=True)

                elif graph_type == "Histogramme":
                    fig = plot_kpi_histogram(df_site, selected_site, kpi, selected_cells)
                    st.pyplot(fig)

                elif graph_type == "Graphique à barres":
                    fig = plot_kpi_bar_chart(df_site, selected_site, kpi, selected_cells)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif graph_type == "Scatter Anomalies":
                    for kpi in selected_kpis:
                        fig = plot_kpi_anomaly_scatter(df, selected_site, kpi, selected_cells,
                            threshold=thresholds.get(kpi),
                            threshold_direction=threshold_direction.get(kpi),
                            use_zscore=use_zscore,
                            zscore_threshold=zscore_threshold,
                            use_moving_avg=use_moving_avg,
                            moving_avg_window=moving_avg_window,
                            moving_avg_thresh=moving_avg_thresh
                        )
                        st.plotly_chart(fig, use_container_width=True)