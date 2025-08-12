# 📡 RAN Automation for KPI Monitoring & Anomaly Detection

## 📌 Project Overview
This project is part of a broader initiative to **automate Radio Access Network (RAN) performance monitoring** and facilitate faster decision-making for network optimization.  
The main objective is to **replace manual KPI analysis** with a fully automated anomaly detection pipeline, allowing radio engineers to focus on **root cause analysis and corrective actions** instead of repetitive data processing.

## 📝 How RAN Automation Works in This Project
The tool chosen for automation is a dashboard developed with **Streamlit**. It allows:
1. **Data Collection**: KPI reports are extracted from the OSS in predefined formats (Excel).
2. **Preprocessing**: Cleaning and structuring data for analysis.
3. **Anomaly Detection**:
   - **Rule-based**: Fixed thresholds per KPI.
   - **Statistical**: Z-score and moving average.
   - **ML-based**: Isolation Forest for outlier detection.
4. **Visualization**: Interactive dashboard for quick inspection of anomalies.

## 🏗️ Project Structure
```
📂 RAN-Automation 
│── 📂 img # Static images for the dashboard
│── 📄 anomaly_detector.py # Anomaly detection algorithms
│── 📄 dashboard.py # Streamlit dashboard app
│── 📄 graph_generator.py # Plotly/Matplotlib visualization functions
│── 📄 kpi_utils.py # Utility KPI functions
│── 📄 preprocessing.py # Data cleaning & preparation
│── 📄 Rapport.pdf 
│── 📄 README.md # Project documentation 
│── 📄 threshold_config.json # KPI threshold settings
└── 📄 utils.py # Utility functions
```

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/senhajiboutayna/RAN-Automation.git
cd RAN-Automation
```

### 2️⃣ Open the application
```bash
streamlit run dashboard.py
```