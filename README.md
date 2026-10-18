# Heavy Truck Fleet Predictive Maintenance & Cost Analytics

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange.svg)](https://scikit-learn.org/)

An end-to-end industrial data engineering and predictive analytics platform for heavy commercial and mining haulage fleets. This project integrates relational fleet telematics modeling, operational availability tracking, cost-sensitive machine learning for early failure detection, and prescriptive maintenance budget optimization.

---

## 📌 Project Overview & Industry Background

In capital-intensive industries such as mining haulage, quarrying, and heavy logistics, **fleet reliability and physical availability directly dictate production throughput**. Unplanned equipment downtime leads to severe operational bottlenecks, haul road blockages, and exorbitant repair costs.

A critical vulnerability in heavy haul trucks is the **Air Pressure System (APS)**, which powers the pneumatic brake system and gear controls. A sudden roadside failure risks vehicle runaway or immediate halting on active pit lanes.

### The Business Challenge: Asymmetric Failure Costs
Standard machine learning models optimize for symmetrical metrics (like accuracy), treating all errors equally. In heavy fleet maintenance, errors carry drastically asymmetric financial penalties:
* **False Positive (Type I Error)**: The model flags a healthy truck as risky. Cost: **$10** (a quick 15-minute diagnostic inspection by workshop technicians).
* **False Negative (Type II Error)**: The model misses an impending breakdown. Cost: **$500+** (emergency road assistance, lowboy towing from hauling roads, secondary component damage, and production loss).

This platform solves this challenge by shifting from passive classification to **prescriptive threshold optimization**, identifying the mathematically optimal decision boundary that minimizes total fleet maintenance spend.

---

## 🏗️ System Architecture

The project consists of 6 core modular components:

```
heavy-truck-fleet-predictive-analytics/
├── data/
│   ├── raw/                           # Raw benchmark telemetry (Kaggle Scania APS dataset)
│   ├── fleet_operations.db            # SQLite relational database (Master, Telemetry, Maintenance, Budget)
│   └── Fleet_Performance_Report.xlsx  # Generated executive Excel report with native formulas
├── src/
│   ├── database/
│   │   ├── schema.sql                 # 4 relational tables (DDL)
│   │   └── db_manager.py              # Database seeding, foreign keys, and query engine
│   ├── analytics/
│   │   ├── kpi_calculator.py          # PA%, MTBF, Breakdown counts, and budget variance
│   │   └── cost_optimizer.py          # Prescriptive cost-curve generator ($10 vs $500 trade-off)
│   ├── ml/
│   │   ├── preprocessor.py            # Robust scaling, median imputation, and feature filtering
│   │   └── model.py                   # HistGradientBoosting with class-weight balancing
│   └── reporting/
│       └── excel_exporter.py          # Corporate openpyxl report engine with Excel formulas
├── app.py                             # Interactive 3-Tab Streamlit web dashboard
├── requirements.txt                   # Production dependencies
└── README.md                          # Project documentation
```

---

## 🚀 Key Results & Impact

| Metric / Evaluation Dimension | Baseline (Default $p = 0.50$) | Prescriptive Optimal ($p^* = 0.029$) | Impact |
|:---|:---:|:---:|:---|
| **ROC-AUC Score** | `0.9870` | `0.9870` | Exceptional class separability |
| **Recall / Sensitivity** | `91.60%` | `95.20%` | Eliminates critical roadside failures |
| **Catastrophic Roadside Failures (FN)** | `21 units` | **12 units** | **-42.9% reduction in breakdowns** |
| **Preventive Workshop Inspections (FP)** | `35 units` | `78 units` | Proactive scheduled interventions |
| **Total Maintenance Expenditure** | `$10,850.00` | **$6,780.00** | **$4,070.00 Saved (37.5% Cost Reduction)** |

---

## 💻 Interactive Streamlit Dashboard

The platform features an executive web interface built in Streamlit (`app.py`), structured into 3 functional modules:

1. **📊 Fleet Health & Operational KPIs**:
   * Executive metric cards: Physical Availability (`PA = 99.34%`), Mean Time Between Failures (`MTBF = 4,087.1 hrs`), and Breakdown counts.
   * Monthly budget variance chart comparing allocated CAPEX/OPEX vs actual maintenance expenses.
   * Master fleet table with dynamic truck model filtering (Scania R500, Volvo FMX, Mercedes Actros).
2. **🤖 Predictive Maintenance & Sensor Diagnostics**:
   * Telemetry diagnostic panel simulating live sensor readings across 162 vehicle telemetry parameters.
   * Real-time failure probability gauge meter with automated alert flags.
   * Actionable dispatch recommendations: *Safe to Haul* vs *Immediate Workshop Inspection*.
3. **💰 Prescriptive Cost Optimizer & Budget Simulator**:
   * Interactive threshold slider ($p \in [0.01, 0.50]$) allowing executives to simulate risk tolerance.
   * Dynamic recalculation of roadside breakdown penalties vs routine inspection costs.
   * Cost vs Threshold curve showing exact empirical global minimum ($p^* = 0.029$).
4. **📥 Corporate Excel Export**:
   * One-click download button in the sidebar generating a native `.xlsx` workbook featuring executive KPI cards, summary totals, and automated `=SUM`, `=AVERAGE`, and `=IF` status formulas.

---

## 🛠️ Installation & Quickstart

### Prerequisites
* Python 3.10, 3.11, or 3.12 (Python 3.13 supported)
* Git

### 1. Clone the Repository
```bash
git clone https://github.com/hikalputra12/heavy-truck-fleet-predictive-analytics.git
cd heavy-truck-fleet-predictive-analytics
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database & Seed Operational Records
```bash
python src/database/db_manager.py
```

### 4. Launch the Interactive Web Dashboard
```bash
streamlit run app.py
```
The application will launch automatically in your browser at `http://localhost:8501`.

---

## 📊 Benchmark Dataset

* **Source**: Scania AB APS Failure at Heavy Trucks Dataset (UCI Machine Learning Repository / Kaggle).
* **Scope**: 170 anonymized telemetry sensor readings (pneumatic pressure, engine temperature, torque, fluid counters) across heavy commercial trucks.
* **Class Imbalance**: Highly skewed operational dataset (~1:59 ratio of failures to normal operations), mirroring realistic heavy industrial operating conditions.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
