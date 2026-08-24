from tkinter import messagebox
import os
from datetime import datetime

def cetak_tiket_masuk(plat_nomor, jenis_kendaraan, waktu_masuk, area_parkir):
    folder = "tiket_masuk"
    if not os.path.exists(folder):
        os.makedirs(folder)

    nama_file = f"{folder}/tiket_masuk_{plat_nomor}_{waktu_masuk.strftime('%Y%m%d_%H%M%S')}.pdf"

    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import cm

        c = canvas.Canvas(nama_file, pagesize=letter)
        lebar, tinggi = letter

        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(lebar/2, tinggi - 3*cm, "TIKET MASUK PARKIR")

        c.line(3*cm, tinggi - 5.5*cm, lebar - 3*cm, tinggi - 5.5*cm)

        c.setFont("Helvetica", 13)
        y = tinggi - 7*cm
        jarak = 0.8*cm

        c.drawString(3.5*cm, y, f"Plat Nomor   : {plat_nomor.upper()}")
        y -= jarak
        c.drawString(3.5*cm, y, f"Jenis Kendaraan: {jenis_kendaraan}")
        y -= jarak
        c.drawString(3.5*cm, y, f"Area Parkir    : {area_parkir}")
        y -= jarak
        c.drawString(3.5*cm, y, f"Waktu Masuk   : {waktu_masuk.strftime('%d-%m-%Y %H:%M:%S')}")

        c.line(3*cm, y - jarak, lebar - 3*cm, y - jarak)

        y -= 1.5*cm
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(lebar/2, y, "Simpan tiket ini dengan baik, akan diperlukan saat keluar!")
        y -= jarak
        c.drawCentredString(lebar/2, y, "Terima Kasih & Hati-hati Berkendara")

        y -= 2*cm
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawCentredString(lebar/2, y, f"Dicetak pada: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

        c.save()
        return nama_file
    
    except Exception as e:
        return f"ERROR: {str(e)}"