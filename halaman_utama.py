import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from koneksi import buat_koneksi
from log_aktivitas import tampilkan_log
from cetak_struk import cetak_struk
from daftar_parkir import tampilkan_daftar
from cetak_struk_masuk import cetak_tiket_masuk
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import xlsxwriter
from datetime import datetime

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

                waktu_sekarang = datetime.now()
                waktu_masuk = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                id_tarif = tarif_list[jenis.capitalize()]["id_tarif"]
                kuror.execute("INSERT INTO tb_transaksi (id_kendaraan, waktu_masuk, id_tarif, status, id_user, id_area) VALUES (%s, %s, %s, 'masuk', %s, %s)",
                            (id_kendaraan, waktu_masuk, id_tarif, aplikasi.id_user, id_area))

                kuror.execute("INSERT INTO tb_log_aktivitas (id_user, aktivitas, waktu_aktivitas) VALUES (%s, %s, %s)",
                            (aplikasi.id_user, f"Kendaraan Masuk: {plat}", waktu_masuk))

                db.commit()
                messagebox.showinfo("Berhasil", f"Kendaraan Masuk!\nPlat: {plat}\nWaktu: {waktu_masuk}")
                
                nama_area = cmb_area.get()
                
                file_tiket = cetak_tiket_masuk(
                    plat_nomor=plat,
                    jenis_kendaraan=cmb_jenis.get(),
                    waktu_masuk=waktu_sekarang,
                    area_parkir=nama_area
                )
                
                messagebox.showinfo("Berhasil", f"Kendaraan Masuk!\n\nTiket Masuk sudah dibuat:\n{file_tiket}")

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
                        fg_color="#4B72AD", width=300, height=40, corner_radius=10,
                        command=proses_masuk).grid(row=5, column=0, columnspan=2, padx=10, pady=(15, 5))
            
            ctk.CTkButton(isi, text="EDIT DATA KENDARAAN",
                        fg_color="#46897C", hover_color="#356B5F", width=300, height=40, corner_radius=10,
                        command=lambda: buka_jendela_edit(aplikasi)).grid(row=6, column=0, columnspan=2, padx=10, pady=(5, 10))

            ctk.CTkButton(frm_btn, text="DAFTAR PARKIR", 
                        fg_color="#5A79A8", hover_color="#466087", width=280, height=50, corner_radius=10, 
                        command=lambda: tampilkan_daftar(aplikasi)).pack(side="left", pady=5, padx=20)

            ctk.CTkButton(frm_btn, text="LOG AKTIVITAS", 
                        fg_color="#7267A3", hover_color="#5A5082", width=280, height=50, corner_radius=10,
                        command=lambda: tampilkan_log(aplikasi)).pack(side="left", pady=5, padx=20)
            
            def buka_jendela_edit(induk):
                jendela_edit = ctk.CTkToplevel(induk)
                jendela_edit.title("EDIT DATA KENDARAAN")
                jendela_edit.geometry("600x550")

                id_transaksi_terpilih = ctk.StringVar(value="")

                frm_atas = ctk.CTkFrame(jendela_edit, fg_color="transparent")
                frm_atas.pack(fill="x", padx=25, pady=(25, 10))

                ctk.CTkLabel(frm_atas, text="Masukkan Plat Nomor yang Ingin Diubah:", 
                            font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")

                ctk.CTkButton(frm_atas, text="BATAL", 
                            fg_color="#dc3545", hover_color="#c82333",
                            width=90, height=30, corner_radius=8,
                            command=jendela_edit.destroy).grid(row=0, column=1, sticky="e")

                frm_atas.grid_columnconfigure(1, weight=1)

                frm_cari = ctk.CTkFrame(jendela_edit, fg_color="transparent")
                frm_cari.pack(fill="x", padx=25, pady=5)

                ent_plat_edit = ctk.CTkEntry(frm_cari, placeholder_text="Contoh: KT 1234 AB", 
                                            width=380, height=42)
                ent_plat_edit.grid(row=0, column=0, padx=(0, 10))

                def cari_data():
                    plat = ent_plat_edit.get().strip().upper()
                    if not plat:
                        messagebox.showwarning("Peringatan", "Masukkan Plat Nomor!")
                        return

                    db = buat_koneksi()
                    if not db: return
                    kuror = db.cursor()

                    try:
                        kuror.execute("""
                            SELECT t.id_parkir, k.plat_nomor, k.jenis_kendaraan, a.nama_area
                            FROM tb_transaksi t
                            JOIN tb_kendaraan k ON t.id_kendaraan = k.id_kendaraan
                            JOIN tb_area_parkir a ON t.id_area = a.id_area
                            WHERE k.plat_nomor = %s AND t.status = 'masuk'
                            LIMIT 1
                        """, (plat,))
                        data = kuror.fetchone()

                        if not data:
                            messagebox.showerror("Tidak Ditemukan", "Kendaraan tidak ada atau sudah keluar!")
                            return

                        id_transaksi, plat_lama, jenis_lama, area_lama = data
                        id_transaksi_terpilih.set(str(id_transaksi))
                        ent_plat_baru.delete(0, "end")
                        ent_plat_baru.insert(0, plat_lama)
                        cmb_jenis_edit.set(jenis_lama.capitalize())
                        cmb_area_edit.set(area_lama)
                        messagebox.showinfo("Ditemukan", "Data ditemukan! Silakan ubah lalu simpan.")

                    except Exception as e:
                        messagebox.showerror("Error", f"Gagal mencari data!\n{e}")
                    finally:
                        kuror.close()
                        db.close()

                btn_cari = ctk.CTkButton(frm_cari, text="CARI", 
                            fg_color="#4B72AD", hover_color="#3A5A8A",
                            width=100, height=36, corner_radius=10,
                            command=cari_data)
                btn_cari.grid(row=0, column=1)

                frm_edit = ctk.CTkFrame(jendela_edit)
                frm_edit.pack(pady=20, padx=30, fill="x")

                lbl_width = 150
                inp_width = 320

                ctk.CTkLabel(frm_edit, text="Plat Nomor Baru:", width=lbl_width, anchor="w").grid(row=0, column=0, padx=10, pady=10, sticky="w")
                ent_plat_baru = ctk.CTkEntry(frm_edit, width=inp_width, height=38)
                ent_plat_baru.grid(row=0, column=1, padx=10, pady=10)

                ctk.CTkLabel(frm_edit, text="Jenis Kendaraan:", width=lbl_width, anchor="w").grid(row=1, column=0, padx=10, pady=10, sticky="w")
                cmb_jenis_edit = ctk.CTkComboBox(frm_edit, values=jenis_opsi, width=inp_width, height=38)
                cmb_jenis_edit.grid(row=1, column=1, padx=10, pady=10)

                ctk.CTkLabel(frm_edit, text="Area Parkir:", width=lbl_width, anchor="w").grid(row=2, column=0, padx=10, pady=10, sticky="w")

                daftar_area = []
                db = buat_koneksi()
                if db:
                    kuror = db.cursor()
                    try:
                        kuror.execute("SELECT nama_area FROM tb_area_parkir ORDER BY nama_area")
                        hasil = kuror.fetchall()
                        daftar_area = [baris[0] for baris in hasil]
                    except Exception as e:
                        print("Gagal ambil area:", e)
                    finally:
                        kuror.close()
                        db.close()

                cmb_area_edit = ctk.CTkComboBox(frm_edit, values=daftar_area, width=inp_width, height=38)
                cmb_area_edit.grid(row=2, column=1, padx=10, pady=10)

                def simpan_perubahan():
                    id_transaksi = id_transaksi_terpilih.get()
                    plat_baru = ent_plat_baru.get().strip().upper()
                    jenis_baru = cmb_jenis_edit.get().lower()
                    area_baru = cmb_area_edit.get()

                    if not id_transaksi:
                        messagebox.showwarning("Peringatan", "Cari data dulu!")
                        return
                    if not plat_baru:
                        messagebox.showwarning("Peringatan", "Plat Nomor tidak boleh kosong!")
                        return

                    db = buat_koneksi()
                    if not db: return
                    kuror = db.cursor()

                    try:
                        kuror.execute("SELECT id_kendaraan, id_area FROM tb_transaksi WHERE id_parkir = %s", (id_transaksi,))
                        id_kendaraan, id_area_lama = kuror.fetchone()

                        kuror.execute("SELECT id_area FROM tb_area_parkir WHERE nama_area = %s", (area_baru,))
                        hasil_area = kuror.fetchone()
                        id_area_baru = hasil_area[0] if hasil_area else id_area_lama

                        kuror.execute("""
                                    UPDATE tb_kendaraan 
                                    SET plat_nomor = %s, jenis_kendaraan = %s 
                                    WHERE id_kendaraan = %s
                        """, (plat_baru, jenis_baru, id_kendaraan))

                        kuror.execute("""
                                    UPDATE tb_transaksi 
                                    SET id_area = %s
                                    WHERE id_parkir = %s
                        """, (id_area_baru, id_transaksi))

                        kuror.execute("INSERT INTO tb_log_aktivitas (id_user, aktivitas, waktu_aktivitas) VALUES (%s, %s, NOW())",
                                    (aplikasi.id_user, f"Edit Data: {plat_baru}"))

                        db.commit()
                        messagebox.showinfo("Berhasil", "Data berhasil diperbarui!")
                        jendela_edit.destroy()

                    except Exception as e:
                        db.rollback()
                        messagebox.showerror("Error", f"Gagal menyimpan!\n{e}")
                    finally:
                        kuror.close()
                        db.close()

                frm_tombol = ctk.CTkFrame(jendela_edit, fg_color="transparent")
                frm_tombol.pack(pady=(5, 20))

                ctk.CTkButton(frm_tombol, text="SIMPAN PERUBAHAN", 
                            fg_color="#46897C", hover_color="#356B5F",
                            width=220, height=45, corner_radius=10,
                            command=simpan_perubahan).grid(row=0, column=0, padx=10)

        elif aplikasi.role == "petugas":
            ctk.CTkButton(isi, text="KENDARAAN KELUAR", 
                        fg_color="#4B72AD", width=300, height=40, corner_radius=10,
                        command=proses_keluar).grid(row=5, column=0, columnspan=2, padx=10, pady=(15, 5))
            
            ctk.CTkButton(frm_btn, text="DAFTAR PARKIR", 
                                    fg_color="#5A79A8", hover_color="#466087", width=280, height=50, corner_radius=10, 
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
        
        data_ekspor = []
        
        def simpan_pdf():
            if not data_ekspor:
                messagebox.showwarning("Peringatan", "Tidak ada data untuk disimpan!")
                return
            
            nama_file = f"rekap_{var_periode.get()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            dokumen = SimpleDocTemplate("rekap_laporan-pdf/" + nama_file, pagesize=A4)
            elemen = []
            gaya = getSampleStyleSheet()
            
            elemen.append(Paragraph(f"REKAPITULASI TRANSAKSI - {var_periode.get().upper()}", gaya["Title"]))
            elemen.append(Paragraph(f"Dicetak: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", gaya["Normal"]))
            elemen.append(Paragraph(" ", gaya["Normal"]))
            
            kepala = [["Periode", "Jumlah Transaksi", "Total Kendaraan", "Total Pendapatan"]]
            isi = kepala + [[str(sel) for sel in baris] for baris in data_ekspor]
            
            tabel_pdf = Table(isi)
            tabel_pdf.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                ("GRID", (0,0), (-1,-1), 1, colors.black),
                ("FONTSIZE", (0,0), (-1,-1), 10),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.lightgrey])
            ]))
            elemen.append(tabel_pdf)
            dokumen.build(elemen)
            messagebox.showinfo("Berhasil", f"Tersimpan:\nrekap_laporan-pdf/{nama_file}")
            
        def simpan_excel():
            if not data_ekspor:
                messagebox.showwarning("Peringatan", "Tidak ada data untuk disimpan!")
                return
            
            nama_file = f"rekap_{var_periode.get()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            lokasi = "rekap_laporan-excel/" + nama_file
            buku = xlsxwriter.Workbook(lokasi)
            lembar = buku.add_worksheet()
            
            judul = ["periode", "Jumlah Transaksi", "Total Kendaraan", "Total Pendapatan"]
            lembar.write_row(0, 0, judul)
            
            baris = 1
            for isi_baris in data_ekspor:
                lembar.write_row(baris, 0, isi_baris)
                baris += 1
                
            buku.close()
            messagebox.showinfo("Berhasil", f"Tersimpan:\nrekap_laporan-excel/{nama_file}")

        def muat_rekap():
            nonlocal data_ekspor
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
                        SELECT 
                            CONCAT(YEAR(waktu_masuk), ' - Minggu ', WEEK(waktu_masuk)) AS periode,
                            COUNT(*) AS jumlah,
                            COUNT(DISTINCT id_kendaraan) AS kendaraan,
                            SUM(biaya_total) AS pendapatan
                        FROM tb_transaksi
                        WHERE status = 'keluar'
                        GROUP BY periode
                        ORDER BY periode DESC
                        LIMIT 12
                    """)
                elif jenis == "bulanan":
                    kuror.execute("""
                        SELECT 
                            CONCAT(YEAR(waktu_masuk), ' - ', MONTHNAME(waktu_masuk)) AS periode,
                            COUNT(*) AS jumlah,
                            COUNT(DISTINCT id_kendaraan) AS kendaraan,
                            SUM(biaya_total) AS pendapatan
                        FROM tb_transaksi
                        WHERE status = 'keluar'
                        GROUP BY periode
                        ORDER BY periode DESC
                        LIMIT 12
                    """)

                data = kuror.fetchall()
                total_pendapatan = 0
                total_transaksi = 0
                total_kendaraan = 0
                data_ekspor = []

                if data:
                    for baris in data:
                        pendapatan = baris[3] if baris[3] else 0
                        total_pendapatan += pendapatan
                        total_transaksi += baris[1]
                        total_kendaraan += baris[2]
                        data_ekspor.append([baris[0], baris[1], baris[2], pendapatan])
                        tabel.insert("", "end", values=(
                            str(baris[0]),
                            str(baris[1]),
                            str(baris[2]),
                            f"Rp {pendapatan:,}"
                        ))
                    
                    data_ekspor.append(["TOTAL SEMUA", total_transaksi, total_kendaraan, total_pendapatan])
                    tabel.insert("", "end", values=(
                        "TOTAL SEMUA",
                        str(total_transaksi),
                        str(total_kendaraan),
                        f"Rp {total_pendapatan:,}"
                    ))
                else:
                    tabel.insert("", "end", values=("Belum Ada Data", "-", "-", "-"))

            except Exception as e:
                tabel.insert("", "end", values=(f"Error: {str(e)}", "", "", ""))
            finally:
                kuror.close()
                db.close()
            
            frm_tombol = ctk.CTkFrame(aplikasi, fg_color="transparent")
            frm_tombol.pack(pady=10)
            
            ctk.CTkButton(frm_tombol, text="Simpan ke PDF", width=180, height=40, fg_color="#254273", hover_color="#1A3057",
                        command=simpan_pdf).pack(side="left", padx=10)
            ctk.CTkButton(frm_tombol, text="Simpan ke Excel", width=180, height=40, fg_color="#20594E", hover_color="#164239",
                        command=simpan_excel).pack(side="left", padx=10)
            

        muat_rekap()
        var_periode.trace("w", lambda *args: muat_rekap())