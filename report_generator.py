from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import tempfile

from datetime import datetime

def generate_anomaly_summary(df, kpi, threshold, direction):
    if direction == "Maximum à ne pas dépasser":
        anomalies = df[df[kpi] > threshold]
    else:
        anomalies = df[df[kpi] < threshold]

    if anomalies.empty:
        return f"Aucune anomalie détectée sur le KPI {kpi}."

    summary = f"{len(anomalies)} anomalies détectées sur le KPI {kpi}.\n"
    summary += f"Seuil : {threshold} ({direction})\n\n"
    for _, row in anomalies.iterrows():
        date = row['Date']
        value = row[kpi]
        # Assuming your date is in format 'YYYY-MM-DD'
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        summary += f"• Le {date_obj.strftime('%Y-%m-%d')}, valeur = {value:.2f}\n"
    return summary

def generate_pdf_report(site_name, kpi_name, cell_name, summary_text, image_files):
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"<font size=16 color='navy'><b>Rapport d'Anomalies  - Site: {site_name} </b></font>", styles["Title"]))
    elements.append(Paragraph(f"KPI : {kpi_name}", styles["Heading2"]))
    elements.append(Paragraph(f"Cellule : {cell_name}", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    # Summary
    elements.append(Paragraph("Analyse automatique des anomalies :", styles["Heading3"]))
    for line in summary_text.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Figures
    elements.append(Paragraph("Figures exportées :", styles["Heading3"]))
    for img_file in image_files:
        elements.append(Image(img_file, width=500, height=300))
        elements.append(Spacer(1, 12))

    # Save PDF
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    doc = SimpleDocTemplate(temp_path, pagesize=A4)
    doc.build(elements)
    return temp_path


"""
st.markdown("### Générer le rapport d'anomalies")
uploaded_images = st.file_uploader(
    "📷 Charger les images PNG exportées", 
    type=["png"], 
    accept_multiple_files=True
)

if uploaded_images and selected_kpis:
        kpi = selected_kpis[0]
        threshold = thresholds.get(kpi, None)
        direction = threshold_direction.get(kpi, None)
        summary_text = generate_anomaly_summary(df_site, kpi, threshold, direction)
        image_paths = [img for img in uploaded_images]

        pdf_path = generate_pdf_report(selected_site, kpi, selected_cells, summary_text, image_paths)
        
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Télécharger le rapport PDF",
                data=f,
                file_name=f"rapport_{selected_site}_{kpi}.pdf",
                mime="application/pdf"
            )
"""