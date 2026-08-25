import customtkinter as ctk
from tkinter import messagebox
from koneksi import buat_koneksi


def buat_halaman_login(aplikasi):
    aplikasi.clear_window()

    # === JUDUL ===
    judul = ctk.CTkLabel(aplikasi, text="LOGIN PETUGAS", font=("Arial", 26, "bold"))
    judul.pack(pady=(50, 25))

    # === KOTAK — TANPA UKURAN TETAP ===
    kotak = ctk.CTkFrame(aplikasi, width=420, corner_radius=10, fg_color="#2B2B2B")
    kotak.pack(pady=10, padx=20)

    # === INPUT USERNAME ===
    lbl_user = ctk.CTkLabel(kotak, text="Nama Pengguna", font=("Arial", 12))
    lbl_user.pack(pady=(25, 8))

    ent_user = ctk.CTkEntry(kotak, placeholder_text="Masukkan Username", 
                            width=280, height=38, corner_radius=8)
    ent_user.pack(pady=5)

    # === INPUT PASSWORD ===
    lbl_pass = ctk.CTkLabel(kotak, text="Kata Sandi", font=("Arial", 12))
    lbl_pass.pack(pady=(20, 8))

    ent_pass = ctk.CTkEntry(kotak, placeholder_text="Masukkan Kata Sandi", 
                            width=280, height=38, corner_radius=8, show="•")
    ent_pass.pack(pady=5)

    # === PROSES LOGIN ===
    def proses():
        user = ent_user.get().strip()
        sandi = ent_pass.get().strip()

        if not user or not sandi:
            messagebox.showwarning("Peringatan", "Harap isi semua kolom!")
            return

        db = buat_koneksi()
        if not db:
            messagebox.showerror("Error", "Tidak bisa terhubung ke database!")
            return

        kuror = db.cursor()
        try:
            kuror.execute("SELECT * FROM tb_user WHERE username=%s AND password=%s AND status_aktif=1", (user, sandi))
            hasil = kuror.fetchone()

            if hasil:
                aplikasi.id_user = hasil[0]
                aplikasi.nama_pengguna = hasil[1]
                aplikasi.role = hasil[4]
                messagebox.showinfo("Berhasil", f"Selamat datang, {aplikasi.nama_pengguna}!\nPeran: {aplikasi.role}")
                aplikasi.tampilkan_halaman_utama()
            else:
                messagebox.showerror("Gagal", "Username atau Kata Sandi salah / akun dinonaktifkan!")

        except Exception as e:
            messagebox.showerror("Error", f"Kesalahan: {e}")
        finally:
            kuror.close()
            db.close()

    # === TOMBOL MASUK ===
    btn_login = ctk.CTkButton(kotak, text="MASUK", width=280, height=40, 
                            corner_radius=8, font=("Arial", 13), command=proses)
    btn_login.pack(pady=(25, 30), padx=30)