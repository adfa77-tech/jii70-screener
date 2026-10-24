import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# ============================================================
# KONFIGURASI HALAMAN STREAMLIT (PRO TERMINAL MODE)
# ============================================================
st.set_page_config(
    page_title="JII70 Syariah Pro Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling CSS Modern Glassmorphism & Neon Financial Theme
st.markdown("""
    <style>
    .main { 
        background: linear-gradient(135deg, #05070b 0%, #0f172a 100%); 
        color: #f1f5f9; 
    }
    .stMetric { 
        background: linear-gradient(145deg, #111827 0%, #1f2937 100%); 
        border: 1px solid #334155; 
        padding: 18px; 
        border-radius: 14px; 
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .stMetric label {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    h1, h2, h3 {
        font-family: 'Segoe UI', sans-serif;
        letter-spacing: -0.5px;
    }
    .terminal-header {
        background: rgba(15, 23, 42, 0.8);
        border-bottom: 1px solid #1e293b;
        padding: 10px 0;
        margin-bottom: 20px;
    }
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
            alasan = "Pergerakan harga dan volume stabil dalam rentang konsolidasi wajar."

            if is_rebound:
                jenis_recom = "Saham Rebound"
                alasan = "Shakeout Rebound: Tekanan jual diredam buyer besar dengan lonjakan volume."
            elif c <= support * 1.015 and c >= support * 0.985:
                jenis_recom = "Saham BOW"
                alasan = "Buy on Weakness: Harga terkoreksi sehat menguji area Support Pivot kuat."
            elif c > ma20 and ma20 > ma50:
                jenis_recom = "Saham Swing"
                alasan = "Swing Trend Following: Struktur tren menengah bullish mapan (MA20 > MA50)."
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
                'Ticker': t, 'Open': round(o, 2), 'Preview': round(p, 2), 'High': round(h, 2),
                'Low': round(l, 2), 'Close': round(c, 2), 'Chg%': round(chg_pct, 2), 'Volume': v,
                'Frekuensi': freq, 'Support': round(support, 2), 'Resist': round(resist, 2),
                'Pivot': round(pivot, 2), 'Recom Beli': round(c, 2), 'Recom Jual': round(resist, 2),
                'Jenis Rekomendasi': jenis_recom, 'Alasan Rekomendasi': alasan
            })
        except Exception:
            continue

    return pd.DataFrame(results), {'current': ihsg_current, 'chg': ihsg_chg}

# ============================================================
# HEADER & BRANDING TERMINAL
# ============================================================
st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 0;">
        <h1 style="margin: 0; font-size: 2.2rem; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ⚡ JII70 SYARIAH PRO TERMINAL
        </h1>
        <span style="background: #1e293b; color: #38bdf8; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; border: 1px solid #334155; font-weight: 600;">
            LIVE MARKET FEED
        </span>
    </div>
""", unsafe_allow_html=True)

# Load Data
with st.spinner("Sinkronisasi real-time dengan server bursa..."):
    df, ihsg_info = download_market_data()

# ============================================================
# KARTU METRIK STATISTIK UTAMA
# ============================================================
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("IHSG Market", f"{ihsg_info['current']:,.2f}", f"{ihsg_info['chg']:+.2f}%")
with m2:
    st.metric("Total Emiten", len(df))
with m3:
    naik = len(df[df['Chg%'] > 0]) if not df.empty else 0
    st.metric("Saham Naik", naik)
with m4:
    turun = len(df[df['Chg%'] < 0]) if not df.empty else 0
    st.metric("Saham Turun", turun)
with m5:
    layak = len(df[~df['Jenis Rekomendasi'].str.contains("Konsolidasi Normal", na=False)]) if not df.empty else 0
    st.metric("Rekomendasi Aktif", layak)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# PANEL KONTROL & NAVIGASI STRATEGI (TABS MODERN)
# ============================================================
st.markdown("### 🔍 Terminal Filter & Analisis Strategi")

tab_labels = [
    "Semua Saham", "Top Gainer 🚀", "Top Loser 🔻", 
    "Saham Rebound ⚡", "Saham BOW 🎯", "Saham Swing 📈", 
    "Saham Scalping 🔥", "Saham BSJP 🌙", "Saham BPJS ☀️"
]

selected_tab = st.radio("Pilih Mode Tampilan Strategi:", tab_labels, horizontal=True, label_visibility="collapsed")

# Filter Pencarian Emiten
c_search, c_space = st.columns([2, 3])
with c_search:
    search_query = st.text_input("🔍 Cari Kode Emiten Cepat (Cth: ADRO, UNTR):", "").strip().upper()

# Proses Filter Berdasarkan Tab Aktif
filtered_df = df.copy()
if not filtered_df.empty:
    if "Top Gainer" in selected_tab:
        filtered_df = filtered_df.sort_values(by="Chg%", ascending=False)
    elif "Top Loser" in selected_tab:
        filtered_df = filtered_df.sort_values(by="Chg%", ascending=True)
    elif "Rebound" in selected_tab:
        filtered_df = filtered_df[filtered_df['Jenis Rekomendasi'] == "Saham Rebound"]
    elif "BOW" in selected_tab:
        filtered_df = filtered_df[filtered_df['Jenis Rekomendasi'] == "Saham BOW"]
    elif "Swing" in selected_tab:
        filtered_df = filtered_df[filtered_df['Jenis Rekomendasi'] == "Saham Swing"]
    elif "Scalping" in selected_tab:
        filtered_df = filtered_df[filtered_df['Jenis Rekomendasi'] == "Saham Scalping"]
    elif "BSJP" in selected_tab:
        filtered_df = filtered_df[filtered_df['Jenis Rekomendasi'] == "Saham BSJP"]
    elif "BPJS" in selected_tab:
        filtered_df = filtered_df[filtered_df['Jenis Rekomendasi'] == "Saham BPJS"]

    if search_query:
        filtered_df = filtered_df[filtered_df['Ticker'].str.contains(search_query, na=False)]

    # ============================================================
    # PEWARNAAN PROFESIONAL & TAMPILAN TABEL
    # ============================================================
    def color_chg(val):
        color = '#4ade80' if val > 0 else '#f87171' if val < 0 else '#94a3b8'
        return f'color: {color}; font-weight: bold;'

    def color_recom(val):
        if "Konsolidasi" in str(val):
            return 'color: #64748b;'
        return 'color: #38bdf8; font-weight: bold;'

    styled_df = filtered_df.style.map(color_chg, subset=['Chg%']).map(color_recom, subset=['Jenis Rekomendasi'])

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tampilkan Tabel Data Interaktif
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=520,
        column_config={
            "Ticker": st.column_config.TextColumn("Kode", help="Kode Emiten JII70"),
            "Open": st.column_config.NumberColumn("Open", format="%.2f"),
            "Preview": st.column_config.NumberColumn("Prev", format="%.2f"),
            "High": st.column_config.NumberColumn("High", format="%.2f"),
            "Low": st.column_config.NumberColumn("Low", format="%.2f"),
            "Close": st.column_config.NumberColumn("Close", format="%.2f"),
            "Chg%": st.column_config.NumberColumn("Chg %", format="%.2f%%"),
            "Volume": st.column_config.NumberColumn("Volume", format="%d"),
            "Frekuensi": st.column_config.NumberColumn("Freq", format="%d"),
            "Support": st.column_config.NumberColumn("Support", format="%.2f"),
            "Resist": st.column_config.NumberColumn("Resist", format="%.2f"),
            "Pivot": st.column_config.NumberColumn("Pivot", format="%.2f"),
        }
    )

    # ============================================================
    # TOMBOL DOWNLOAD & FITUR EKSTRA
    # ============================================================
    b1, b2 = st.columns([1, 4])
    with b1:
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export to CSV",
            data=csv_data,
            file_name="jii70_pro_terminal_report.csv",
            mime="text/csv"
        )
else:
    st.warning("⚠️ Tidak ada data emiten yang cocok dengan filter atau kriteria pencarian.")
