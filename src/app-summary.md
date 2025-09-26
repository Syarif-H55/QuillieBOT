# Ringkasan BOT Telegram Pencatat Pengeluaran Harian

## 📋 Gambaran Umum
Bot Telegram multi-user untuk mencatat pengeluaran harian dengan fitur pelaporan otomatis dan on-demand.

## 🗃️ Database Structure
**Database: SQLite (atau PostgreSQL untuk skalabilitas)**

### Tabel-tabel:
1. **users**
   - user_id (Primary Key)
   - telegram_user_id (Unique)
   - username
   - first_name
   - last_name
   - created_at

2. **expenses**
   - expense_id (Primary Key)
   - user_id (Foreign Key)
   - amount (DECIMAL)
   - category (VARCHAR)
   - description (TEXT)
   - date (DATE)
   - created_at

3. **categories** (opsional, untuk konsistensi)
   - category_id
   - category_name
   - user_id (nullable untuk kategori default)

## 🔄 Alur Aplikasi

### 1. Registrasi & Setup
```
User → /start → Bot menyapa & membuat profil user di database
```

### 2. Pencatatan Pengeluaran
```
User → /tambah [jumlah] [kategori] [deskripsi?]
       atau
User → /tambah → Bot memandu step-by-step:
  1. Masukkan jumlah
  2. Pilih/ketik kategori
  3. Masukkan deskripsi (opsional)
  4. Konfirmasi & simpan
```

### 3. Melihat Laporan
```
User → /laporan [periode?] → Bot menampilkan:
  - Total pengeluaran periode tersebut
  - Breakdown per kategori
  - Grafik sederhana (jika memungkinkan)

Periode: hari ini, minggu ini, bulan ini, custom
```

### 4. Laporan Otomatis
```
Setiap Minggu jam 09:00 WIB:
  - Bot mengirim laporan mingguan ke semua user aktif
  - Ringkasan pengeluaran 7 hari terakhir
  - Perbandingan dengan minggu sebelumnya
```

## 🚀 Fitur Utama

### ✅ Fitur Wajib
1. **Multi-user Support**
   - Setiap user memiliki data terpisah
   - Identifikasi berdasarkan Telegram User ID

2. **Pencatatan Pengeluaran**
   - Input cepat dengan command langsung
   - Input terpandu untuk user baru
   - Validasi input (jumlah harus angka, dll)

3. **Laporan On-Demand**
   - `/laporan` - laporan hari ini
   - `/laporan minggu` - laporan mingguan
   - `/laporan bulan` - laporan bulanan
   - `/laporan 2024-03-01 2024-03-31` - laporan custom

4. **Laporan Otomatis Mingguan**
   - Terkirim setiap Minggu pagi
   - Format menarik dengan emoji
   - Opsi unsubscribe untuk user

### 💡 Fitur Tambahan (Nice to Have)
1. **Manajemen Kategori**
   - `/kategori` - lihat/tambah kategori
   - Kategori default + custom per user

2. **Budget Setting**
   - `/set_budget` - atur budget bulanan
   - Notifikasi ketika mendekati budget

3. **Ekspor Data**
   - `/export` - ekspor data ke CSV/Excel

4. **Backup Data**
   - Auto-backup periodic
   - Restore data untuk user

## 🏗️ Arsitektur Teknis

### Stack Technology
- **Language**: Python 3.8+
- **Framework**: python-telegram-bot
- **Database**: SQLite (development), PostgreSQL (production)
- **Scheduler**: APScheduler untuk report mingguan
- **Cache**: Redis (opsional, untuk performa)

### Struktur File
```
bot_pengeluaran/
├── main.py              # Entry point
├── database/
│   ├── models.py        # Model database
│   └── operations.py    # CRUD operations
├── handlers/
│   ├── start.py         # /start handler
│   ├── expenses.py      # Pengeluaran handlers
│   ├── reports.py       # Laporan handlers
│   └── scheduler.py     # Job scheduler
├── utils/
│   ├── validators.py    # Validasi input
│   └── formatters.py    # Format pesan
└── config.py           # Konfigurasi
```

## 💬 Contoh Interaksi

### Contoh 1: Input Cepat
```
User: /tambah 50000 makan "makan siang"
Bot: ✅ Pengeluaran tercatat!
    💰 Rp 50,000
    🏷️ Makan
    📝 makan siang
```

### Contoh 2: Input Terpandu
```
User: /tambah
Bot: Masukkan jumlah pengeluaran:
User: 75000
Bot: Pilih kategori: [Transportasi, Makan, Belanja, Lainnya]
User: Transportasi
Bot: Masukkan deskripsi (opsional):
User: Bensin motor
Bot: Konfirmasi pengeluaran:
    💰 Rp 75,000 - Transportasi - Bensin motor
    ✅ Simpan / ❌ Batal
```

### Contoh 3: Laporan Mingguan
```
User: /laporan minggu
Bot: 📊 Laporan Minggu Ini (1-7 Mar 2024)
    
    Total: Rp 450,000
    ──────────────────
    🍔 Makan: Rp 200,000 (44%)
    🚗 Transportasi: Rp 150,000 (33%)
    🛍️ Belanja: Rp 100,000 (22%)
    
    📈 vs minggu lalu: -15% 🔽
```

## 🔄 Flowchart Singkat
```
Start
  ↓
/user starts bot → Create user profile
  ↓
/user adds expense → Validate & store in database
  ↓
/user requests report → Query database & format response
  ↓
Weekly scheduler runs → Generate reports for all users
  ↓
Send automated reports
```

Bot ini akan membantu user tracking pengeluaran dengan mudah melalui interface Telegram yang familiar! 🚀

Launch the bot at @main.py with pip install -r requirements.txt