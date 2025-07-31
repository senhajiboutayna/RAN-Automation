import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from preprocessing import clean_data
from graph_generator import plot_kpi_time_series, plot_kpi_histogram, plot_dual_axis_kpi_time_series

# ----------- Config -----------
def set_page_config():
    st.set_page_config(
        page_title="Analyse KPI 4G", 
        page_icon=":bar_chart:",
        layout="wide")
    
    st.markdown("<style> footer {visibility: hidden;} </style>", unsafe_allow_html=True)

set_page_config()
st.title("Analyse des Performances Radio 2G/3G/4G")

# Layout principal
left_col, right_col = st.columns([1, 3])

df = None
df_site = None
site_col = None
selected_site = None
selected_kpis = []
normalize = True

# ----------- KPI Selection -----------
with left_col:
    st.markdown("### 📥 Chargement du rapport")
    uploaded_file = st.file_uploader("Charger le rapport contenant les KPIs", type=["xlsx"])

    graph_type = st.selectbox("📊 Type de graphique", 
        ["Histogramme", "Graphique temporel", "Graphique 2 axes (double KPI)"])

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

            if selected_kpis:
                threshold_input = st.checkbox("⚠️ Afficher les seuils critiques ?", value=False)
                if threshold_input:
                    for kpi in selected_kpis:
                        st.number_input(f"Seuil critique pour {kpi}", value=0.0)

                for kpi in selected_kpis:
                    normalize = st.checkbox(f"🔧 Normaliser {kpi} (0-1)", key=f"norm_{kpi}")

        except Exception as e:
            st.error(f"Erreur lors du traitement du fichier : {e}")

# ----------- Graphe Visualisation -----------
with right_col:
    if uploaded_file is not None and df is not None:
        st.subheader("Aperçu des données")
        st.dataframe(df.head())

        if selected_site and graph_type == "Graphique 2 axes (double KPI)":
            kpi_duo = st.multiselect("Sélectionner exactement 2 KPIs", numeric_cols, max_selections=2)
            if len(kpi_duo) == 2:
                fig = plot_dual_axis_kpi_time_series(df, selected_site, kpi_duo[0], kpi_duo[1], selected_cells)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Veuillez sélectionner 2 KPIs pour le graphique à deux axes.")
        
        elif selected_kpis:
            for kpi in selected_kpis:
                st.markdown(f"### 📈 {kpi}")
                if graph_type == "Graphique temporel":
                    fig = plot_kpi_time_series(df, selected_site, kpi, selected_cells, normalize=normalize)
                    st.plotly_chart(fig, use_container_width=True)
                elif graph_type == "Histogramme":
                    fig = plot_kpi_histogram(df_site, selected_site, kpi)
                    st.pyplot(fig)
