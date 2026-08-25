import customtkinter as ctk
from tkinter import ttk
from koneksi import buat_koneksi
from datetime import datetime

def tampilkan_daftar(induk):
    jendela = ctk.CTkToplevel(induk)
    jendela.title("DAFTAR PARKIR TERBARU")
    jendela.geometry("720x420")

    frm_atas = ctk.CTkFrame(jendela, fg_color="transparent")
    frm_atas.pack(fill="x", padx=15, pady=5)

    ctk.CTkLabel(frm_atas, text="DAFTAR TRANSAKSI PARKIR", font=("Arial", 14, "bold")).pack(side="left")

    cols = ("ID", "Plat Nomor", "Jenis", "Area", "Waktu Masuk", "Waktu Keluar", "Biaya", "Status")
    tabel = ttk.Treeview(jendela, columns=cols, show="headings", height=15)

    lebar = [50, 120, 100, 110, 140, 140, 100, 90]
    for i, col in enumerate(cols):
        tabel.heading(col, text=col)
        tabel.column(col, width=lebar[i], anchor="center")

    tabel.pack(padx=15, pady=10, fill="both", expand=True)

    def muat_data():
        for baris in tabel.get_children():
            tabel.delete(baris)

        db = buat_koneksi()
        if not db:
            return
        kuror = db.cursor()

        try:
            kuror.execute("""
                SELECT t.id_parkir, k.plat_nomor, k.jenis_kendaraan, 
                    a.nama_area, t.waktu_masuk, t.waktu_keluar, t.biaya_total, t.status
                FROM tb_transaksi t
                JOIN tb_kendaraan k ON t.id_kendaraan = k.id_kendaraan
                JOIN tb_area_parkir a ON t.id_area = a.id_area
                ORDER BY t.waktu_masuk DESC
                LIMIT 30
            """)
            daftar = kuror.fetchall()
        except Exception as e:
            pass
        finally:
            kuror.close()
            db.close()

        if daftar:
            for baris in daftar:
                biaya = f"Rp {int(baris[6]):,}" if baris[6] else "-"
                keluar = baris[5].strftime('%d-%m %H:%M') if baris[5] else "MASIH PARKIR"
                tabel.insert("", "end", values=(
                    baris[0],
                    baris[1],
                    baris[2].capitalize(),
                    baris[3],
                    baris[4].strftime('%d-%m %H:%M'),
                    keluar,
                    biaya,
                    baris[7].upper()
                ))
        else:
            tabel.insert("", "end", values=("", "BELUM ADA DATA", "", "", "", ""))

    def auto_refresh():
        muat_data()
        jendela.after(5000, auto_refresh)

    muat_data()
    auto_refresh()