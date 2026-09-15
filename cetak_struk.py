from reportlab.pdfgen import canvas
from tkinter import messagebox
import os
from datetime import datetime

def cetak_struk(plat, jenis, masuk, keluar, lama, tarif, total):
    nama_folder = "struk_parkir"
    if not os.path.exists(nama_folder):
        os.makedirs(nama_folder)
    nama_file = f"struk_{plat}_{keluar.strftime('%Y%m%d_%H%M%S')}.pdf"
    path_lengkap = os.path.join(nama_folder, nama_file)
    
    c = canvas.Canvas(path_lengkap)
    lebar_halaman = 595       # Lebar A4
    lebar_blok = 320           # Lebar area teks agar rapi
    posisi_mulai = (lebar_halaman - lebar_blok) / 2  # Mulai dari sini agar blok di TENGAH

    # === JUDUL DI TENGAH ===
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(lebar_halaman/2, 780, "========== STRUK PARKIR ==========")

    # === ISI — BLOK DI TENGAH TAPI RATA KIRI ===
    c.setFont("Helvetica", 12)
    y = 750

    def tulis_baris(teks):
        nonlocal y
        c.drawString(posisi_mulai, y, teks)
        y -= 22

    tulis_baris(f"Plat Nomor    : {plat}")
    tulis_baris(f"Jenis         : {jenis}")
    tulis_baris(f"Waktu Masuk   : {masuk.strftime('%d-%m-%Y %H:%M')}")
    tulis_baris(f"Waktu Keluar  : {keluar.strftime('%d-%m-%Y %H:%M')}")
    tulis_baris(f"Lama Parkir   : {lama} Jam")
    tulis_baris(f"Tarif per Jam : Rp {tarif:,}")
    
    c.drawString(posisi_mulai, y, "-" * 35); y -= 25
    
    c.setFont("Helvetica-Bold", 13)
    tulis_baris(f"TOTAL BAYAR   : Rp {total:,}")
    
    y -= 10
    c.setFont("Helvetica", 11)
    c.drawCentredString(lebar_halaman/2, y, "Terima Kasih, Hati-hati Berkendara")

    c.save()

    messagebox.showinfo("Berhasil", 
        f"Struk disimpan di folder:\n{os.path.abspath(nama_folder)}\n\nNama file: {nama_file}")