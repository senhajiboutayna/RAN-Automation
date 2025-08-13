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
col_img = st.columns([2, 6, 2]) 
with col_img[1]: 
    st.image("img/Stade_casa.png", caption="Stade MV Casablanca")

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
            # Define how many graphs per line based on the total number
            default_cols = 1 if len(selected_kpis) == 1 else 2

            max_cols = min(len(selected_kpis), 4) 
            cols_per_row = st.number_input(
                "Nombre de graphes par ligne",
                min_value=1,
                max_value=max_cols,
                value=default_cols,
                step=1
            )
            

            # Create lines dynamically    
            for i in range(0, len(selected_kpis), cols_per_row):
                row_kpis = selected_kpis[i:i+cols_per_row]
                cols = st.columns(cols_per_row) 

                for col, kpi in zip(cols, row_kpis):
                    with col:
                        st.markdown(f"### 📈 {kpi}")
                
                
                        if graph_type == "Graphique temporel":
                            fig = plot_kpi_time_series(df, selected_site, kpi, selected_cells, y_range=custom_y_range, threshold=thresholds.get(kpi, None), threshold_direction=threshold_direction.get(kpi, None))
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
                                    threshold_direction=threshold_direction.get(kpi)
                                )
                                st.plotly_chart(fig, use_container_width=True)
