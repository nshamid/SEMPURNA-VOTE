import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

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

# ================= THEME (BPS ORANGE) =================
st.markdown("""
<style>
.stApp {
    background-color: #FFF4E6;
}
h1, h2, h3, h4 {
    color: #F15A24;
}
div.stButton > button {
    background-color: #F7941D;
    color: white;
    border-radius: 10px;
    font-weight: bold;
}
div.stButton > button:hover {
    background-color: #F15A24;
}
.stProgress > div > div {
    background-color: #F15A24;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.image("images/banner.jpg", use_container_width=True)

col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("images/logo_bps.png", width=90)
with col_title:
    st.markdown("""
    <h2>Badan Pusat Statistik Kota Palembang</h2>
    <p><b>E-Voting SEMPURNA</b></p>
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
    return pd.read_csv(VOTERS_PATH, dtype=str)

def load_votes():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

voters_df = load_voters()
votes_df = load_votes()

# ================= SESSION =================
if "hasil_auth" not in st.session_state:
    st.session_state.hasil_auth = False

# ================= SIDEBAR =================
st.sidebar.title("📌 Menu")
menu = st.sidebar.radio("", ["🗳️ Voting", "🏆 Hasil & Ranking"])

# ================= VOTING PAGE =================
if menu == "🗳️ Voting":
    st.subheader("🗳️ Form Voting")

    st.info(
        "📢 **Ketentuan Voting:**\n\n"
        "- Setiap pegawai **hanya diperbolehkan melakukan voting sebanyak 1 kali**.\n"
        "- Voting menggunakan **NIP terdaftar**.\n"
        "- Setelah vote dikirim, **tidak dapat diubah**.\n"
        "- Pastikan pilihan Anda sudah benar sebelum menekan tombol pilih."
    )

    nip_input = st.text_input("Masukkan NIP Terdaftar")

    if nip_input:
        if nip_input not in voters_df["nip"].astype(str).values:
            st.error("❌ NIP tidak terdaftar.")

        elif not votes_df.empty and nip_input in votes_df["nip"].astype(str).values:
            st.warning("⚠️ NIP ini sudah melakukan voting.")

        else:
            nama = voters_df.loc[
                voters_df["nip"].astype(str) == nip_input, "nama"
            ].values[0]

            st.success(f"Selamat datang **{nama}**")

            cols = st.columns(3)
            selected = None

            for i, k in enumerate(kandidat):
                with cols[i % 3]:
                    st.image(k["foto"], use_container_width=True)
                    if st.button(
                        f"Pilih {k['nama']}",
                        key=f"vote_{k['nama']}",
                        use_container_width=True
                    ):
                        selected = k["nama"]

            if selected:
                sheet.append_row([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    nip_input,
                    selected
                ])

                st.success("✅ Voting berhasil disimpan")
                st.balloons()
                st.experimental_rerun()

# ================= HASIL =================
elif menu == "🏆 Hasil & Ranking":
    st.subheader("🔒 Hasil Voting")

    if not st.session_state.hasil_auth:
        pwd = st.text_input("Password", type="password")
        if pwd == RESULT_PASSWORD:
            st.session_state.hasil_auth = True
            st.experimental_rerun()
        elif pwd:
            st.error("Password salah")
    else:
        if votes_df.empty:
            st.warning("Belum ada suara.")
        else:
            total = len(votes_df)
            hasil = votes_df["kandidat"].value_counts().reset_index()
            hasil.columns = ["Kandidat", "Jumlah"]
            hasil["Persentase (%)"] = round(hasil["Jumlah"] / total * 100, 2)
            hasil = hasil.sort_values("Jumlah", ascending=False).reset_index(drop=True)
            hasil["Ranking"] = hasil.index + 1

            for _, r in hasil.iterrows():
                st.markdown(
                    f"**🏅 {r['Ranking']} – {r['Kandidat']}**  \n"
                    f"{r['Jumlah']} suara ({r['Persentase (%)']}%)"
                )
                st.progress(r["Persentase (%)"] / 100)

            fig = px.bar(
                hasil,
                x="Kandidat",
                y="Jumlah",
                color="Kandidat",
                text="Persentase (%)"
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
