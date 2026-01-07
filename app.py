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

kandidat = [
    {"nama": "Syifa", "foto": "images/kandidat1.jpeg"},
    {"nama": "Yuwa", "foto": "images/kandidat2.jpeg"},
    {"nama": "IST (Y'Era)", "foto": "images/kandidat3.jpg"},
    {"nama": "Evi", "foto": "images/kandidat4.jpg"},
    {"nama": "Fivi", "foto": "images/kandidat5.jpg"},
    {"nama": "Atika", "foto": "images/kandidat6.jpg"},
    {"nama": "Abe", "foto": "images/kandidat7.jpg"},
    {"nama": "Yogi", "foto": "images/kandidat8.jpg"},
]

# ================= INIT DATA =================
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["voter_id", "kandidat"]).to_csv(DATA_PATH, index=False)

df = pd.read_csv(DATA_PATH)

# ================= FUNCTION =================
def hash_identity(text):
    return hashlib.sha256(text.encode()).hexdigest()

# ================= SIDEBAR =================
st.sidebar.title("📌 Navigasi")
menu = st.sidebar.radio(
    "",
    ["🗳️ Voting", "🏆 Hasil & Ranking"]
)

# ================== HALAMAN VOTING ==================
if menu == "🗳️ Voting":
    st.title("🗳️ E-Voting Online")

    st.markdown("""
    <div style="background-color:#1f2937;padding:15px;border-radius:10px">
    <h4 style="color:white">📢 Ketentuan Voting</h4>
    <ul style="color:#d1d5db">
        <li>Setiap orang hanya boleh voting <b>1 kali</b></li>
        <li>Identitas disimpan secara aman (hash)</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

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

# ================== HALAMAN HASIL & RANKING ==================
else:
    st.title("🏆 Hasil Voting & Ranking")

    if df.empty:
        st.warning("Belum ada suara masuk.")
    else:
        total_votes = len(df)

        hasil = (
            df["kandidat"]
            .value_counts()
            .reset_index()
        )
        hasil.columns = ["Kandidat", "Jumlah"]

        hasil["Persentase (%)"] = round(
            (hasil["Jumlah"] / total_votes) * 100, 2
        )

        hasil = hasil.sort_values(
            by="Jumlah",
            ascending=False
        ).reset_index(drop=True)

        hasil["Ranking"] = hasil.index + 1

        # ================== RANKING CARD ==================
        st.subheader("🏅 Ranking Kandidat")

        for _, row in hasil.iterrows():
            medal = "🥇" if row["Ranking"] == 1 else "🥈" if row["Ranking"] == 2 else "🥉" if row["Ranking"] == 3 else "🎯"

            st.markdown(
                f"""
                **{medal} Peringkat {row['Ranking']} – {row['Kandidat']}**  
                {row['Jumlah']} suara ({row['Persentase (%)']}%)
                """
            )
            st.progress(row["Persentase (%)"] / 100)

        st.divider()

        # ================== BAR CHART ==================
        fig = px.bar(
            hasil,
            x="Kandidat",
            y="Jumlah",
            color="Kandidat",
            text="Persentase (%)",
            title="Distribusi Suara Kandidat",
        )

        fig.update_layout(
            template="plotly_dark",
            xaxis_title="Kandidat",
            yaxis_title="Jumlah Suara"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # ================== TABLE ==================
        st.subheader("📋 Tabel Rekapitulasi")

        st.dataframe(
            hasil[["Ranking", "Kandidat", "Jumlah", "Persentase (%)"]],
            use_container_width=True
        )
