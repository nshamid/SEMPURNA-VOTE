import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ================= CONFIG =================
st.set_page_config(
    page_title="E-Voting BPS Kota Palembang",
    layout="wide",
    initial_sidebar_state="expanded"
)

VOTERS_PATH = "data/voters.csv"
VOTES_PATH = "data/votes.csv"

ADMIN_PASSWORD = "adminbps123"      # GANTI
RESULT_PASSWORD = "hasilbps123"     # GANTI

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
    color: white;
}

.sidebar .sidebar-content {
    background-color: #F7941D;
}

.stProgress > div > div {
    background-color: #F15A24;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER (BANNER + LOGO) =================
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

# ================= INIT FILE =================
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(VOTERS_PATH):
    st.error("❌ File data/voters.csv tidak ditemukan!")
    st.stop()

voters_df = pd.read_csv(VOTERS_PATH)

if not os.path.exists(VOTES_PATH):
    pd.DataFrame(columns=["nip", "kandidat"]).to_csv(VOTES_PATH, index=False)

votes_df = pd.read_csv(VOTES_PATH)

# ================= SESSION =================
if "hasil_auth" not in st.session_state:
    st.session_state.hasil_auth = False

if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

# ================= SIDEBAR =================
st.sidebar.title("📌 Menu")
menu = st.sidebar.radio(
    "",
    ["🗳️ Voting", "🏆 Hasil & Ranking", "🔐 Admin"]
)

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
        elif nip_input in votes_df["nip"].astype(str).values:
            st.warning("⚠️ NIP ini sudah melakukan voting.")
        else:
            nama = voters_df[voters_df["nip"].astype(str) == nip_input]["nama"].values[0]
            st.success(f"Selamat datang **{nama}**")

            cols = st.columns(3)
            selected = None

            for i, k in enumerate(kandidat):
                with cols[i % 3]:
                    st.image(k["foto"], use_container_width=True)
                    if st.button(f"Pilih {k['nama']}", use_container_width=True):
                        selected = k["nama"]

            if selected:
                new_vote = pd.DataFrame([[nip_input, selected]], columns=["nip", "kandidat"])
                votes_df = pd.concat([votes_df, new_vote], ignore_index=True)
                votes_df.to_csv(VOTES_PATH, index=False)

                st.success("✅ Voting berhasil disimpan")
                st.balloons()

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

# ================= ADMIN =================
else:
    st.subheader("🔐 Admin Panel")

    pwd = st.text_input("Password Admin", type="password")
    if pwd == ADMIN_PASSWORD:
        if st.button("🗑️ Reset Semua Voting"):
            pd.DataFrame(columns=["nip", "kandidat"]).to_csv(VOTES_PATH, index=False)
            st.success("Data voting berhasil direset")
            st.experimental_rerun()
