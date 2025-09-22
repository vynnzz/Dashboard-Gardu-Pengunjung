import streamlit as st
import pandas as pd
import gspread

# =================================================================================
# KONFIGURASI APLIKASI
# =================================================================================
st.set_page_config(
    page_title="PLN Area Malang - Dashboard Pengunjung",
    page_icon="assets/logo_pln.png",
    layout="wide"
)

# =================================================================================
# FUNGSI KONEKSI & DATA
# =================================================================================
@st.cache_resource(ttl=600)
def get_gspread_connection():
    try:
        creds = dict(st.secrets["g_sheets"])  # ambil dari secrets.toml
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
            df = df.dropna(how="all")  # buang baris kosong
            return df
        except Exception as e:
            st.error(f"Gagal mengambil data dari worksheet '{worksheet_name}': {e}")
            return pd.DataFrame()
    return pd.DataFrame()


# =================================================================================
# SIDEBAR
# =================================================================================
with st.sidebar:
    st.image("assets/logo_pln.png", width=100)
    st.markdown("## PLN AREA MALANG")
    st.markdown("### Dashboard Pengunjung")
    st.info("Developed by Brawijaya University")

# =================================================================================
# HALAMAN UTAMA
# =================================================================================
st.title(" Informasi Pekerjaan Gardu - Sedang Proses")

df = get_data_from_sheet("History")

if not df.empty:
    # Filter data yang statusnya 'Proses'
    df_proses = df[df["STATUS"].str.lower() == "proses"]

    if not df_proses.empty:
        # Mengonversi kolom 'TIMESTAMP' menjadi datetime untuk pengurutan
        df_proses["TIMESTAMP"] = pd.to_datetime(df_proses["TIMESTAMP"], errors='coerce')

        # Mengurutkan berdasarkan 'TIMESTAMP' terbaru (descending)
        df_proses = df_proses.sort_values("TIMESTAMP", ascending=False)

        for _, row in df_proses.iterrows():
            with st.container():
                st.markdown("---")

                # Menampilkan data dalam satu kotak
                st.subheader(f"🔌 **Penyulang**: {row.get('PENYULANG', '-')} | **Section**: {row.get('SECTION', '-')}")

                # Membuat kolom untuk menampilkan informasi terkait
                with st.expander(f"Detail Pekerjaan Gardu - {row.get('PENYULANG', '-')}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("**ID Gardu**:")
                        st.write(f"```{row.get('ID', 'undefined')}```")

                        st.markdown("**Pengawas**:")
                        st.write(f"```{row.get('PENGAWAS', 'undefined')}```")

                        st.markdown("**Pelaksana**:")
                        st.write(f"```{row.get('PELAKSANA', 'undefined')}```")

                    with col2:
                        st.markdown("**Status**:")
                        st.markdown(f"#### {row.get('STATUS', 'undefined')}")  # Status dengan penekanan

                        st.markdown("**Status Gardu**:")
                        st.write(f"```{row.get('STATUS_GARDU', 'undefined')}```")

                        st.markdown("**Jenis Pekerjaan**:")
                        st.write(f"```{row.get('JENIS_PEKERJAAN', 'undefined')}```")

                    with col3:
                        st.markdown("**Waktu Mulai**:")
                        st.write(f"```{row.get('WAKTU_MULAI', 'undefined')}```")

                        st.markdown("**Waktu Selesai**:")
                        st.write(f"```{row.get('WAKTU_SELESAI', 'undefined')}```")

                        st.markdown("**Timestamp Input**:")
                        st.write(f"```{row.get('TIMESTAMP', 'undefined')}```")

    else:
        st.info("✅ Tidak ada pekerjaan gardu yang sedang diproses.")
else:
    st.warning("Tidak dapat memuat data dari Google Sheets.")