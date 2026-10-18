# Sistem Analitik Prediktif & Optimasi Biaya Perawatan Armada Truk Berat
### *(Heavy Truck Fleet Predictive Maintenance & Cost Analytics)*

[![Versi Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Lisensi](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-orange.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20Relational-lightgrey.svg)](https://sqlite.org/)

Platform rekayasa data industri (*industrial data engineering*), *machine learning*, dan sistem pelaporan eksekutif terintegrasi untuk pengelolaan armada truk muatan berat (*heavy haulage trucks*), operasional kontraktor pertambangan, dan logistik industri.

Proyek ini menggabungkan pemodelan basis data relasional telematika, pemantauan kesiapan unit (*fleet availability*), deteksi dini anomali sensor dengan *cost-sensitive machine learning*, optimasi anggaran perawatan preskriptif, serta otomasi pelaporan korporat Microsoft Excel.

---

## 📌 Latar Belakang Industri & Masalah Bisnis

Dalam industri padat modal seperti pertambangan terbuka (*open-pit mining*), penggalian (*quarrying*), dan transportasi material curah, **keandalan dan kesiapan fisik armada (*Physical Availability*) menentukan langsung kapasitas produksi harian**. Mogok mendadak pada truk pengangkut berkapasitas 40 hingga 100 ton tidak hanya menimbulkan biaya perbaikan mekanis, namun juga memblokir jalur angkut tambang (*haul road*), menghentikan rantai kerja alat gali (*excavator/shovel*), dan mengakibatkan kerugian finansial yang masif.

Salah satu komponen paling vital dan rawan pada truk muatan berat adalah **Sistem Rem Angin / Pneumatik (*Air Pressure System - APS*)**. Sistem APS berfungsi menghasilkan, mengeringkan, dan mendistribusikan udara bertekanan tinggi untuk:
* Menggerakkan sistem pengereman utama (*service brake*) dan rem darurat (*fail-safe spring brake*).
* Membantu perpindahan gigi transmisi otomatis armada berat.
* Mengatur suspensi udara dan katup penyeimbang beban (*load-leveling valves*).

Jika tekanan angin tiba-tiba hilang atau kompresor terkunci saat truk melintasi tanjakan atau turunan terjal di jalur tambang, sistem pengereman darurat akan terkunci seketika atau gagal mengerem, yang berisiko fatal terhadap keselamatan kerja dan terhentinya operasi *hauling*.

---

## 🎯 6 Masalah Nyata yang Diselesaikan oleh Platform Ini

Platform ini memecahkan **6 tantangan operasional, teknis data, dan finansial** yang umum dihadapi di industri alat berat:

### 1. Jebakan Akurasi Biasa pada Data Sangat Timpang (*Imbalanced Data*)
* **Masalah:** Pada operasional nyata, sekitar $98.4\%$ armada beroperasi sehat, dan hanya sekitar $1.6\%$ yang mengalami kerusakan komponen APS. Model Machine Learning konvensional yang dilatih tanpa penyesuaian akan selalu menebak "Truk Sehat" untuk seluruh armada. Akurasi statistiknya tampak memukau (**$98.4\%$**), namun model tersebut **gagal mendeteksi satu pun kerusakan**, sehingga semua truk bermasalah tetap beroperasi hingga akhirnya mogok di jalan tambang.
* **Solusi yang Diterapkan:** Membangun alur pra-pemrosesan data dengan penskalaan kokoh (*RobustScaler*) dan algoritma *HistGradientBoosting* dengan penyeimbang bobot kelas (*balanced class weights*). Model berhasil mencapai skor **ROC-AUC 0.9870** dan **Recall (Sensitivitas) 91.60%**, memastikan potensi kegagalan terdeteksi sebelum terjadi mogok.

### 2. Asimetri Biaya Kerusakan yang Sangat Jomplang ($10 vs $500)
* **Masalah:** Algoritma klasifikasi standar mengasumsikan konsekuensi kesalahan seimbang (menggunakan ambang batas default $p = 0.50$). Di lapangan, biaya kesalahan sangat asimetris:
  * **Alarm Palsu (*False Positive - FP*)**: Mengarahkan truk sehat ke bengkel hanya menghabiskan biaya **$10** (pemeriksaan rutin 15 menit oleh teknisi bengkel/workshop).
  * **Kerusakan Lolos (*False Negative - FN*)**: Membiarkan truk yang nyaris rusak tetap beroperasi mengakibatkan mogok di jalan dengan kerugian mencapai **$500+** (biaya derek alat berat *lowboy*, penalti antrean ritase, kerusakan komponen sekunder, dan waktu kerja mekanik darurat).
* **Solusi yang Diterapkan:** Menerapkan fungsi biaya preskriptif pada file `cost_optimizer.py`:
  $$\text{Total Biaya Perawatan} = (10 \times \text{False Positives}) + (500 \times \text{False Negatives})$$
  Melalui simulasi kurva biaya pada data uji, ambang batas probabilitas optimal ditemukan di angka **$p^* = 0.029$** (bukan 0.50). Penurunan ambang alarm ini terbukti:
  * Memangkas kejadian truk mogok di jalan sebesar **42.9%** (dari 21 unit menjadi 12 unit).
  * Menghemat total anggaran perawatan sebesar **$4,070.00 (Efisiensi 37.5%)**, dari $10,850.00 turun menjadi $6,780.00 per siklus evaluasi.

### 3. Fragmentasi Data Operasional (Data Tercecer Tanpa Relasi)
* **Masalah:** Seringkali data pembacaan sensor IoT/telematika terisolasi dalam file log mentah, sementara identitas armada truk, catatan perbaikan bengkel, dan perencanaan anggaran bulanan disimpan dalam dokumen yang terpisah tanpa integrasi relasional.
* **Solusi yang Diterapkan:** Merancang skema basis data relasional SQLite berstandar korporat dengan 4 tabel yang terhubung melalui *Foreign Keys*: `truck_master`, `telemetry_logs`, `maintenance_records`, dan `budget_plan` (`schema.sql` dan `db_manager.py`).

### 4. Visibilitas Kesiapan & Keandalan Armada (*PA & MTBF Tracking*)
* **Masalah:** Pihak pimpinan operasional membutuhkan indikator terukur untuk memastikan armada memenuhi target kontrak angkut dan mengetahui apakah perawatan preventif efektif menekan laju kerusakan.
* **Solusi yang Diterapkan:** Membangun modul analitik KPI otomatis (`kpi_calculator.py`) yang mengkalkulasi metrik industri:
  * **Physical Availability (PA): 99.34%** (Rasio ketersediaan unit siap kerja).
  * **Mean Time Between Failures (MTBF): 4,087.1 jam** (Keandalan waktu rata-rata antar kerusakan).
  * **Analisis Varians Anggaran**: Selisih anggaran rencana vs realisasi biaya servis per bulan.

### 5. Proses Pembuatan Laporan Excel Manual yang Lambat & Rentan Salah
* **Masalah:** Pembuatan laporan mingguan di Microsoft Excel oleh tim administrasi pemeliharaan kerap dilakukan dengan *copy-paste* nilai angka mati (*hardcoded values*), yang memperlambat pelaporan dan tidak dapat diaudit rumusnya oleh manajemen finansial.
* **Solusi yang Diterapkan:** Membangun mesin pelaporan otomatis berbasis Python `openpyxl` (`excel_exporter.py`) yang menghasilkan berkas Excel formal `.xlsx` dengan **formula native Excel** (`=SUM`, `=AVERAGE`, `=IF`), penyorotan status otomatis (*conditional formatting*), dan kartu KPI eksekutif yang bersih.

### 6. Minimnya Sarana Pengambilan Keputusan Interaktif Manajemen
* **Masalah:** Manajemen sering kesulitan memvisualisasikan dampak perubahan toleransi risiko terhadap pengeluaran biaya operasional riil.
* **Solusi yang Diterapkan:** Mengembangkan dashboard interaktif berbasis web menggunakan **Streamlit** (`app.py`), dilengkapi panel simulasi *slider threshold*, visualisasi diagnostik sinyal telemetri, grafik kurva biaya interaktif Plotly, dan tombol unduh laporan Excel langsung dari browser.

---

## 📊 Asal-Usul & Spesifikasi Dataset

Proyek ini dibangun menggunakan dataset resmi benchmark industri internasional yang diakui secara global:

* **Nama Dataset Resmi:** [APS Failure at Heavy Trucks Dataset](https://www.kaggle.com/datasets/uciml/aps-failure-at-scania-trucks-data-set)
* **Penyedia / Asal Data:** **Scania AB** (produsen kendaraan komersial berat asal Swedia) bekerja sama dengan **UCI Machine Learning Repository** dan dipublikasikan untuk kompetisi ilmiah *International Symposium on Intelligent Data Analysis (IDA 2016)*.
* **Cakupan Data:**
  * 60.000 log rekaman data pada *training set* dan 16.000 log pada *test set*.
  * **171 kolom sensor telemetri mentah** mencakup pembacaan tekanan udara kompresor, suhu oli mesin, siklus bukaan katup solenoid rem, keausan mekanikal, dan konsumsi pelumas.
* **Alasan Pemilihan Dataset:** Dataset ini merupakan standar baku emas (*gold-standard*) dalam riset *Predictive Maintenance* karena menyediakan matriks penalti biaya nyata ($10 untuk inspeksi terencana vs $500 untuk truk mogok di jalan), menjadikannya studi kasus sempurna yang menghubungkan rekayasa data dengan dampak finansial korporat.

---

## 🏗️ Struktur Proyek & Repositori Kode

```
heavy-truck-fleet-predictive-analytics/
├── data/
│   ├── raw/                           # Dataset mentah Scania APS Kaggle (44.6 MB)
│   ├── fleet_operations.db            # Basis data relasional SQLite (Master, Telematika, Servis, Anggaran)
│   └── Fleet_Performance_Report.xlsx  # Laporan Excel korporat berformula native yang di-generate otomatis
├── src/
│   ├── database/
│   │   ├── schema.sql                 # Skema DDL 4 tabel relasional lengkap dengan foreign key
│   │   └── db_manager.py              # Inisialisasi basis data, populasi data contoh, dan abstraksi kueri
│   ├── analytics/
│   │   ├── kpi_calculator.py          # Kalkulator KPI armada: PA%, MTBF, rasio breakdown, varians anggaran
│   │   └── cost_optimizer.py          # Simulator kurva optimasi biaya preskriptif ($10 vs $500)
│   ├── ml/
│   │   ├── preprocessor.py            # Filter missing value, Imputasi Median, dan RobustScaler (IQR)
│   │   └── model.py                   # Pelatihan model HistGradientBoosting dengan balanced class weights
│   └── reporting/
│       └── excel_exporter.py          # Mesin generator laporan Excel korporat dengan rumus native openpyxl
├── app.py                             # Dashboard interaktif web 3 Tab (Streamlit & Plotly)
├── requirements.txt                   # Daftar dependensi pustaka Python
└── README.md                          # Dokumentasi lengkap proyek
```

---

## 🚀 Ringkasan Hasil Empiris & Dampak Finansial

| Dimensi Evaluasi / Metrik | Model Standar (Default $p = 0.50$) | Model Optimal Preskriptif ($p^* = 0.029$) | Dampak Nyata pada Operasional |
|:---|:---:|:---:|:---|
| **Skor ROC-AUC** | `0.9870` | `0.9870` | Kemampuan separasi kelas sangat tinggi |
| **Recall / Sensitivitas** | `91.60%` | `95.20%` | Menangkap 95%+ potensi kerusakan di awal |
| **Kejadian Truk Mogok di Jalan (FN)** | `21 unit` | **12 unit** | **Penurunan insiden mogok sebesar 42.9%** |
| **Inspeksi Preventif Terjadwal (FP)** | `35 unit` | `78 unit` | Peningkatan servis murah terencana di bengkel |
| **Total Pengeluaran Perawatan** | `$10,850.00` | **$6,780.00** | **Hemat $4,070.00 (Efisiensi Biaya 37.5%)** |

---

## 💻 Antarmuka Dashboard Interaktif (Streamlit)

Aplikasi web dapat dijalankan secara lokal melalui perintah `streamlit run app.py` dan memuat 3 modul interaktif:

1. **📊 Fleet Health & Operational KPIs**:
   * Ringkasan kartu metrik: Kesiapan Fisik (`PA = 99.34%`), Keandalan (`MTBF = 4,087.1 jam`), Jumlah Mogok (`7 unit`), dan Total Biaya Servis (`$4,090.00`).
   * Grafik batang interaktif Plotly untuk membandingkan alokasi anggaran vs realisasi biaya servis per bulan.
   * Tabel armada dengan filter dinamis berdasarkan tipe truk (Scania R500, Volvo FMX, Mercedes Actros).
2. **🤖 Predictive Maintenance & Sensor Diagnostics**:
   * Panel diagnostik telemetri sensor yang mensimulasikan parameter operasional kendaraan.
   * *Gauge meter* probabilitas kerusakan rem angin (APS) dengan batas toleransi risiko preskriptif ($2.9\%$).
   * Rekomendasi tindakan armada (*Aman Beroperasi* vs *Segera Lakukan Inspeksi Bengkel*).
3. **💰 Prescriptive Cost Optimizer & Budget Simulator**:
   * *Slider* interaktif pemilihan ambang batas probabilitas alarm ($p \in [0.01, 0.50]$).
   * Perhitungan otomatis perubahan beban biaya mogok darurat vs biaya inspeksi preventif.
   * Grafik interaktif kurva biaya (*Cost vs Threshold Curve*) yang menunjukkan posisi ambang batas terpilih terhadap titik minimum optimal $p^* = 0.029$.
4. **📥 Unduh Laporan Excel Korporat**:
   * Tombol di bilah samping (*sidebar*) untuk mengunduh laporan performa armada dalam format `.xlsx` secara dinamis.

---

## 🛠️ Panduan Instalasi & Menjalankan Proyek

### Prasyarat Sistem
* Python versi 3.10, 3.11, atau 3.12 (kompatibel dengan Python 3.13)
* Git

### 1. Kloning Repositori
```bash
git clone https://github.com/hikalputra12/heavy-truck-fleet-predictive-analytics.git
cd heavy-truck-fleet-predictive-analytics
```

### 2. Pasang Dependensi Pustaka
```bash
pip install -r requirements.txt
```

### 3. Inisialisasi Basis Data Relasional
```bash
python src/database/db_manager.py
```

### 4. Jalankan Dashboard Web Interaktif
```bash
streamlit run app.py
```
Aplikasi akan terbuka secara otomatis di peramban web pada alamat `http://localhost:8501`.

---

## 📄 Lisensi

Proyek ini dirilis di bawah lisensi terbuka [MIT License](LICENSE).
