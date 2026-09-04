# Aplikasi Sistem Informasi Pengelolaan Parkir

Aplikasi berbasis desktop untuk pencatatan transaksi parkir, perhitungan biaya otomatis, dan laporan rekapitulasi pendapatan. Dibuat menggunakan **Python** dengan antarmuka **CustomTkinter** dan basis data **MySWL**.

## Fitur Utama
**Sistem Login** — Pembagian hak akses: Admin, Petugas, Pemilik
**Kendaraan Masuk** — Input data kendaraan oleh Admin
**Kendaraan Keluar** — Cari nomor plat -> hitung biaya otomatis -> cetak struk
**Edit Data** — Ubah data transaksi parkir
**Daftar Transaksi** — Lihat riwayat lengkap parkir
**Rekapitulasi Laporan** — Harian, Mingguan, Bulanan
**Ekspor PDF & Excel** — Simpan laporan rekap ke file PDF dan Excel
**Log Aktivitas** — Pantau riwayat pengguna

## Teknologi yang Digunakan
Bahasa Pemrograman — Python 3
Antarmuka — CustomTkinter
Basis Data — MySQL
Laporan PDF — ReportLab
Laporan Excel — XlsxWriter

## Langkah Instalasi 
*Langkah Pertama* — Pastikan **Python 3** sudah terpasang di komputermu (https://www.python.org/downloads/)
*Langkah Kedua* — Instal pustaka yang dibutuhkan
Buka **Terminal/CMD**, lalu jalankan perintah berikut satu per satu:
'''bash
| pip install tkinter 
| pip install customtkinter
| pip install mysql-connector-python
| pip install reportlab
| pip install xlsxwriter
