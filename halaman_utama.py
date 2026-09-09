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

        

        frm_btn = ctk.CTkFrame(aplikasi, fg_color="transparent")
        frm_btn.pack(pady=15, padx=20)

        btn_warna = {"width": 280, "height": 60, "corner_radius": 12}

        # === PERAN ADMIN — DASHBOARD LENGKAP ===
        if aplikasi.role == "admin":
            ctk.CTkLabel(isi, text="📊 DASHBOARD ADMIN", 
                         font=("Arial", 18, "bold"), text_color="#4ECDC4").grid(row=0, column=0, columnspan=2, pady=(15, 20))

            # === AMBIL DATA RINGKASAN ===
            db = buat_koneksi()
            parkir_masuk = 0
            transaksi_hari_ini = 0
            pendapatan_hari_ini = 0
            jumlah_area = 0
            daftar_kendaraan = []

            if db:
                kuror = db.cursor()
                try:
                    kuror.execute("SELECT COUNT(*) FROM tb_transaksi WHERE status = 'masuk'")
                    parkir_masuk = kuror.fetchone()[0]

                    kuror.execute("SELECT COUNT(*), SUM(biaya_total) FROM tb_transaksi WHERE DATE(waktu_masuk) = CURDATE() AND status = 'keluar'")
                    hasil = kuror.fetchone()
                    transaksi_hari_ini = hasil[0] if hasil[0] else 0
                    pendapatan_hari_ini = hasil[1] if hasil[1] else 0

                    kuror.execute("SELECT COUNT(*) FROM tb_area_parkir")
                    jumlah_area = kuror.fetchone()[0]

                    # === AMBIL DAFTAR KENDARAAN SEDANG PARKIR ===
                    kuror.execute("""
                        SELECT t.id_parkir, k.plat_nomor, k.jenis_kendaraan, 
                               t.waktu_masuk, a.nama_area
                        FROM tb_transaksi t
                        JOIN tb_kendaraan k ON t.id_kendaraan = k.id_kendaraan
                        JOIN tb_area_parkir a ON t.id_area = a.id_area
                        WHERE t.status = 'masuk'
                        ORDER BY t.waktu_masuk DESC
                        LIMIT 10
                    """)
                    daftar_kendaraan = kuror.fetchall()

                except Exception as e:
                    print("Data dashboard:", e)
                finally:
                    kuror.close()
                    db.close()

            # === KOTAK INFORMASI ===
            frm_info = ctk.CTkFrame(isi, fg_color="transparent")
            frm_info.grid(row=1, column=0, columnspan=2, pady=(0, 15))

            def buat_kotak_info(induk, judul, nilai, warna):
                kotak = ctk.CTkFrame(induk, corner_radius=14, fg_color=warna, width=140, height=110)
                kotak.pack(side="left", padx=10, pady=5)
                kotak.pack_propagate(False)
                ctk.CTkLabel(kotak, text=judul, font=("Arial", 11), text_color="#E8E8E8").pack(pady=(18, 8))
                ctk.CTkLabel(kotak, text=str(nilai), font=("Arial", 22, "bold"), text_color="#FFFFFF").pack()

            buat_kotak_info(frm_info, "Sedang Parkir", parkir_masuk, "#1E3A5F")
            buat_kotak_info(frm_info, "Transaksi Hari Ini", transaksi_hari_ini, "#1E4D42")
            buat_kotak_info(frm_info, "Pendapatan Hari Ini", f"Rp {pendapatan_hari_ini:,}", "#2E4D72")
            buat_kotak_info(frm_info, "Jumlah Area", jumlah_area, "#4A3F72")
            
            ctk.CTkLabel(isi, text="🔧 KELOLA DATA", 
             font=("Arial", 13, "bold")).grid(row=2, column=0, columnspan=2, pady=(0, 8))

            ctk.CTkButton(isi, text="🅿️ KELOLA AREA PARKIR",
                         fg_color="#254273", hover_color="#1A3057", 
                         width=275, height=42, corner_radius=12,
                         font=("Arial", 12, "bold"),
                         command=kelola_area_parkir).grid(row=3, column=0, padx=(10, 6), pady=(0, 10))

            ctk.CTkButton(isi, text="💰 KELOLA TARIF PARKIR",
                         fg_color="#42366B", hover_color="#312852", 
                         width=275, height=42, corner_radius=12,
                         font=("Arial", 12, "bold"),
                         command=kelola_tarif_parkir).grid(row=3, column=1, padx=(6, 10), pady=(0, 10))

            # === TABEL DAFTAR KENDARAAN (DENGAN SCROLL) ===
            ctk.CTkLabel(isi, text="🚗 DAFTAR KENDARAAN SEDANG PARKIR", 
                        font=("Arial", 13, "bold")).grid(row=4, column=0, columnspan=2, pady=(5, 8))

            # HEADER TABEL
            frm_header = ctk.CTkFrame(isi, fg_color="#254273", corner_radius=10)
            frm_header.grid(row=5, column=0, columnspan=2, padx=15, pady=(0, 0), sticky="nsew")
            ctk.CTkLabel(frm_header, text="Plat Nomor", font=("Arial", 11, "bold"), width=150).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(frm_header, text="Jenis", font=("Arial", 11, "bold"), width=100).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(frm_header, text="Waktu Masuk", font=("Arial", 11, "bold"), width=180).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(frm_header, text="Area Parkir", font=("Arial", 11, "bold"), width=150).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(frm_header, text="Aksi", font=("Arial", 11, "bold"), width=80).pack(side="left", padx=10, pady=8)

            # === AREA SCROLL — TINGGI DIPERKECIL! ===
            frm_scroll = ctk.CTkScrollableFrame(isi, label_text="", height=300)  # ← BISA BESAR LAGI!
            frm_scroll.grid(row=6, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="nsew")

            # ISI TABEL
            if daftar_kendaraan:
                for idx, data in enumerate(daftar_kendaraan):
                    id_parkir, plat, jenis, waktu, area = data
                    warna_baris = "#2C2C2C" if idx % 2 == 0 else "#383838"
                    baris = ctk.CTkFrame(frm_scroll, fg_color=warna_baris, corner_radius=6)
                    baris.pack(fill="x", padx=2, pady=1)
                    waktu_str = waktu.strftime("%d-%m-%Y %H:%M") if waktu else "-"
                    ctk.CTkLabel(baris, text=plat, font=("Arial", 10), width=150).pack(side="left", padx=10, pady=6)  # ← pady diperkecil
                    ctk.CTkLabel(baris, text=jenis, font=("Arial", 10), width=100).pack(side="left", padx=10, pady=6)
                    ctk.CTkLabel(baris, text=waktu_str, font=("Arial", 10), width=180).pack(side="left", padx=10, pady=6)
                    ctk.CTkLabel(baris, text=area, font=("Arial", 10), width=150).pack(side="left", padx=10, pady=6)
                    ctk.CTkButton(baris, text="EDIT", width=60, height=28, corner_radius=6,
                                  fg_color="#2F7265", hover_color="#23574E",
                                  font=("Arial", 10, "bold"),
                                  command=lambda pid=id_parkir: buka_jendela_edit(aplikasi, pid)).pack(side="left", padx=10, pady=6)
            else:
                ctk.CTkLabel(frm_scroll, text="Tidak ada kendaraan yang sedang parkir", 
                             font=("Arial", 12), text_color="#888888").pack(pady=30)

            
        # === PERAN PETUGAS ===
        elif aplikasi.role == "petugas":
            # Petugas: Input MASUK + KELUAR keduanya
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
                            
            ctk.CTkButton(isi, text="📥 KENDARAAN MASUK", 
                        fg_color="#254273", width=300, height=40, corner_radius=10,
                        command=proses_masuk).grid(row=5, column=0, columnspan=2, padx=10, pady=(15, 5))

            ctk.CTkButton(isi, text="📤 KENDARAAN KELUAR", 
                        fg_color="#20594E", width=300, height=40, corner_radius=10,
                        command=proses_keluar).grid(row=6, column=0, columnspan=2, padx=10, pady=5)

            ctk.CTkButton(frm_btn, text="📋 DAFTAR PARKIR", 
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
        
        frm_btn = ctk.CTkFrame(aplikasi, fg_color="transparent")
        frm_btn.pack(pady=15, padx=20)
        
        ctk.CTkButton(frm_btn, text="LOG AKTIVITAS", 
                                fg_color="#7267A3", hover_color="#5A5082", width=280, height=50, corner_radius=10,
                                command=lambda: tampilkan_log(aplikasi)).pack(side="left", pady=5, padx=20)

def buka_jendela_edit(induk, id_parkir=None):
    jendela_edit = ctk.CTkToplevel(induk)
    jendela_edit.title("EDIT DATA KENDARAAN")
    jendela_edit.geometry("520x480")
    jendela_edit.resizable(False, False)

    id_transaksi_terpilih = ctk.StringVar(value="")

    # === VARIABEL UNTUK MENAMPUNG DATA DARI DATABASE ===
    data_terpilih = None

    # === JIKA ADA ID YANG DIKIRIM DARI DASHBOARD → LANGSUNG AMBIL DATANYA! ===
    if id_parkir:
        db = buat_koneksi()
        if db:
            try:
                kuror = db.cursor()
                kuror.execute("""
                    SELECT t.id_parkir, k.plat_nomor, k.jenis_kendaraan, 
                           t.waktu_masuk, t.id_area, a.nama_area
                    FROM tb_transaksi t
                    JOIN tb_kendaraan k ON t.id_kendaraan = k.id_kendaraan
                    JOIN tb_area_parkir a ON t.id_area = a.id_area
                    WHERE t.id_parkir = %s
                """, (id_parkir,))
                data_terpilih = kuror.fetchone()
                kuror.close()
            except Exception as e:
                print("Gagal ambil data edit:", e)
            finally:
                db.close()

    # === JUDUL FORM ===
    ctk.CTkLabel(jendela_edit, text="✏️ EDIT DATA KENDARAAN", 
                 font=("Arial", 16, "bold")).pack(pady=(20, 15))

    frm_isian = ctk.CTkFrame(jendela_edit)
    frm_isian.pack(padx=30, pady=10, fill="x")

    # === PLAT NOMOR ===
    ctk.CTkLabel(frm_isian, text="Plat Nomor Kendaraan").grid(row=0, column=0, padx=15, pady=(20, 5), sticky="w")
    ent_plat = ctk.CTkEntry(frm_isian, placeholder_text="Contoh: B 1234 ABC", width=300, height=38)
    ent_plat.grid(row=0, column=1, padx=15, pady=(20, 5))

    # === JENIS KENDARAAN ===
    ctk.CTkLabel(frm_isian, text="Jenis Kendaraan").grid(row=1, column=0, padx=15, pady=(15, 5), sticky="w")
    cmb_jenis = ctk.CTkComboBox(frm_isian, values=["motor", "mobil", "lainnya"], width=300, height=38)
    cmb_jenis.grid(row=1, column=1, padx=15, pady=(15, 5))

    # === AREA PARKIR ===
    ctk.CTkLabel(frm_isian, text="Area Parkir").grid(row=2, column=0, padx=15, pady=(15, 5), sticky="w")
    cmb_area = ctk.CTkComboBox(frm_isian, values=[], width=300, height=38)
    cmb_area.grid(row=2, column=1, padx=15, pady=(15, 5))

    # === WAKTU MASUK ===
    ctk.CTkLabel(frm_isian, text="Waktu Masuk").grid(row=3, column=0, padx=15, pady=(15, 5), sticky="w")
    ent_waktu = ctk.CTkEntry(frm_isian, placeholder_text="TTTT-BB-HH JJ:MM", width=300, height=38)
    ent_waktu.grid(row=3, column=1, padx=15, pady=(15, 5))

    # === ISI OTOMATIS JIKA ADA DATA TERPILIH ===
    if data_terpilih:
        id_p, plat, jenis, waktu, id_a, nama_a = data_terpilih
        id_transaksi_terpilih.set(str(id_p))  # simpan ID untuk disimpan nanti
        ent_plat.insert(0, plat)
        cmb_jenis.set(jenis)
        # Isi daftar area & pilih yang sesuai
        db = buat_koneksi()
        daftar_area = []
        if db:
            kuror = db.cursor()
            kuror.execute("SELECT id_area, nama_area FROM tb_area_parkir")
            daftar_area = [f"{row[0]} - {row[1]}" for row in kuror.fetchall()]
            kuror.close()
            db.close()
        cmb_area.configure(values=daftar_area)
        cmb_area.set(f"{id_a} - {nama_a}")
        # Format waktu
        waktu_str = waktu.strftime("%Y-%m-%d %H:%M") if waktu else ""
        ent_waktu.insert(0, waktu_str)

    # === TOMBOL SIMPAN PERUBAHAN ===
    def simpan_perubahan():
        plat_baru = ent_plat.get().strip().upper()
        jenis_baru = cmb_jenis.get()
        area_pilih = cmb_area.get()
        waktu_baru = ent_waktu.get().strip()
        id_p = id_transaksi_terpilih.get()

        if not id_p:
            messagebox.showwarning("Peringatan", "Silakan pilih kendaraan dari daftar terlebih dahulu!")
            return
        if not plat_baru:
            messagebox.showwarning("Peringatan", "Plat nomor tidak boleh kosong!")
            return

        # Ambil id_area dari teks yang dipilih
        id_area_baru = area_pilih.split(" - ")[0] if " - " in area_pilih else area_pilih

        db = buat_koneksi()
        if not db: return
        kuror = db.cursor()
        try:
            kuror.execute("""
                UPDATE tb_kendaraan k
                JOIN tb_transaksi t ON k.id_kendaraan = t.id_kendaraan
                SET k.plat_nomor = %s, k.jenis_kendaraan = %s, t.id_area = %s, t.waktu_masuk = %s
                WHERE t.id_parkir = %s
            """, (plat_baru, jenis_baru, id_area_baru, waktu_baru, id_p))
            db.commit()
            messagebox.showinfo("Berhasil", "✅ Data kendaraan berhasil diperbarui!")
            jendela_edit.destroy()
        except Exception as e:
            db.rollback()
            messagebox.showerror("Error", f"Gagal menyimpan:\n{str(e)}")
        finally:
            kuror.close()
            db.close()

    ctk.CTkButton(jendela_edit, text="💾 SIMPAN PERUBAHAN",
                  fg_color="#2F7265", hover_color="#23574E",
                  width=260, height=45, corner_radius=12,
                  font=("Arial", 13, "bold"),
                  command=simpan_perubahan).pack(pady=(10, 25))
    
def kelola_area_parkir():
    # === 1. BUAT JENDELA DULU ===
    jendela = ctk.CTkToplevel()
    jendela.title("KELOLA AREA PARKIR")
    jendela.geometry("520x480")

    # === 2. BUAT FRAME ISIAN FORM ===
    frm_isian = ctk.CTkFrame(jendela)
    frm_isian.pack(padx=25, pady=(20, 10), fill="x")

    # === ISIAN: NAMA AREA ===
    ctk.CTkLabel(frm_isian, text="Nama Area Parkir").grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
    ent_nama = ctk.CTkEntry(frm_isian, placeholder_text="Contoh: Area A - Mobil", width=300, height=38)
    ent_nama.grid(row=0, column=1, padx=15, pady=(10, 5))

    # === ISIAN: KAPASITAS ===
    ctk.CTkLabel(frm_isian, text="Kapasitas Tempat").grid(row=1, column=0, padx=15, pady=(15, 5), sticky="w")
    ent_kapasitas = ctk.CTkEntry(frm_isian, placeholder_text="Jumlah tempat, contoh: 20", width=300, height=38)
    ent_kapasitas.grid(row=1, column=1, padx=15, pady=(15, 5))

    # === 3. FUNGSI SIMPAN DATA ===
    def simpan_area():
        nama_area = ent_nama.get().strip()
        kapasitas = ent_kapasitas.get().strip()

        if not nama_area or not kapasitas:
            messagebox.showwarning("Peringatan", "Nama Area dan Kapasitas WAJIB diisi!")
            return

        db = buat_koneksi()
        if not db: return
        kuror = db.cursor()
        try:
            kuror.execute("""
                INSERT INTO tb_area_parkir (nama_area, kapasitas)
                VALUES (%s, %s)
            """, (nama_area, kapasitas))
            db.commit()
            messagebox.showinfo("Berhasil", "✅ Area Parkir Berhasil Disimpan!")
            ent_nama.delete(0, "end")
            ent_kapasitas.delete(0, "end")
            muat_data()
        except Exception as e:
            db.rollback()
            messagebox.showerror("Error", f"Gagal menyimpan:\n{str(e)}")
        finally:
            kuror.close()
            db.close()

    # === 🔴 FUNGSI HAPUS DATA ===
    def hapus_area():
        terpilih = tabel.selection()
        if not terpilih:
            messagebox.showwarning("Peringatan", "Pilih dulu data yang ingin dihapus dari tabel!")
            return

        # Ambil ID area dari baris yang dipilih
        nilai = tabel.item(terpilih[0])["values"]
        id_area = nilai[0]  # kolom pertama = ID

        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Yakin ingin MENGHAPUS Area Parkir ini?\n\nID: {id_area}\nNama: {nilai[1]}"
        )
        if not konfirmasi:
            return

        db = buat_koneksi()
        if not db: return
        kuror = db.cursor()
        try:
            kuror.execute("DELETE FROM tb_area_parkir WHERE id_area = %s", (id_area,))
            db.commit()
            messagebox.showinfo("Berhasil", "✅ Area Parkir Berhasil Dihapus!")
            muat_data()  # ← Refresh tabel setelah hapus
        except Exception as e:
            db.rollback()
            messagebox.showerror("Error", f"Gagal menghapus:\n{str(e)}\n\nKemungkinan: Area ini masih dipakai di data transaksi!")
        finally:
            kuror.close()
            db.close()

    # === TOMBOL SIMPAN & HAPUS ===
    frm_tombol = ctk.CTkFrame(frm_isian, fg_color="transparent")
    frm_tombol.grid(row=2, column=0, columnspan=2, pady=15)

    ctk.CTkButton(frm_tombol, text="💾 SIMPAN AREA",
                  fg_color="#2F7265", hover_color="#23574E",
                  width=180, height=40, corner_radius=10,
                  command=simpan_area).pack(side="left", padx=5)

    ctk.CTkButton(frm_tombol, text="🗑️ HAPUS TERPILIH",
                  fg_color="#A82C3C", hover_color="#8C2432",
                  width=180, height=40, corner_radius=10,
                  command=hapus_area).pack(side="left", padx=5)

    # === 4. BUAT TABEL ===
    frm_tabel = ctk.CTkFrame(jendela)
    frm_tabel.pack(pady=(5, 15), padx=25, fill="both", expand=True)

    cols = ("ID", "Nama Area Parkir", "Kapasitas")
    tabel = ttk.Treeview(frm_tabel, columns=cols, show="headings", height=8)
    for judul in cols:
        tabel.heading(judul, text=judul)
        tabel.column(judul, width=150, anchor="center")
    tabel.pack(fill="both", expand=True)

    # === 5. FUNGSI MUAT DATA KE TABEL ===
    def muat_data():
        for baris in tabel.get_children():
            tabel.delete(baris)
        db = buat_koneksi()
        if not db: return
        kuror = db.cursor()
        kuror.execute("SELECT id_area, nama_area, kapasitas FROM tb_area_parkir ORDER BY id_area")
        for data in kuror.fetchall():
            tabel.insert("", "end", values=data)
        kuror.close()
        db.close()

    muat_data()


def kelola_tarif_parkir():
    jendela = ctk.CTkToplevel()
    jendela.title("KELOLA TARIF PARKIR")
    jendela.geometry("500x480")

    # === JUDUL ===
    ctk.CTkLabel(jendela, text="KELOLA TARIF PARKIR", 
                 font=("Arial", 16, "bold")).pack(pady=(20, 15))

    # === FORM INPUT ===
    frm = ctk.CTkFrame(jendela)
    frm.pack(pady=10, padx=40, fill="x")

    # Jenis kendaraan → TAMPIL SAJA, TIDAK DIUBAH
    ctk.CTkLabel(frm, text="Jenis Kendaraan", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=15, pady=(20, 8), sticky="w")
    lbl_jenis = ctk.CTkLabel(frm, text="Pilih dari tabel", font=("Arial", 12), fg_color="#333333", corner_radius=6, width=200, height=38)
    lbl_jenis.grid(row=0, column=1, padx=15, pady=(20, 8))

    # Tarif → yang diubah saja
    ctk.CTkLabel(frm, text="Tarif per Jam (Rp)", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=15, pady=(15, 8), sticky="w")
    ent_tarif = ctk.CTkEntry(frm, placeholder_text="Contoh: 3000", height=38)
    ent_tarif.grid(row=1, column=1, padx=15, pady=(15, 8))

    # Simpan ID yang sedang diedit
    id_dipilih = {"nilai": None}

    # === FUNGSI: AMBIL DATA DARI TABEL KE FORM ===
    def ambil_data_untuk_edit():
        terpilih = tabel.selection()
        if not terpilih:
            messagebox.showinfo("Info", "Klik dulu salah satu baris di tabel!")
            return

        nilai = tabel.item(terpilih[0])["values"]
        id_dipilih["nilai"] = nilai[0]          # ID
        lbl_jenis.configure(text=nilai[1])       # Jenis kendaraan
        ent_tarif.delete(0, "end")
        ent_tarif.insert(0, str(nilai[2]))       # Tarif

    # === FUNGSI: SIMPAN PERUBAHAN ===
    def simpan_perubahan():
        if not id_dipilih["nilai"]:
            messagebox.showwarning("Peringatan", "Pilih dulu dari tabel yang mau diubah!")
            return

        tarif_baru = ent_tarif.get().strip()
        if not tarif_baru or not tarif_baru.isdigit():
            messagebox.showwarning("Peringatan", "Masukkan tarif dengan ANGKA saja!")
            return

        db = buat_koneksi()
        if not db: return
        kuror = db.cursor()
        try:
            kuror.execute("""
                UPDATE tb_tarif 
                SET tarif_per_jam = %s 
                WHERE id_tarif = %s
            """, (tarif_baru, id_dipilih["nilai"]))
            db.commit()
            messagebox.showinfo("Berhasil", "✅ Tarif Berhasil Diperbarui!")
            # Kosongkan form
            lbl_jenis.configure(text="Pilih dari tabel")
            ent_tarif.delete(0, "end")
            id_dipilih["nilai"] = None
            muat_data()  # Refresh tabel
        except Exception as e:
            db.rollback()
            messagebox.showerror("Error", f"Gagal menyimpan!\n{str(e)}")
        finally:
            kuror.close()
            db.close()

    # === TOMBOL ===
    frm_tombol = ctk.CTkFrame(frm, fg_color="transparent")
    frm_tombol.grid(row=2, column=0, columnspan=2, pady=(15, 20))

    ctk.CTkButton(frm_tombol, text="📋 PILIH DARI TABEL", 
                  fg_color="#254273", width=200, command=ambil_data_untuk_edit).pack(side="left", padx=5)
    ctk.CTkButton(frm_tombol, text="💾 SIMPAN PERUBAHAN", 
                  fg_color="#7267A3", width=200, command=simpan_perubahan).pack(side="left", padx=5)

    # === TABEL DAFTAR TARIF ===
    frm_tabel = ctk.CTkFrame(jendela)
    frm_tabel.pack(pady=5, padx=30, fill="both", expand=True)

    cols = ("ID", "Jenis Kendaraan", "Tarif per Jam (Rp)")
    tabel = ttk.Treeview(frm_tabel, columns=cols, show="headings", height=6)
    for judul in cols:
        tabel.heading(judul, text=judul)
        tabel.column(judul, width=140, anchor="center")
    tabel.pack(fill="both", expand=True, padx=10, pady=10)

    # === FUNGSI MUAT DATA ===
    def muat_data():
        for baris in tabel.get_children():
            tabel.delete(baris)
        db = buat_koneksi()
        if not db: return
        kuror = db.cursor()
        kuror.execute("SELECT id_tarif, jenis_kendaraan, tarif_per_jam FROM tb_tarif ORDER BY id_tarif")
        for data in kuror.fetchall():
            tabel.insert("", "end", values=data)
        kuror.close()
        db.close()

    muat_data()