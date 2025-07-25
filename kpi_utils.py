import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
def get_kpi_info(kpi_name):

    kpi_definitions = {
        "RRC Setup Fail": {
            "description": "Mesure les échecs d'établissement de connexions RRC (Radio Resource Control) ; indique des problèmes d'accessibilité.",
            "Catégorie" : "disponibilité",
            "formula": "",
        },
        "RRC Setup Success Rate": {
            "description": "Taux de réussite d'établissement des connexions RRC (Radio Resource Control) entre l'UE et le réseau.",
            "Catégorie" : "disponibilité",
            "formula": "RRC Setup Success Rate = (RRC Setup Successes / RRC Setup Attempts) x 100",
        },
        "VoLTE Traffic": {
            "description": "Volume de trafic voix sur LTE ; utile pour analyser la charge VoLTE et l'usage des services voix.",
            "Catégorie" : "",
            "formula": "",
        },
        "4G PS Traffic": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "ERAB Success Rate": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "4G Cell Availability": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "CSSR": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "CSR": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "DL User throughput": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "UL User throughput": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "DL PRB Usage": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "CDR": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "CSFB Success Rate": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "S1 Success Rate": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "Handover Success Rate": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "UL interference": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "Average RSRP Reported": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
        "SINR": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
        },
    }

    return kpi_definitions.get(kpi_name)


kpis_4G = [
    'RRC Setup Fail', 'RRC_Succes_Rate', 'VoLTE Traffic', '4G PS Traffic(GB)',
    'Average Nb of Users', 'Erab_Succes_Rate', '4G_Cell_Availability(%)', 'CSSR 4G',
    '4G_CSR_(HM)', 'DL User throughput', 'UL User throughput', 'DL PRB Usage(%)',
    'CDR_DDRX (%) LH', '4G_CSFB Success Rate(%)(%)', 'S1_Succes_Rate',
    'Handover success rate of CA UEs', 'Active User', 'UL interference',
    'Average RSRP Reported(dBm)'
]

df_4G = pd.read_excel('data/cleaned_kpis.xlsx', sheet_name='4G_KPIs')

corr_matrix = df_4G[kpis_4G].corr(method='pearson')

plt.figure(figsize=(14, 10))
sns.heatmap(
    corr_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    linewidths=0.5,
    cbar_kws={'label': 'Corrélation'}
)
plt.title("Matrice de Corrélation des KPIs 4G", fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('plots/heatmap_4G.png')
