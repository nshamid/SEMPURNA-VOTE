import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ================= CONFIG =================
st.set_page_config(
    page_title="E-Voting BPS Kota Palembang",
    layout="wide"
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
.stApp {
    background-color: #FFE2C6;
}

h1, h2, h3 {
    color: #F15A24;
}

/* BUTTON VOTING */
div.stButton > button {
    background-color: #F7941D;
    color: white;
    width: 100%;
    height: 45px;
    font-weight: bold;
    border-radius: 8px;
    border: none;
}

div.stButton > button:hover {
    background-color: #E67E00;
}

/* RANK 1 BOX */
.rank-box {
    background: linear-gradient(135deg, #F7941D, #F15A24);
    color: white;
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    cursor: pointer;
    box-shadow: 0 10px 25px rgba(0,0,0,0.25);
}

/* RANK LIST */
.rank-item {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    border-left: 6px solid #F7941D;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.image("images/banner.jpg", use_container_width=True)

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

# ================= DATA =================
@st.cache_data
def load_voters():
    return pd.read_csv(VOTERS_PATH, dtype=str)

def load_votes():
    return pd.DataFrame(sheet.get_all_records())

def nip_sudah_vote(nip):
    return nip in sheet.col_values(2)

voters_df = load_voters()

# ================= SESSION =================
st.session_state.setdefault("hasil_auth", False)
st.session_state.setdefault("show_balloons", False)

# ================= SIDEBAR =================
menu = st.sidebar.radio("Menu", ["🗳️ Voting", "🏆 Hasil & Ranking"])

# ================= VOTING =================
if menu == "🗳️ Voting":
    st.subheader("🗳️ Form Voting")

    nip = st.text_input("Masukkan NIP")

    if nip:
        if nip not in voters_df["nip"].values:
            st.error("❌ NIP tidak terdaftar")
        elif nip_sudah_vote(nip):
            st.warning("⚠️ NIP ini sudah melakukan voting")
        else:
            nama = voters_df.loc[voters_df["nip"] == nip, "nama"].values[0]
            st.success(f"Selamat datang {nama}")

            cols = st.columns(3)
            for i, k in enumerate(kandidat):
                with cols[i % 3]:
                    st.image(k["foto"], use_container_width=True)
                    if st.button(f"Pilih {k['nama']}", key=k["nama"]):
                        sheet.append_row([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            nip,
                            k["nama"]
                        ])
                        st.success("✅ Voting berhasil")
                        st.rerun()

# ================= HASIL =================
else:
    st.subheader("🔐 Hasil Voting")

    if not st.session_state.hasil_auth:
        pwd = st.text_input("Password", type="password")
        if pwd == RESULT_PASSWORD:
            st.session_state.hasil_auth = True
            st.rerun()
    else:
        votes = load_votes()
        hasil = votes["kandidat"].value_counts().reset_index()
        hasil.columns = ["Kandidat", "Jumlah"]
        hasil = hasil.sort_values("Jumlah", ascending=False)
        total = hasil["Jumlah"].sum()
        hasil["Persentase"] = round(hasil["Jumlah"] / total * 100, 2)
        hasil["Ranking"] = range(1, len(hasil) + 1)

        juara = hasil.iloc[0]
        foto_juara = next(k["foto"] for k in kandidat if k["nama"] == juara["Kandidat"])

        if st.container():
            if st.button("🏆 PERINGKAT 1", use_container_width=True):
                st.balloons()

            st.markdown(f"""
            <div class="rank-box">
                <h2>{juara['Kandidat']}</h2>
                <p>{juara['Jumlah']} suara ({juara['Persentase']}%)</p>
            </div>
            """, unsafe_allow_html=True)

            st.image(foto_juara, width=250)

        st.markdown("### 📊 Ranking Lainnya")
        for _, r in hasil.iloc[1:].iterrows():
            st.markdown(f"""
            <div class="rank-item">
                <b>🏅 {r['Ranking']} - {r['Kandidat']}</b><br>
                {r['Jumlah']} suara ({r['Persentase']}%)
            </div>
            """, unsafe_allow_html=True)

        fig = px.bar(hasil, x="Kandidat", y="Jumlah", text="Persentase")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
