import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analyse KPI 4G", layout="wide")

st.title("Dashboard d'Analyse des Performances Radio 2G/3G/4G")

# ----------- Upload du fichier Excel -----------
uploaded_file = st.file_uploader("Charger le rapport contenant les KPIs", type=["xlsx"])

if uploaded_file is not None:
    # Lecture du fichier Excel
    try:
        df = pd.read_excel(uploaded_file)
        st.success("Rapport chargé avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
        st.stop()
    
    st.subheader("Aperçu des données")
    st.dataframe(df.head())

    # ----------- Sélection du site -----------
    site_column_candidates = ["eNodeB Name", "Cell Name", "LocalCell Id"]
    site_col = None
    for col in site_column_candidates:
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

    # ----------- Sélection des KPIs -----------
    # On exclut les colonnes non numériques
    numeric_cols = df_site.select_dtypes(include=['float64', 'int64']).columns.tolist()

    if numeric_cols:
        selected_kpis = st.multiselect("Sélectionner les KPIs à visualiser", numeric_cols)
        if selected_kpis:
            st.line_chart(df_site[selected_kpis])
        else:
            st.info("Sélectionnez au moins un KPI pour afficher le graphique.")
    else:
        st.warning("Aucune colonne numérique détectée pour l'analyse des KPIs.")
