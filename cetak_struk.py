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

    c.setFont("Helvetica-Bold", 16)
    c.drawString(70, 780, "========= STRUK PARKIR =========")

    c.setFont("Helvetica", 11)
    y = 750

    c.drawString(50, y, f"Plat Nomor    : {plat}"); y-=20
    c.drawString(50, y, f"Jenis         : {jenis}"); y-=20
    c.drawString(50, y, f"Waktu Masuk   : {masuk.strftime('%d-%m-%Y %H:%M')}"); y-=20
    c.drawString(50, y, f"Waktu Keluar  : {keluar.strftime('%d-%m-%Y %H:%M')}"); y-=20
    c.drawString(50, y, f"Lama Parkir   : {lama} Jam"); y-=20
    c.drawString(50, y, f"Tarif per Jam : Rp {tarif:,}"); y-=20
    c.drawString(50, y, "-"*40); y-=15
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"TOTAL BAYAR   : Rp {total:,}"); y-=30

    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Terima Kasih, Hati-hati Berkendara")

    c.save()
    messagebox.showinfo("Berhasil", 
        f"Struk disimpan di folder:\n{os.path.abspath(nama_folder)}\n\nNama file: {nama_file}")