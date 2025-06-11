# 🌀 LoopFi Automation Bot

Bot Python otomatis untuk mengikuti giveaway LoopFi secara massal. Bot ini akan:
- Generate wallet EVM baru
- Membuat email sementara
- Solve reCAPTCHA v3 secara otomatis via API SCTG
- Submit data ke campaign LoopFi
- Melengkapi seluruh task sosial (Twitter, Telegram, Discord, dsb)

## ✨ Fitur
- Auto wallet generator (EVM)
- Auto email dan password generator
- Auto solve reCAPTCHA v3 (via [SCTG API](https://t.me/Xevil_check_bot?start=1824331381))
- Support proxy (HTTP format, optional)
- Multi-task submission
- Logging warna dan stylish (Colorama + Rich)

## 🛠️ Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/danzkyxyz/Loopfi-Automation.git
cd Loopfi-Automation
```
### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
atau
```bash
pip install requests names eth-account faker beautifulsoup4 colorama rich
```
### 3. Siapkan File Tambahan
- proxy.txt
Satu proxy per baris (format http://user:pass@ip:port atau http://ip:port)

## ⚙️ Konfigurasi
Edit SCTG_API_KEY di script utama dengan API key dari https://t.me/Xevil_check_bot?start=1824331381

## ▶️ Cara Menjalankan
```bash
python bot.py
```
atau
```bash
python3 bot.py
```

## 📁 Struktur Folder
```bash
loopfi-Automation/
├── bot.py               # Script utama
├── proxy.txt             # Daftar proxy (opsional)
├── data.json             # Data akun yang dibuat
├── pkevm.txt             # Wallet yang dihasilkan
└── README.md             # Dokumentasi
```

## 📌 Catatan Penting
- Script menggunakan reCAPTCHA v3, pastikan API key SCTG kamu aktif.
- Gunakan proxy jika banyak request agar tidak diblokir.
- Domain email sementara diambil dari https://generator.email.

# ⚠️ Disclaimer
Script ini dibuat hanya untuk edukasi & automasi testing. Penggunaan terhadap sistem yang tidak diizinkan dapat melanggar ToS dari layanan terkait. Gunakan dengan tanggung jawab pribadi.
