import customtkinter as ctk
from halaman_login import buat_halaman_login
from halaman_utama import buat_halaman_utama

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AplikasiParkir(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SISTEM INFORMASI PARKIR")
        self.geometry("650x626")

        self.id_user = ""
        self.nama_pengguna = ""
        self.role = ""

        self.tampilkan_halaman_login()

    def tampilkan_halaman_login(self):
        buat_halaman_login(self)

    def tampilkan_halaman_utama(self):
        buat_halaman_utama(self)

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = AplikasiParkir()
    app.mainloop()