import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from preprocessing import clean_data
from graph_generator import plot_kpi_time_series, plot_kpi_histogram, plot_dual_axis_kpi_time_series

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

    # ----------- KPI selection + Visualisation-----------
    # Exclude non-numeric columns
    #numeric_cols = df_site.select_dtypes(include=['float64', 'int64']).columns.tolist()
    exclude_columns = ['Date', 'eNodeB Name', 'eNodeB Function Name', 'Cell Name', 'LocalCell Id', 'Cell FDD TDD Indication', 'Integrity']
    columns = df.columns
    numeric_cols = [col for col in columns if col not in exclude_columns]

    if numeric_cols:
        selected_kpis = st.multiselect("Sélectionner les KPIs à visualiser", numeric_cols)
        threshold_input = st.checkbox("Afficher les seuils critiques ?", value=False)
        graph_type = st.selectbox("Type de graphique", ["Histogramme", "Graphique temporel", "Graphique 2 axes (double KPI)"])

        available_cells = df_site["Cell Name"].dropna().unique()
        special_options = ["Toutes les cellules", "Moyenne du site"]
        cell_options = np.concatenate((special_options, available_cells))

        # Default selection : The first cell available
        default_selection = [available_cells[0]]

        selected_cells = st.multiselect("Sélectionner les cellules à afficher", cell_options, default=default_selection)

        if selected_kpis:
            for kpi in selected_kpis:
                st.markdown(f"## KPI : {kpi}")
                threshold_value = None
                if threshold_input:
                    # to be improved
                    threshold_value = st.number_input(f"Saisir le seuil critique pour {kpi}", value=0.0)

            # Advanced options for the scale
            st.markdown("### Modification de l'échelle :")

            normalize = st.checkbox(f"Normaliser les données pour {kpi} (0-1)", key=f"norm_{kpi}")
            """
            y_min, y_max = st.slider(
                f"Définir l'échelle Y pour {kpi}",
                min_value=float(df_site[kpi].min()),
                max_value=float(df_site[kpi].max()),
                value=(float(df_site[kpi].min()), float(df_site[kpi].max())),
                step=0.1,
                key=f"slider_{kpi}"
            )
            """

            if graph_type == "Graphique temporel":
                fig = plot_kpi_time_series(df, selected_site, kpi, selected_cells, normalize=normalize)
                st.plotly_chart(fig, use_container_width=True)
            
            elif graph_type == "Graphique 2 axes (double KPI)":
                st.markdown("### Sélectionner deux KPIs à comparer")
                kpi_duo = st.multiselect("Sélectionner exactement 2 KPIs", numeric_cols, max_selections=2)

                if len(kpi_duo) == 2:
                    fig = plot_dual_axis_kpi_time_series(df, selected_site, kpi_duo[0], kpi_duo[1], selected_cells)
                    st.plotly_chart(fig, use_container_width=True)
                
                else :
                    st.warning("Veuillez sélectionner exactement 2 KPIs pour générer le graphique à double axe.")

            elif graph_type == "Histogramme":
                fig = plot_kpi_histogram(df_site, selected_site, kpi)
                st.pyplot(fig)

        else:
            st.info("Sélectionnez au moins un KPI pour afficher le graphique.")
    else:
        st.warning("Aucune colonne numérique détectée pour l'analyse des KPIs.")
