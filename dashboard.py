import streamlit as st
import pandas as pd
import numpy as np
from preprocessing import clean_data
from graph_generator import plot_kpi_time_series

def set_page_config():
    st.set_page_config(
        page_title="Analyse KPI 4G", 
        page_icon=":bar_chart:",
        layout="wide")
    
    st.markdown("<style> footer {visibility: hidden;} </style>", unsafe_allow_html=True)

set_page_config()
st.title("Analyse des Performances Radio 2G/3G/4G")

# ----------- Upload Excel file -----------
uploaded_file = st.file_uploader("Charger le rapport contenant les KPIs", type=["xlsx"])

if uploaded_file is not None:
    # Reading the Excel file
    try:
        df = pd.read_excel(uploaded_file)
        st.success("Rapport chargé avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
        st.stop()
    
    # Data cleaning
    df = clean_data(df)
    
    st.subheader("Aperçu des données")
    st.dataframe(df.head())

    # ----------- Selection of the site -----------
    site_column = ["eNodeB Name", "Cell Name", "LocalCell Id"]
    site_col = None
    for col in site_column:
        if col in df.columns:
            site_col = col
            break
    
    if site_col:
        sites = df[site_col].dropna().unique()
        selected_site = st.selectbox("Sélectionner un site à analyser", sites)
        df_site = df[df[site_col] == selected_site]
    else:
        st.warning("Aucune colonne de site reconnue dans le fichier.")
        df_site = df

    # ----------- KPI selection + Visualisation -----------
    # Exclude non-numeric columns
    #numeric_cols = df_site.select_dtypes(include=['float64', 'int64']).columns.tolist()
    exclude_columns = ['Date', 'eNodeB Name', 'eNodeB Function Name', 'Cell Name', 'LocalCell Id', 'Cell FDD TDD Indication', 'Integrity', 'Average Nb of Users', 'Active User']
    columns = df.columns
    numeric_cols = [col for col in columns if col not in exclude_columns]

    if numeric_cols:
        selected_kpis = st.multiselect("Sélectionner les KPIs à visualiser", numeric_cols)
        if selected_kpis:
            for kpi in selected_kpis:
                plot_kpi_time_series(df_site, site_name=selected_site, kpi=kpi)
        else:
            st.info("Sélectionnez au moins un KPI pour afficher le graphique.")
    else:
        st.warning("Aucune colonne numérique détectée pour l'analyse des KPIs.")
