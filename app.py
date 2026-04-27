import streamlit as st
import requests 
import pandas as pd
import os
import hashlib
from datetime import datetime
import plotly.express as px
import base64
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
from io import BytesIO 
from fpdf import FPDF
import tempfile
import urllib.request
import re

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard IPH Kota Batu",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS KUSTOM (tema BPS + font Lexend) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* === GLOBAL === */
        * {
            font-family: 'Lexend', sans-serif;
        }
        .stApp {
            background: linear-gradient(145deg, #F1F5F9 0%, #E2E8F0 100%);
        }
        
        /* === SIDEBAR ELEGAN === */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E2A3A 0%, #0F1722 100%);
            border-right: none;
            box-shadow: 4px 0 20px rgba(0,0,0,0.08);
        }
        [data-testid="stSidebar"] * {
            color: #F1F5F9 !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255, 255, 255, 0.05);
            border: none;
            border-radius: 12px;
            text-align: left;
            font-weight: 500;
            width: 100%;
            margin-bottom: 6px;
            transition: all 0.25s ease;
            backdrop-filter: blur(4px);
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(249, 115, 22, 0.2);
            transform: translateX(6px);
            border-left: 2px solid #F97316;
        }
        .sidebar-logo-area {
            text-align: center;
            margin-bottom: 1.8rem;
            padding-bottom: 1.2rem;
            border-bottom: 1px solid rgba(255, 193, 7, 0.3);
        }
        .sidebar-user-avatar {
            background: linear-gradient(135deg, #F97316, #F59E0B);
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.3rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .sidebar-section-title {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #F59E0B !important;
            margin-top: 1.8rem;
            margin-bottom: 0.8rem;
            font-weight: 600;
        }
        .notif-badge {
            background: #F97316;
            color: white;
            border-radius: 30px;
            padding: 2px 8px;
            font-size: 0.7rem;
            margin-left: 8px;
        }
        
        /* === HEADER UTAMA === */
        .main-header {
            background: linear-gradient(105deg, #D35400 0%, #F39C12 100%);
            padding: 1.8rem;
            border-radius: 28px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 12px 24px -8px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        }
        .main-header h1 {
            color: white;
            margin: 0;
            font-size: 2rem;
            font-weight: 600;
        }
        .main-header p {
            margin: 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }
        
        /* === CARD METRIK (GLASSMORPHISM) === */
        .metric-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(12px);
            border-radius: 24px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 8px 20px rgba(0,0,0,0.05);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 16px 28px -8px rgba(0,0,0,0.12);
            background: rgba(255, 255, 255, 0.9);
        }
        .metric-card h3 {
            color: #475569;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-card p:first-of-type {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E293B;
            margin: 0.2rem 0 0 0;
        }
        
        /* === TOMBOL === */
        .stButton > button {
            background: linear-gradient(90deg, #F97316, #EA580C);
            color: white;
            border: none;
            border-radius: 40px;
            font-weight: 600;
            padding: 0.6rem 1.2rem;
            transition: all 0.25s ease;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .stButton > button:hover {
            background: linear-gradient(90deg, #EA580C, #C2410C);
            transform: scale(1.02);
            box-shadow: 0 6px 14px rgba(0,0,0,0.15);
        }
        
        /* === TAB === */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background: white;
            padding: 6px 12px;
            border-radius: 60px;
            display: inline-flex;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .stTabs [data-baseweb="tab"] {
            font-weight: 600;
            padding: 8px 20px;
            border-radius: 40px;
            color: #475569;
            transition: all 0.2s;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #F97316;
            color: white !important;
        }
        
        /* === DATAFRAME === */
        .stDataFrame {
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        
        /* === INPUT FIELD === */
        .stTextInput > div > div > input, 
        .stSelectbox > div > div, 
        .stNumberInput > div > div > input {
            border-radius: 16px;
            border: 1px solid #E2E8F0;
            transition: all 0.2s;
        }
        .stTextInput > div > div > input:focus {
            border-color: #F97316;
            box-shadow: 0 0 0 2px rgba(249,115,22,0.2);
        }
        
        /* === EXPANDER === */
        .streamlit-expanderHeader {
            background: white;
            border-radius: 20px;
            border: none;
            padding: 0.8rem 1.2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .streamlit-expanderContent {
            background: white;
            border-radius: 0 0 20px 20px;
            padding: 1rem;
        }
        
        /* === PLOTLY CHART === */
        .js-plotly-plot .plotly .main-svg {
            border-radius: 24px;
            background: white;
            box-shadow: 0 8px 24px rgba(0,0,0,0.05);
        }
        
        /* === TOMBOL HAPUS === */
        .stButton > button[kind="secondary"] {
            background: #EF4444;
            background: linear-gradient(90deg, #EF4444, #DC2626);
        }
        .stButton > button[kind="secondary"]:hover {
            background: #DC2626;
        }
        
        /* === INFO, SUCCESS, ERROR === */
        .stAlert {
            border-radius: 20px;
            border-left: 6px solid #F97316;
            background: white;
        }
        
        /* === TOAST === */
        .stToast {
            border-radius: 20px;
            background: white;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# --- FUNGSI HASH PASSWORD ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

USER_DB = "users_list.csv"
def init_db():
    if not os.path.exists(USER_DB):
        df = pd.DataFrame([["admin", hash_password("admin123"), "Admin"]], columns=["username", "password", "role"])
        df.to_csv(USER_DB, index=False)
def add_user(name, pwd):
    df = pd.read_csv(USER_DB)
    if name in df['username'].values:
        return False
    new_user = pd.DataFrame([[name, hash_password(pwd), "Pegawai"]], columns=["username", "password", "role"])
    pd.concat([df, new_user]).to_csv(USER_DB, index=False)
    return True
def check_login(name, pwd):
    df = pd.read_csv(USER_DB)
    hashed = hash_password(pwd)
    user = df[(df['username'] == name) & (df['password'] == hashed)]
    if not user.empty:
        return user.iloc[0]['role']
    return None
init_db()

# --- INISIALISASI DATABASE ---
RAPAT_DB = "rapat_tpid.csv"
IPH_DB = "data_iph_harian.csv"
KOMODITAS_DB = "komoditas_list.csv"
NOTIF_DB = "notifikasi.csv"

DEFAULT_KOMODITAS = [
    "BERAS", "DAGING AYAM RAS", "TELUR AYAM RAS", "DAGING SAPI",
    "CABAI MERAH", "CABAI RAWIT", "BAWANG MERAH", "BAWANG PUTIH",
    "MINYAK GORENG", "GULA PASIR", "TEPUNG TERIGU", "PISANG", "JERUK"
]

if not os.path.exists(KOMODITAS_DB):
    pd.DataFrame(DEFAULT_KOMODITAS, columns=["komoditas"]).to_csv(KOMODITAS_DB, index=False)

if not os.path.exists(RAPAT_DB):
    df_rapat = pd.DataFrame(columns=[
        "id", "tanggal", "pegawai", "link_undangan", "link_bahan_materi", "link_dokumentasi",
        "ringkasan_indikator", "resume", "action_items", "status", "last_editor", "created_by", "created_at"
    ])
    df_rapat.to_csv(RAPAT_DB, index=False)

df_rapat_check = pd.read_csv(RAPAT_DB)
if 'gambar_dokumentasi' not in df_rapat_check.columns:
    df_rapat_check['gambar_dokumentasi'] = ''
    df_rapat_check.to_csv(RAPAT_DB, index=False)

if not os.path.exists(IPH_DB):
    df_iph = pd.DataFrame(columns=[
        "tahun", "bulan", "minggu_ke", "komoditas", "harga", "persen_change", "last_updated"
    ])
    df_iph.to_csv(IPH_DB, index=False)

if not os.path.exists(NOTIF_DB):
    df_notif = pd.DataFrame(columns=["id_rapat", "pegawai", "pesan", "dibaca", "tanggal"])
    df_notif.to_csv(NOTIF_DB, index=False)

# --- INISIALISASI DAFTAR PEGAWAI (DINAMIS) ---
PEGAWAI_DB = "daftar_pegawai.csv"
DEFAULT_PEGAWAI_LIST = [
    "Ir. Yuniarni Erry Wahyuti",
    "Adam Mahmud",
    "Gatot Suharmoko",
    "Muhammad Arief Nurohman",
    "Sayu Made Widiari",
    "Eka Cahyani",
    "Dwi Esti Kurniasih",
    "Arif Nugroho Wicaksono",
    "FX Gugus Febri Putranto",
    "Sulistyono",
    "Adina Astasia",
    "Eko Wibowo",
    "Singgih Wicaksono",
    "Nurlaila Oktarahmayanti",
    "Dhika Devara Prihastiono",
    "Mulia Estiwilaras",
    "Wahyu Mega Alfazip",
]
if not os.path.exists(PEGAWAI_DB):
    pd.DataFrame(DEFAULT_PEGAWAI_LIST, columns=["nama"]).to_csv(PEGAWAI_DB, index=False)

def load_pegawai():
    return pd.read_csv(PEGAWAI_DB)['nama'].tolist()

DAFTAR_PEGAWAI = load_pegawai()

# --- FUNGSI BANTU ---
def get_minggu_dari_tanggal(tanggal):
    day = tanggal.day
    if day <= 7: return 1
    elif day <= 14: return 2
    elif day <= 21: return 3
    elif day <= 28: return 4
    else: return 5

def get_previous_price(tahun, bulan, minggu_ke, komoditas):
    df = pd.read_csv(IPH_DB)
    prev_minggu = minggu_ke - 1
    if prev_minggu < 1:
        return None
    prev_data = df[(df['tahun'] == tahun) & (df['bulan'] == bulan) & (df['minggu_ke'] == prev_minggu) & (df['komoditas'] == komoditas)]
    if not prev_data.empty:
        return prev_data.iloc[0]['harga']
    return None

def generate_ringkasan_indikator(tahun, bulan, minggu_ke):
    analisis_file = "iph_analisis.csv"
    if not os.path.exists(analisis_file) or os.path.getsize(analisis_file) == 0:
        return "Data ringkasan IPH belum tersedia."
    
    df = pd.read_csv(analisis_file)
    data_periode = df[(df['tahun'] == tahun) & (df['bulan'] == bulan) & (df['minggu_ke'] == minggu_ke)]
    
    if data_periode.empty:
        return f"Data untuk minggu ke-{minggu_ke} bulan {bulan} tahun {tahun} belum tersedia."
    
    row = data_periode.iloc[0]
    
    # Format angka sesuai input asli (tidak dibatasi 2 desimal)
    def format_original(value):
        if isinstance(value, (int, float)):
            s = f"{value:.10f}"
            s = s.rstrip('0').rstrip('.')
            return s
        return value
    
    indikator = row['indikator']
    if indikator > 0:
        jenis = "inflasi"
    elif indikator < 0:
        jenis = "deflasi"
    else:
        jenis = "stabil"
    
    kom_list = row['komoditas_andil'].split("|")
    nilai_list = [float(x) if x.strip() else 0.0 for x in row['nilai_andil'].split("|")]
    
    andil_lines = []
    for i, (kom, nil) in enumerate(zip(kom_list, nilai_list), start=1):
        andil_lines.append(f"{i}. {kom.title()} ({format_original(nil)}%)")
    andil_str = "\n".join(andil_lines)
    
    fluk_kom = row['fluktuasi_komoditas']
    fluk_nilai = row['fluktuasi_nilai']
    
    bulan_nama = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"][bulan-1]
    
    ringkasan = (
        f"Berikut kami sampaikan IPH Kota Batu minggu ke-{minggu_ke} {bulan_nama} {tahun}.\n"
        f"Kota Batu mengalami {jenis} sebesar {format_original(indikator)}%\n\n"
        f"Komoditas penyumbang andil terbesar:\n{andil_str}\n"
        f"Fluktuasi harga tertinggi terjadi pada {fluk_kom.title()} dengan perubahan {format_original(fluk_nilai)}%."
    )
    return ringkasan

def update_persen_change():
    df = pd.read_csv(IPH_DB)
    for idx, row in df.iterrows():
        prev_harga = get_previous_price(row['tahun'], row['bulan'], row['minggu_ke'], row['komoditas'])
        if prev_harga and prev_harga != 0:
            perubahan = ((row['harga'] - prev_harga) / prev_harga) * 100
            df.at[idx, 'persen_change'] = round(perubahan, 2)
        else:
            df.at[idx, 'persen_change'] = 0
    df.to_csv(IPH_DB, index=False)

def save_iph_data(tahun, bulan, minggu_ke, komoditas_list, harga_list):
    df = pd.read_csv(IPH_DB)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for komoditas, harga in zip(komoditas_list, harga_list):
        existing = df[(df['tahun'] == tahun) & (df['bulan'] == bulan) & (df['minggu_ke'] == minggu_ke) & (df['komoditas'] == komoditas)]
        if not existing.empty:
            idx = existing.index[0]
            df.at[idx, 'harga'] = harga
            df.at[idx, 'last_updated'] = now_str
        else:
            new_row = pd.DataFrame([{'tahun': tahun, 'bulan': bulan, 'minggu_ke': minggu_ke, 'komoditas': komoditas, 'harga': harga, 'persen_change': 0, 'last_updated': now_str}])
            df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(IPH_DB, index=False)
    update_persen_change()

def get_komoditas_list():
    df = pd.read_csv(KOMODITAS_DB)
    return df['komoditas'].tolist()

def add_komoditas(nama_baru):
    df = pd.read_csv(KOMODITAS_DB)
    if nama_baru.upper() not in df['komoditas'].str.upper().tolist():
        new = pd.DataFrame({'komoditas': [nama_baru.upper()]})
        pd.concat([df, new], ignore_index=True).to_csv(KOMODITAS_DB, index=False)
        return True
    return False

def delete_komoditas(nama):
    df = pd.read_csv(KOMODITAS_DB)
    df = df[df['komoditas'] != nama]
    df.to_csv(KOMODITAS_DB, index=False)

def tambah_pegawai(nama_baru):
    df = pd.read_csv(PEGAWAI_DB)
    nama_baru = nama_baru.strip()
    if not nama_baru:
        return False, "Nama tidak boleh kosong."
    if nama_baru in df['nama'].values:
        return False, "Nama sudah ada."
    new = pd.DataFrame({'nama': [nama_baru]})
    pd.concat([df, new], ignore_index=True).to_csv(PEGAWAI_DB, index=False)
    global DAFTAR_PEGAWAI
    DAFTAR_PEGAWAI = load_pegawai()
    return True, "Pegawai berhasil ditambahkan."

def hapus_pegawai(nama):
    df = pd.read_csv(PEGAWAI_DB)
    if nama not in df['nama'].values:
        return False, "Nama tidak ditemukan."
    df = df[df['nama'] != nama]
    df.to_csv(PEGAWAI_DB, index=False)
    global DAFTAR_PEGAWAI
    DAFTAR_PEGAWAI = load_pegawai()
    return True, "Pegawai berhasil dihapus."

def buat_notifikasi(id_rapat, daftar_pegawai, tanggal):
    df_notif = pd.read_csv(NOTIF_DB)
    for peg in daftar_pegawai:
        if not ((df_notif['id_rapat'] == id_rapat) & (df_notif['pegawai'] == peg)).any():
            new_notif = pd.DataFrame([{
                "id_rapat": id_rapat,
                "pegawai": peg,
                "pesan": f"Anda ditugaskan untuk mengisi resume rapat tanggal {tanggal}",
                "dibaca": False,
                "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            df_notif = pd.concat([df_notif, new_notif], ignore_index=True)
    df_notif.to_csv(NOTIF_DB, index=False)

def get_notifikasi(pegawai):
    df = pd.read_csv(NOTIF_DB)
    return df[df['pegawai'] == pegawai]

def tandai_baca(id_rapat, pegawai):
    df = pd.read_csv(NOTIF_DB)
    df.loc[(df['id_rapat'] == id_rapat) & (df['pegawai'] == pegawai), 'dibaca'] = True
    df.to_csv(NOTIF_DB, index=False)

def generate_pdf_resume(row):
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # ========== HEADER SATU BLOK BIRU ==========
        pdf.set_fill_color(30, 60, 120)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Times", 'B', 16)
        pdf.cell(0, 10, "LAPORAN HASIL RAPAT TPID", ln=True, align='C', fill=True)
        pdf.set_font("Times", 'B', 11)
        pdf.cell(0, 8, "Tim Pengendalian Inflasi Daerah Kota Batu", ln=True, align='C', fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(6)
        
        def safe_str(val, default="-"):
            s = str(val) if pd.notna(val) and str(val).strip() != '' else default
            return s
        
        # ========== TABEL INFORMASI (RAPI) ==========
        col_w_label = 45
        col_w_value = pdf.w - pdf.l_margin - col_w_label - pdf.r_margin
        line_h = 8
        
        def draw_table_row(label, value):
            pdf.set_font("Times", 'B', 12)
            pdf.cell(col_w_label, line_h, " " + label + " ", border=1, ln=0)
            pdf.set_font("Times", '', 12)
            pdf.multi_cell(col_w_value, line_h, " " + safe_str(value) + " ", border=1, ln=1)
            pdf.set_x(pdf.l_margin)
        
        draw_table_row("Tanggal Rapat", safe_str(row.get('tanggal')))
        draw_table_row("Petugas", safe_str(row.get('pegawai')))
        draw_table_row("Link Undangan", safe_str(row.get('link_undangan')))
        draw_table_row("Link Bahan", safe_str(row.get('link_bahan_materi')))
        draw_table_row("Link Dokumentasi", safe_str(row.get('link_dokumentasi')))
        pdf.ln(5)
        
        # ========== RINGKASAN INDIKATOR ==========
        pdf.set_font("Times", 'B', 13)
        pdf.set_text_color(30, 60, 120)
        pdf.cell(0, 8, "RINGKASAN INDIKATOR PERUBAHAN HARGA", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Times", '', 11)
        pdf.multi_cell(0, 6, safe_str(row.get('ringkasan_indikator'), "Data tidak tersedia."))
        pdf.ln(4)
        
        # ========== RESUME ==========
        pdf.set_font("Times", 'B', 13)
        pdf.set_text_color(30, 60, 120)
        pdf.cell(0, 8, "RESUME HASIL RAPAT", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Times", '', 11)
        pdf.multi_cell(0, 6, safe_str(row.get('resume'), "Belum diisi"))
        pdf.ln(4)
        
        # ========== TINDAK LANJUT ==========
        pdf.set_font("Times", 'B', 13)
        pdf.set_text_color(30, 60, 120)
        pdf.cell(0, 8, "TINDAK LANJUT / ACTION ITEMS", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Times", '', 11)
        pdf.multi_cell(0, 6, safe_str(row.get('action_items'), "Belum diisi"))
        pdf.ln(4)
        
        # ========== STATUS ==========
        pdf.set_font("Times", 'B', 13)
        pdf.set_text_color(30, 60, 120)
        pdf.cell(0, 8, "STATUS PENYELESAIAN", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Times", '', 12)
        pdf.cell(0, 6, safe_str(row.get('status'), 'Belum ditentukan'), ln=True)
        pdf.ln(6)
        
        # ========== DOKUMENTASI GAMBAR (GRID 2 KOLOM, KECIL) ==========
        gambar_links = []
        if 'gambar_dokumentasi' in row and pd.notna(row['gambar_dokumentasi']) and str(row['gambar_dokumentasi']).strip():
            gambar_links = [link.strip() for link in str(row['gambar_dokumentasi']).split('\n') if link.strip()]
        
        if gambar_links:
            pdf.set_font("Times", 'B', 13)
            pdf.set_text_color(30, 60, 120)
            pdf.cell(0, 8, "DOKUMENTASI KEGIATAN", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(3)
            
            # Pengaturan grid
            img_w = 80          # lebar gambar kecil
            img_h = 60          # perkiraan tinggi (akan disesuaikan proporsional)
            margin_x = 10       # jarak antar gambar
            margin_y = 5        # jarak vertikal antar baris
            start_x = pdf.l_margin + 5
            start_y = pdf.get_y()
            current_x = start_x
            current_y = start_y
            count_in_row = 0
            
            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0'})
            
            for idx, link in enumerate(gambar_links, start=1):
                try:
                    resp = session.get(link, timeout=15)
                    if resp.status_code == 200 and 'image' in resp.headers.get('Content-Type', ''):
                        img_data = BytesIO(resp.content)
                        # Tempatkan gambar di posisi saat ini
                        pdf.image(img_data, x=current_x, y=current_y, w=img_w)
                        count_in_row += 1
                        # Pindah ke kanan untuk gambar berikutnya
                        current_x += img_w + margin_x
                        # Jika sudah 2 gambar, pindah ke baris baru
                        if count_in_row == 2:
                            current_x = start_x
                            current_y += img_h + margin_y
                            count_in_row = 0
                    else:
                        raise Exception(f"HTTP {resp.status_code} atau bukan gambar")
                except Exception as e:
                    pdf.set_font("Times", 'I', 9)
                    pdf.set_xy(current_x, current_y)
                    pdf.cell(img_w, 6, f"(Gambar {idx} gagal)", ln=True)
                    # Tetap majukan posisi agar tidak bertumpuk
                    current_x += img_w + margin_x
                    if count_in_row == 2:
                        current_x = start_x
                        current_y += 10
                        count_in_row = 0
            
            # Pindahkan kursor ke bawah grid terakhir
            if count_in_row != 0:
                current_y += img_h + margin_y
            pdf.set_y(current_y + 5)
        else:
            pdf.set_font("Times", 'I', 11)
            pdf.cell(0, 8, "Tidak ada gambar dokumentasi.", ln=True)
        
        return bytes(pdf.output())
    
    except Exception as e:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Times", '', 12)
        pdf.multi_cell(0, 10, f"Gagal membuat PDF: {e}")
        return bytes(pdf.output())

# --- SESSION STATE LOGIN (VERSI TERBARU UNTUK MULTISELECT) ---
query_params = st.query_params

if query_params.get("view") == "shared":
    st.session_state.logged_in = True
    st.session_state.user_role = "Publik_Shared"
    st.session_state.username = "Guest"
    
    # 1. Ambil data Tahun IPH dari link
    if "tahun_iph" in query_params:
        try:
            # Mengubah "2023|2024" jadi [2023, 2024]
            th_iph_list = [int(x) for x in query_params["tahun_iph"].split("|")]
            st.session_state["iph_ultra_final"] = th_iph_list
        except:
            pass
            
    # 2. Ambil data Tahun Andil dari link
    if "tahun_andil" in query_params:
        try:
            th_andil_list = [int(x) for x in query_params["tahun_andil"].split("|")]
            st.session_state["andil_year_multiselect"] = th_andil_list
        except:
            pass

elif 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = ""

# ======================= HALAMAN LOGIN =======================
if not st.session_state.logged_in:
    # --- Custom CSS for Login Page (Dark & Orange Theme) ---
    st.markdown("""
        <style>
            /* Latar belakang gelap + gradasi aksen oranye */
            .stApp {
                background: linear-gradient(145deg, #1E1E1E 0%, #2D2D2D 50%, #3E3E3E 100%) !important;
            }
            /* Sembunyikan sidebar */
            [data-testid="stSidebar"] {
                display: none;
            }
            /* Judul & teks */
            h1, h2, h3 {
                color: #F97316 !important;
            }
            p, .stCaption {
                color: #EEEEEE !important;
            }
            /* Kontainer tab */
            .stTabs [data-baseweb="tab-list"] {
                background: transparent;
                gap: 12px;
                justify-content: center;
            }
            /* Tab (non-aktif) */
            .stTabs button[data-baseweb="tab"] {
                background: rgba(255, 255, 255, 0.1) !important;
                color: #FFFFFF !important;
                font-weight: 500;
                padding: 0.5rem 2rem;
                border-radius: 40px;
                border: 1px solid rgba(249, 115, 22, 0.3) !important;
                box-shadow: none !important;
                transition: all 0.3s ease;
            }
            /* Hover tab non-aktif */
            .stTabs button[data-baseweb="tab"]:hover {
                background: rgba(249, 115, 22, 0.25) !important;
                border-color: #F97316 !important;
            }
            /* Tab aktif */
            .stTabs button[data-baseweb="tab"][aria-selected="true"] {
                background: #F97316 !important;
                color: #FFFFFF !important;
                font-weight: 700;
                border: 1px solid #F97316 !important;
                box-shadow: 0 0 15px rgba(249, 115, 22, 0.4);
            }
            /* Label form */
            .stTextInput label, .stSelectbox label {
                color: #EEEEEE !important;
                font-weight: 500;
            }
            /* Input field */
            .stTextInput > div > div > input,
            .stSelectbox > div > div {
                background: rgba(30, 30, 30, 0.8) !important;
                border: 1px solid #F97316 !important;
                color: #FFFFFF !important;
                border-radius: 14px !important;
                padding: 0.6rem 1rem;
            }
            ::placeholder {
                color: #FF9800 !important;
                opacity: 0.7;
            }
            /* >>> TAMBAHKAN DI SINI <<< */
            .stSelectbox [data-baseweb="select"] [aria-selected="true"] {
                color: #FFFFFF !important;
            }
            .stSelectbox [data-baseweb="select"] span {
                color: #FFFFFF !important;
            }
            /* Tombol utama (oranye gradasi) */
            div.stButton > button:first-child {
                background: linear-gradient(90deg, #F97316 0%, #EA580C 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 30px !important;
                font-weight: 600 !important;
                padding: 0.6rem 1.5rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4);
            }
            div.stButton > button:first-child:hover {
                background: linear-gradient(90deg, #EA580C 0%, #C2410C 100%) !important;
                box-shadow: 0 6px 18px rgba(249, 115, 22, 0.6);
                transform: translateY(-2px);
            }
            /* Notifikasi / Alert */
            .stAlert {
                background: rgba(249, 115, 22, 0.15) !important;
                color: #FFFFFF !important;
                border-left: 4px solid #F97316 !important;
                border-radius: 12px;
            }
            /* Label form berwarna oranye terang */
            .stTextInput label, .stSelectbox label {
                color: #FF9800 !important;
                font-weight: 600 !important;
            }
            /* Pastikan teks yang dipilih di dropdown berwarna putih */
            .stSelectbox div[data-baseweb="select"] div {
                color: #FFFFFF !important;
            }
            .stSelectbox [data-baseweb="select"] span {
                color: #FFFFFF !important;
            }
            /* Paksa teks pilihan di dropdown menjadi putih */
            div[data-baseweb="select"] span[class*="singleValue"],
            div[data-baseweb="select"] div[class*="singleValue"],
            div[data-baseweb="select"] div[data-value] {
                color: #FFFFFF !important;
            }
        </style>
    """, unsafe_allow_html=True)


    def get_base64(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except:
            return None

    file_name = "Logo-Badan-Pusat-Statistik-BPS.png"
    bin_str = get_base64(file_name)
    
    if bin_str:
        logo_html = f'<img src="data:image/png;base64,{bin_str}" width="100">'
    else:
        logo_html = "<span>Logo Not Found</span>"

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: -5px;">
                {logo_html}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("""
            <div style="text-align: center;">
                <h1 style='color:#F97316; margin-bottom: 0px; font-size: 34px;'>Dashboard IPH Kota Batu</h1>
                <p style='color:#CCCCCC; margin-top: -10px; font-weight: 500;'>Tim Pengendalian Inflasi Daerah (TPID)</p>
            </div>
            <p style='text-align:center; font-size:12px; color:#BBBBBB; margin-top: -10px;'>
            Sistem monitoring Indeks Perkembangan Harga (IPH) untuk analisis inflasi daerah secara berkala.
            </p>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
       
        tab_login, tab_register = st.tabs(["Login", "Register"])
        with tab_login:
            with st.form("login_form"):
                user_options = ["admin"] + DAFTAR_PEGAWAI
                user_input = st.selectbox("Pilih Username", user_options)
                pass_input = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Masuk", use_container_width=True)
                if submitted:
                    role = check_login(user_input, pass_input)
                    if role:
                        if user_input == "admin" and role != "Admin":
                            st.error("Akun admin tidak valid.")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.user_role = role
                            st.session_state.username = user_input
                            st.rerun()
                    else:
                        st.error("Username atau password salah!")
        with tab_register:
            with st.form("register_form"):
                st.info("Pilih nama Anda dari daftar pegawai. Username akan otomatis sesuai nama.")
                selected_pegawai = st.selectbox("Pilih nama pegawai", DAFTAR_PEGAWAI)
                new_pass = st.text_input("Password", type="password")
                conf_pass = st.text_input("Konfirmasi Password", type="password")
                register_btn = st.form_submit_button("Daftar", use_container_width=True)
                if register_btn:
                    if not selected_pegawai or not new_pass:
                        st.error("Nama dan password tidak boleh kosong.")
                    elif new_pass != conf_pass:
                        st.error("Password tidak cocok.")
                    else:
                        if add_user(selected_pegawai, new_pass):
                            st.success(f"Akun untuk {selected_pegawai} berhasil dibuat! Silakan login dengan nama tersebut.")
                        else:
                            st.error("Username sudah digunakan. Silakan hubungi admin.")
    st.stop()

# ======================= TAMPILAN KHUSUS UNTUK SHARED VIEW =======================
if st.session_state.user_role == "Publik_Shared":
    st.markdown("""
        <style>
            [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
            .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
            * { font-family: 'Lexend', sans-serif; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='main-header'><h1> Laporan IPH Kota Batu</h1></div>", unsafe_allow_html=True)
    
    analisis_file = "iph_analisis.csv"
    
    if not os.path.exists(analisis_file) or os.path.getsize(analisis_file) == 0:
        st.warning("Belum ada data IPH.")
        st.stop()
    
    df = pd.read_csv(analisis_file)
    if df.empty:
        st.warning("Data IPH kosong.")
        st.stop()
    
    bulan_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"}
    df['bulan_nama'] = df['bulan'].apply(lambda x: bulan_map[x])
    
    def format_original(value):
        if isinstance(value, (int, float)):
            s = f"{value:.10f}"
            s = s.rstrip('0').rstrip('.')
            return s
        return value
    
    # Ambil SEMUA tahun yang tersedia, urutkan
    tahun_tersedia = sorted(df['tahun'].unique())
    
    # ------------------------------------------------------------
    # GRAFIK IPH (semua tahun, overlay)
    # ------------------------------------------------------------
    st.subheader("Tren Indikator Perubahan Harga (%)")
    
    # Buat mapping x untuk semua data
    pair_list = df[['bulan', 'minggu_ke']].drop_duplicates().sort_values(['bulan','minggu_ke'])
    x_mapping = {}
    for idx, (b, m) in enumerate(zip(pair_list['bulan'], pair_list['minggu_ke'])):
        x_mapping[(b, m)] = idx
    df['x_pos'] = df.apply(lambda row: x_mapping[(row['bulan'], row['minggu_ke'])], axis=1)
    df = df.sort_values(['tahun','x_pos'])
    
    tickvals, ticktext = [], []
    bulan_sebelumnya = None
    for (b,m), pos in x_mapping.items():
        if b != bulan_sebelumnya:
            tickvals.append(pos)
            ticktext.append(bulan_map[b])
            bulan_sebelumnya = b
    
    fig = go.Figure()
    colors = ['#54A24B', '#D35400', '#F1C40F', '#2980B9', '#8E44AD', '#E67E22', '#9B59B6']
    for i, th in enumerate(tahun_tersedia):
        df_th = df[df['tahun'] == th].sort_values('x_pos')
        if df_th.empty:
            continue
        x_vals = df_th['x_pos'].tolist()
        y_vals = df_th['indikator'].tolist()
        tooltips = df_th.apply(
            lambda r: f"<b>Tahun {r['tahun']}</b><br>Minggu {r['minggu_ke']} {bulan_map[r['bulan']]}<br>IPH: {format_original(r['indikator'])}%",
            axis=1
        ).tolist()
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals,
            mode='lines+markers',
            name=f"<b>{th}</b>",
            line=dict(width=4, color=colors[i % len(colors)], shape='spline', smoothing=1.3),
            marker=dict(size=8, line=dict(width=1.5, color='white')),
            hovertemplate='%{text}<extra></extra>',
            text=tooltips,
            hoverinfo='text'
        ))
    
    fig.update_layout(
        height=500,
        font=dict(family="Lexend, sans-serif"),
        plot_bgcolor='white',
        hovermode='x unified',
        margin=dict(t=80, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Lexend")),
        annotations=[dict(
            text="<b>Indikator Perubahan Harga (%) per Minggu</b>",
            xref="paper", yref="paper", x=0, y=1.12, showarrow=False,
            font=dict(size=16, color="#333333", family="Lexend"), align="left"
        )]
    )
    fig.update_xaxes(tickmode='array', tickvals=tickvals, ticktext=ticktext, tickangle=0,
                     range=[min(tickvals)-0.5, max(tickvals)+0.5] if tickvals else [0,1],
                     showgrid=True, gridcolor='#F0F0F0', tickfont=dict(family="Lexend"))
    fig.update_yaxes(showgrid=True, gridcolor='#F0F0F0', tickfont=dict(family="Lexend"))
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabel detail
    st.write("**Data Detail Mingguan:**")
    try:
        tabel = df.pivot_table(index='tahun', columns=['bulan','minggu_ke'], values='indikator').round(2)
        tabel.columns = [f"{bulan_map.get(b,b)} M{int(m)}" for b,m in tabel.columns]
        st.dataframe(tabel, use_container_width=True)
    except:
        pass
    
    # ------------------------------------------------------------
    # ANDIL KOMODITAS (gabungan semua tahun)
    # ------------------------------------------------------------
    st.subheader("Komoditas Paling Sering Menjadi Andil Perubahan Harga")
    # Frekuensi digabung untuk semua tahun
    freq = {}
    for _, row in df.iterrows():
        for kom in row['komoditas_andil'].split("|"):
            kom = kom.strip()
            freq[kom] = freq.get(kom, 0) + 1
    
    # 5 teratas
    top_kom = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
    if top_kom:
        df_bar = pd.DataFrame(top_kom, columns=['Komoditas', 'Frekuensi'])
        fig_bar = px.bar(df_bar, x='Komoditas', y='Frekuensi',
                         title="5 Besar Komoditas Andil Perubahan Harga (Semua Tahun)",
                         color_discrete_sequence=['#FDCB6E'])
        fig_bar.update_traces(marker=dict(line=dict(width=1, color='white'), cornerradius=10),
                              textposition='outside', textfont_size=12, textfont_family="Lexend")
        fig_bar.update_layout(font_family="Lexend", plot_bgcolor='rgba(0,0,0,0)',
                              xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#E2E8F0'))
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Belum ada data andil.")
    
    st.caption(f"Laporan diakses pada {datetime.now().strftime('%d %B %Y, %H:%M')} WIB")
    st.stop()

def render_sidebar():
    # --- INISIALISASI current_menu (HARUS PALING AWAL) ---
    if 'current_menu' not in st.session_state:
        st.session_state.current_menu = "Beranda"
    
    # Logo BPS
    file_name = "Logo-Badan-Pusat-Statistik-BPS.png"
    bin_str = None
    try:
        with open(file_name, 'rb') as f:
            bin_str = base64.b64encode(f.read()).decode()
    except:
        pass

    st.sidebar.markdown(
        f"""
        <div class="sidebar-logo-area">
            {f'<img src="data:image/png;base64,{bin_str}" width="100">' if bin_str else '<span style="font-size:28px;">📊</span>'}
            <h3 style="color:#F8FAFC; margin:0.5rem 0 0 0;">IPH Kota Batu</h3>
            <p style="color:#94A3B8; font-size:0.8rem; margin:0;">Tim Pengendalian Inflasi Daerah</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Info Pengguna
    inisial = st.session_state.username[0].upper() if st.session_state.username else "?"
    st.sidebar.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:1.5rem; padding:0.5rem; background:#1E3A8A; border-radius:12px;">
            <div class="sidebar-user-avatar">{inisial}</div>
            <div>
                <strong style="color:#F8FAFC;">{st.session_state.username}</strong><br>
                <span style="font-size:0.75rem; color:#94A3B8;">{st.session_state.user_role}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Notifikasi (hanya untuk Pegawai) - DIBUNGKUS TRY-EXCEPT
    if st.session_state.user_role == "Pegawai":
        try:
            notif_df = get_notifikasi(st.session_state.username)
            notif_belum = notif_df[notif_df['dibaca'] == False]
            if len(notif_belum) > 0:
                st.sidebar.markdown(
                    f"""
                    <div style="background:#7F1D1D; padding:8px 12px; border-radius:8px; margin-bottom:0.5rem;">
                        <span style="font-size:1.2rem; margin-right:8px;">🔔</span>
                        <span>Anda memiliki <span class="notif-badge">{len(notif_belum)}</span> tugas baru</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                for i, (_, notif) in enumerate(notif_belum.head(3).iterrows()):
                    col1, col2 = st.sidebar.columns([4, 1])
                    with col1:
                        pesan_singkat = notif['pesan'][:35] + "..." if len(notif['pesan']) > 35 else notif['pesan']
                        st.markdown(f"<small style='color:#CBD5E1;'>{pesan_singkat}</small>", unsafe_allow_html=True)
                    with col2:
                        if st.button("✔️", key=f"baca_{notif['id_rapat']}_{i}", help="Tandai sudah dibaca"):
                            tandai_baca(notif['id_rapat'], st.session_state.username)
                            st.rerun()
        except Exception as e:
            # Jika notifikasi gagal, jangan hentikan sidebar
            pass

    # === FUNGSI TOMBOL MENU ===
    def menu_button(label, key, icon=""):
        current = st.session_state.get("current_menu", "Beranda")
        is_active = (current == label)
        if is_active:
            st.sidebar.markdown(
                f"""
                <div style="background:#F97316; border-left:4px solid #FFE0B2; padding:0.6rem 1rem; border-radius:8px; margin-bottom:2px; color:white !important; font-weight:500;">
                    {icon} {label}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            if st.sidebar.button(f"{icon} {label}", key=key, use_container_width=True):
                st.session_state.current_menu = label
                st.rerun()

    # === MENU UTAMA ===
    st.sidebar.markdown('<div class="sidebar-section-title">MENU UTAMA</div>', unsafe_allow_html=True)
    menu_button("Beranda", "nav_beranda", "")
    
    if st.session_state.user_role == "Admin":
        menu_button("Kelola Rapat", "nav_kelola_rapat", "")
        menu_button("Monitoring Resume", "nav_monitoring", "")
        menu_button("Kelola Pegawai", "nav_kelola_pegawai", "")
        menu_button("Input Rekap IPH", "nav_input_iph", "")
    
    if st.session_state.user_role == "Pegawai":
        menu_button("Isi Resume Rapat", "nav_isi_resume", "")
        menu_button("Input Rekap IPH", "nav_input_iph", "")

    menu_button("Rekapan IPH", "nav_rekapan", "")
    
    # === VISUALISASI & ANALISIS ===
    st.sidebar.markdown('<div class="sidebar-section-title">VISUALISASI & ANALISIS</div>', unsafe_allow_html=True)
    if st.session_state.user_role in ["Admin", "Pegawai"]:
        menu_button("Visualisasi IPH", "nav_visualisasi", "")
        menu_button("Analisis IPH", "nav_analisis", "")

    # === LOGOUT ===
    if st.session_state.user_role != "Publik_Shared":
        if st.sidebar.button("Keluar", use_container_width=True):
            for key in ['logged_in', 'user_role', 'username', 'current_menu']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    st.sidebar.markdown("<hr style='margin:1.5rem 0; border-color:#2D4A6E;'>", unsafe_allow_html=True)

    # Inisialisasi current_menu jika belum ada
    if 'current_menu' not in st.session_state:
        st.session_state.current_menu = "Beranda"

# Panggil fungsi sidebar
render_sidebar()

# Variabel menu diambil dari session state
menu = st.session_state.current_menu

# ======================= BERANDA =======================
if menu == "Beranda":
    st.markdown("<div class='main-header'><h1>Selamat Datang di Dashboard IPH Kota Batu</h1><p>Monitoring inflasi dan rapat TPID</p></div>", unsafe_allow_html=True)
    analisis_file = "iph_analisis.csv"
    indeks_text = "-"
    indeks_caption = "Data IPH belum tersedia"
    if os.path.exists(analisis_file) and os.path.getsize(analisis_file) > 0:
        df_iph = pd.read_csv(analisis_file)
        if not df_iph.empty:
            # Cari periode terbaru: tahun terbesar, lalu bulan terbesar, lalu minggu terbesar
            max_tahun = df_iph['tahun'].max()
            df_tahun = df_iph[df_iph['tahun'] == max_tahun]
            max_bulan = df_tahun['bulan'].max()
            df_bulan = df_tahun[df_tahun['bulan'] == max_bulan]
            max_minggu = df_bulan['minggu_ke'].max()
            data_terbaru = df_bulan[df_bulan['minggu_ke'] == max_minggu]
            if not data_terbaru.empty:
                indikator = data_terbaru.iloc[0]['indikator']   # ambil nilai indikator
                if indikator > 0:
                    status = "Inflasi"
                elif indikator < 0:
                    status = "Deflasi"
                else:
                    status = "Stabil"
                # Format angka sesuai input asli, tidak dibatasi 2 desimal
                def format_original(value):
                    if isinstance(value, (int, float)):
                        s = f"{value:.10f}"
                        s = s.rstrip('0').rstrip('.')
                        return s
                    return value
                indeks_text = f"{format_original(indikator)}%".replace('.', ',')
                bulan_nama = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"][max_bulan-1]
                indeks_caption = f"{status} (Minggu {max_minggu} {bulan_nama} {max_tahun})"
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><h3>Indeks Perkembangan Harga</h3><p style='font-size:2rem;'>{indeks_text}</p><p>{indeks_caption}</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'><h3>Rapat TPID</h3><p style='font-size:2rem;'>"+str(len(pd.read_csv(RAPAT_DB)))+"</p><p>Total rapat</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card'><h3>Pegawai Aktif</h3><p style='font-size:2rem;'>"+str(len(DAFTAR_PEGAWAI))+"</p><p>Anggota tim</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Sekilas tentang Dashboard")
    st.markdown("""
    Dashboard ini digunakan untuk:
    - Memantau Indeks Perkembangan Harga (IPH) Kota Batu
    - Mengelola rapat TPID, undangan, dan dokumentasi
    - Merekam resume rapat dan tindak lanjut
    - Visualisasi data harga komoditas secara interaktif
    """)
    if st.session_state.user_role == "Admin":
        st.info("Sebagai Admin, Anda dapat membuat rapat, memilih petugas, dan memonitor pengisian resume.")
    elif st.session_state.user_role == "Pegawai":
        st.info("Sebagai Pegawai, Anda akan mendapatkan notifikasi jika ditugaskan mengisi resume rapat.")

# ======================= ADMIN: KELOLA RAPAT =======================
if st.session_state.user_role == "Admin" and menu == "Kelola Rapat":
    st.title("Kelola Rapat TPID")
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0
    form_key = f"form_rapat_baru_{st.session_state.form_key}"
    with st.form(form_key):
        tanggal = st.date_input("Tanggal Rapat", datetime.now())
        pegawai_terpilih = st.multiselect("Pilih Pegawai Yang Bertugas Mengisi Resume", DAFTAR_PEGAWAI)
        link_undangan = st.text_input("Link Radiogram/Undangan")
        link_bahan = st.text_input("Link Bahan Materi")
        link_dok = st.text_input("Upload Dokumentasi pada Tautan berikut")
        submitted = st.form_submit_button("Buat Rapat")
        if submitted:
            if not link_undangan.strip() or not link_bahan.strip() or not link_dok.strip():
                st.error("Semua link wajib diisi.")
            elif not pegawai_terpilih:
                st.error("Pilih minimal satu pegawai.")
            else:
                tahun_rapat = tanggal.year
                bulan_rapat = tanggal.month
                minggu_rapat = get_minggu_dari_tanggal(tanggal)
                ringkasan_awal = generate_ringkasan_indikator(tahun_rapat, bulan_rapat, minggu_rapat)
                df = pd.read_csv(RAPAT_DB)
                teks_cols = ['ringkasan_indikator', 'resume', 'action_items', 'gambar_dokumentasi', 'status', 'last_editor', 'created_by', 'link_undangan', 'link_bahan_materi', 'link_dokumentasi', 'pegawai']
                for col in teks_cols:
                    if col in df.columns:
                        df[col] = df[col].fillna('').astype(str)
                new_id = len(df) + 1 if not df.empty else 1
                new_row = pd.DataFrame([{
                    "id": new_id, "tanggal": tanggal, "pegawai": " || ".join(pegawai_terpilih),
                    "link_undangan": link_undangan, "link_bahan_materi": link_bahan, "link_dokumentasi": link_dok,
                    "ringkasan_indikator": ringkasan_awal,
                    "resume": "", "action_items": "", "status": "Belum Diisi",
                    "last_editor": st.session_state.username, "created_by": st.session_state.username,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                pd.concat([df, new_row], ignore_index=True).to_csv(RAPAT_DB, index=False)
                buat_notifikasi(new_id, pegawai_terpilih, tanggal.strftime("%Y-%m-%d"))
                st.success(f"Rapat tanggal {tanggal} berhasil dibuat.")
                st.session_state.form_key += 1
                st.rerun()
    st.subheader("Daftar Rapat")
    df_rapat = pd.read_csv(RAPAT_DB)
    if not df_rapat.empty:
        for idx, row in df_rapat.iterrows():
            with st.expander(f"Rapat ID {row['id']} - {row['tanggal']}"):
                st.markdown(f"**Tanggal:** {row['tanggal']}")
                st.markdown(f"**Pegawai Bertugas:** {row['pegawai']}")
                st.markdown(f"**Link Undangan:** {row['link_undangan']}")
                st.markdown(f"**Link Bahan:** {row['link_bahan_materi']}")
                st.markdown(f"**Link Dokumentasi:** {row['link_dokumentasi']}")
                st.markdown("---")
                st.markdown(f"**Ringkasan Indikator:** {row['ringkasan_indikator']}")
                st.markdown(f"**Resume:** {row['resume']}")
                st.markdown(f"**Action Items:** {row['action_items']}")
                st.markdown(f"**Status:** {row['status']}")
                st.caption(f"Terakhir diedit: {row['last_editor']}")
                with st.form(key=f"edit_slot_{row['id']}_{idx}"):
                    tgl = st.date_input("Tanggal", value=pd.to_datetime(row['tanggal']), key=f"tgl_{row['id']}_{idx}")
                    current_pegawai_raw = row['pegawai'].split(" || ") if pd.notna(row['pegawai']) and row['pegawai'] != "" else []
                    current_pegawai = [p for p in current_pegawai_raw if p in DAFTAR_PEGAWAI]
                    pegawai_edit = st.multiselect("Pegawai Bertugas", DAFTAR_PEGAWAI, default=current_pegawai, key=f"peg_{row['id']}_{idx}")
                    link_und = st.text_input("Link Undangan", value=row['link_undangan'] if pd.notna(row['link_undangan']) else "", key=f"und_{row['id']}_{idx}")
                    link_bahan = st.text_input("Link Bahan Materi", value=row['link_bahan_materi'] if pd.notna(row['link_bahan_materi']) else "", key=f"bahan_{row['id']}_{idx}")
                    link_dok = st.text_input("Link Dokumentasi", value=row['link_dokumentasi'] if pd.notna(row['link_dokumentasi']) else "", key=f"dok_{row['id']}_{idx}")
                    update_slot = st.form_submit_button("Update Rapat")
                    if update_slot:
                        df = pd.read_csv(RAPAT_DB)
                        df.loc[df['id'] == row['id'], ['tanggal', 'pegawai', 'link_undangan', 'link_bahan_materi', 'link_dokumentasi']] = [tgl, " || ".join(pegawai_edit), link_und, link_bahan, link_dok]
                        df.to_csv(RAPAT_DB, index=False)
                        buat_notifikasi(row['id'], pegawai_edit, tgl.strftime("%Y-%m-%d"))
                        st.success("Rapat diupdate!")
                        st.rerun()
                if st.button(f"🗑️ Hapus Rapat", key=f"hapus_{row['id']}_{idx}"):
                    df_temp = pd.read_csv(RAPAT_DB)
                    df_temp = df_temp[df_temp['id'] != row['id']]
                    df_temp = df_temp.reset_index(drop=True)
                    df_temp['id'] = df_temp.index + 1
                    df_temp.to_csv(RAPAT_DB, index=False)
                    df_notif = pd.read_csv(NOTIF_DB)
                    df_notif = df_notif[df_notif['id_rapat'] != row['id']]
                    df_notif.to_csv(NOTIF_DB, index=False)
                    st.success(f"Rapat ID {row['id']} dihapus.")
                    st.rerun()
    else:
        st.info("Belum ada rapat.")

# ======================= ADMIN: MONITORING RESUME =======================
if st.session_state.user_role == "Admin" and menu == "Monitoring Resume":
    st.title("Monitoring Pengisian Resume Rapat")
    df_rapat = pd.read_csv(RAPAT_DB)
    if df_rapat.empty:
        st.info("Belum ada rapat.")
    else:
        st.dataframe(df_rapat[["id", "tanggal", "pegawai", "status", "last_editor"]], use_container_width=True)
        st.subheader("Detail Resume")
        pilih_id = st.selectbox("Pilih ID Rapat", df_rapat['id'].unique())
        row = df_rapat[df_rapat['id'] == pilih_id].iloc[0]
        st.markdown(f"**Tanggal:** {row['tanggal']}")
        st.markdown(f"**Petugas:** {row['pegawai']}")
        st.markdown(f"**Ringkasan Indikator:** {row['ringkasan_indikator']}")
        st.markdown(f"**Resume:** {row['resume']}")
        st.markdown(f"**Action Items:** {row['action_items']}")
        st.markdown(f"**Status:** {row['status']}")
        st.markdown("---")
        if st.button("Export PDF", key=f"pdf_admin_{pilih_id}"):
                pdf_bytes = generate_pdf_resume(row)
                st.download_button(
                    label="📥 Unduh PDF",
                    data=pdf_bytes,
                    file_name=f"resume_rapat_{row['id']}.pdf",
                    mime="application/pdf",
                    key=f"download_admin_{pilih_id}"
                )        

# ======================= ADMIN: KELOLA PEGAWAI =======================
if st.session_state.user_role == "Admin" and menu == "Kelola Pegawai":
    st.title("Kelola Pegawai TPID")
    
    tab1, tab2 = st.tabs(["➕ Tambah Pegawai", "➖ Hapus Pegawai"])
    
    with tab1:
        with st.form("form_tambah_pegawai"):
            nama_baru = st.text_input("Nama Pegawai Baru (tanpa gelar)")
            btn_tambah = st.form_submit_button("Tambah")
            if btn_tambah:
                sukses, pesan = tambah_pegawai(nama_baru)
                if sukses:
                    st.success(pesan)
                    st.rerun()
                else:
                    st.error(pesan)
    
    with tab2:
        pegawai_list = load_pegawai()
        if not pegawai_list:
            st.info("Belum ada pegawai.")
        else:
            with st.form("form_hapus_pegawai"):
                nama_hapus = st.selectbox("Pilih Pegawai yang Akan Dihapus", pegawai_list)
                btn_hapus = st.form_submit_button("Hapus")
                if btn_hapus:
                    sukses, pesan = hapus_pegawai(nama_hapus)
                    if sukses:
                        st.success(pesan)
                        st.rerun()
                    else:
                        st.error(pesan)
    
    st.subheader("Daftar Pegawai Saat Ini")
    st.write(load_pegawai())

# ======================= PEGAWAI: ISI RESUME RAPAT =======================
def form_isi_resume_pegawai(row):
    with st.form(f"form_resume_pegawai_{row['id']}"):
        ringkasan = st.text_area("Ringkasan awal", value=row['ringkasan_indikator'] if pd.notna(row['ringkasan_indikator']) else "", height=100)
        resume = st.text_area("Resume Hasil Rapat", value=row['resume'] if pd.notna(row['resume']) else "", height=150)
        action = st.text_area("Action Items", value=row['action_items'] if pd.notna(row['action_items']) else "", height=100)
        old_val = row['gambar_dokumentasi'] if pd.notna(row.get('gambar_dokumentasi')) else ""
        gambar_dok = st.text_area(
            "Link Gambar Dokumentasi (satu link per baris)",
            value=old_val,
            height=100,
            help="Tempel link Google Drive apa adanya (biasa atau direct). Sistem akan otomatis mengubahnya.",
            placeholder="https://drive.google.com/file/d/...\nhttps://drive.google.com/uc?export=view&id=..."
        )
        status = st.selectbox("Status", ["Belum Diisi", "Proses", "Selesai"], index=["Belum Diisi", "Proses", "Selesai"].index(row['status'] if pd.notna(row['status']) else "Belum Diisi"))
        submitted = st.form_submit_button("Simpan Resume")
        if submitted:
            df = pd.read_csv(RAPAT_DB)
            idx = df[df['id'] == row['id']].index[0]
            df.at[idx, 'ringkasan_indikator'] = ringkasan
            df.at[idx, 'resume'] = resume
            df.at[idx, 'action_items'] = action
            # Konversi semua link ke direct link
            import re
            links = gambar_dok.strip().split('\n')
            direct_links = []
            for link in links:
                link = link.strip()
                if not link:
                    continue
                # Cari pola /file/d/ID/
                match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', link)
                if match:
                    file_id = match.group(1)
                    direct_link = f"https://drive.google.com/uc?export=view&id={file_id}"
                    direct_links.append(direct_link)
                else:
                    # Biarkan jika sudah direct link
                    direct_links.append(link)
            gambar_dok_bersih = "\n".join(direct_links)
            
            df.at[idx, 'gambar_dokumentasi'] = gambar_dok_bersih
            df.at[idx, 'status'] = status
            df.at[idx, 'last_editor'] = st.session_state.username
            df.to_csv(RAPAT_DB, index=False)
            st.success("Resume berhasil disimpan!")
            st.rerun()

if st.session_state.user_role == "Pegawai" and menu == "Isi Resume Rapat":
    st.title("Isi Resume Rapat yang Ditugaskan")
    df_rapat = pd.read_csv(RAPAT_DB)
    tugas = []
    username_clean = st.session_state.username.strip()
    for _, row in df_rapat.iterrows():
        if pd.notna(row['pegawai']) and row['pegawai'] != "":
            daftar_pegawai_raw = row['pegawai'].split(" || ")
            daftar_pegawai = [p.strip() for p in daftar_pegawai_raw]
            if any(username_clean.lower() == p.lower() for p in daftar_pegawai):
                tugas.append(row)
    if not tugas:
        st.info("Anda belum ditugaskan untuk mengisi resume rapat apapun.")
    else:
        for row in tugas:
            with st.expander(f"Rapat {row['tanggal']} - Status: {row['status']}"):
                st.markdown(f"**Link Undangan:** {row['link_undangan']}")
                st.markdown(f"**Link Bahan:** {row['link_bahan_materi']}")
                st.markdown(f"**Upload Dokumentasi di Tautan Berikut:** {row['link_dokumentasi']}")
                st.markdown("---")
                form_isi_resume_pegawai(row)
                st.markdown("---")
            if st.button("📄 Export PDF", key=f"pdf_pegawai_{row['id']}"):
                pdf_bytes = generate_pdf_resume(row)
                st.download_button(
                    label="📥 Unduh PDF",
                    data=pdf_bytes,
                    file_name=f"resume_rapat_{row['id']}.pdf",
                    mime="application/pdf",
                    key=f"download_pegawai_{row['id']}"
                )            

# ======================= REKAPAN IPH (Data Ringkasan) =======================
if menu == "Rekapan IPH":
    st.title("Rekapan Data IPH (Ringkasan per Minggu)")
    
    analisis_file = "iph_analisis.csv"
    if not os.path.exists(analisis_file) or os.path.getsize(analisis_file) == 0:
        st.warning("Belum ada data. Silakan input data melalui menu Input Rekap IPH.")
    else:
        df = pd.read_csv(analisis_file)
        bulan_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"}
        df['bulan_nama'] = df['bulan'].apply(lambda x: bulan_map[x])
        df['periode'] = df.apply(lambda x: f"Minggu {x['minggu_ke']} {x['bulan_nama']} {x['tahun']}", axis=1)
        
        # Filter tahun
        tahun_list = sorted(df['tahun'].unique())
        tahun_pilih = st.selectbox("Filter Tahun", ["Semua"] + tahun_list)
        if tahun_pilih != "Semua":
            df_filter = df[df['tahun'] == tahun_pilih]
        else:
            df_filter = df
        
        st.dataframe(df_filter[['periode','indikator','komoditas_andil','nilai_andil','fluktuasi_komoditas','fluktuasi_nilai','last_updated']], use_container_width=True, hide_index=True)
        
        csv = df_filter.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data (CSV)", data=csv, file_name="rekap_iph_ringkasan.csv", mime="text/csv")
        
        # --- FITUR HAPUS DATA PER PERIODE ---
        st.markdown("---")
        st.subheader("Hapus Data Periode Tertentu")
        col1, col2, col3 = st.columns(3)
        with col1:
            tahun_hapus = st.selectbox("Tahun", tahun_list, key="hapus_tahun")
        with col2:
            bulan_hapus = st.selectbox("Bulan", range(1,13), format_func=lambda x: bulan_map[x], key="hapus_bulan")
        with col3:
            # Ambil minggu yang tersedia untuk kombinasi tahun dan bulan yang dipilih
            if not df.empty:
                minggu_tersedia = sorted(df[(df['tahun']==tahun_hapus) & (df['bulan']==bulan_hapus)]['minggu_ke'].unique())
            else:
                minggu_tersedia = []
            minggu_hapus = st.selectbox("Minggu ke-", minggu_tersedia, key="hapus_minggu")
        
        if st.button("Hapus Data", type="secondary", use_container_width=True):
            if not minggu_tersedia:
                st.error("Tidak ada data untuk periode yang dipilih.")
            else:
                # Baca data asli
                df_original = pd.read_csv(analisis_file)
                # Hapus baris yang sesuai
                df_original = df_original[~((df_original['tahun']==tahun_hapus) & (df_original['bulan']==bulan_hapus) & (df_original['minggu_ke']==minggu_hapus))]
                df_original.to_csv(analisis_file, index=False)
                st.toast(f"Data untuk Minggu {minggu_hapus} {bulan_map[bulan_hapus]} {tahun_hapus} berhasil dihapus.", icon="🗑️")
                st.rerun()
                
# ======================= INPUT REKAP IPH (Ringkasan: Indikator, Andil, Fluktuasi) =======================
if (st.session_state.user_role in ["Admin", "Pegawai"]) and menu == "Input Rekap IPH":
    st.title("Input Rekap IPH Mingguan")
    
    tab1, tab2 = st.tabs(["Input Manual", "Import Excel"])
    
    # ========== TAB 1: INPUT MANUAL (KODE ASLI ANDA) ==========
    with tab1:
        # Inisialisasi key form untuk reset
        if 'form_key' not in st.session_state:
            st.session_state.form_key = 0
        
        # Ambil daftar komoditas master
        komoditas_master = get_komoditas_list()
        if not komoditas_master:
            st.warning("Belum ada komoditas. Silakan tambah komoditas terlebih dahulu.")
            with st.expander("Tambah Komoditas"):
                kom_baru = st.text_input("Nama komoditas baru")
                if st.button("Tambah"):
                    if kom_baru and add_komoditas(kom_baru):
                        st.rerun()
            st.stop()
        
        # Tentukan default komoditas (3 komoditas pertama)
        default_kom1 = komoditas_master[0]
        default_kom2 = komoditas_master[1] if len(komoditas_master) > 1 else komoditas_master[0]
        default_kom3 = komoditas_master[2] if len(komoditas_master) > 2 else komoditas_master[0]
        default_fluk = komoditas_master[0]
        
        # Form dengan key dinamis
        with st.form(key=f"iph_form_{st.session_state.form_key}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                tahun = st.number_input("Tahun", min_value=2020, max_value=2030, value=datetime.now().year)
            with col2:
                bulan = st.selectbox("Bulan", range(1,13), format_func=lambda x: ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'][x-1], index=datetime.now().month-1)
            with col3:
                minggu = st.number_input("Minggu ke-", min_value=1, max_value=5, value=1)
            
            # Indikator: text_input agar bebas desimal
            indikator_str = st.text_input("Indikator Perubahan Harga (%)", value="0", help="Gunakan titik sebagai desimal (contoh: -1.34 atau 2.5678)")
            
            st.markdown("### Tiga Komoditas Andil Perubahan Harga")
            col_kom1, col_kom2, col_kom3 = st.columns(3)
            with col_kom1:
                kom1 = st.selectbox("Komoditas 1", komoditas_master, index=komoditas_master.index(default_kom1))
            with col_kom2:
                kom2 = st.selectbox("Komoditas 2", komoditas_master, index=komoditas_master.index(default_kom2))
            with col_kom3:
                kom3 = st.selectbox("Komoditas 3", komoditas_master, index=komoditas_master.index(default_kom3))
            
            col_nil1, col_nil2, col_nil3 = st.columns(3)
            with col_nil1:
                nilai1_str = st.text_input(f"Nilai {kom1} (%)", value="0", help="Contoh: -0.773 atau 0.333")
            with col_nil2:
                nilai2_str = st.text_input(f"Nilai {kom2} (%)", value="0")
            with col_nil3:
                nilai3_str = st.text_input(f"Nilai {kom3} (%)", value="0")
            
            st.markdown("### Fluktuasi Harga Tertinggi")
            col_fluk1, col_fluk2 = st.columns(2)
            with col_fluk1:
                fluk_kom = st.selectbox("Komoditas", komoditas_master, index=komoditas_master.index(default_fluk))
            with col_fluk2:
                fluk_nilai_str = st.text_input("Nilai Fluktuasi", value="0", help="Contoh: 0.0553 atau 0.0329914")
            
            submitted = st.form_submit_button("Simpan Data", type="primary", use_container_width=True)
            
            if submitted:
                # Konversi string ke float (ganti koma dengan titik)
                try:
                    indikator = float(indikator_str.replace(',', '.'))
                except:
                    indikator = 0.0
                try:
                    nilai1 = float(nilai1_str.replace(',', '.'))
                except:
                    nilai1 = 0.0
                try:
                    nilai2 = float(nilai2_str.replace(',', '.'))
                except:
                    nilai2 = 0.0
                try:
                    nilai3 = float(nilai3_str.replace(',', '.'))
                except:
                    nilai3 = 0.0
                try:
                    fluk_nilai = float(fluk_nilai_str.replace(',', '.'))
                except:
                    fluk_nilai = 0.0
                
                analisis_file = "iph_analisis.csv"
                # Baca existing data
                if os.path.exists(analisis_file) and os.path.getsize(analisis_file) > 0:
                    df_existing = pd.read_csv(analisis_file)
                    # Hapus periode yang sama
                    df_existing = df_existing[~((df_existing['tahun']==tahun) & (df_existing['bulan']==bulan) & (df_existing['minggu_ke']==minggu))]
                else:
                    df_existing = pd.DataFrame()
                
                # Data baru
                new_data = pd.DataFrame([{
                    'tahun': tahun,
                    'bulan': bulan,
                    'minggu_ke': minggu,
                    'indikator': indikator,
                    'komoditas_andil': f"{kom1}|{kom2}|{kom3}",
                    'nilai_andil': f"{nilai1}|{nilai2}|{nilai3}",
                    'fluktuasi_komoditas': fluk_kom,
                    'fluktuasi_nilai': fluk_nilai,
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                df_combined = pd.concat([df_existing, new_data], ignore_index=True)
                df_combined.to_csv(analisis_file, index=False)
                
                # Notifikasi toast (akan muncul dan tidak langsung hilang karena rerun)
                st.toast("✅ Data berhasil disimpan!", icon="✅")
                # Reset form dengan mengubah key
                st.session_state.form_key += 1
                st.rerun()
        
        # Manajemen komoditas (sama seperti sebelumnya)
        with st.expander("Kelola Daftar Komoditas"):
            col_tambah, col_hapus = st.columns(2)
            with col_tambah:
                kom_baru = st.text_input("Nama komoditas baru", key="tambah_kom_iph")
                if st.button("Tambah Komoditas", key="tambah_btn_iph"):
                    if kom_baru and add_komoditas(kom_baru):
                        st.toast(f"Komoditas {kom_baru} ditambahkan!", icon="✅")
                        st.session_state.form_key += 1
                        st.rerun()
                    elif kom_baru:
                        st.warning("Komoditas sudah ada.")
            with col_hapus:
                if komoditas_master:
                    kom_hapus = st.selectbox("Pilih komoditas", komoditas_master, key="hapus_kom_iph")
                    if st.button("Hapus Komoditas", key="hapus_btn_iph"):
                        delete_komoditas(kom_hapus)
                        st.toast(f"Komoditas {kom_hapus} dihapus!", icon="🗑️")
                        st.session_state.form_key += 1
                        st.rerun()
                else:
                    st.info("Tidak ada komoditas.")
    
    # ========== TAB 2: IMPORT EXCEL ==========
    with tab2:
        st.subheader("Import Data IPH dari Excel")
        st.markdown("""
        **Format file Excel yang diterima:**
        File harus memiliki kolom dengan header berikut (huruf besar/kecil bebas):
        - `Tahun` (angka, contoh: 2023)
        - `Bulan` (teks nama bulan, contoh: Januari)
        - `Minggu ke-` (angka 1-5)
        - `Indikator Perubahan Harga (%)` (angka desimal)
        - `Komoditas1`, `Nilai1`, `Komoditas2`, `Nilai2`, `Komoditas3`, `Nilai3`
        - `Komoditas Fluktuasi`, `Nilai Fluktuasi`
        
        **Contoh data:**  
        | Tahun | Bulan   | Minggu ke- | Indikator Perubahan Harga (%) | Komoditas1 | Nilai1 | Komoditas2 | Nilai2 | Komoditas3 | Nilai3 | Komoditas Fluktuasi | Nilai Fluktuasi |
        |-------|---------|------------|-------------------------------|------------|--------|------------|--------|------------|--------|---------------------|-----------------|
        | 2023  | Januari | 1          | -1.34                         | TELUR AYAM RAS | -0.773 | PISANG     | -0.333 | DAGING AYAM RAS | -0.287 | CABAI RAWIT         | 0.0553          |
        """)
        
        # Download template
        template_data = pd.DataFrame({
            'Tahun': [2023],
            'Bulan': ['Januari'],
            'Minggu ke-': [1],
            'Indikator Perubahan Harga (%)': [-1.34],
            'Komoditas1': ['TELUR AYAM RAS'],
            'Nilai1': [-0.773],
            'Komoditas2': ['PISANG'],
            'Nilai2': [-0.333],
            'Komoditas3': ['DAGING AYAM RAS'],
            'Nilai3': [-0.287],
            'Komoditas Fluktuasi': ['CABAI RAWIT'],
            'Nilai Fluktuasi': [0.0553]
        })
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            template_data.to_excel(writer, index=False, sheet_name='Template')
        excel_data = output.getvalue()
        st.download_button(
            label="📥 Download Template Excel",
            data=excel_data,
            file_name="template_iph.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        uploaded_file = st.file_uploader("Upload file Excel (.xlsx)", type=["xlsx"], key="import_excel")
        if uploaded_file:
            try:
                df_input = pd.read_excel(uploaded_file)
                df_input.columns = df_input.columns.str.strip()
                # Mapping kolom yang diharapkan
                kolom_map = {
                    'Tahun': 'tahun',
                    'Bulan': 'bulan_str',
                    'Minggu ke-': 'minggu_ke',
                    'Indikator Perubahan Harga (%)': 'indikator',
                    'Komoditas1': 'kom1',
                    'Nilai1': 'nilai1',
                    'Komoditas2': 'kom2',
                    'Nilai2': 'nilai2',
                    'Komoditas3': 'kom3',
                    'Nilai3': 'nilai3',
                    'Komoditas Fluktuasi': 'fluk_kom',
                    'Nilai Fluktuasi': 'fluk_nilai'
                }
                required_cols = list(kolom_map.keys())
                missing = [c for c in required_cols if c not in df_input.columns]
                if missing:
                    st.error(f"Kolom yang hilang: {missing}. Pastikan file memiliki kolom sesuai template.")
                else:
                    df_input.rename(columns=kolom_map, inplace=True)
                    # Konversi bulan teks ke angka
                    bulan_map_teks = {
                        'januari':1, 'februari':2, 'maret':3, 'april':4, 'mei':5, 'juni':6,
                        'juli':7, 'agustus':8, 'september':9, 'oktober':10, 'november':11, 'desember':12
                    }
                    df_input['bulan_str'] = df_input['bulan_str'].astype(str).str.strip().str.lower()
                    df_input['bulan'] = df_input['bulan_str'].map(bulan_map_teks)
                    if df_input['bulan'].isna().any():
                        invalid = df_input[df_input['bulan'].isna()]['bulan_str'].unique()
                        st.error(f"Bulan tidak valid: {invalid}")
                        st.stop()
                    df_input.drop(columns=['bulan_str'], inplace=True)
                    # Konversi ke numerik
                    numeric_cols = ['tahun','minggu_ke','indikator','nilai1','nilai2','nilai3','fluk_nilai']
                    for col in numeric_cols:
                        df_input[col] = pd.to_numeric(df_input[col], errors='coerce')
                    # Buat kolom komoditas_andil dan nilai_andil
                    df_input['komoditas_andil'] = df_input['kom1'] + "|" + df_input['kom2'] + "|" + df_input['kom3']
                    df_input['nilai_andil'] = df_input['nilai1'].astype(str) + "|" + df_input['nilai2'].astype(str) + "|" + df_input['nilai3'].astype(str)
                    # Pilih kolom final
                    df_output = df_input[['tahun','bulan','minggu_ke','indikator','komoditas_andil','nilai_andil','fluk_kom','fluk_nilai']].copy()
                    df_output.rename(columns={'fluk_kom':'fluktuasi_komoditas', 'fluk_nilai':'fluktuasi_nilai'}, inplace=True)
                    df_output['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # Gabung dengan data existing
                    analisis_file = "iph_analisis.csv"
                    if os.path.exists(analisis_file) and os.path.getsize(analisis_file) > 0:
                        df_existing = pd.read_csv(analisis_file)
                        for _, row in df_output.iterrows():
                            t = row['tahun']
                            b = row['bulan']
                            m = row['minggu_ke']
                            df_existing = df_existing[~((df_existing['tahun']==t) & (df_existing['bulan']==b) & (df_existing['minggu_ke']==m))]
                        df_combined = pd.concat([df_existing, df_output], ignore_index=True)
                    else:
                        df_combined = df_output
                    df_combined.to_csv(analisis_file, index=False)
                    st.success(f"Berhasil mengimpor {len(df_output)} baris数据. Data periode yang sama telah diganti.")
                    st.subheader("Preview data yang diimpor")
                    st.dataframe(df_output, use_container_width=True)
                    if st.button("Refresh halaman", use_container_width=True, key="refresh_import"):
                        st.rerun()
            except Exception as e:
                st.error(f"Error membaca file: {e}")

# ======================= VISUALISASI IPH =======================
if menu == "Visualisasi IPH":
    st.markdown("<h1 style='text-align: center; font-family: Lexend;'>Visualisasi IPH</h1>", unsafe_allow_html=True)
    analisis_file = "iph_analisis.csv"
    if not os.path.exists(analisis_file) or os.path.getsize(analisis_file) == 0:
        st.warning("Belum ada data. Silakan input data melalui menu Input Rekap IPH.")
        st.stop()
    
    df = pd.read_csv(analisis_file)
    bulan_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"}
    df['bulan_nama'] = df['bulan'].apply(lambda x: bulan_map[x])
    
    # Fungsi format angka tanpa batasan desimal
    def format_angka(val):
        if pd.isna(val):
            return "NaN"
        if val == int(val):
            return str(int(val))
        s = f"{val:.10f}".rstrip('0').rstrip('.')
        return s
    
# ------------------------------------------------------------
    # GRAFIK IPH: ULTIMATE AESTHETIC (VERSI BERKELAS)
    # ------------------------------------------------------------
    st.subheader("Tren Indikator Perubahan Harga (%)")
    st.write("Data yang akan diplot:", df_plot[['tahun', 'bulan', 'minggu_ke', 'indikator']].head(10))
    
    tahun_list = sorted(df['tahun'].unique())
    tahun_iph = st.multiselect("Pilih Tahun Analisis", tahun_list, default=tahun_list, key="iph_ultra_final")

    if tahun_iph:
        from plotly.subplots import make_subplots
        import plotly.graph_objects as go

        df_plot = df[df['tahun'].isin(tahun_iph)].copy()
        
# 1. SETUP JUDUL (GANTI: Tambah tag <b> agar Bold)
        judul_dalam = ""
        if not df_plot.empty:
            min_th, max_th = df_plot['tahun'].min(), df_plot['tahun'].max()
            start_bln = bulan_map.get(df_plot[df_plot['tahun'] == min_th]['bulan'].min(), "")
            end_bln = bulan_map.get(df_plot[df_plot['tahun'] == max_th]['bulan'].max(), "")
            # Teks dibungkus <b> agar Bold
            judul_dalam = f"<b>Indikator Perubahan Harga (%) per minggu, {start_bln} {min_th} - {end_bln} {max_th}</b>"

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        colors = ['#54A24B', '#D35400', '#F1C40F', '#2980B9', '#8E44AD']

        for i, th in enumerate(tahun_iph):
            df_th = df_plot[df_plot['tahun'] == th].sort_values(['bulan', 'minggu_ke'])
            if not df_th.empty:
                x_vals = df_th['bulan'] + (df_th['minggu_ke'] - 1) / 4
                is_giant = df_th['indikator'].abs().max() > 100

                fig.add_trace(
                    go.Scatter(
                        x=x_vals,
                        y=df_th['indikator'],
                        mode='lines+markers',
                        name=f"<b>{th}</b>", # GANTI: Nama tahun di legenda jadi Bold
                        line=dict(width=4, color=colors[i % len(colors)], shape='spline', smoothing=1.3),
                        marker=dict(size=8, line=dict(width=1.5, color='white')),
                        connectgaps=True,
                        hovertemplate=f"<b>Tahun {th}</b><br>Minggu %{{x}}<br>IPH: %{{y}}%<extra></extra>"
                    ),
                    secondary_y=is_giant
                )

        # 2. UPDATE LAYOUT (GANTI: Tambah font family Lexend & Bold)
        fig.update_layout(
            height=500,
            # Font Global pakai Lexend
            font=dict(family="Lexend, sans-serif"), 
            margin=dict(t=100, b=50, l=60, r=60),
            plot_bgcolor='white',
            hovermode='x unified',
            legend=dict(
                orientation="h", 
                yanchor="bottom", y=1.02, 
                xanchor="right", x=1,
                font=dict(size=12, family="Lexend") # Font Legenda
            ),
            annotations=[
                dict(
                    text=judul_dalam,
                    xref="paper", yref="paper",
                    x=0, y=1.1, 
                    showarrow=False,
                    # GANTI: Font size sedikit lebih besar & warna lebih gelap (Lexend)
                    font=dict(size=16, color="#333333", family="Lexend"),
                    align="left"
                )
            ]
        )
        
        # Tambahan: Pastikan sumbu X & Y juga pakai Lexend
        fig.update_xaxes(tickfont=dict(family="Lexend"), range=[0.8, 12.8])
        fig.update_yaxes(tickfont=dict(family="Lexend"), secondary_y=False)

        # Sumbu X: Fix Desember agar M-4 tidak kepotong
        fig.update_xaxes(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'],
            range=[0.8, 12.8], # Memberikan ruang napas di ujung Desember
            showgrid=True,
            gridcolor='#F0F0F0',
            zeroline=False
        )

        # Sumbu Y: Skala utama di Kiri
        fig.update_yaxes(
            title_text=None, 
            secondary_y=False, 
            showgrid=True, 
            gridcolor='#F0F0F0',
            tickformat=',.2f' # Format angka dua desimal
        )
        fig.update_yaxes(title_text=None, secondary_y=True, showgrid=False)

        st.plotly_chart(fig, use_container_width=True)

        # Tabel Detail di Bawahnya
        st.write("**Data Detail Mingguan:**")
        try:
            df_table = df_plot.pivot_table(
                index='tahun', columns=['bulan', 'minggu_ke'], values='indikator'
            ).round(2)
            df_table.columns = [f"{bulan_map.get(b, b)} M{int(m)}" for b, m in df_table.columns]
            st.dataframe(df_table, use_container_width=True)
        except:
            pass
    else:
        st.info("Pilih minimal satu tahun.")
    
    # ------------------------------------------------------------
    # GRAFIK ANDIL KOMODITAS
    # ------------------------------------------------------------
    st.subheader("Komoditas Paling Sering Menjadi Andil Perubahan Harga")
    tahun_andil_multi = st.multiselect("Pilih Tahun untuk Andil Komoditas", tahun_list, default=[tahun_list[-1]], key="andil_year_multiselect")
    if not tahun_andil_multi:
        st.info("Pilih minimal satu tahun.")
    else:
        # Kumpulkan frekuensi per tahun
        freq_dict = {}
        for th in tahun_andil_multi:
            df_th = df[df['tahun'] == th]
            freq = {}
            for _, row in df_th.iterrows():
                kom_list = row['komoditas_andil'].split("|")
                for kom in kom_list:
                    kom = kom.strip().upper()
                    freq[kom] = freq.get(kom, 0) + 1
            freq_dict[th] = freq
        
        # Semua komoditas unik
        all_kom = set()
        for f in freq_dict.values():
            all_kom.update(f.keys())
        data = []
        for kom in all_kom:
            row = {'Komoditas': kom}
            for th in tahun_andil_multi:
                row[str(th)] = freq_dict[th].get(kom, 0)
            data.append(row)
        df_plot = pd.DataFrame(data)
        df_plot['Total'] = df_plot[[str(th) for th in tahun_andil_multi]].sum(axis=1)
        df_plot = df_plot.sort_values('Total', ascending=False)
        top5 = df_plot.head(5)['Komoditas'].tolist()
        df_top = df_plot[df_plot['Komoditas'].isin(top5)]
        # Urutkan berdasarkan total agar batang tertinggi di kiri
        df_top = df_top.sort_values('Total', ascending=False)
        df_melt = df_top.melt(id_vars=['Komoditas'], value_vars=[str(th) for th in tahun_andil_multi],
                              var_name='Tahun', value_name='Frekuensi')
        df_melt['Komoditas'] = pd.Categorical(df_melt['Komoditas'], categories=top5, ordered=True)
        df_melt = df_melt.sort_values('Komoditas')
        pastel_colors = ['#FDCB6E', '#6AB0DE', '#8CCB7E', '#F2A77C', '#C5A4D6', '#F4B8B8', '#B8D4E3']
        fig_bar = px.bar(df_melt, x='Komoditas', y='Frekuensi', color='Tahun', barmode='group',
                         title="5 Besar Komoditas Andil Perubahan Harga",
                         labels={'Frekuensi':'Jumlah Kemunculan'},
                         color_discrete_sequence=pastel_colors)
        fig_bar.update_traces(
            textposition='outside',
            marker=dict(line=dict(width=1, color='white'), cornerradius=10),
            opacity=0.9,
            textfont_size=12,
            textfont_family="Lexend"
        )
        fig_bar.update_layout(
            font_family="Lexend",
            xaxis_tickangle=0,
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#E2E8F0')
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # ------------------------------------------------------------
    # LINK SHARE
    # ------------------------------------------------------------
    st.markdown("---")
    with st.expander("🔗 Bagikan Tampilan Ini"):
        base_url = "https://dashboard-iph-kota-batu-cwg5au63betgavnrt2lmpk.streamlit.app"
        import urllib.parse
        
        # Mengubah list tahun [2023, 2024] jadi string "2023|2024"
        th_iph_str = "|".join(map(str, tahun_iph)) if tahun_iph else ""
        th_andil_str = "|".join(map(str, tahun_andil_multi)) if tahun_andil_multi else ""
        
        share_params = {
            "view": "shared"
        }

        query_string = urllib.parse.urlencode(share_params)
        full_link = f"{base_url}/?{query_string}"
        
        st.info("Salin link di bawah untuk membagikan laporan ini.")
        st.code(full_link, language="text")
        
# ======================= ANALISIS IPH OTOMATIS =======================
if menu == "Analisis IPH":
    st.title("Analisis IPH Ringkasan")
    analisis_file = "iph_analisis.csv"
    
    if not os.path.exists(analisis_file) or os.path.getsize(analisis_file) == 0:
        st.warning("Belum ada data ringkasan IPH. Silakan input melalui menu Input Rekap IPH.")
        st.stop()
    
    df = pd.read_csv(analisis_file)
    bulan_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"}
    
    col1, col2, col3 = st.columns(3)
    with col1:
        tahun_list = sorted(df['tahun'].unique())
        tahun_pilih = st.selectbox("Tahun", tahun_list, index=len(tahun_list)-1)
    with col2:
        df_tahun = df[df['tahun'] == tahun_pilih]
        bulan_list = sorted(df_tahun['bulan'].unique())
        bulan_pilih = st.selectbox("Bulan", bulan_list, format_func=lambda x: bulan_map[x])
    with col3:
        df_bulan = df_tahun[df_tahun['bulan'] == bulan_pilih]
        minggu_list = sorted(df_bulan['minggu_ke'].unique())
        minggu_pilih = st.selectbox("Minggu ke-", minggu_list, index=len(minggu_list)-1)
    
    # Panggil fungsi baru (3 parameter)
    teks_ringkasan = generate_ringkasan_indikator(tahun_pilih, bulan_pilih, minggu_pilih)
    
    st.subheader("Ringkasan Indikator")
    st.code(teks_ringkasan, language='text')
    
    # Tombol download untuk memudahkan copy
    st.download_button(
        label="📋 Salin Teks (Download .txt)",
        data=teks_ringkasan,
        file_name=f"ringkasan_iph_{tahun_pilih}_{bulan_map[bulan_pilih]}_minggu{minggu_pilih}.txt",
        mime="text/plain"
    )