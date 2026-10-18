# Heavy Truck Fleet Predictive Maintenance & Cost Analytics

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20Relational-lightgrey.svg)](https://sqlite.org/)

An end-to-end industrial data engineering, machine learning, and executive reporting platform designed for heavy equipment fleets, mining haulage operations, and heavy transport logistics. 

This project integrates relational telematics modeling, fleet availability tracking, cost-sensitive machine learning for early failure prediction, prescriptive budget optimization, and automated corporate Excel reporting.

---

## 📌 Project Overview & Industry Background

In capital-intensive heavy industries (such as open-pit mining contractors, quarrying, and heavy logistics), **equipment availability directly dictates production throughput**. An unplanned breakdown of a 40-to-100-ton haul truck does not just cost repair money—it blocks narrow haul roads, disrupts shovel-and-truck queuing cycles, and halts pit production.

A primary failure mode in heavy commercial vehicles is the **Air Pressure System (APS)**. The APS generates, dries, and distributes compressed air used for:
* Actuating the heavy pneumatic service and emergency brake systems.
* Shifting gears and clutch controls in automated manual transmissions.
* Air suspension height and load-leveling valves.

A sudden pressure loss or compressor seizure while hauling tons of overburden or coal leads to catastrophic wheel lockup or brake failure on active pit ramps.

---

## 🎯 Problems Solved by This Platform

This project solves **6 critical operational, technical, and financial problems** faced by fleet operations:

### 1. The Fallacy of Standard Machine Learning Accuracy
* **Problem**: In fleet telemetry, ~98.4% of operating trucks are healthy, while only ~1.6% suffer component failure. A naive model that blindly predicts "Healthy" for every unit achieves a misleading **98.4% accuracy**, yet fails to detect a single breakdown, leading to operational catastrophe.
* **Solution**: Developed a cost-sensitive pipeline utilizing `HistGradientBoosting` with balanced class weights, optimizing for **ROC-AUC (0.9870)** and **Recall / Sensitivity (91.60%)** to catch impending failures before they happen.

### 2. Extreme Cost Asymmetry ($10 False Alarm vs $500 Roadside Breakdown)
* **Problem**: Standard classification assumes a 50/50 cost balance (decision threshold $p = 0.50$). In mining operations, costs are drastically asymmetric:
  * **False Positive (FP - False Alarm)**: Sending a healthy truck to the workshop costs only **$10** (a 15-minute technician inspection and gauge check).
  * **False Negative (FN - Missed Failure)**: Letting a damaged truck head out to the pit results in a breakdown costing **$500+** (emergency road assistance, lowboy transport, secondary component damage, and production downtime).
* **Solution**: Implemented a **Prescriptive Cost Optimizer** (`cost_optimizer.py`) that models the financial cost function:
  $$\text{Total Cost} = (10 \times \text{False Positives}) + (500 \times \text{False Negatives})$$
  By shifting the decision threshold from $p = 0.50$ down to the empirical optimum **$p^* = 0.029$**, the system reduces catastrophic breakdowns by **42.9%** and slashes total maintenance spend by **37.5% ($4,070 saved per cycle)**.

### 3. Data Fragmentation & Siloed Information
* **Problem**: Sensor telemetry, master asset records, work orders, and financial budget plans are traditionally stored in disconnected spreadsheets and legacy software.
* **Solution**: Designed an enterprise-grade **4-table relational database schema** (`schema.sql`) with explicit primary/foreign keys (`truck_master`, `telemetry_logs`, `maintenance_records`, `budget_plan`) ensuring end-to-end data integrity.

### 4. Visibility over Fleet Availability & Operational KPIs
* **Problem**: Fleet executives require real-time visibility into whether maintenance operations meet production SLAs and targets.
* **Solution**: Built an automated KPI analytics engine (`kpi_calculator.py`) calculating **Physical Availability (PA = 99.34%)**, **Mean Time Between Failures (MTBF = 4,087.1 hours)**, breakdown counts, and monthly planned vs actual budget variance.

### 5. Inefficient, Error-Prone Manual Excel Reporting
* **Problem**: Maintenance teams waste hours every week manually copying and pasting static numbers into Excel sheets, resulting in broken formulas and un-auditable reports.
* **Solution**: Created a programmatic report generator (`excel_exporter.py`) using `openpyxl`. It produces corporate-grade `.xlsx` files with **native Excel formulas** (`=SUM`, `=AVERAGE`, `=IF`), dynamic conditional formatting, and executive KPI cards.

### 6. Lack of Executive Decision Support
* **Problem**: Senior management cannot interactively simulate "what-if" budget scenarios or understand the impact of risk-tolerance policies on operational costs.
* **Solution**: Deployed an interactive 3-tab **Streamlit web application** (`app.py`) allowing users to adjust risk thresholds on the fly and monitor real-time cost curves.

---

## 📊 Dataset Provenance & Specifications

This platform is grounded on a world-class, real-world industrial benchmark dataset:

* **Dataset Name**: [APS Failure at Heavy Trucks Dataset](https://www.kaggle.com/datasets/uciml/aps-failure-at-scania-trucks-data-set)
* **Origin / Publisher**: **Scania AB** (Sweden, global manufacturer of heavy commercial vehicles) in collaboration with the **UCI Machine Learning Repository** and the International Symposium on Intelligent Data Analysis (IDA 2016).
* **Dataset Scale**:
  * 60,000 operational training logs and 16,000 testing logs.
  * 171 raw telemetry attributes representing anonymized operational sensor readings (pneumatic pressure levels, compressor operating temperature, solenoid valve actuation counters, engine torque, oil counters).
* **Class Imbalance**: Highly skewed (~59 healthy records per 1 failure record), mirroring realistic heavy industry operational environments.
* **Why This Dataset?**: It is the global standard benchmark for industrial predictive maintenance because Scania defined the exact real-world business cost metric ($10 vs $500), bridging the gap between statistical machine learning and financial decision-making.

---

## 🏗️ System Architecture & Workflow

```
heavy-truck-fleet-predictive-analytics/
├── data/
│   ├── raw/                           # Kaggle Scania APS dataset (44.6 MB)
│   ├── fleet_operations.db            # SQLite relational database (Master, Telemetry, Work Orders, Budget)
│   └── Fleet_Performance_Report.xlsx  # Generated corporate Excel workbook with native formulas
├── src/
│   ├── database/
│   │   ├── schema.sql                 # Relational DDL (4 tables with foreign keys)
│   │   └── db_manager.py              # SQLite seeding engine and querying abstraction
│   ├── analytics/
│   │   ├── kpi_calculator.py          # Operational KPIs: PA%, MTBF, Breakdown rates, Budget variance
│   │   └── cost_optimizer.py          # Prescriptive cost curve generator ($10 vs $500 trade-off)
│   ├── ml/
│   │   ├── preprocessor.py            # Missing value filter, Median Imputation, and RobustScaler (IQR)
│   │   └── model.py                   # HistGradientBoosting classifier with balanced class weighting
│   └── reporting/
│       └── excel_exporter.py          # Corporate openpyxl engine with native Excel formulas
├── app.py                             # Interactive 3-Tab Streamlit web dashboard
├── requirements.txt                   # Dependency specifications
└── README.md                          # Repository documentation
```

---

## 🚀 Empirical Results & Quantitative Impact

| Evaluation Dimension | Default Baseline ($p = 0.50$) | Prescriptive Optimal ($p^* = 0.029$) | Realized Business Impact |
|:---|:---:|:---:|:---|
| **ROC-AUC Score** | `0.9870` | `0.9870` | Near-perfect class separability |
| **Recall / Sensitivity** | `91.60%` | `95.20%` | Catches 95%+ of impending failures |
| **Catastrophic Breakdowns (FN)** | `21 units` | **12 units** | **-42.9% reduction in road stoppages** |
| **Proactive Inspections (FP)** | `35 units` | `78 units` | Scheduled cheap workshop visits |
| **Total Maintenance Cost** | `$10,850.00` | **$6,780.00** | **$4,070.00 Net Savings (37.5% Cost Reduction)** |

---

## 💻 Interactive Streamlit Dashboard

Launchable locally via `streamlit run app.py`, the user interface contains 3 interactive tabs:

1. **📊 Fleet Health & Operational KPIs**:
   * Live cards: Physical Availability (`PA = 99.34%`), MTBF (`4,087.1 hrs`), Breakdowns (`7 units`), Maintenance Spend (`$4,090.00`).
   * Grouped Plotly bar chart comparing allocated budget vs actual cost variance across periods.
   * Master fleet table with dynamic filtering by model (Scania R500, Volvo FMX, Mercedes Actros).
2. **🤖 Predictive Maintenance & Sensor Diagnostics**:
   * Interactive telemetry diagnosis panel simulating 162 sensor features.
   * Real-time failure probability gauge meter with prescriptive threshold lines ($p^* = 2.9\%$).
   * Automated dispatch action banner (*Safe to Haul* vs *Immediate Workshop Inspection*).
3. **💰 Prescriptive Cost Optimizer & Budget Simulator**:
   * Interactive threshold slider ($p \in [0.01, 0.50]$) to simulate executive risk appetite.
   * Real-time recalculation of roadside breakdown costs vs inspection costs.
   * Plotly interactive Cost vs Threshold curve showing the global minimum at $p^* = 0.029$.
4. **📥 Corporate Excel Export**:
   * One-click download button in the sidebar generating `Fleet_Performance_Report.xlsx` on the fly.

---

## 🛠️ Quickstart & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/hikalputra12/heavy-truck-fleet-predictive-analytics.git
cd heavy-truck-fleet-predictive-analytics
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database & Seed Operational Telemetry
```bash
python src/database/db_manager.py
```

### 4. Run the Web Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
