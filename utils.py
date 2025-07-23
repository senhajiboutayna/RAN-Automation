import pandas as pd
import numpy as np

def get_site_column(df):
    """
    Identifie automatiquement la colonne qui contient les noms de site.

    Args:
        df (pd.DataFrame)

    Returns:
        nom_colonne_site (str) ou None
    """
    site_column = ["eNodeB Name", "eNodeB Function Name", "Cell Name", "LocalCell Id"]
    for col in site_column:
        if col in df.columns:
            return col
    return None


def get_sites_list(df):
    """
    Retourne la liste des sites uniques à partir de la colonne reconnue.

    Args:
        df (pd.DataFrame)

    Returns:
        liste des sites (list), nom_colonne (str)
    """
    site_col = get_site_column(df)
    if site_col:
        sites = df[site_col].dropna().unique().tolist()
        return sites, site_col
    else:
        return [], None

"""
df = pd.read_excel('data/raw/4G_KPI.xlsx')
sites, site_col = get_sites_list(df)
print('Sites:', sites, 'colonne:',site_col)
"""
