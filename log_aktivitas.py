import customtkinter as ctk
from tkinter import ttk, messagebox
from koneksi import buat_koneksi
from datetime import datetime

def tampilkan_log(induk):
    db = buat_koneksi()
    if not db:
        return
    kuror = db.cursor()

    try:
        kuror.execute("""
            SELECT l.id_log, u.nama_lengkap, l.aktivitas, l.waktu_aktivitas
            FROM tb_log_aktivitas l
            JOIN tb_user u ON l.id_user = u.id_user
            ORDER BY l.waktu_aktivitas DESC
            LIMIT 50
        """)
        daftar_log = kuror.fetchall()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal ambil data log!\n{e}")
        kuror.close()
        db.close()
        return

    kuror.close()
    db.close()

    jendela = ctk.CTkToplevel(induk)
    jendela.title("LOG AKTIVITAS SISTEM")
    jendela.geometry("650x420")

    ctk.CTkLabel(jendela, text="RIWAYAT AKTIVITAS PENGGUNA", font=("Arial", 18, "bold")).pack(pady=10)

    cols = ("ID", "Pengguna", "Aktivitas", "Waktu")
    tabel = ttk.Treeview(jendela, columns=cols, show="headings", height=15)

    for col in cols:
        tabel.heading(col, text=col)
    tabel.column("ID", width=50)
    tabel.column("Pengguna", width=150)
    tabel.column("Aktivitas", width=400)
    tabel.column("Waktu", width=200)

    if daftar_log:
        for baris in daftar_log:
            tabel.insert("", "end", values=(
                baris[0],
                baris[1],
                baris[2],
                baris[3].strftime('%d-%m-%Y %H:%M:%S')
            ))
    else:
        jendela.geometry("400x150")
        ctk.CTkLabel(jendela, text="Belum ada riwayat aktivitas!", font=("Arial", 16)).pack(pady=50)
        return

    tabel.pack(padx=15, pady=10, fill="both", expand=True)