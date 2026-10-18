import os
import sys
from datetime import datetime, timedelta
import pandas as pd

# Pastikan Python dapat menemukan folder src saat file ini dijalankan langsung
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from src.database.db_manager import query_dataframe


def get_fleet_kpis(days=30):
    """
    Menghitung KPI utama performa armada (PA, MTBF, dan biaya perawatan) 
    dalam rentang hari tertentu
    """
    # Total unit truk yang aktif beroperasi
    df_trucks = query_dataframe("SELECT COUNT(*) AS total_trucks FROM truck_master WHERE operational_status != 'RETIRED';")
    total_trucks = int(df_trucks["total_trucks"].iloc[0]) if not df_trucks.empty else 0

    # Catatan perbaikan dan mogok dalam rentang periode
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    df_maint = query_dataframe("""
        SELECT service_type, downtime_hours, actual_cost_usd, failure_subsystem
        FROM maintenance_records
        WHERE inspection_date >= ?;
    """, (start_date,))

    # Pemisahan kategori servis: mogok darurat vs servis preventif terencana
    breakdown_df = df_maint[df_maint["service_type"] == "EMERGENCY_BREAKDOWN"]
    preventive_df = df_maint[df_maint["service_type"] == "PREVENTIVE_INSPECTION"]

    total_breakdowns = len(breakdown_df)
    total_preventive = len(preventive_df)
    total_downtime_hours = float(df_maint["downtime_hours"].sum()) if not df_maint.empty else 0.0
    total_maintenance_cost = float(df_maint["actual_cost_usd"].sum()) if not df_maint.empty else 0.0

    # Total jam terjadwal: total unit * jumlah hari * 24 jam
    total_scheduled_hours = total_trucks * days * 24.0
    operating_hours = max(0.0, total_scheduled_hours - total_downtime_hours)

    # Physical Availability (PA): Rasio kesiapan unit (%)
    physical_availability = (operating_hours / total_scheduled_hours * 100.0) if total_scheduled_hours > 0 else 100.0

    # Mean Time Between Failures (MTBF): Rata-rata jam operasional antar insiden mogok
    mtbf = (operating_hours / total_breakdowns) if total_breakdowns > 0 else operating_hours

    # Deteksi unit kritis dari pembacaan sensor terakhir yang perlu diwaspadai
    df_critical = query_dataframe("""
        SELECT COUNT(DISTINCT truck_id) AS critical_count
        FROM telemetry_logs
        WHERE status_label = 'CRITICAL' AND timestamp >= ?;
    """, (start_date,))
    critical_units = int(df_critical["critical_count"].iloc[0]) if not df_critical.empty else 0

    return {
        "period_days": days,
        "total_trucks": total_trucks,
        "physical_availability_pct": round(physical_availability, 2),
        "mtbf_hours": round(mtbf, 1),
        "total_breakdowns": total_breakdowns,
        "total_preventive_inspections": total_preventive,
        "total_downtime_hours": round(total_downtime_hours, 1),
        "total_maintenance_cost_usd": round(total_maintenance_cost, 2),
        "critical_units_at_risk": critical_units
    }


def get_weekly_trend():
    """
    Menghasilkan agregasi mingguan untuk melihat tren jumlah mogok, 
    servis rutin, biaya mingguan, dan total jam unit berhenti operasi
    """
    df = query_dataframe("""
        SELECT 
            strftime('%Y-W%W', inspection_date) AS week_period,
            COUNT(CASE WHEN service_type = 'EMERGENCY_BREAKDOWN' THEN 1 END) AS emergency_breakdowns,
            COUNT(CASE WHEN service_type = 'PREVENTIVE_INSPECTION' THEN 1 END) AS preventive_inspections,
            SUM(actual_cost_usd) AS weekly_cost_usd,
            SUM(downtime_hours) AS weekly_downtime_hours
        FROM maintenance_records
        GROUP BY week_period
        ORDER BY week_period ASC;
    """)
    return df


def get_downtime_by_subsystem():
    """
    Mengelompokkan penyebab downtime berdasarkan subsistem kendaraan 
    (Air Pressure System, Rem, Kompresor, atau Katup)
    """
    df = query_dataframe("""
        SELECT 
            failure_subsystem,
            COUNT(*) AS incident_count,
            SUM(downtime_hours) AS total_downtime_hours,
            SUM(actual_cost_usd) AS total_cost_usd
        FROM maintenance_records
        GROUP BY failure_subsystem
        ORDER BY total_cost_usd DESC;
    """)
    return df


def get_budget_variance():
    """
    Membandingkan anggaran bulanan yang direncanakan dengan realisasi biaya perawatan 
    untuk menghitung surplus atau defisit anggaran
    """
    df = query_dataframe("""
        SELECT 
            b.period_month,
            b.allocated_budget_usd,
            COALESCE(SUM(m.actual_cost_usd), 0.0) AS actual_cost_usd,
            (b.allocated_budget_usd - COALESCE(SUM(m.actual_cost_usd), 0.0)) AS variance_budget_usd,
            b.target_fleet_availability
        FROM budget_plan b
        LEFT JOIN maintenance_records m 
            ON strftime('%Y-%m', m.inspection_date) = b.period_month
        GROUP BY b.period_month
        ORDER BY b.period_month ASC;
    """)
    return df


if __name__ == "__main__":
    print("Menghitung KPI Eksekutif Armada (30 Hari Terakhir):")
    kpis = get_fleet_kpis()
    for key, val in kpis.items():
        print(f"  {key}: {val}")
    
    print("\nAnalisis Varians Anggaran Perawatan Bulanan:")
    print(get_budget_variance())