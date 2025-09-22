import streamlit as st
import pandas as pd
import gspread
import datetime
from datetime import datetime

# =================================================================================
# KONFIGURASI HALAMAN
# =================================================================================
st.set_page_config(
    page_title="PLN Area Malang - Riwayat Pekerjaan",
    page_icon="E:\MAGANGGG\ADM PLN\DASHBOARD PENGUNJUNG\Dashboard Pengunjung\assets\logo_pln.png",
    layout="wide"
)

@st.cache_resource(ttl=600)
def get_gspread_connection():
    try:
        creds = dict(st.secrets["g_sheets"])
        return gspread.service_account_from_dict(creds)
    except Exception as e:
        st.error(f"Gagal terhubung ke Google Sheets: {e}")
        return None

@st.cache_data(ttl=1)
def get_data_from_sheet(worksheet_name):
    gspread_connection = get_gspread_connection()
    if gspread_connection:
        try:
            spreadsheet_url = st.secrets["g_sheets"]["spreadsheet"]
            spreadsheet = gspread_connection.open_by_url(spreadsheet_url)

            worksheet = spreadsheet.worksheet(worksheet_name)
            df = pd.DataFrame(worksheet.get_all_records())

            # pastikan nama kolom rapi
            df.columns = df.columns.str.strip()
            df = df.dropna(how="all")  # hapus baris kosong
            return df
        except Exception as e:
            st.error(f"Gagal mengambil data dari worksheet '{worksheet_name}': {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# =================================================================================
# TAMPILAN
# =================================================================================
st.title("Riwayat Pekerjaan Gardu")

# 🔑 Ganti ke sheet yang benar
df = get_data_from_sheet("History")

if not df.empty:
    # Filter data yang statusnya 'Selesai'
    df_history = df[(df["STATUS"].str.lower() == "selesai")]

    if not df_history.empty:
        # Mengonversi kolom 'TIMESTAMP' menjadi datetime untuk pengurutan
        df_history["TIMESTAMP"] = pd.to_datetime(df_history["TIMESTAMP"], errors='coerce')

        # Menambahkan filter berdasarkan rentang hari
        days_filter = st.selectbox(
            "Pilih Rentang Hari:",
            ["7 Hari Terakhir", "14 Hari Terakhir", "30 Hari Terakhir"]
        )

        # Mendapatkan tanggal hari ini
        today = datetime.today()

        # Menentukan batas tanggal berdasarkan pilihan pengguna
        if days_filter == "7 Hari Terakhir":
            start_date = today - pd.Timedelta(days=7)
        elif days_filter == "14 Hari Terakhir":
            start_date = today - pd.Timedelta(days=14)
        elif days_filter == "30 Hari Terakhir":
            start_date = today - pd.Timedelta(days=30)

        # Memfilter data berdasarkan rentang waktu yang dipilih
        df_history_filtered = df_history[df_history["TIMESTAMP"] >= start_date]

        if not df_history_filtered.empty:
            # Mengurutkan berdasarkan 'TIMESTAMP' terbaru (descending)
            df_history_filtered = df_history_filtered.sort_values("TIMESTAMP", ascending=False)

            # Menata ulang kolom dengan 'TIMESTAMP' di depan
            cols = ["TIMESTAMP", "PENYULANG", "SECTION", "ID", "PENGAWAS", "PELAKSANA", "STATUS", 
                    "STATUS_GARDU", "JENIS_PEKERJAAN", "WAKTU_MULAI", "WAKTU_SELESAI"]
            df_history_filtered = df_history_filtered[cols]

            # Menambahkan opsi untuk membatasi jumlah baris yang ditampilkan
            rows_to_show = st.slider(
                "Pilih Jumlah Baris yang Ditampilkan:",
                min_value=5,
                max_value=len(df_history_filtered),
                value=10,
                step=5
            )

            # Menampilkan tabel dengan jumlah baris yang sesuai
            st.dataframe(df_history_filtered.head(rows_to_show))

            # Jika lebih banyak data tersedia, beri opsi "Tampilkan Lebih Banyak"
            if rows_to_show < len(df_history_filtered):
                if st.button("Tampilkan Lebih Banyak"):
                    st.dataframe(df_history_filtered)
        else:
            st.info(f"ℹ️ Tidak ada riwayat pekerjaan gardu dalam rentang {days_filter}.")
    else:
        st.info("ℹ️ Belum ada riwayat pekerjaan gardu yang selesai.")
else:
    st.warning("Tidak dapat memuat data dari Google Sheets.")