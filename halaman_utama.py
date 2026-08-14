import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from koneksi import buat_koneksi
from log_aktivitas import tampilkan_log
from cetak_struk import cetak_struk
from daftar_parkir import tampilkan_daftar
from cetak_struk_masuk import cetak_struk_masuk

def buat_halaman_utama(aplikasi):
    aplikasi.clear_window()

    baris_atas = ctk.CTkFrame(aplikasi, fg_color="transparent")
    baris_atas.pack(fill="x", padx=20, pady=10)

    teks_info = f"{aplikasi.nama_pengguna} | Peran: {aplikasi.role} | {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    info = ctk.CTkLabel(baris_atas, text=teks_info, font=("Arial", 12))
    info.pack(side="left")

    btn_keluar = ctk.CTkButton(
        baris_atas, text="KELUAR",
        fg_color="#dc3545", hover_color="#c82333",
        width=90, height=32, corner_radius=8,
        command=aplikasi.tampilkan_halaman_login
    )
    btn_keluar.pack(side="right")

    judul = ctk.CTkLabel(aplikasi, text="SISTEM PARKIR", font=("Arial", 24, "bold"))
    judul.pack(pady=5)

    garis = ctk.CTkFrame(aplikasi, width=600, height=2)
    garis.pack(pady=5)

    if aplikasi.role != "owner":

        db = buat_koneksi()
        tarif_list = {}
        area_opsi = []
        jenis_opsi = []

        if db:
            kuror = db.cursor()
            kuror.execute("SELECT jenis_kendaraan, tarif_per_jam, id_tarif FROM tb_tarif")
            data_tarif = kuror.fetchall()
            for jns, hrg, idt in data_tarif:
                kunci = jns.capitalize()
                tarif_list[kunci] = {"tarif": int(hrg), "id_tarif": idt}
            jenis_opsi = list(tarif_list.keys())

            kuror.execute("SELECT id_area, nama_area FROM tb_area_parkir")
            data_area = kuror.fetchall()
            area_opsi = [f"{row[0]} - {row[1]}" for row in data_area]
            kuror.close()
            db.close()

        if not jenis_opsi:
            jenis_opsi = ["Motor", "Mobil", "Lainnya"]
        if not area_opsi:
            area_opsi = ["1 - Area A", "2 - Area B"]

        frm = ctk.CTkFrame(aplikasi)
        frm.pack(pady=15, padx=40, fill="both", expand=True)

        isi = ctk.CTkFrame(frm, fg_color="transparent")
        isi.pack(pady=15, padx=20)

        lbl_width = 180
        inp_width = 300

        ctk.CTkLabel(isi, text="Plat Nomor Kendaraan", width=lbl_width, anchor="w").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        ent_plat = ctk.CTkEntry(isi, placeholder_text="Contoh: KT 1234 AB", width=inp_width, height=38)
        ent_plat.grid(row=0, column=1, padx=10, pady=8)

        ctk.CTkLabel(isi, text="Jenis Kendaraan", width=lbl_width, anchor="w").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        cmb_jenis = ctk.CTkComboBox(isi, values=jenis_opsi, width=inp_width, height=38)
        cmb_jenis.set(jenis_opsi[0])
        cmb_jenis.grid(row=1, column=1, padx=10, pady=8)

        ctk.CTkLabel(isi, text="Area Parkir", width=lbl_width, anchor="w").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        cmb_area = ctk.CTkComboBox(isi, values=area_opsi, width=inp_width, height=38)
        cmb_area.set(area_opsi[0])
        cmb_area.grid(row=2, column=1, padx=10, pady=8)

        ctk.CTkLabel(isi, text="Warna Kendaraan", width=lbl_width, anchor="w").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        ent_warna = ctk.CTkEntry(isi, placeholder_text="Merah, Hitam, dll", width=inp_width, height=38)
        ent_warna.grid(row=3, column=1, padx=10, pady=8)

        ctk.CTkLabel(isi, text="Nama Pemilik", width=lbl_width, anchor="w").grid(row=4, column=0, padx=10, pady=8, sticky="w")
        ent_pemilik = ctk.CTkEntry(isi, placeholder_text="Nama Pemilik Kendaraan", width=inp_width, height=38)
        ent_pemilik.grid(row=4, column=1, padx=10, pady=8)

        def proses_masuk():
            plat = ent_plat.get().strip().upper()
            jenis = cmb_jenis.get().strip().lower()
            warna = ent_warna.get().strip()
            pemilik = ent_pemilik.get().strip()
            area_pilih = cmb_area.get().split(" - ")
            id_area = int(area_pilih[0])

            if not plat or not warna or not pemilik:
                messagebox.showwarning("Peringatan", "Lengkapi semua data kendaraan!")
                return

            db = buat_koneksi()
            if not db: return
            kuror = db.cursor()

            try:
                kuror.execute("INSERT INTO tb_kendaraan (plat_nomor, jenis_kendaraan, warna, pemilik, id_user) VALUES (%s, %s, %s, %s, %s)",
                            (plat, jenis, warna, pemilik, aplikasi.id_user))
                id_kendaraan = kuror.lastrowid

                waktu_masuk = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                id_tarif = tarif_list[jenis.capitalize()]["id_tarif"]
                kuror.execute("INSERT INTO tb_transaksi (id_kendaraan, waktu_masuk, id_tarif, status, id_user, id_area) VALUES (%s, %s, %s, 'masuk', %s, %s)",
                            (id_kendaraan, waktu_masuk, id_tarif, aplikasi.id_user, id_area))

                kuror.execute("INSERT INTO tb_log_aktivitas (id_user, aktivitas, waktu_aktivitas) VALUES (%s, %s, %s)",
                            (aplikasi.id_user, f"Kendaraan Masuk: {plat}", waktu_masuk))

                db.commit()
                messagebox.showinfo("Berhasil", f"Kendaraan Masuk!\nPlat: {plat}\nWaktu: {waktu_masuk}")
                
                rincian = f"""PLAT NOMOR: {plat}
                            JENIS: {jenis.capitalize()}
                            MASUK: {waktu_masuk.strftime('%d-%m-%Y %H:%M')}
                            PEMILIK: {pemilik}"""
                
                if messagebox.askyesno("Cetak Struk", "Cetak struk masuk?"):
                    cetak_struk_masuk(plat, jenis.capitalize(), waktu_masuk, area_pilih, pemilik)

                ent_plat.delete(0, "end")
                ent_warna.delete(0, "end")
                ent_pemilik.delete(0, "end")

            except Exception as e:
                db.rollback()
                messagebox.showerror("Error", f"Gagal menyimpan data!\n{e}")
            finally:
                kuror.close()
                db.close()

        def proses_keluar():
            plat = ent_plat.get().strip().upper()
            if not plat:
                messagebox.showwarning("Peringatan", "Masukkan Plat Nomor Kendaraan!")
                return

            db = buat_koneksi()
            if not db: return
            kuror = db.cursor()

            try:
                kuror.execute("""
                    SELECT t.id_parkir, t.id_kendaraan, t.waktu_masuk, t.id_tarif, k.jenis_kendaraan
                    FROM tb_transaksi t
                    JOIN tb_kendaraan k ON t.id_kendaraan = k.id_kendaraan
                    WHERE k.plat_nomor = %s AND t.status = 'masuk'
                    LIMIT 1
                """, (plat,))
                data = kuror.fetchone()
                if not data:
                    messagebox.showerror("Gagal", "Kendaraan tidak terdaftar atau sudah keluar!")
                    return

                id_parkir, id_kendaraan, waktu_masuk, id_tarif, jenis = data
                waktu_keluar = datetime.now()
                lama_jam = max(1, round((waktu_keluar - waktu_masuk).total_seconds() / 3600, 1))
                tarif = tarif_list[jenis.capitalize()]["tarif"]
                biaya = int(lama_jam * tarif)

                kuror.execute("""
                    UPDATE tb_transaksi 
                    SET waktu_keluar=%s, durasi_jam=%s, biaya_total=%s, status='keluar'
                    WHERE id_parkir=%s
                """, (waktu_keluar.strftime("%Y-%m-%d %H:%M:%S"), lama_jam, biaya, id_parkir))

                kuror.execute("INSERT INTO tb_log_aktivitas (id_user, aktivitas, waktu_aktivitas) VALUES (%s, %s, %s)",
                            (aplikasi.id_user, f"Kendaraan Keluar: {plat} - Biaya: Rp{biaya}", waktu_keluar))

                db.commit()

                rincian = f"""PLAT NOMOR: {plat}
                JENIS: {jenis.capitalize()}
                MASUK: {waktu_masuk.strftime('%d-%m-%Y %H:%M')}
                KELUAR: {waktu_keluar.strftime('%d-%m-%Y %H:%M')}
                LAMA: {lama_jam} Jam
                TARIF PER JAM: Rp {tarif:,}
                TOTAL BAYAR: Rp {biaya:,}"""
                messagebox.showinfo("Pembayaran", rincian)

                if messagebox.askyesno("Cetak Struk", "Cetak struk pembayaran?"):
                    cetak_struk(plat, jenis.capitalize(), waktu_masuk, waktu_keluar, lama_jam, tarif, biaya)

                ent_plat.delete(0, "end")
                ent_warna.delete(0, "end")
                ent_pemilik.delete(0, "end")

            except Exception as e:
                db.rollback()
                messagebox.showerror("Error", f"Gagal memproses keluar!\n{e}")
            finally:
                kuror.close()
                db.close()

        frm_btn = ctk.CTkFrame(aplikasi, fg_color="transparent")
        frm_btn.pack(pady=15, padx=20)

        btn_warna = {"width": 280, "height": 60, "corner_radius": 12}

        if aplikasi.role == "admin":
            ctk.CTkButton(isi, text="KENDARAAN MASUK", 
                        fg_color="#3b8ed0", width=300, height=40, corner_radius=10,
                        command=proses_masuk).grid(row=5, column=0, columnspan=2, padx=10, pady=(15, 5))

            ctk.CTkButton(frm_btn, text="DAFTAR PARKIR", 
                        fg_color="#fd7e14", hover_color="#e86e05", width=280, height=50, corner_radius=10, 
                        command=lambda: tampilkan_daftar(aplikasi)).pack(side="left", pady=5, padx=20)

            ctk.CTkButton(frm_btn, text="LOG AKTIVITAS", 
                        fg_color="#00b894", hover_color="#00a085", width=280, height=50, corner_radius=10,
                        command=lambda: tampilkan_log(aplikasi)).pack(side="left", pady=5, padx=20)

        elif aplikasi.role == "petugas":
            ctk.CTkButton(isi, text="KENDARAAN KELUAR", 
                        fg_color="#3b8ed0", width=300, height=40, corner_radius=10,
                        command=proses_keluar).grid(row=5, column=0, columnspan=2, padx=10, pady=(15, 5))
            
            ctk.CTkButton(frm_btn, text="DAFTAR PARKIR", 
                                    fg_color="#fd7e14", hover_color="#e86e05", width=280, height=50, corner_radius=10, 
                                    command=lambda: tampilkan_daftar(aplikasi)).pack(side="left", pady=5, padx=20)

    else:
        frm_pilih = ctk.CTkFrame(aplikasi)
        frm_pilih.pack(pady=5, padx=40, fill="x")

        ctk.CTkLabel(frm_pilih, text="Pilih Periode:", font=("Arial", 12, "bold")).pack(side="left", padx=20)

        var_periode = ctk.StringVar(value="harian")
        ctk.CTkRadioButton(frm_pilih, text="Harian", variable=var_periode, value="harian", font=("Arial", 11)).pack(side="left", padx=15)
        ctk.CTkRadioButton(frm_pilih, text="Mingguan", variable=var_periode, value="mingguan", font=("Arial", 11)).pack(side="left", padx=15)
        ctk.CTkRadioButton(frm_pilih, text="Bulanan", variable=var_periode, value="bulanan", font=("Arial", 11)).pack(side="left", padx=15)

        frm_tabel = ctk.CTkFrame(aplikasi)
        frm_tabel.pack(pady=15, padx=40, fill="both", expand=True)

        cols = ("Periode", "Jumlah Transaksi", "Total Kendaraan", "Total Pendapatan")
        tabel = ttk.Treeview(frm_tabel, columns=cols, show="headings", height=10)

        tabel.heading("Periode", text="Periode")
        tabel.heading("Jumlah Transaksi", text="Jumlah Transaksi")
        tabel.heading("Total Kendaraan", text="Total Kendaraan")
        tabel.heading("Total Pendapatan", text="Total Pendapatan")

        tabel.column("Periode", width=200, anchor="center")
        tabel.column("Jumlah Transaksi", width=200, anchor="center")
        tabel.column("Total Kendaraan", width=200, anchor="center")
        tabel.column("Total Pendapatan", width=200, anchor="center")

        tabel.pack(fill="both", expand=True)

        def muat_rekap():
            for baris in tabel.get_children():
                tabel.delete(baris)

            jenis = var_periode.get()
            db = buat_koneksi()
            if not db:
                tabel.insert("", "end", values=("Gagal Terhubung", "", "", ""))
                return
            kuror = db.cursor()

            try:
                if jenis == "harian":
                    kuror.execute("""
                        SELECT DATE(waktu_masuk) AS periode,
                            COUNT(*) AS jumlah,
                            COUNT(DISTINCT id_kendaraan) AS kendaraan,
                            SUM(biaya_total) AS pendapatan
                        FROM tb_transaksi
                        WHERE status = 'keluar'
                        GROUP BY DATE(waktu_masuk)
                        ORDER BY periode DESC
                        LIMIT 30
                    """)
                elif jenis == "mingguan":
                    kuror.execute("""
                        SELECT CONCAT(YEAR(waktu_masuk), ' - Minggu ', WEEK(waktu_masuk)) AS periode,
                            COUNT(*) AS jumlah,
                            COUNT(DISTINCT id_kendaraan) AS kendaraan,
                            SUM(biaya_total) AS pendapatan
                        FROM tb_transaksi
                        WHERE status = 'keluar'
                        GROUP BY YEAR(waktu_masuk), WEEK(waktu_masuk)
                        ORDER BY waktu_masuk DESC
                        LIMIT 12
                    """)
                elif jenis == "bulanan":
                    kuror.execute("""
                        SELECT CONCAT(YEAR(waktu_masuk), ' - ', MONTHNAME(waktu_masuk)) AS periode,
                            COUNT(*) AS jumlah,
                            COUNT(DISTINCT id_kendaraan) AS kendaraan,
                            SUM(biaya_total) AS pendapatan
                        FROM tb_transaksi
                        WHERE status = 'keluar'
                        GROUP BY YEAR(waktu_masuk), MONTH(waktu_masuk)
                        ORDER BY waktu_masuk DESC
                        LIMIT 12
                    """)

                data = kuror.fetchall()
                total_pendapatan = 0
                total_transaksi = 0
                total_kendaraan = 0

                if data:
                    for baris in data:
                        pendapatan = baris[3] if baris[3] else 0
                        total_pendapatan += pendapatan
                        total_transaksi += baris[1]
                        total_kendaraan += baris[2]
                        tabel.insert("", "end", values=(
                            str(baris[0]),
                            str(baris[1]),
                            str(baris[2]),
                            f"Rp {pendapatan:,}"
                        ))
                    tabel.insert("", "end", values=(
                        "TOTAL SEMUA",
                        str(total_transaksi),
                        str(total_kendaraan),
                        f"Rp {total_pendapatan:,}"
                    ))
                else:
                    tabel.insert("", "end", values=("Belum Ada Data", "-", "-", "-"))

            except Exception as e:
                tabel.insert("", "end", values=(f"Error", "", "", ""))
            finally:
                kuror.close()
                db.close()

        muat_rekap()
        var_periode.trace("w", lambda *args: muat_rekap())