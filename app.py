import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from zoneinfo import ZoneInfo

# Mengatur zona waktu khusus ke Waktu Indonesia Barat (WIB / Jakarta)
waktu_wib = datetime.now(ZoneInfo("Asia/Jakarta"))
current_time_str = waktu_wib.strftime("%A, %d %b %Y | %H:%M:%S")

st.write(f"🕒 Waktu Akses: {current_time_str}")

import os

# ============================================================
# KONFIGURASI HALAMAN STREAMLIT (MOBILE FRIENDLY)
# ============================================================
st.set_page_config(
    page_title="JII70 Syariah Pro Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling CSS Glassmorphism Dark Neon (Menyesuaikan tema terminal Anda)
st.markdown("""
    <style>
    .main { background-color: #07090e; color: #f1f5f9; }
    .stMetric { background-color: #111827; border: 1px solid #1f2937; padding: 15px; border-radius: 12px; }
    .metric-card { background-color: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 15px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

JII70_TICKERS = [
    'AADI', 'ACES', 'ADMR', 'ADRO', 'AKRA', 'ANTM', 'ARCI', 'AVIA', 'BKSL', 'BRIS',
    'BRMS', 'BSDE', 'BTPS', 'BUMI', 'CMRY', 'CPIN', 'CTRA', 'DEWA', 'DKFT', 'DSNG',
    'ELSA', 'ENRG', 'ERAA', 'ESSA', 'EXCL', 'HEAL', 'HRTA', 'HRUM', 'ICBP', 'IMPC',
    'INDF', 'INDY', 'INKP', 'INTP', 'ISAT', 'ITMG', 'JPFA', 'JSMR', 'KIJA', 'KLBF',
    'KPIG', 'LSIP', 'MAPA', 'MAPI', 'MARK', 'MBMA', 'MDKA', 'MEDC', 'MIKA', 'MTEL',
    'MYOR', 'PGAS', 'PTBA', 'RAJA', 'RATU', 'SIDO', 'SMGR', 'SMRA', 'SRTG', 'SSIA',
    'TAPG', 'TCPI', 'TINS', 'TKIM', 'TLKM', 'TOBA', 'TPIA', 'UNTR', 'UNVR', 'WIFI'
]

@st.cache_data(ttl=300)
def download_market_data():
    results = []
    ihsg_current = 0.0
    ihsg_chg = 0.0

    try:
        ihsg_df = yf.download("^JKSE", period="5d", interval="1d", progress=False, auto_adjust=False)
        if isinstance(ihsg_df.columns, pd.MultiIndex):
            ihsg_df.columns = ihsg_df.columns.get_level_values(0)
        if not ihsg_df.empty and "Close" in ihsg_df.columns:
            closes = pd.to_numeric(ihsg_df["Close"].iloc[:, 0] if isinstance(ihsg_df["Close"], pd.DataFrame) else ihsg_df["Close"], errors="coerce").dropna()
            if len(closes) >= 2:
                ihsg_current = float(closes.iloc[-1])
                ihsg_prev = float(closes.iloc[-2])
                ihsg_chg = ((ihsg_current - ihsg_prev) / ihsg_prev) * 100.0
    except Exception:
        pass

    for t in JII70_TICKERS:
        symbol = f"{t}.JK"
        try:
            hist = yf.download(symbol, period="1mo", interval="1d", progress=False, auto_adjust=False, timeout=10)
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            
            if hist is None or hist.empty or len(hist) < 2:
                continue

            def get_s(col):
                if col not in hist.columns:
                    return pd.Series(dtype=float)
                d = hist[col]
                if isinstance(d, pd.DataFrame):
                    d = d.iloc[:, 0]
                return pd.to_numeric(d, errors="coerce").dropna()

            o_s, h_s, l_s, c_s, v_s = get_s("Open"), get_s("High"), get_s("Low"), get_s("Close"), get_s("Volume")
            if len(c_s) < 2:
                continue

            o = float(o_s.iloc[-1]) if len(o_s) > 0 else float(c_s.iloc[-1])
            p = float(c_s.iloc[-2])
            h = float(h_s.iloc[-1]) if len(h_s) > 0 else float(c_s.iloc[-1])
            l = float(l_s.iloc[-1]) if len(l_s) > 0 else float(c_s.iloc[-1])
            c = float(c_s.iloc[-1])
            v = int(max(0, float(v_s.iloc[-1]))) if len(v_s) > 0 else 0

            if p <= 0:
                continue

            chg_pct = ((c - p) / p) * 100.0
            freq = int(v / 1500) if v > 0 else 100

            pivot = (h + l + c) / 3.0
            support = (2.0 * pivot) - h
            resist = (2.0 * pivot) - l
            vwap = ((pivot * v) / v) if v > 0 else pivot

            ma5 = float(c_s.rolling(window=min(5, len(c_s))).mean().iloc[-1])
            ma20 = float(c_s.rolling(window=min(20, len(c_s))).mean().iloc[-1])
            ma50 = float(c_s.rolling(window=min(50, len(c_s))).mean().iloc[-1]) if len(c_s) >= 50 else ma20

            vol_sma5 = float(v_s.rolling(window=min(5, len(v_s))).mean().iloc[-1]) if len(v_s) else 0.0
            intraday_drop = ((l - h) / h) * 100.0
            rebound_low = ((c - l) / l) * 100.0
            
            is_rebound = (intraday_drop <= -2.5) and (rebound_low >= 2.0) and (v > vol_sma5 * 1.8) and (c >= vwap)

            jenis_recom = "Konsolidasi Normal"
            alasan = "Pergerakan harga dan volume stabil dalam rentang konsolidasi pasar wajar."

            if is_rebound:
                jenis_recom = "Saham Rebound"
                alasan = "Shakeout Rebound: Tekanan jual diredam buyer besar dengan lonjakan volume di atas VWAP."
            elif c <= support * 1.015 and c >= support * 0.985:
                jenis_recom = "Saham BOW"
                alasan = "Buy on Weakness: Harga terkoreksi sehat menguji area Support Pivot kuat."
            elif c > ma20 and ma20 > ma50:
                jenis_recom = "Saham Swing"
                alasan = "Swing Trend Following: Struktur tren menengah bullish mapan (MA20 di atas MA50)."
            elif chg_pct > 3.0 and v > (vol_sma5 * 1.6):
                jenis_recom = "Saham Scalping"
                alasan = "Momentum Scalping: Lonjakan harga impulsif disertai volume masif."
            elif c > ma5 and 0.3 < chg_pct < 3.0 and c >= o:
                jenis_recom = "Saham BSJP"
                alasan = "Beli Sore Jual Pagi: Akumulasi institusi menjelang penutupan."
            elif 0.0 < chg_pct <= 1.2:
                jenis_recom = "Saham BPJS"
                alasan = "Beli Pagi Jual Siang: Stabilitas harga di sesi pertama aman."

            results.append({
                'Ticker': t,
                'Open': round(o, 2),
                'Preview': round(p, 2),
                'High': round(h, 2),
                'Low': round(l, 2),
                'Close': round(c, 2),
                'Chg%': round(chg_pct, 2),
                'Volume': v,
                'Frekuensi': freq,
                'Support': round(support, 2),
                'Resist': round(resist, 2),
                'Pivot': round(pivot, 2),
                'Recom Beli': round(c, 2),
                'Recom Jual': round(resist, 2),
                'Jenis Rekomendasi': jenis_recom,
                'Alasan Rekomendasi': alasan
            })
        except Exception:
            continue

    return pd.DataFrame(results), {'current': ihsg_current, 'chg': ihsg_chg}

# Header Utama
st.title("⚡ JII70 SYARIAH PRO TERMINAL")
st.write(f"🕒 Waktu Akses: {datetime.now().strftime('%A, %d %b %Y | %H:%M:%S')}")

# Load Data
with st.spinner("Menghubungkan ke server Yahoo Finance untuk data riil bursa..."):
    df, ihsg_info = download_market_data()

# Widget IHSG & Statistik
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    col_color = "normal" if ihsg_info['chg'] >= 0 else "inverse"
    st.metric("IHSG Market", f"{ihsg_info['current']:,.2f}", f"{ihsg_info['chg']:+.2f}%")
with col2:
    st.metric("Total Emiten", len(df))
with col3:
    naik = len(df[df['Chg%'] > 0]) if not df.empty else 0
    st.metric("Saham Naik", naik)
with col4:
    turun = len(df[df['Chg%'] < 0]) if not df.empty else 0
    st.metric("Saham Turun", turun)
with col5:
    layak = len(df[~df['Jenis Rekomendasi'].str.contains("Konsolidasi Normal", na=False)]) if not df.empty else 0
    st.metric("Rekomendasi Aktif", layak)

st.markdown("---")

# Filter Sidebar / Kontrol
st.subheader("🔍 Filter & Navigasi Pasar")
f_col1, f_col2 = st.columns(2)

with f_col1:
    filter_option = st.selectbox("Pilih Strategi Filter:", [
        "Semua Saham JII70", "Top Gainer", "Top Loser", 
        "Saham BPJS", "Saham BSJP", "Saham Swing", 
        "Saham Scalping", "Saham Rebound", "Saham BOW"
    ])

with f_col2:
    search_query = st.text_input("Cari Kode Emiten (Cth: ADRO):", "").strip().upper()

# Terapkan Filter
filtered_df = df.copy()
if not filtered_df.empty:
    if filter_option == "Top Gainer":
        filtered_df = filtered_df.sort_values(by="Chg%", ascending=False)
    elif filter_option == "Top Loser":
        filtered_df = filtered_df.sort_values(by="Chg%", ascending=True)
    elif filter_option != "Semua Saham JII70":
        filtered_df = filtered_df[filtered_df['Jenis Rekomendasi'] == filter_option]

    if search_query:
        filtered_df = filtered_df[filtered_df['Ticker'].str.contains(search_query, na=False)]

# Tampilkan Tabel Data
if not filtered_df.empty:
    st.dataframe(filtered_df, use_container_width=True, height=500)
    
    # Tombol Download Excel
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data CSV / Excel",
        data=csv_data,
        file_name="jii70_screener_output.csv",
        mime="text/csv"
    )
else:
    st.warning("Tidak ada data emiten yang cocok dengan filter.")
