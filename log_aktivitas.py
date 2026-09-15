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

    # === JENDELA — WARNA LATAR SAMA ===
    jendela = ctk.CTkToplevel(induk)
    jendela.title("LOG AKTIVITAS SISTEM")
    jendela.geometry("750x520")
    jendela.configure(fg_color="#F0F4F8")  # ← WARNA LATAR SAMA!

    # === JUDUL ===
    ctk.CTkLabel(
        jendela,
        text="RIWAYAT AKTIVITAS PENGGUNA",
        font=("Arial", 18, "bold"),
        text_color="#2D3748"  # ← TULISAN GELAP JELAS
    ).pack(pady=(25, 20))

    # === CARD TABEL ===
    frm_card = ctk.CTkFrame(
        jendela,
        fg_color="#FFFFFF",
        corner_radius=12
    )
    frm_card.pack(pady=(0, 25), padx=40, fill="both", expand=True)

    cols = ("ID", "Pengguna", "Aktivitas", "Waktu")
    tabel = ttk.Treeview(frm_card, columns=cols, show="headings", height=12)

    tabel.heading("ID", text="ID")
    tabel.heading("Pengguna", text="Pengguna")
    tabel.heading("Aktivitas", text="Aktivitas")
    tabel.heading("Waktu", text="Waktu")

    # === PERLEBAR KOLOM & PERBESAR TULISAN ===
    tabel.column("ID", width=60, anchor="center")
    tabel.column("Pengguna", width=180, anchor="center")
    tabel.column("Aktivitas", width=320, anchor="center")
    tabel.column("Waktu", width=180, anchor="center")

    # === PERBESAR TULISAN DI TABEL ===
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 13, "bold"))
    style.configure("Treeview", font=("Arial", 11), rowheight=32)

    if daftar_log:
        for baris in daftar_log:
            tabel.insert("", "end", values=(
                baris[0],
                baris[1],
                baris[2],
                baris[3].strftime('%d-%m-%Y %H:%M:%S')
            ))
    else:
        jendela.geometry("450x180")
        ctk.CTkLabel(
            jendela,
            text="Belum ada riwayat aktivitas!",
            font=("Arial", 15),
            text_color="#4A5568"
        ).pack(pady=60)
        return

    tabel.pack(padx=20, pady=20, fill="both", expand=True)