import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import os

# ================= CONFIG =================
st.set_page_config(
    page_title="E-Voting",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_PATH = "data/votes.csv"

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

# ================= INIT DATA =================
if not os.path.exists("data"):
    os.makedirs("data")

try:
    df = pd.read_csv(DATA_PATH)
except:
    df = pd.DataFrame(columns=["voter_id", "kandidat"])
    df.to_csv(DATA_PATH, index=False)

if "voter_id" not in df.columns or "kandidat" not in df.columns:
    df = pd.DataFrame(columns=["voter_id", "kandidat"])
    df.to_csv(DATA_PATH, index=False)

# ================= FUNCTION =================
def hash_identity(text):
    return hashlib.sha256(text.encode()).hexdigest()

# ================= SESSION STATE =================
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

# ================== VOTING PAGE ==================
if menu == "🗳️ Voting":
    st.title("🗳️ E-Voting SEMPURNA")

    st.info("Setiap orang hanya diperbolehkan **1 kali voting**")

    identity = st.text_input(
        "Masukkan NIP",
        placeholder="contoh: 1981082420xxxxxxxx"
    )

    if identity:
        voter_id = hash_identity(identity)

        if voter_id in df["voter_id"].values:
            st.error("❌ Anda sudah melakukan voting.")
        else:
            st.subheader("Pilih Kandidat")

            cols = st.columns(3)
            selected = None

            for i, k in enumerate(kandidat):
                with cols[i % 3]:
                    st.image(k["foto"], use_column_width=True)
                    if st.button(f"Vote {k['nama']}", use_container_width=True):
                        selected = k["nama"]

            if selected:
                new_vote = pd.DataFrame(
                    [[voter_id, selected]],
                    columns=["voter_id", "kandidat"]
                )
                df = pd.concat([df, new_vote], ignore_index=True)
                df.to_csv(DATA_PATH, index=False)

                st.success(f"✅ Voting berhasil untuk **{selected}**")
                st.balloons()

# ================== HASIL & RANKING (PASSWORD) ==================
elif menu == "🏆 Hasil & Ranking":
    st.title("🔒 Halaman Hasil Voting")

    if not st.session_state.hasil_auth:
        password = st.text_input(
            "Masukkan Password untuk Melihat Hasil",
            type="password"
        )

        if password:
            if password == RESULT_PASSWORD:
                st.session_state.hasil_auth = True
                st.success("Akses diberikan")
                st.experimental_rerun()
            else:
                st.error("Password salah")
    else:
        st.subheader("🏆 Hasil Voting & Ranking")

        if df.empty:
            st.warning("Belum ada suara masuk.")
        else:
            total_votes = len(df)

            hasil = df["kandidat"].value_counts().reset_index()
            hasil.columns = ["Kandidat", "Jumlah"]

            hasil["Persentase (%)"] = round(
                hasil["Jumlah"] / total_votes * 100, 2
            )

            hasil = hasil.sort_values("Jumlah", ascending=False).reset_index(drop=True)
            hasil["Ranking"] = hasil.index + 1

            for _, row in hasil.iterrows():
                medal = (
                    "🥇" if row["Ranking"] == 1 else
                    "🥈" if row["Ranking"] == 2 else
                    "🥉" if row["Ranking"] == 3 else
                    "🎯"
                )

                st.markdown(
                    f"**{medal} Peringkat {row['Ranking']} – {row['Kandidat']}**  \n"
                    f"{row['Jumlah']} suara ({row['Persentase (%)']}%)"
                )
                st.progress(row["Persentase (%)"] / 100)

            fig = px.bar(
                hasil,
                x="Kandidat",
                y="Jumlah",
                color="Kandidat",
                text="Persentase (%)",
                title="Distribusi Suara Kandidat"
            )

            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                hasil[["Ranking", "Kandidat", "Jumlah", "Persentase (%)"]],
                use_container_width=True
            )

# ================== ADMIN PAGE ==================
elif menu == "🔐 Admin":
    st.title("🔐 Admin Panel")

    if not st.session_state.admin_auth:
        password = st.text_input(
            "Masukkan Password Admin",
            type="password"
        )

        if password:
            if password == ADMIN_PASSWORD:
                st.session_state.admin_auth = True
                st.success("Login admin berhasil")
                st.experimental_rerun()
            else:
                st.error("Password salah")
    else:
        st.warning("⚠️ Aksi di bawah ini akan menghapus SELURUH data voting")

        if st.button("🗑️ Reset Semua Data Voting", use_container_width=True):
            df = pd.DataFrame(columns=["voter_id", "kandidat"])
            df.to_csv(DATA_PATH, index=False)

            st.success("✅ Data voting berhasil dibersihkan")
            st.experimental_rerun()
