import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import time

# ================= CONFIG =================
st.set_page_config(
    page_title="E-Voting BPS Kota Palembang",
    layout="wide",
    initial_sidebar_state="expanded"
)

VOTERS_PATH = "data/voters.csv"

kandidat = [
    {"nama": "Syifa", "foto": "images/Kandidat1.jpg"},
    {"nama": "Yuwa", "foto": "images/Kandidat2.jpg"},
    {"nama": "IST (Y'Era)", "foto": "images/Kandidat3.jpg"},
    {"nama": "Fivi", "foto": "images/Kandidat4.jpg"},
    {"nama": "Atika", "foto": "images/Kandidat5.jpg"},
    {"nama": "Abe", "foto": "images/Kandidat6.jpg"},
    {"nama": "Yogi", "foto": "images/Kandidat7.jpg"},
]

# ================= THEME =================
st.markdown("""
<style>
/* Mengatur background utama */
.stApp { 
    background-color: #FFEADE; 
}

/* Memaksa semua teks heading dan paragraf menjadi hitam */
h1, h2, h3, h4, p, span, label {
    color: #000000 !important;
}

/* Khusus untuk label input (Masukkan Tanggal Lahir Terdaftar) */
.stWidgetLabel p {
    color: #000000 !important;
    font-weight: bold;
}

/* Tombol tetap dengan warna branding Anda */
div.stButton > button { 
    background-color: #F7941D; 
    color: white !important; /* Teks di dalam tombol tetap putih */
    border-radius: 10px; 
    font-weight: bold; 
} 

div.stButton > button:hover { 
    background-color: #F15A24; 
    color: white !important;
}

/* Box Juara 1 (Teks di dalam sini tetap putih agar kontras dengan orange) */
.rank-box h1, .rank-box h3, .rank-box p {
    color: white !important;
}

.rank-box {
    background-color: #F7941D;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 6px 15px rgba(0,0,0,0.2);
}

/* Item Ranking (Teks hitam) */
.rank-item {
    background-color: white;
    color: #000000 !important;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    border-left: 6px solid #F7941D;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.image("images/banner.jpg", use_container_width=True)

col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("images/logo_bps.png", width=90)
with col_title:
    # Menambahkan style color: black secara inline
    st.markdown("""
    <h2 style="color: black; margin-bottom: 0;">Badan Pusat Statistik Kota Palembang</h2>
    <p style="color: black;"><b>E-Voting SEMPURNA</b></p>
    """, unsafe_allow_html=True)

st.divider()

# ================= GOOGLE SHEETS =================
SHEET_ID = st.secrets["app_config"]["SHEET_ID"]
RESULT_PASSWORD = st.secrets["app_config"]["RESULT_PASSWORD"]

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# ================= LOAD DATA =================
@st.cache_data
def load_voters():
    # Gunakan utf-8-sig untuk menghindari masalah BOM
    df = pd.read_csv(VOTERS_PATH, dtype=str, encoding='utf-8-sig')
    
    # Pembersihan total nama kolom
    df.columns = df.columns.str.strip()
    
    # Tambahan: hapus spasi di dalam data tanggal_lahir jika ada
    if 'tanggal_lahir' in df.columns:
        df['tanggal_lahir'] = df['tanggal_lahir'].str.strip()
        
    return df

def tgl_sudah_vote(tanggal_lahir):
    try:
        return tanggal_lahir in sheet.col_values(2)
    except:
        return False

voters_df = load_voters()

# ================= SESSION =================
if "hasil_auth" not in st.session_state:
    st.session_state.hasil_auth = False

if "sudah_vote" not in st.session_state:
    st.session_state.sudah_vote = False

# ================= SIDEBAR =================
st.sidebar.title("📌 Menu")
menu = st.sidebar.radio("", ["🗳️ Voting", "🏆 Hasil & Ranking"])

# ================= VOTING =================
if menu == "🗳️ Voting":
    st.subheader("🗳️ Form Voting")

    st.info(
        "📢 **Ketentuan Voting:**\n\n"
        "- Setiap pegawai **hanya diperbolehkan melakukan voting sebanyak 1 kali**.\n"
        "- Voting menggunakan **Tanggal Lahir (Format: DD-MM-YYYY)**.\n"
        "- Setelah vote dikirim, **tidak dapat diubah**."
    )

    tgl_input = st.text_input("Masukkan Tanggal Lahir (Contoh: 01-01-2001)")

    if tgl_input:
        if tgl_input not in voters_df["tanggal_lahir"].astype(str).values:
            st.error("❌ Tanggal Lahir yang dimasukkan salah/tidak terdaftar.")
        elif tgl_sudah_vote(tgl_input):
            st.warning("⚠️ Pegawai dengan Tanggal Lahir ini sudah melakukan voting.")
        else:
            nama = voters_df.loc[voters_df["tanggal_lahir"] == tgl_input, "nama"].values[0]
            st.success(f"Selamat datang **{nama}**")

            cols = st.columns(3)
            selected = None

            for i, k in enumerate(kandidat):
                with cols[i % 3]:
                    st.image(k["foto"], use_container_width=True)
                    if st.button(
                        f"Vote {k['nama']}",
                        key=f"Vote_{k['nama']}", 
                        use_container_width=True 
                    ): 
                        selected = k["nama"]

            if selected:
                sheet.append_row([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    tgl_input,
                    selected
                ])
                st.success("✅ Voting berhasil disimpan")
                st.balloons()
                time.sleep(2)
                st.rerun()

# ================= HASIL & RANKING =================
elif menu == "🏆 Hasil & Ranking":
    st.subheader("🔒 Hasil Voting")

    if not st.session_state.hasil_auth:
        pwd = st.text_input("Masukkan Password", type="password")
        if pwd:
            if pwd == RESULT_PASSWORD:
                st.session_state.hasil_auth = True
                st.rerun()
            else:
                st.error("Password salah")
    else:
        votes_df = load_votes()

        if votes_df.empty:
            st.warning("Belum ada suara.")
        else:
            total = len(votes_df)

            hasil = votes_df["kandidat"].value_counts().reset_index()
            hasil.columns = ["Kandidat", "Jumlah"]
            hasil["Persentase"] = round(hasil["Jumlah"] / total * 100, 2)
            hasil = hasil.sort_values("Jumlah", ascending=False).reset_index(drop=True)
            hasil["Ranking"] = hasil.index + 1

            # ================= RANK 1 BOX =================
            juara = hasil.iloc[0]
            st.markdown(f"""
            <div class="rank-box">
                <h3>🏆 JUARA</h3>
                <h1>{juara['Kandidat']}</h1>
                <p>{juara['Jumlah']} suara ({juara['Persentase']}%)</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 📊 Ranking Lengkap")

            for _, r in hasil.iloc[1:].iterrows():
                st.markdown(f"""
                <div class="rank-item">
                    <b>🏅 {r['Ranking']} – {r['Kandidat']}</b><br>
                    {r['Jumlah']} suara ({r['Persentase']}%)
                </div>
                """, unsafe_allow_html=True)

            # ================= SINGLE BAR CHART =================
            fig = px.bar(
                hasil,
                x="Kandidat",
                y="Jumlah",
                color="Kandidat",
                text="Persentase",
                title="📊 Distribusi Suara Seluruh Kandidat"
            )
            fig.update_layout(
                showlegend=False,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
