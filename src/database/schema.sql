-- Master Data: Daftar Aset Armada Truk
CREATE TABLE IF NOT EXISTS truck_master (
    truck_id VARCHAR(20) PRIMARY KEY,
    model_type VARCHAR(50) NOT NULL,
    commissioning_year INTEGER NOT NULL,
    odometer_km REAL NOT NULL,
    base_depot VARCHAR(50) NOT NULL,
    rated_payload_tons REAL NOT NULL,
    operational_status VARCHAR(20) DEFAULT 'ACTIVE' -- ACTIVE, IN_WORKSHOP, RETIRED
);

-- Telemetry Logs: Data Sensor Berkala (Air Pressure System, Suhu, Getaran)
CREATE TABLE IF NOT EXISTS telemetry_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_id VARCHAR(20) NOT NULL,
    timestamp DATETIME NOT NULL,
    air_pressure_bar REAL NOT NULL,           -- Tekanan angin utama (Normal: 8.0 - 12.0 bar)
    compressor_temp_c REAL NOT NULL,         -- Suhu kompresor (Normal: 65 - 95 °C)
    vibration_rms REAL NOT NULL,              -- Getaran mesin RMS (Normal: 1.5 - 3.5 mm/s)
    valve_actuation_counter INTEGER NOT NULL, -- Siklus kerja katup pneumatik
    operating_hours REAL NOT NULL,            -- Total jam jalan mesin
    predicted_risk_score REAL DEFAULT 0.0,    -- Skor probabilitas risiko dari Machine Learning
    status_label VARCHAR(20) DEFAULT 'HEALTHY', -- HEALTHY, WATCH, CRITICAL
    FOREIGN KEY (truck_id) REFERENCES truck_master(truck_id)
);

-- Maintenance Records: Catatan Servis Bengkel & Insiden Mogok
CREATE TABLE IF NOT EXISTS maintenance_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_id VARCHAR(20) NOT NULL,
    inspection_date DATE NOT NULL,
    service_type VARCHAR(50) NOT NULL,        -- PREVENTIVE_INSPECTION ($10) vs EMERGENCY_BREAKDOWN ($500)
    failure_subsystem VARCHAR(50),            -- AIR_PRESSURE_SYSTEM, BRAKES, COMPRESSOR, VALVES, NONE
    downtime_hours REAL NOT NULL,             -- Jam unit berhenti operasi
    actual_cost_usd REAL NOT NULL,            -- Biaya riil ($10 inspeksi / $500 mogok jalan)
    mechanic_notes TEXT,
    FOREIGN KEY (truck_id) REFERENCES truck_master(truck_id)
);

-- Budget Plan: Perencanaan Anggaran Bulanan & Target KPI
CREATE TABLE IF NOT EXISTS budget_plan (
    period_month VARCHAR(7) PRIMARY KEY,      -- Format: YYYY-MM (misal: 2026-10)
    allocated_budget_usd REAL NOT NULL,       -- Total anggaran perawatan yang dialokasikan
    target_fleet_availability REAL NOT NULL,  -- Target Kesiapan Fisik Armada (misal: 92.0%)
    target_mtbf_hours REAL NOT NULL,          -- Target Mean Time Between Failures (misal: 350 jam)
    emergency_cost_ceiling_usd REAL NOT NULL  -- Batas toleransi maksimal biaya darurat
);

-- Indeks kueri untuk mempercepat pencarian data
CREATE INDEX IF NOT EXISTS idx_telemetry_truck ON telemetry_logs(truck_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_time ON telemetry_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_maintenance_date ON maintenance_records(inspection_date);