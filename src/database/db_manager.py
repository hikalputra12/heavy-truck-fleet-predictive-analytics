import os
import sqlite3
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Path database dan skema SQL
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "fleet_operations.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


def get_connection(db_path=DB_PATH):
    """Membuka koneksi ke database SQLite lokal dan mengaktifkan foreign key"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database(db_path=DB_PATH, schema_path=SCHEMA_PATH):
    """Membaca schema.sql dan membuat tabel relasional di SQLite"""
    conn = get_connection(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()


def seed_fleet_data(db_path=DB_PATH, num_trucks=40, days=30):
    """
    Mengisi data awal armada truk dan telemetri sensor berdasarkan 
    karakteristik fisik dataset industri Scania APS Failure
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Cek apakah database sudah terisi sebelumnya agar tidak duplikat
    cursor.execute("SELECT COUNT(*) FROM truck_master;")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Master armada truk
    truck_models = ["Scania R450 Heavy Hauler", "Scania G410 Transport", "Scania P380 Heavy Duty"]
    depots = ["Depot-Balikpapan-North", "Depot-Samarinda-Hub", "Depot-Tanjung-Enim"]
    
    truck_ids = [f"TRK-{i:03d}" for i in range(1, num_trucks + 1)]
    truck_rows = []
    
    for t_id in truck_ids:
        model = random.choice(truck_models)
        year = random.randint(2019, 2024)
        mileage = random.uniform(80000, 320000)
        depot = random.choice(depots)
        payload = 45.0 if "P380" in model else (65.0 if "G410" in model else 80.0)
        truck_rows.append((t_id, model, year, round(mileage, 1), depot, payload, "ACTIVE"))

    cursor.executemany("""
        INSERT INTO truck_master (truck_id, model_type, commissioning_year, odometer_km, base_depot, rated_payload_tons, operational_status)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, truck_rows)

    # Telemetri harian & riwayat servis
    base_date = datetime.now() - timedelta(days=days)
    telemetry_rows = []
    maintenance_rows = []

    for t_id in truck_ids:
        # Simulasi: sebagian kecil unit (~15%) mengalami degradasi sistem rem angin
        is_prone_to_failure = random.random() < 0.15
        current_hours = random.uniform(2500, 12000)
        
        for d in range(days):
            date_curr = base_date + timedelta(days=d)
            
            if is_prone_to_failure and d > (days - random.randint(3, 8)):
                # Kondisi anomali: tekanan angin drop (<8 bar), suhu kompresor melonjak (>100 C)
                air_pressure = max(4.5, np.random.normal(6.2, 0.8))
                comp_temp = min(118.0, np.random.normal(104.0, 5.0))
                vibration = np.random.normal(4.8, 0.7)
                valve_count = random.randint(180, 260)
                risk_score = round(random.uniform(0.75, 0.96), 3)
                status_label = "CRITICAL"
                
                # Truk mogok darurat di jalan jika tidak tertangani tepat waktu
                if d == days - 2:
                    maintenance_rows.append((
                        t_id, date_curr.strftime("%Y-%m-%d"), "EMERGENCY_BREAKDOWN", 
                        "AIR_PRESSURE_SYSTEM", 14.5, 500.0,
                        "Tekanan angin drop mendadak di jalan. Derek darurat dan penggantian modul katup."
                    ))
            else:
                # Kondisi operasional normal
                air_pressure = np.random.normal(10.2, 0.5)
                comp_temp = np.random.normal(78.0, 4.0)
                vibration = np.random.normal(2.2, 0.3)
                valve_count = random.randint(80, 130)
                risk_score = round(random.uniform(0.01, 0.07), 3)
                status_label = "HEALTHY"

                # Jadwal servis preventif rutin berkala ($10)
                if random.random() < 0.04:
                    maintenance_rows.append((
                        t_id, date_curr.strftime("%Y-%m-%d"), "PREVENTIVE_INSPECTION",
                        "NONE", 1.5, 10.0,
                        "Pemeriksaan kebocoran selang rem angin dan penggantian filter rutin."
                    ))

            current_hours += random.uniform(8.0, 14.0)
            telemetry_rows.append((
                t_id, date_curr.strftime("%Y-%m-%d %H:%M:%S"),
                round(float(air_pressure), 2), round(float(comp_temp), 1),
                round(float(vibration), 2), valve_count, round(float(current_hours), 1),
                risk_score, status_label
            ))

    cursor.executemany("""
        INSERT INTO telemetry_logs (truck_id, timestamp, air_pressure_bar, compressor_temp_c, vibration_rms, valve_actuation_counter, operating_hours, predicted_risk_score, status_label)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, telemetry_rows)

    cursor.executemany("""
        INSERT INTO maintenance_records (truck_id, inspection_date, service_type, failure_subsystem, downtime_hours, actual_cost_usd, mechanic_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, maintenance_rows)

    # Rencana budget bulanan
    months = [
        (datetime.now() - timedelta(days=60)).strftime("%Y-%m"),
        (datetime.now() - timedelta(days=30)).strftime("%Y-%m"),
        datetime.now().strftime("%Y-%m")
    ]
    budget_rows = [
        (months[0], 25000.0, 92.0, 350.0, 8000.0),
        (months[1], 28000.0, 93.0, 360.0, 7500.0),
        (months[2], 30000.0, 94.0, 380.0, 6000.0)
    ]
    cursor.executemany("""
        INSERT INTO budget_plan (period_month, allocated_budget_usd, target_fleet_availability, target_mtbf_hours, emergency_cost_ceiling_usd)
        VALUES (?, ?, ?, ?, ?);
    """, budget_rows)

    conn.commit()
    conn.close()


def query_dataframe(sql, params=(), db_path=DB_PATH):
    """Mengeksekusi kueri SQL dan mengembalikan hasilnya sebagai Pandas DataFrame"""
    conn = get_connection(db_path)
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


if __name__ == "__main__":
    print("1. Menginisialisasi database dari schema.sql...")
    init_database()
    print("2. Mengisi data awal armada truk dan telemetri...")
    seed_fleet_data()
    print("Database siap di:", DB_PATH)
    
    # Tes verifikasi kueri SQL
    sample_df = query_dataframe("SELECT COUNT(*) AS total_trucks FROM truck_master;")
    print("Verifikasi: Total truk terdaftar =", sample_df["total_trucks"].iloc[0])