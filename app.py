import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
import plotly.express as px
import base64
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

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
        * {
            font-family: 'Lexend', sans-serif;
        }
        .stApp {
            background: linear-gradient(135deg, #f0f4f8 0%, #e6edf4 100%);
        }
        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e0e7ed;
        }
        .main-header {
            background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%);
            padding: 1.2rem;
            border-radius: 20px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .main-header h1 {
            color: white;
            margin: 0;
            font-size: 1.8rem;
        }
        .main-header p {
            margin: 0;
            opacity: 0.9;
        }
        .metric-card {
            background: white;
            border-radius: 16px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border-top: 4px solid #10b981;
        }
        .metric-card h3 {
            font-size: 1rem;
            margin-bottom: 0.25rem;
        }
        .metric-card p {
            font-size: 0.8rem;
        }
        .metric-card p:first-of-type {
            font-size: 1.5rem;
            font-weight: 600;
            margin: 0.2rem 0;
        }    
        .stButton > button {
            background: #1e3a8a;
            color: white;
            border-radius: 30px;
            font-weight: 500;
            transition: 0.2s;
        }
        .stButton > button:hover {
            background: #2563eb;
            transform: translateY(-2px);
        }
        h1, h2, h3 {
            color: #1e293b;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            justify-content: center;
        }
        .stTabs [data-baseweb="tab"] {
            font-weight: 600;
            font-size: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- DAFTAR PEGAWAI ---
DAFTAR_PEGAWAI = [
    "Ir. Yuniarni Erry Wahyuti, MM",
    "Adam Mahmud, SE, MM",
    "Gatot Suharmoko, M.Si.",
    "Muhammad Arief Nurohman, S.Si",
    "Sayu Made Widiari, S.ST, M.Si",
    "Eka Cahyani, S.ST",
    "Dwi Esti Kurniasih, S.Si, M.AP, M.P.P.",
    "Arif Nugroho Wicaksono, S.Si",
    "FX Gugus Febri Putranto, SST, M.E.",
    "Sulistyono, SE",
    "Adina Astasia, S.ST, M.Stat",
    "Eko Wibowo, SE",
    "Singgih Wicaksono, SE",
    "Nurlaila Oktarahmayanti, S.ST",
    "Dhika Devara Prihastiono, S.ST",
    "Mulia Estiwilaras, SM",
    "Wahyu Mega Alfazip, A.Md.Kb.N.",
]

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

if not os.path.exists(IPH_DB):
    df_iph = pd.DataFrame(columns=[
        "tahun", "bulan", "minggu_ke", "komoditas", "harga", "persen_change", "last_updated"
    ])
    df_iph.to_csv(IPH_DB, index=False)

if not os.path.exists(NOTIF_DB):
    df_notif = pd.DataFrame(columns=["id_rapat", "pegawai", "pesan", "dibaca", "tanggal"])
    df_notif.to_csv(NOTIF_DB, index=False)

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

def generate_ringkasan_indikator(tahun, bulan, minggu_ke, df_iph):
    data_periode = df_iph[(df_iph['tahun']==tahun) & (df_iph['bulan']==bulan) & (df_iph['minggu_ke']==minggu_ke)]
    if data_periode.empty:
        return "Data tidak tersedia untuk periode ini."
    prev_tahun = tahun
    prev_bulan = bulan
    prev_minggu = minggu_ke - 1
    if prev_minggu < 1:
        if prev_bulan > 1:
            prev_bulan -= 1
            data_prev_bulan = df_iph[(df_iph['tahun']==prev_tahun) & (df_iph['bulan']==prev_bulan)]
            if not data_prev_bulan.empty:
                prev_minggu = data_prev_bulan['minggu_ke'].max()
            else:
                prev_minggu = None
        else:
            prev_tahun -= 1
            prev_bulan = 12
            data_prev_bulan = df_iph[(df_iph['tahun']==prev_tahun) & (df_iph['bulan']==prev_bulan)]
            if not data_prev_bulan.empty:
                prev_minggu = data_prev_bulan['minggu_ke'].max()
            else:
                prev_minggu = None
    if prev_minggu is None:
        return "Data minggu sebelumnya tidak tersedia."
    data_prev = df_iph[(df_iph['tahun']==prev_tahun) & (df_iph['bulan']==prev_bulan) & (df_iph['minggu_ke']==prev_minggu)]
    if data_prev.empty:
        return f"Data minggu sebelumnya (minggu ke-{prev_minggu} {prev_bulan}/{prev_tahun}) tidak tersedia."
    merged = data_periode.merge(data_prev[['komoditas','harga']], on='komoditas', suffixes=('', '_prev'))
    merged['perubahan'] = ((merged['harga'] - merged['harga_prev']) / merged['harga_prev']) * 100
    rata_perubahan = merged['perubahan'].mean()
    if rata_perubahan >= 0:
        jenis = "inflasi"
        top3 = merged.nlargest(3, 'perubahan')[['komoditas', 'perubahan']]
    else:
        jenis = "deflasi"
        top3 = merged.nsmallest(3, 'perubahan')[['komoditas', 'perubahan']]
    def format_angka(x, desimal=4):
        return f"{x:.{desimal}f}".replace('.', ',')
    rata_str = format_angka(rata_perubahan, 2)
    def format_komoditas(kom):
        return kom.title()
    andil_list = []
    for i, (_, row) in enumerate(top3.iterrows(), 1):
        kom = format_komoditas(row['komoditas'])
        perubahan = row['perubahan']
        andil_list.append(f"{i}. {kom} ({format_angka(perubahan, 4)}), ")
    andil_str = "\n".join(andil_list)
    bulan_nama = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"][bulan-1]
    ringkasan = f"Berikut kami sampaikan IPH Kota Batu minggu ke-{minggu_ke} {bulan_nama} {tahun}. Kota Batu mengalami {jenis} sebesar {rata_str}\n\nBerikut adalah komoditi yg menyumbang andil terbesar\n{andil_str}"
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

# --- FUNGSI NOTIFIKASI ---
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

# --- SESSION STATE LOGIN ---
query_params = st.query_params
if query_params.get("view") == "shared":
    st.session_state.logged_in = True
    st.session_state.user_role = "Publik_Shared"
    st.session_state.username = "Guest"
elif 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = ""

# ======================= HALAMAN LOGIN =======================
if not st.session_state.logged_in:
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
                <h1 style='color:#1F3C88; margin-bottom: 0px; font-size: 34px;'>Dashboard IPH Kota Batu</h1>
                <p style='color:#555; margin-top: -10px; font-weight: 500;'>Tim Pengendalian Inflasi Daerah (TPID)</p>
            </div>
            <p style='text-align:center; font-size:12px; color:#666; margin-top: -10px;'>
            Sistem monitoring Indeks Perkembangan Harga (IPH) untuk analisis inflasi daerah secara berkala.
            </p>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])
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
        if st.button("🔍 Lihat Dashboard Publik", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_role = "Publik"
            st.session_state.username = "Guest"
            st.rerun()
        st.caption(f"Update: {datetime.now().strftime('%d %B %Y')}")
    st.stop()

# ======================= TAMPILAN KHUSUS UNTUK SHARED VIEW =======================
if st.session_state.user_role == "Publik_Shared":
    # Sembunyikan sidebar dan kontrol navigasi
    st.markdown("""
        <style>
            [data-testid="stSidebar"], [data-testid="collapsedControl"] {
                display: none;
            }
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='main-header'><h1>📊 Laporan IPH Kota Batu</h1></div>", unsafe_allow_html=True)
    
    params = st.query_params
    
    # Parameter dasar
    try:
        tahun = int(params.get("th", 0))
        bulan = int(params.get("bl", 0))
        minggu = int(params.get("mg", 0))
    except:
        st.error("Parameter tahun/bulan/minggu tidak valid.")
        st.stop()
    
    if not all([tahun, bulan, minggu]):
        st.error("Link tidak lengkap.")
        st.stop()
    
    df_iph = pd.read_csv(IPH_DB)
    if df_iph.empty:
        st.warning("Data IPH belum tersedia.")
        st.stop()
    
    # Tampilkan ringkasan teks (selalu ada)
    data_periode = df_iph[(df_iph['tahun']==tahun) & (df_iph['bulan']==bulan) & (df_iph['minggu_ke']==minggu)]
    if data_periode.empty:
        st.warning(f"Data untuk minggu ke-{minggu} bulan {bulan} {tahun} tidak ditemukan.")
        st.stop()
    
    ringkasan = generate_ringkasan_indikator(tahun, bulan, minggu, df_iph)
    st.markdown("### 📝 Ringkasan Indikator")
    st.code(ringkasan, language='text')
    st.markdown("---")
    
    # Ambil parameter visualisasi
    chart_type = params.get("chart", "")
    
    bulan_map = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"Mei", 6:"Jun", 7:"Jul", 8:"Agu", 9:"Sep", 10:"Okt", 11:"Nov", 12:"Des"}
    
    # --- Render grafik sesuai chart_type ---
    if chart_type == "Tren Harga (Bulanan/Mingguan)":
        mode = params.get("mode", "")
        if mode == "Bulanan (Perbandingan Tahun)":
            kom_param = params.get("kom", "")
            thn_param = params.get("thn", "")
            kom_pilih = kom_param.split("|") if kom_param else []
            th_pilih = [int(x) for x in thn_param.split("|") if x] if thn_param else []
            
            if not kom_pilih or not th_pilih:
                st.warning("Parameter komoditas atau tahun tidak lengkap.")
            else:
                plot_df = df_iph[(df_iph['komoditas'].isin(kom_pilih)) & (df_iph['tahun'].isin(th_pilih))]
                if plot_df.empty:
                    st.warning("Data tidak ditemukan untuk filter yang diberikan.")
                else:
                    plot_df = plot_df.groupby(['tahun', 'bulan', 'komoditas'])['harga'].mean().reset_index()
                    plot_df['legenda'] = plot_df['tahun'].astype(str) + " - " + plot_df['komoditas']
                    tab_pivot = plot_df.pivot_table(index='legenda', columns='bulan', values='harga').reset_index()
                    for b in range(1,13):
                        if b not in tab_pivot.columns:
                            tab_pivot[b] = None
                    tab_pivot = tab_pivot[['legenda'] + list(range(1,13))]
                    
                    def format_ribuan(x):
                        if pd.isna(x): return ""
                        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    
                    header_values = ['<b>Tahun / Komoditas</b>'] + [f"<b>{bulan_map[i]}</b>" for i in range(1,13)]
                    cell_values = [tab_pivot['legenda'].tolist()]
                    for b in range(1,13):
                        cell_values.append([format_ribuan(v) for v in tab_pivot[b]])
                    
                    fig = make_subplots(
                        rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.6, 0.4],
                        specs=[[{"type": "scatter"}], [{"type": "table"}]]
                    )
                    for leg in tab_pivot['legenda']:
                        data_leg = plot_df[plot_df['legenda'] == leg].sort_values('bulan')
                        fig.add_trace(
                            go.Scatter(x=data_leg['bulan'], y=data_leg['harga'],
                                       mode='lines+markers', line=dict(width=3), name=leg),
                            row=1, col=1
                        )
                    fig.add_trace(
                        go.Table(
                            header=dict(values=header_values, fill_color='#1e3a8a',
                                        font=dict(color='white', size=12), align='center'),
                            cells=dict(values=cell_values, fill_color='white',
                                       align=['left'] + ['center']*12, height=25)
                        ),
                        row=2, col=1
                    )
                    fig.update_layout(
                        title="<b>Tren Harga Rata-rata Bulanan</b>",
                        height=750,
                        margin=dict(l=20, r=20, t=60, b=80),
                        plot_bgcolor='white',
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    fig.update_xaxes(tickmode='array', tickvals=list(range(1,13)),
                                     ticktext=list(bulan_map.values()), showgrid=True, gridcolor='lightgray', row=1, col=1)
                    fig.update_yaxes(title="Harga (Rp)", showgrid=True, gridcolor='lightgray', row=1, col=1)
                    st.plotly_chart(fig, use_container_width=True)
        
        else:  # Mingguan
            th_s = int(params.get("th_s", tahun))
            bl_s = int(params.get("bl_s", bulan))
            kom_param = params.get("kom", "")
            mg_param = params.get("mg_pilih", "")
            kom_pilih = kom_param.split("|") if kom_param else []
            mg_pilih = [int(x) for x in mg_param.split("|") if x] if mg_param else []
            
            if not kom_pilih or not mg_pilih:
                st.warning("Parameter tidak lengkap.")
            else:
                plot_df = df_iph[(df_iph['tahun']==th_s) & (df_iph['bulan']==bl_s) &
                                 (df_iph['komoditas'].isin(kom_pilih)) & (df_iph['minggu_ke'].isin(mg_pilih))]
                if plot_df.empty:
                    st.warning("Data tidak ditemukan.")
                else:
                    fig = px.line(plot_df, x='minggu_ke', y='harga', color='komoditas',
                                  markers=True, title=f"Harga Asli Mingguan ({bulan_map[bl_s]} {th_s})")
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Tabel Harga Asli (Rp):**")
                    tab_m = plot_df.pivot_table(index='komoditas', columns='minggu_ke', values='harga', fill_value=0)
                    st.dataframe(tab_m, use_container_width=True)
    
    elif chart_type == "Andil Perubahan Harga (Frekuensi)":
        df_iph['persen_change'] = pd.to_numeric(df_iph['persen_change'], errors='coerce').fillna(0)
        andil_df = df_iph[df_iph['persen_change'] != 0].groupby('komoditas').size().reset_index(name='frekuensi')
        if andil_df.empty:
            st.info("Belum ada data perubahan harga.")
        else:
            andil_df = andil_df.sort_values('frekuensi', ascending=False)
            fig = px.bar(andil_df, x='frekuensi', y='komoditas', orientation='h',
                         title="Frekuensi Perubahan Harga", text='frekuensi')
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(andil_df.set_index('komoditas'), use_container_width=True)
    
    elif chart_type == "Komoditas Paling Fluktuatif":
        fluktuasi = df_iph.groupby('komoditas')['harga'].std().reset_index(name='std_dev')
        fluktuasi = fluktuasi.sort_values('std_dev', ascending=False).head(5)
        fig = px.bar(fluktuasi, x='komoditas', y='std_dev', title="Top 5 Komoditas Paling Fluktuatif", text='std_dev')
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(fluktuasi.set_index('komoditas'), use_container_width=True)
    
    elif chart_type == "Indikator Perubahan Harga (%)":
        th_p = int(params.get("th_p", tahun))
        kom_param = params.get("kom", "")
        kom_pilih = kom_param.split("|") if kom_param else []
        if not kom_pilih:
            st.warning("Pilih komoditas tidak ditemukan.")
        else:
            ind_df = df_iph[(df_iph['tahun']==th_p) & (df_iph['komoditas'].isin(kom_pilih))].sort_values(['bulan', 'minggu_ke'])
            ind_df['periode'] = ind_df.apply(lambda x: f"{bulan_map[x['bulan']]} M{x['minggu_ke']}", axis=1)
            fig = px.line(ind_df, x='periode', y='persen_change', color='komoditas',
                          markers=True, title="Perubahan Harga (%)")
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
            tab_persen = ind_df.pivot_table(index='komoditas', columns='periode', values='persen_change', fill_value=0)
            st.dataframe(tab_persen, use_container_width=True)
    
    else:
        # Fallback: tampilkan bar chart mingguan sederhana
        st.markdown("### 📈 Harga Komoditas Minggu Ini")
        plot_df = data_periode.sort_values('harga', ascending=False)
        fig = px.bar(plot_df, x='komoditas', y='harga', text='harga', color='harga',
                     color_continuous_scale='Blues',
                     title=f"Minggu ke-{minggu} {bulan_map[bulan]} {tahun}")
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📋 Tabel Harga Lengkap")
        tabel = data_periode[['komoditas', 'harga', 'persen_change']].copy()
        tabel['harga'] = tabel['harga'].apply(lambda x: f"{x:,.2f}")
        tabel['persen_change'] = tabel['persen_change'].apply(lambda x: f"{x:+.2f}%")
        st.dataframe(tabel.rename(columns={'komoditas':'Komoditas','harga':'Harga (Rp)','persen_change':'Perubahan (%)'}),
                     use_container_width=True, hide_index=True)
    
    st.caption(f"Laporan diakses pada {datetime.now().strftime('%d %B %Y, %H:%M')} WIB")
    st.stop()

# ======================= SIDEBAR =======================
def get_base64_sidebar(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

file_name = "Logo-Badan-Pusat-Statistik-BPS.png"
bin_str = get_base64_sidebar(file_name)
if bin_str:
    logo_html_sidebar = f'<div style="display: flex; justify-content: center; margin-bottom: 20px; margin-top: 10px;"><img src="data:image/png;base64,{bin_str}" width="120"></div>'
else:
    logo_html_sidebar = '<div style="text-align: center; margin-bottom: 20px;">Logo BPS tidak tersedia</div>'

st.sidebar.markdown(logo_html_sidebar, unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='text-align:center;'><strong>{st.session_state.username}</strong><br><span style='background:#e2e8f0; padding:2px 8px; border-radius:20px;'>{st.session_state.user_role}</span></div>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Notifikasi untuk pegawai
if st.session_state.user_role == "Pegawai":
    notif_df = get_notifikasi(st.session_state.username)
    notif_belum = notif_df[notif_df['dibaca'] == False]
    if len(notif_belum) > 0:
        st.sidebar.markdown(f"<div style='background:#fee2e2; padding:10px; border-radius:12px;'><span>🔔 Notifikasi <span style='background:#ef4444; color:white; border-radius:50px; padding:0 6px;'>{len(notif_belum)}</span></span></div>", unsafe_allow_html=True)
        for _, notif in notif_belum.iterrows():
            st.sidebar.markdown(f"- {notif['pesan']} <br><small>{notif['tanggal']}</small>", unsafe_allow_html=True)
            if st.sidebar.button(f"Tandai baca", key=f"baca_{notif['id_rapat']}"):
                tandai_baca(notif['id_rapat'], st.session_state.username)
                st.rerun()
    else:
        st.sidebar.markdown("Tidak ada notifikasi baru")
    st.sidebar.markdown("---")

# Menu berdasarkan role
if st.session_state.user_role == "Admin":
    menu = st.sidebar.radio("Navigasi", ["Beranda", "Kelola Rapat", "Input Rekap IPH", "Rekapan IPH", "Visualisasi IPH", "Analisis IPH", "Monitoring Resume"])
elif st.session_state.user_role == "Pegawai":
    menu = st.sidebar.radio("Navigasi", ["Beranda", "Isi Resume Rapat", "Input Rekap IPH", "Rekapan IPH", "Visualisasi IPH", "Analisis IPH"])
elif st.session_state.user_role == "Publik_Shared":
    # Tidak akan pernah tercapai karena sudah di-stop di atas
    menu = None
else:
    menu = st.sidebar.radio("Navigasi", ["Beranda", "Visualisasi IPH", "Lihat Rapat"])

if st.session_state.user_role != "Publik_Shared":
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.query_params.clear()
        st.rerun()

# --- FUNGSI FORM ISI RESUME (untuk admin, tidak dipakai pegawai) ---
def form_isi_resume(rapat_row, is_admin=False):
    if not is_admin:
        daftar_pegawai = [p.strip() for p in rapat_row['pegawai'].split(" || ")] if pd.notna(rapat_row['pegawai']) else []
        if st.session_state.username not in daftar_pegawai:
            st.warning("Anda tidak ditugaskan untuk mengisi resume rapat ini.")
            return
    with st.form(f"form_resume_{rapat_row['id']}"):
        ringkasan = st.text_area("Ringkasan awal dari tabel indikator", value=rapat_row['ringkasan_indikator'] if pd.notna(rapat_row['ringkasan_indikator']) else "", height=100)
        resume = st.text_area("Resume Hasil Rapat", value=rapat_row['resume'] if pd.notna(rapat_row['resume']) else "", height=150)
        action = st.text_area("Action Items (Tindak Lanjut)", value=rapat_row['action_items'] if pd.notna(rapat_row['action_items']) else "", height=100)
        status = st.selectbox("Status", ["Belum Diisi", "Proses", "Selesai"], index=["Belum Diisi", "Proses", "Selesai"].index(rapat_row['status'] if pd.notna(rapat_row['status']) else "Belum Diisi"))
        submitted = st.form_submit_button("Simpan Resume")
        if submitted:
            df = pd.read_csv(RAPAT_DB)
            idx = df[df['id'] == rapat_row['id']].index[0]
            df.at[idx, 'ringkasan_indikator'] = ringkasan
            df.at[idx, 'resume'] = resume
            df.at[idx, 'action_items'] = action
            df.at[idx, 'status'] = status
            df.at[idx, 'last_editor'] = st.session_state.username
            df.to_csv(RAPAT_DB, index=False)
            st.success("Resume berhasil disimpan!")
            st.rerun()

# ======================= BERANDA =======================
if menu == "Beranda":
    st.markdown("<div class='main-header'><h1>Selamat Datang di Dashboard IPH Kota Batu</h1><p>Monitoring inflasi dan rapat TPID</p></div>", unsafe_allow_html=True)
    df_iph = pd.read_csv(IPH_DB)
    indeks_text = "-"
    indeks_caption = "Data IPH belum tersedia"
    if not df_iph.empty:
        max_tahun = df_iph['tahun'].max()
        df_tahun = df_iph[df_iph['tahun'] == max_tahun]
        max_bulan = df_tahun['bulan'].max()
        df_bulan = df_tahun[df_tahun['bulan'] == max_bulan]
        max_minggu = df_bulan['minggu_ke'].max()
        data_terbaru = df_bulan[df_bulan['minggu_ke'] == max_minggu]
        if not data_terbaru.empty:
            rata_persen = data_terbaru['persen_change'].mean()
            if rata_persen > 0:
                status = "Inflasi"
            elif rata_persen < 0:
                status = "Deflasi"
            else:
                status = "Stabil"
            indeks_text = f"{rata_persen:+.2f}%".replace('.', ',')
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
    else:
        st.info("Anda mengakses sebagai publik. Data rapat dan grafik IPH dapat dilihat.")

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
        link_dok = st.text_input("Link Folder Dokumentasi")
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
                df_iph_rapat = pd.read_csv(IPH_DB)
                ringkasan_awal = generate_ringkasan_indikator(tahun_rapat, bulan_rapat, minggu_rapat, df_iph_rapat)
                df = pd.read_csv(RAPAT_DB)
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

# ======================= PEGAWAI: ISI RESUME RAPAT =======================
def form_isi_resume_pegawai(row):
    with st.form(f"form_resume_pegawai_{row['id']}"):
        ringkasan = st.text_area("Ringkasan awal", value=row['ringkasan_indikator'] if pd.notna(row['ringkasan_indikator']) else "", height=100)
        resume = st.text_area("Resume Hasil Rapat", value=row['resume'] if pd.notna(row['resume']) else "", height=150)
        action = st.text_area("Action Items", value=row['action_items'] if pd.notna(row['action_items']) else "", height=100)
        status = st.selectbox("Status", ["Belum Diisi", "Proses", "Selesai"], index=["Belum Diisi", "Proses", "Selesai"].index(row['status'] if pd.notna(row['status']) else "Belum Diisi"))
        submitted = st.form_submit_button("Simpan Resume")
        if submitted:
            df = pd.read_csv(RAPAT_DB)
            idx = df[df['id'] == row['id']].index[0]
            df.at[idx, 'ringkasan_indikator'] = ringkasan
            df.at[idx, 'resume'] = resume
            df.at[idx, 'action_items'] = action
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
                st.markdown(f"**Link Dokumentasi:** {row['link_dokumentasi']}")
                st.markdown("---")
                form_isi_resume_pegawai(row)

# ======================= REKAPAN DATA IPH =======================
if menu == "Rekapan IPH":
    st.title("📋 Rekapan Data IPH - Per Komoditas per Minggu")
    df_iph = pd.read_csv(IPH_DB)
    if df_iph.empty:
        st.warning("Belum ada data IPH.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            tahun_list = sorted(df_iph['tahun'].unique())
            tahun_pilih = st.multiselect("Pilih Tahun", tahun_list, default=tahun_list)
        with col2:
            bulan_list = sorted(df_iph['bulan'].unique())
            bulan_pilih = st.multiselect("Pilih Bulan", bulan_list, default=bulan_list, format_func=lambda x: ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"][x-1])
        komoditas_all = get_komoditas_list()
        pilih_semua_kom = st.checkbox("Pilih Semua Komoditas", value=True)
        if pilih_semua_kom:
            komoditas_pilih = komoditas_all
        else:
            komoditas_pilih = st.multiselect("Pilih Komoditas", komoditas_all, default=komoditas_all[:5])
        if not tahun_pilih or not bulan_pilih or not komoditas_pilih:
            st.info("Pilih minimal satu tahun, satu bulan, dan satu komoditas.")
        else:
            filtered = df_iph[(df_iph['tahun'].isin(tahun_pilih)) & (df_iph['bulan'].isin(bulan_pilih)) & (df_iph['komoditas'].isin(komoditas_pilih))]
            if filtered.empty:
                st.warning("Tidak ada data untuk filter ini.")
            else:
                pivot_df = filtered.pivot_table(index='komoditas', columns=['tahun', 'bulan', 'minggu_ke'], values='harga', aggfunc='first').fillna(0)
                pivot_df = pivot_df.sort_index(axis=1)
                bulan_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"}
                new_cols = []
                for t, b, m in pivot_df.columns:
                    new_cols.append(f"{bulan_map[b]} {t} - M{m}")
                pivot_df.columns = new_cols
                pivot_df['Rata-rata'] = pivot_df.mean(axis=1).round(3)
                st.subheader("Tabel Harga per Komoditas (Rp)")
                st.dataframe(pivot_df, use_container_width=True)
                csv = pivot_df.reset_index().to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Tabel (CSV)", data=csv, file_name=f"rekap_iph_pivot_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
                with st.expander("Lihat Data Mentah"):
                    st.dataframe(filtered.sort_values(['tahun','bulan','minggu_ke','komoditas']), use_container_width=True)

# ======================= INPUT REKAP IPH =======================
if (st.session_state.user_role in ["Admin", "Pegawai"]) and menu == "Input Rekap IPH":
    st.title("📊 Input Rekap IPH")
    col1, col2, col3 = st.columns(3)
    with col1:
        tahun = st.number_input("Tahun", min_value=2020, max_value=2030, value=datetime.now().year, key="tahun_input")
    with col2:
        bulan = st.selectbox("Bulan", range(1,13), index=datetime.now().month-1, format_func=lambda x: ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"][x-1], key="bulan_input")
    with col3:
        minggu = st.number_input("Minggu ke-", min_value=1, max_value=5, value=1, key="minggu_input")
    komoditas_list = get_komoditas_list()
    if not komoditas_list:
        st.warning("Belum ada komoditas.")
        with st.expander("➕ Tambah Komoditas"):
            kom_baru = st.text_input("Nama komoditas baru")
            if st.button("Tambah") and kom_baru:
                add_komoditas(kom_baru)
                st.rerun()
        st.stop()
    df_iph = pd.read_csv(IPH_DB)
    existing = df_iph[(df_iph['tahun']==tahun) & (df_iph['bulan']==bulan) & (df_iph['minggu_ke']==minggu)]
    edit_df = pd.DataFrame({"Komoditas": komoditas_list})
    edit_df["Harga"] = "0"
    for _, row in existing.iterrows():
        idx = edit_df[edit_df["Komoditas"] == row['komoditas']].index
        if not idx.empty:
            val = row['harga']
            if isinstance(val, float) and val.is_integer():
                edit_df.at[idx[0], "Harga"] = str(int(val))
            else:
                s = f"{val:.10f}".rstrip('0').rstrip('.')
                edit_df.at[idx[0], "Harga"] = s
    if 'reset_counter' not in st.session_state:
        st.session_state.reset_counter = 0
    st.markdown("### ✏️ Edit Harga per Komoditas")
    edited_df = st.data_editor(edit_df, column_config={"Komoditas": st.column_config.TextColumn(disabled=True), "Harga": st.column_config.TextColumn()}, use_container_width=True, hide_index=True, key=f"iph_editor_{st.session_state.reset_counter}")
    def parse_harga(s):
        if s is None or s == "": return 0.0
        s = str(s).strip().replace(',', '.')
        try: return float(s)
        except: return 0.0
    col_save, col_reset = st.columns(2)
    with col_save:
        if st.button("💾 Simpan Data", use_container_width=True, type="primary"):
            harga_list = [parse_harga(row["Harga"]) for _, row in edited_df.iterrows()]
            save_iph_data(tahun, bulan, minggu, komoditas_list, harga_list)
            st.success(f"Data periode {tahun}-{bulan}-{minggu} berhasil disimpan!")
            st.session_state.reset_counter += 1
            st.rerun()
    with col_reset:
        if st.button("🔄 Reset (kosongkan semua)", use_container_width=True):
            df_ip_reset = pd.read_csv(IPH_DB)
            df_ip_reset = df_ip_reset[~((df_ip_reset['tahun']==tahun) & (df_ip_reset['bulan']==bulan) & (df_ip_reset['minggu_ke']==minggu))]
            df_ip_reset.to_csv(IPH_DB, index=False)
            st.session_state.reset_counter += 1
            st.rerun()
    with st.expander("✏️ Kelola Daftar Komoditas"):
        col_tambah, col_hapus = st.columns(2)
        with col_tambah:
            kom_baru = st.text_input("Nama komoditas baru", key="tambah_kom")
            if st.button("Tambah Komoditas"):
                if kom_baru and add_komoditas(kom_baru):
                    st.session_state.reset_counter += 1
                    st.rerun()
        with col_hapus:
            if komoditas_list:
                kom_hapus = st.selectbox("Pilih komoditas", komoditas_list, key="hapus_kom")
                if st.button("Hapus Komoditas"):
                    df_kom = pd.read_csv(KOMODITAS_DB)
                    df_kom = df_kom[df_kom['komoditas'] != kom_hapus]
                    df_kom.to_csv(KOMODITAS_DB, index=False)
                    df_ip = pd.read_csv(IPH_DB)
                    df_ip = df_ip[df_ip['komoditas'] != kom_hapus]
                    df_ip.to_csv(IPH_DB, index=False)
                    st.session_state.reset_counter += 1
                    st.rerun()

# ======================= VISUALISASI IPH =======================
if menu == "Visualisasi IPH":
    st.markdown("<h1 style='text-align: center;'>📊 Visualisasi Data IPH</h1>", unsafe_allow_html=True)
    df_iph = pd.read_csv(IPH_DB)
    if df_iph.empty:
        st.warning("Belum ada data.")
    else:
        bulan_map = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"Mei", 6:"Jun", 7:"Jul", 8:"Agu", 9:"Sep", 10:"Okt", 11:"Nov", 12:"Des"}
        
        # --- Bagian Share Link (membangun URL dengan state) ---
        st.markdown("### 🔗 Bagikan Laporan Periode Tertentu")
        col_share1, col_share2, col_share3 = st.columns(3)
        with col_share1:
            tahun_share = st.selectbox("Tahun", sorted(df_iph['tahun'].unique(), reverse=True), key="share_tahun_vis")
        with col_share2:
            bulan_share = st.selectbox("Bulan", sorted(df_iph[df_iph['tahun']==tahun_share]['bulan'].unique()), format_func=lambda x: bulan_map[x], key="share_bulan_vis")
        with col_share3:
            minggu_share = st.selectbox("Minggu ke-", sorted(df_iph[(df_iph['tahun']==tahun_share) & (df_iph['bulan']==bulan_share)]['minggu_ke'].unique()), key="share_minggu_vis")
        
        # Pilihan visualisasi utama (state akan di-capture)
        jenis_grafik = st.selectbox("Pilih Jenis Analisis Grafik:", [
            "Tren Harga (Bulanan/Mingguan)",
            "Andil Perubahan Harga (Frekuensi)",
            "Komoditas Paling Fluktuatif",
            "Indikator Perubahan Harga (%)"
        ])
        
        # Inisialisasi share_params
        share_params = {
            "view": "shared",
            "th": tahun_share,
            "bl": bulan_share,
            "mg": minggu_share,
            "chart": jenis_grafik
        }
        
        # Variabel untuk menampung pilihan user (digunakan baik untuk plotting maupun share link)
        mode = None
        kom_pilih = []
        th_pilih = []
        
        if jenis_grafik == "Tren Harga (Bulanan/Mingguan)":
            mode = st.radio("Pilih Level Tampilan:", ["Bulanan (Perbandingan Tahun)", "Mingguan (Detail Harga Asli)"], horizontal=True)
            share_params["mode"] = mode
            if mode == "Bulanan (Perbandingan Tahun)":
                col1, col2 = st.columns(2)
                with col1:
                    kom_all = sorted(df_iph['komoditas'].unique())
                    kom_pilih = st.multiselect("Pilih Komoditas", kom_all, default=kom_all[:1] if kom_all else [])
                with col2:
                    th_all = sorted(df_iph['tahun'].unique(), reverse=True)
                    th_pilih = st.multiselect("Pilih Tahun", th_all, default=th_all[:3] if len(th_all) >= 3 else th_all)
                share_params["kom"] = "|".join(kom_pilih)
                share_params["thn"] = "|".join(map(str, th_pilih))
                if kom_pilih and th_pilih:
                    plot_df = df_iph[(df_iph['komoditas'].isin(kom_pilih)) & (df_iph['tahun'].isin(th_pilih))]
                    if not plot_df.empty:
                        plot_df = plot_df.groupby(['tahun', 'bulan', 'komoditas'])['harga'].mean().reset_index()
                        plot_df['legenda'] = plot_df['tahun'].astype(str) + " - " + plot_df['komoditas']
                        tab_pivot = plot_df.pivot_table(index='legenda', columns='bulan', values='harga').reset_index()
                        for b in range(1,13):
                            if b not in tab_pivot.columns:
                                tab_pivot[b] = None
                        tab_pivot = tab_pivot[['legenda'] + list(range(1,13))]
                        def format_ribuan(x):
                            if pd.isna(x): return ""
                            return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        header_values = ['<b>Tahun / Komoditas</b>'] + [f"<b>{bulan_map[i]}</b>" for i in range(1,13)]
                        cell_values = [tab_pivot['legenda'].tolist()]
                        for b in range(1,13):
                            cell_values.append([format_ribuan(v) for v in tab_pivot[b]])
                        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                                            row_heights=[0.6, 0.4], specs=[[{"type": "scatter"}], [{"type": "table"}]])
                        for leg in tab_pivot['legenda']:
                            data_leg = plot_df[plot_df['legenda'] == leg].sort_values('bulan')
                            fig.add_trace(go.Scatter(x=data_leg['bulan'], y=data_leg['harga'],
                                                     mode='lines+markers', line=dict(width=3), name=leg), row=1, col=1)
                        fig.add_trace(go.Table(header=dict(values=header_values, fill_color='#1e3a8a',
                                                           font=dict(color='white', size=12), align='center'),
                                               cells=dict(values=cell_values, fill_color='white',
                                                          align=['left'] + ['center']*12, height=25)), row=2, col=1)
                        fig.update_layout(title="<b>Tren Harga Rata-rata Bulanan</b>", height=750,
                                          margin=dict(l=20, r=20, t=60, b=80), plot_bgcolor='white',
                                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                        fig.update_xaxes(tickmode='array', tickvals=list(range(1,13)), ticktext=list(bulan_map.values()),
                                         showgrid=True, gridcolor='lightgray', row=1, col=1)
                        fig.update_yaxes(title="Harga (Rp)", showgrid=True, gridcolor='lightgray', row=1, col=1)
                        st.plotly_chart(fig, use_container_width=True)
            else:  # Mingguan
                col1, col2, col3 = st.columns(3)
                with col1:
                    th_s = st.selectbox("Tahun", sorted(df_iph['tahun'].unique(), reverse=True), key="th_s_minggu")
                with col2:
                    bl_s = st.selectbox("Bulan", sorted(df_iph[df_iph['tahun']==th_s]['bulan'].unique()), format_func=lambda x: bulan_map[x], key="bl_s_minggu")
                with col3:
                    k_all = sorted(df_iph['komoditas'].unique())
                    k_m = st.multiselect("Komoditas", k_all, default=k_all[:3] if k_all else [], key="k_m_minggu")
                minggu_tersedia = sorted(df_iph[(df_iph['tahun']==th_s) & (df_iph['bulan']==bl_s)]['minggu_ke'].unique())
                minggu_pilih = st.multiselect("Pilih Minggu ke-", minggu_tersedia, default=minggu_tersedia, key="minggu_pilih")
                share_params["th_s"] = th_s
                share_params["bl_s"] = bl_s
                share_params["kom"] = "|".join(k_m)
                share_params["mg_pilih"] = "|".join(map(str, minggu_pilih))
                if k_m and minggu_pilih:
                    plot_df = df_iph[(df_iph['tahun']==th_s) & (df_iph['bulan']==bl_s) & (df_iph['komoditas'].isin(k_m)) & (df_iph['minggu_ke'].isin(minggu_pilih))]
                    if not plot_df.empty:
                        fig = px.line(plot_df, x='minggu_ke', y='harga', color='komoditas', markers=True,
                                      title=f"Harga Asli Mingguan ({bulan_map[bl_s]} {th_s})")
                        st.plotly_chart(fig, use_container_width=True)
                        st.write("**Tabel Harga Asli (Rp):**")
                        tab_m = plot_df.pivot_table(index='komoditas', columns='minggu_ke', values='harga', fill_value=0)
                        st.dataframe(tab_m, use_container_width=True)
        
        elif jenis_grafik == "Andil Perubahan Harga (Frekuensi)":
            df_iph['persen_change'] = pd.to_numeric(df_iph['persen_change'], errors='coerce').fillna(0)
            andil_df = df_iph[df_iph['persen_change'] != 0].groupby('komoditas').size().reset_index(name='frekuensi')
            if not andil_df.empty:
                andil_df = andil_df.sort_values('frekuensi', ascending=False)
                fig = px.bar(andil_df, x='frekuensi', y='komoditas', orientation='h', title="Frekuensi Perubahan Harga", text='frekuensi')
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(andil_df.set_index('komoditas'), use_container_width=True)
            else:
                st.info("Belum ada data perubahan harga.")
        
        elif jenis_grafik == "Komoditas Paling Fluktuatif":
            fluktuasi = df_iph.groupby('komoditas')['harga'].std().reset_index(name='std_dev')
            fluktuasi = fluktuasi.sort_values('std_dev', ascending=False).head(5)
            fig = px.bar(fluktuasi, x='komoditas', y='std_dev', title="Top 5 Komoditas Paling Fluktuatif", text='std_dev')
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(fluktuasi.set_index('komoditas'), use_container_width=True)
        
        elif jenis_grafik == "Indikator Perubahan Harga (%)":
            th_p = st.selectbox("Tahun", sorted(df_iph['tahun'].unique(), reverse=True), key="th_p_ind")
            k_p = st.multiselect("Pilih Komoditas", sorted(df_iph['komoditas'].unique()), default=sorted(df_iph['komoditas'].unique())[:2], key="k_p_ind")
            share_params["th_p"] = th_p
            share_params["kom"] = "|".join(k_p)
            if k_p:
                ind_df = df_iph[(df_iph['tahun']==th_p) & (df_iph['komoditas'].isin(k_p))].sort_values(['bulan', 'minggu_ke'])
                ind_df['periode'] = ind_df.apply(lambda x: f"{bulan_map[x['bulan']]} M{x['minggu_ke']}", axis=1)
                fig = px.line(ind_df, x='periode', y='persen_change', color='komoditas', markers=True, title="Perubahan Harga (%)")
                fig.add_hline(y=0, line_dash="dash", line_color="red")
                st.plotly_chart(fig, use_container_width=True)
                tab_persen = ind_df.pivot_table(index='komoditas', columns='periode', values='persen_change', fill_value=0)
                st.dataframe(tab_persen, use_container_width=True)
        
        # --- Tampilkan link share ---
        base_url = "https://dashboard-iph-kota-batu-cwg5au63betgavnrt2lmpk.streamlit.app"
        # Gunakan urllib.parse.urlencode dengan aman
        import urllib.parse
        query_string = urllib.parse.urlencode(share_params, doseq=True)
        share_link = f"{base_url}/?{query_string}"
        st.info("Salin link di bawah ini untuk dibagikan. Penerima akan melihat laporan yang sama tanpa login.")
        st.code(share_link, language="text")
        st.markdown("---")

# ======================= ANALISIS IPH OTOMATIS =======================
if menu == "Analisis IPH":
    st.title("📊 Analisis IPH Otomatis")
    df_iph = pd.read_csv(IPH_DB)
    if df_iph.empty:
        st.warning("Belum ada data IPH.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            tahun_list = sorted(df_iph['tahun'].unique())
            tahun_pilih = st.selectbox("Tahun", tahun_list, index=len(tahun_list)-1 if tahun_list else 0)
        with col2:
            bulan_list = sorted(df_iph[df_iph['tahun']==tahun_pilih]['bulan'].unique())
            bulan_pilih = st.selectbox("Bulan", bulan_list, format_func=lambda x: ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"][x-1]) if bulan_list else None
        with col3:
            if bulan_pilih:
                minggu_list = sorted(df_iph[(df_iph['tahun']==tahun_pilih) & (df_iph['bulan']==bulan_pilih)]['minggu_ke'].unique())
                minggu_pilih = st.selectbox("Minggu ke-", minggu_list, index=len(minggu_list)-1 if minggu_list else 0)
            else:
                minggu_pilih = None
        if bulan_pilih and minggu_pilih:
            ringkasan = generate_ringkasan_indikator(tahun_pilih, bulan_pilih, minggu_pilih, df_iph)
            st.subheader("📝 Ringkasan Indikator")
            st.code(ringkasan, language='text')
            st.markdown("---")
            st.subheader("📈 Indikator Ringkasan")
            data_periode = df_iph[(df_iph['tahun']==tahun_pilih) & (df_iph['bulan']==bulan_pilih) & (df_iph['minggu_ke']==minggu_pilih)]
            max_harga = data_periode['harga'].max()
            min_harga = data_periode['harga'].min()
            komoditas_max = data_periode[data_periode['harga']==max_harga]['komoditas'].iloc[0]
            komoditas_min = data_periode[data_periode['harga']==min_harga]['komoditas'].iloc[0]
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Harga Tertinggi", f"Rp {max_harga:,.2f}", delta=f"{komoditas_max}")
                st.metric("Harga Terendah", f"Rp {min_harga:,.2f}", delta=f"{komoditas_min}")
            with col_b:
                st.metric("Rata-rata Harga", f"Rp {data_periode['harga'].mean():,.2f}")
                st.metric("Disparitas Harga", f"Rp {max_harga - min_harga:,.2f}")

# ======================= PUBLIK: LIHAT RAPAT =======================
if st.session_state.user_role == "Publik" and menu == "Lihat Rapat":
    st.title("Daftar Rapat TPID")
    df_rapat = pd.read_csv(RAPAT_DB)
    if df_rapat.empty:
        st.info("Belum ada rapat.")
    else:
        for _, row in df_rapat.iterrows():
            with st.expander(f"Rapat {row['tanggal']}"):
                st.markdown(f"**Pegawai:** {row['pegawai']}")
                st.markdown(f"**Undangan:** [Link]({row['link_undangan']})" if row['link_undangan'] else "")
                st.markdown(f"**Bahan:** [Link]({row['link_bahan_materi']})" if row['link_bahan_materi'] else "")
                st.markdown(f"**Dokumentasi:** [Link]({row['link_dokumentasi']})" if row['link_dokumentasi'] else "")
                st.markdown(f"**Ringkasan:** {row['ringkasan_indikator']}")
                st.markdown(f"**Resume:** {row['resume']}")
                st.markdown(f"**Action Items:** {row['action_items']}")