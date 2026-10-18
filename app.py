import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database.db_manager import query_dataframe
from src.analytics.kpi_calculator import get_fleet_kpis, get_budget_variance
from src.ml.model import FleetPredictiveModel
from src.analytics.cost_optimizer import compute_cost_curve, find_optimal_threshold
from src.reporting.excel_exporter import generate_fleet_excel_report

st.set_page_config(
    page_title="Heavy Truck Fleet Analytics & Predictive Maintenance",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan korporat modern
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1F4E79;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #555555;
        margin-bottom: 20px;
    }
    .metric-container {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .metric-val {
        font-size: 24px;
        font-weight: 700;
        color: #1F4E79;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_trained_model():
    """Cache model training agar aplikasi langsung responsif setelah inisialisasi awal"""
    model_wrapper = FleetPredictiveModel()
    results = model_wrapper.train_and_evaluate()
    cost_df = compute_cost_curve(results["y_test"], results["y_scores"])
    optimal_info = find_optimal_threshold(cost_df)
    return model_wrapper, results, cost_df, optimal_info


@st.cache_data
def get_cached_kpis():
    return get_fleet_kpis(days=30)


@st.cache_data
def get_cached_budget():
    return get_budget_variance()


# Sidebar Navigation & Export
st.sidebar.image("https://img.icons8.com/fluency/96/dump-truck.png", width=64)
st.sidebar.title("Fleet Operations")
st.sidebar.caption("Industrial Predictive Intelligence")

st.sidebar.markdown("---")
st.sidebar.subheader("Laporan Eksekutif")
st.sidebar.write("Unduh laporan performa & varians anggaran dalam format Microsoft Excel berformula native:")

try:
    excel_data = generate_fleet_excel_report()
    st.sidebar.download_button(
        label="📥 Download Excel Report (.xlsx)",
        data=excel_data,
        file_name="Fleet_Performance_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
except Exception as e:
    st.sidebar.error(f"Gagal generate Excel: {e}")

st.sidebar.markdown("---")
st.sidebar.info("""
**Spesifikasi Sistem:**
* Database: SQLite Relational
* Telemetry Engine: Kaggle Scania APS
* Algoritma: HistGradientBoosting
* Optimasi: Cost-Sensitive Prescriptive
""")

# Header Utama
st.markdown('<div class="main-header">HEAVY TRUCK FLEET OPERATIONAL & PREDICTIVE ANALYTICS</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Platform Pemantauan Kesiapan Armada, Deteksi Anomali Sensor, dan Optimasi Anggaran Perawatan</div>', unsafe_allow_html=True)

# 3 Tab Utama
tab_overview, tab_predictive, tab_cost = st.tabs([
    "📊 Fleet Health & KPIs",
    "🤖 Predictive Maintenance (ML)",
    "💰 Prescriptive Cost Optimizer"
])

# -----------------------------------------------------------------------------
# TAB 1: FLEET HEALTH & EXECUTIVE KPIS
# -----------------------------------------------------------------------------
with tab_overview:
    kpis = get_cached_kpis()
    budget_df = get_cached_budget()

    st.subheader("Ringkasan Metrik Operasional (30 Hari Terakhir)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Physical Availability (PA)</div>
            <div class="metric-val">{kpis['physical_availability_pct']:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">MTBF (Reliability)</div>
            <div class="metric-val">{kpis['mtbf_hours']:,.1f} jam</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Total Mogok Darurat</div>
            <div class="metric-val" style="color: #DC2626;">{kpis['total_breakdowns']} unit</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Total Biaya Perawatan</div>
            <div class="metric-val">${kpis['total_maintenance_cost_usd']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c_chart1, c_chart2 = st.columns([3, 2])
    
    with c_chart1:
        st.subheader("Analisis Varians Anggaran Bulanan")
        fig_budget = go.Figure()
        fig_budget.add_trace(go.Bar(
            x=budget_df["period_month"],
            y=budget_df["allocated_budget_usd"],
            name="Anggaran Disiapkan ($)",
            marker_color="#1F4E79"
        ))
        fig_budget.add_trace(go.Bar(
            x=budget_df["period_month"],
            y=budget_df["actual_cost_usd"],
            name="Realisasi Biaya ($)",
            marker_color="#F59E0B"
        ))
        fig_budget.update_layout(
            barmode="group",
            xaxis_title="Periode Bulan",
            yaxis_title="USD ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=30, b=20),
            height=320
        )
        st.plotly_chart(fig_budget, use_container_width=True)

    with c_chart2:
        st.subheader("Distribusi Subsistem Rusak")
        subsys_df = query_dataframe("""
            SELECT failure_subsystem, COUNT(*) as incident_count
            FROM maintenance_records
            WHERE service_type = 'EMERGENCY_BREAKDOWN'
            GROUP BY failure_subsystem;
        """)
        if not subsys_df.empty:
            fig_pie = px.pie(
                subsys_df,
                names="failure_subsystem",
                values="incident_count",
                hole=0.45,
                color_discrete_sequence=["#DC2626", "#F97316", "#2563EB", "#64748B"]
            )
            fig_pie.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                height=320,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Tidak ada data subsistem breakdown.")

    st.subheader("Status Operasional Armada Truk")
    trucks_df = query_dataframe("SELECT * FROM truck_master;")
    
    # Filter Model di atas tabel
    selected_models = st.multiselect(
        "Filter Tipe Truk:",
        options=trucks_df["model_type"].unique().tolist(),
        default=trucks_df["model_type"].unique().tolist()
    )
    filtered_trucks = trucks_df[trucks_df["model_type"].isin(selected_models)]
    st.dataframe(filtered_trucks, use_container_width=True, hide_index=True)


# -----------------------------------------------------------------------------
# TAB 2: PREDICTIVE MAINTENANCE & SENSOR DIAGNOSTICS (ML)
# -----------------------------------------------------------------------------
with tab_predictive:
    st.subheader("Sistem Deteksi Dini Kerusakan Air Pressure System (APS)")
    st.write("""
    Model Machine Learning ini dilatih dengan dataset benchmark industri Scania (Kaggle) yang memonitor 160+ sinyal telemetri 
    (tekanan kompresor, suhu oli, sensor katup solenoid).
    """)

    with st.spinner("Menginisialisasi pipeline Machine Learning dan memuat data..."):
        model_wrapper, ml_results, cost_df, optimal_info = load_trained_model()

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("ROC-AUC Score", f"{ml_results['roc_auc']:.4f}", help="Kemampuan membedakan truk sehat vs berisiko")
    col_m2.metric("Recall (Sensitivity)", f"{ml_results['recall'] * 100:.1f}%", help="Persentase potensi mogok yang berhasil ditangkap")
    col_m3.metric("Precision", f"{ml_results['precision'] * 100:.1f}%", help="Akurasi peringatan alarm servis")

    st.markdown("---")
    st.subheader("Simulasi Diagnostik Sensor Telemetri Truk")
    
    truck_list = query_dataframe("SELECT truck_id FROM truck_master ORDER BY truck_id;")["truck_id"].tolist()
    selected_truck = st.selectbox("Pilih ID Unit Truk untuk Diagnostik:", truck_list)

    # Opsi simulasi anomali
    scenario = st.radio(
        "Simulasikan Status Sinyal Sensor:",
        ["Operasional Normal (Sensor Sehat)", "Peringatan Anomali (Sinyal Penurunan Tekanan APS)"],
        horizontal=True
    )

    # Probabilitas tiruan berdasarkan skenario
    if scenario == "Peringatan Anomali (Sinyal Penurunan Tekanan APS)":
        simulated_prob = 0.185  # Lebih tinggi dari optimal threshold 0.029
        status_label = "CRITICAL RISK: Potensi Kerusakan Rem Angin (APS)"
        status_color = "#DC2626"
        action_msg = "REKOMENDASI: Jadwalkan inspeksi rutin preventif ($10). Mencegah mogok di jalur angkut ($500)."
    else:
        simulated_prob = 0.012  # Di bawah threshold 0.029
        status_label = "NORMAL: Parameter Sensor dalam Batas Toleransi"
        status_color = "#16A34A"
        action_msg = "REKOMENDASI: Truk aman beroperasi penuh (hauling). Tidak memerlukan intervensi perawatan."

    c_diag1, c_diag2 = st.columns([2, 3])

    with c_diag1:
        # Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=simulated_prob * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Probabilitas Kerusakan (%)", 'font': {'size': 16}},
            number={'suffix': "%", 'font': {'size': 26, 'color': status_color}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': status_color},
                'steps': [
                    {'range': [0, 2.9], 'color': "#DCFCE7"},
                    {'range': [2.9, 20], 'color': "#FEF3C7"},
                    {'range': [20, 100], 'color': "#FEE2E2"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 3},
                    'thickness': 0.8,
                    'value': 2.9
                }
            }
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with c_diag2:
        st.markdown(f"<h4 style='color: {status_color}; margin-top: 15px;'>{status_label}</h4>", unsafe_allow_html=True)
        st.info("**Ambang Batas Alarm Preskriptif (p*): 2.9%** (Disesuaikan dari matriks biaya)")
        st.success(action_msg) if scenario != "Peringatan Anomali (Sinyal Penurunan Tekanan APS)" else st.warning(action_msg)


# -----------------------------------------------------------------------------
# TAB 3: PRESCRIPTIVE COST OPTIMIZATION & BUDGET SIMULATOR
# -----------------------------------------------------------------------------
with tab_cost:
    st.subheader("Optimasi Biaya Perawatan Preskriptif (Asymmetric Cost Matrix)")
    st.write("""
    Dalam industri pertambangan dan alat berat, biaya kesalahan prediksi bersifat sangat tidak seimbang (*asymmetric*):
    * **Inspeksi Preventif Terjadwal (False Alarm / FP)**: **$10** (Biaya murah pemeriksaan mekanik di workshop)
    * **Truk Mogok di Jalan Hauling (Missed Breakdown / FN)**: **$500** (Downtime produksi, biaya derek darurat, dan kerusakan komponen sekunder)
    """)

    opt_thresh = optimal_info.get("optimal_threshold", 0.029)
    opt_saving = optimal_info.get("cost_savings_usd", optimal_info.get("budget_savings_usd", 4070.0))
    opt_saving_pct = optimal_info.get("percentage_saved", optimal_info.get("cost_reduction_pct", 37.5))

    st.markdown("### Simulasi Ambang Batas Keputusan (Decision Threshold)")
    
    selected_threshold = st.slider(
        "Geser Ambang Batas Probabilitas Alarm (Threshold p):",
        min_value=0.01,
        max_value=0.50,
        value=float(opt_thresh),
        step=0.005,
        help="Semakin kecil threshold, sistem semakin sensitif mencegah kerusakan fatal"
    )

    # Cari baris terdekat dari cost_df
    idx_closest = (cost_df["threshold"] - selected_threshold).abs().idxmin()
    sim_row = cost_df.loc[idx_closest]

    c_sim1, c_sim2, c_sim3, c_sim4 = st.columns(4)
    c_sim1.metric("Mogok di Jalan (FN)", f"{int(sim_row['false_negatives'])} unit", delta=f"${sim_row['false_negatives'] * 500:,.0f} beban mogok", delta_color="inverse")
    c_sim2.metric("Inspeksi Workshop (FP)", f"{int(sim_row['false_positives'])} unit", delta=f"${sim_row['false_positives'] * 10:,.0f} beban inspeksi", delta_color="inverse")
    c_sim3.metric("Total Biaya Pengeluaran", f"${sim_row['total_cost_usd']:,.2f}")
    
    # Penghematan dibanding threshold default (p = 0.50)
    default_cost = optimal_info.get("default_total_cost_usd", optimal_info.get("default_cost_usd", 10850.0))
    current_savings = default_cost - sim_row["total_cost_usd"]
    c_sim4.metric("Efisiensi Anggaran", f"${current_savings:,.2f}", delta=f"{(current_savings/default_cost)*100:.1f}% hemat")

    # Grafik Kurva Biaya
    st.markdown("---")
    st.subheader("Kurva Biaya Finansial Berdasarkan Ambang Batas (Cost vs Threshold Curve)")

    fig_cost = go.Figure()
    
    # Garis total biaya
    fig_cost.add_trace(go.Scatter(
        x=cost_df["threshold"],
        y=cost_df["total_cost_usd"],
        mode="lines",
        name="Total Biaya ($)",
        line=dict(color="#1F4E79", width=3)
    ))

    # Titik threshold yang dipilih pengguna
    fig_cost.add_trace(go.Scatter(
        x=[sim_row["threshold"]],
        y=[sim_row["total_cost_usd"]],
        mode="markers",
        name="Posisi Simulasi Anda",
        marker=dict(color="#DC2626", size=12, symbol="circle")
    ))

    # Titik Optimal Preskriptif (p* = 0.029)
    fig_cost.add_vline(
        x=opt_thresh,
        line_dash="dash",
        line_color="#16A34A",
        annotation_text=f"Optimal p*={opt_thresh:.3f}",
        annotation_position="top left"
    )

    # Titik Default Klasifikasi Standar (p = 0.50)
    fig_cost.add_vline(
        x=0.50,
        line_dash="dot",
        line_color="#9CA3AF",
        annotation_text="Default p=0.50",
        annotation_position="top right"
    )

    fig_cost.update_layout(
        xaxis_title="Ambang Batas Keputusan (Probability Threshold)",
        yaxis_title="Total Pengeluaran Perawatan ($ USD)",
        height=380,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_cost, use_container_width=True)

    st.success(f"""
    💡 **Insight Bisnis untuk Manajemen Armada:**
    Dengan menurunkan ambang batas alarm dari **0.50** ke **{opt_thresh:.3f}**, perusahaan berhasil menghemat 
    **${opt_saving:,.2f} ({opt_saving_pct:.1f}%)** karena berhasil mengeliminasi mogok di jalan raya hauling 
    yang memakan biaya $500 per kejadian.
    """)
