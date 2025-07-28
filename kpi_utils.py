import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
def get_kpi_info(kpi_name):

    kpi_definitions = {
        "RRC Setup Fail": {
            "description": "Mesure les échecs d'établissement de connexions RRC (Radio Resource Control) ; indique des problèmes d'accessibilité.",
            "Catégorie" : "Accessibilité",
            "formula": "La somme de tous les échecs d'établissement de connexions RRC.",
            "Unité" : "-",
        },
        "RRC_Success_Rate": {
            "description": "Taux de réussite d'établissement des connexions RRC (Radio Resource Control) entre l'UE et le réseau.",
            "Catégorie" : "Accessibilité",
            "formula": "RRC Setup Success Rate = (RRC Setup Successes / RRC Setup Attempts) x 100",
            "Unité" : "%",
        },
        "VoLTE Traffic": {
            "description": "Volume de trafic voix sur LTE ; utile pour analyser la charge VoLTE et l'usage des services voix.",
            "Catégorie" : "Trafic",
            "formula": "-",
            "Unité" : "",
        },
        "4G PS Traffic": {
            "description": "Trafic de données paquet sur 4G ; montre l’intensité d’utilisation du réseau data.",
            "Catégorie" : "Trafic",
            "formula": "-",
            "Unité" : "GB",
        },
        "Erab_Succes_Rate": {
            "description": "Taux de réussite de l'établissement des bearers E-RAB, reflète la capacité à établir les connexions data.",
            "Catégorie" : "Accessibilité",
            "formula": "Erab Setup Success Rate = (Erab Setup Successes / Erab Setup Attempts) x 100",
            "Unité" : "%",
        },
        "4G Cell Availability": {
            "description": "Disponibilité de la cellule (impacte la stabilité).",
            "Catégorie" : "Stabilité",
            "formula": "-",
            "Unité" : "%",
        },
        "CSSR 4G": {
            "description": "Taux global de réussite des tentatives d'établissement d'appel voix (circuit ou VoIP).",
            "Catégorie" : "Accessibilité",
            "formula": "CSSR = (Number of Successful Call Setups / Total Number of Call Attempts) x 100",
            "Unité" : "%",
        },
        "CSR": {
            "description": "",
            "Catégorie" : "",
            "formula": "",
            "Unité" : "",
        },
        "DL User throughput": {
            "description": "",
            "Catégorie" : "Intégrité",
            "formula": "",
            "Unité" : "MHz",
        },
        "UL User throughput": {
            "description": "",
            "Catégorie" : "Intégrité",
            "formula": "",
            "Unité" : "",
        },
        "DL PRB Usage": {
            "description": "L'utilisation des blocs de ressources physiques (PRB) en liaison descendante (DL) fait référence à la quantité de ressources spectrales allouées aux utilisateurs dans le sens du réseau vers l'appareil",
            "Catégorie" : "Intégrité",
            "formula": "-",
            "Unité" : "%",
        },
        "CDR": {
            "description": "Pourcentage d'appels voix interrompus après avoir été établis avec succès. Indicateur de stabilité du service voix.",
            "Catégorie" : "Stabilité",
            "formula": "CDR = (Nombre d'appels interrompus / Nombre total d'appels établis) x 100",
            "Unité" : "%",
        },
        "C4G_CSFB Success Rate": {
            "description": "Mécanisme permettant à un terminal LTE de basculer vers 2G/3G pour établir un appel voix (en l'absence de VoLTE). ",
            "Catégorie" : "Accessibilité",
            "formula": "CSFB Success Rate = (Nb de CSFB réussis / Nb de tentatives CSFB) x 100",
            "Unité" : "%",
        },
        "S1_Succes_Rate": {
            "description": "S1 Setup Success Rate désigne le pourcentage de connexions de signalisation établies avec succès entre les eNodeB et les entités de gestion de la mobilité (MME) via l'interface S1",
            "Catégorie" : "Accessibilité",
            "formula": "S1-Setup Success Rate = (S1 Setup Successes / S1 Setup Attempts) x 100",
            "Unité" : "%",
        },
        "Handover success rate of CA UEs": {
            "description": "Succès de la mobilité pour les utilisateurs Carrier Aggregation.",
            "Catégorie" : "Mobilité",
            "formula": "Handover Success Rate = (Handover Successes / Handover Attempts) x 100",
            "Unité" : "%",
        },
        "UL interference": {
            "description": "Niveau d'interférences en uplink ; indicateur de qualité radio et de congestion possible.",
            "Catégorie" : "Intégrité",
            "formula": "-",
            "Unité" : "dBm",
        },
        "Average RSRP Reported": {
            "description": "Le RSRP est crucial pour déterminer la couverture et la qualité du signal dans les réseaux mobiles. Une valeur RSRP plus élevée (rapprochée de 0 dBm) indique un signal plus fort, tandis qu'une valeur plus faible (plus négative) indique un signal plus faible. ",
            "Catégorie" : "Intégrité",
            "formula": "",
            "Unité" : "dBm",
        },
        "SINR": {
            "description": "Le SINR est un rapport entre la puissance du signal souhaité et la puissance combinée du bruit et des interférences. ",
            "Catégorie" : "Intégrité",
            "formula": "SINR = Signal Power / (Interference Power + Noise Power)",
            "Unité" : "dB",
        },
    }

    return kpi_definitions.get(kpi_name)


def categorize_kpi(kpi_name):
    kpi_info = get_kpi_info(kpi_name)
    if kpi_info:
        return kpi_info["Catégorie"]
    return "Inconnu"


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

# Liste des KPIs à afficher ensemble 

['RRC Setup Fail', 'RRC_Succes_Rate']
['DL User throughput', 'DL User throughput']