import mysql.connector
from tkinter import messagebox
def buat_koneksi():
    try:
        konek = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="parkir"
        )
        return konek
    except Exception as err:
        messagebox.showerror("Error Koneksi")
        return None