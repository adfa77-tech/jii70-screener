import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from zoneinfo import ZoneInfo

# ============================================================
# KONFIGURASI HALAMAN STREAMLIT (PRO TERMINAL V3)
# ============================================================
st.set_page_config(
    page_title="JII70 Syariah Pro Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling CSS & Warna Berbeda di Setiap Kolom Angka (Multi-Color Financial Terminal)
st.markdown("""
    <style>
    .main { 
        background: linear-gradient(135deg, #030712 0%, #0f172a 100%); 
        color: #f1f5f9; 
    }
    
    /* Ukuran Kotak Kartu Metrik Lebih Kecil & Warna Berbeda-beda */
    .metric-ihsg { background: linear-gradient(145deg, #1e1b4b 0%, #312e81 100%); border: 1px solid #4338ca; padding: 12px; border-radius: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    .metric-emiten { background: linear-gradient(145deg, #064e3b 0%, #065f46 100%); border: 1px solid #059669; padding: 12px; border-radius: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    .metric-naik { background: linear-gradient(145deg, #14532d 0%, #166534 100%); border: 1px solid #22c55e; padding: 12px; border-radius: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    .metric-turun { background: linear-gradient(145deg, #7f1d1d 0%, #991b1b 100%); border: 1px solid #ef4444; padding: 12px; border-radius: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    .metric-rekom { background: linear-gradient(145deg, #3b0764 0%, #581c87 100%); border: 1px solid #a855f7; padding: 12px; border-radius: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    
    .metric-label { font-size: 0.75rem; color: #cbd5e1; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
    .metric-value { font-size: 1.25rem; font-weight: 800; color: #ffffff; }
    
    /* Jam Realtime WIB Box */
    .clock-box {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #38bdf8;
        padding: 8px 16px;
        border-radius: 8px;
        color: #38bdf8;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }
    
    /* Styling Header Tabel agar Bold dan Berwarna Profesional */
    thead tr th {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        font-weight: 900 !important;
        font-size: 0.95rem !important;
        text-align: center !important;
        border-bottom: 2px solid #0284c7 !important;
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
                'Ticker': t, 
                'Open': f"{o:,.0f}".replace(",", "."), 
                'Preview': f"{p:,.0f}".replace(",", "."), 
                'High': f"{h:,.0f}".replace(",", "."),
                'Low': f"{l:,.0f}".replace(",", "."), 
                'Close': f"{c:,.0f}".replace(",", "."), 
                'Chg%': f"{chg_pct:+.2f}%",  # Dibuat sederhana 2 digit desimal
                'Volume': f"{v:,.0f}".replace(",", "."),
                'Frekuensi': f"{freq:,.0f}".replace(",", "."), 
                'Support': f"{support:,.0f}".replace(",", "."), 
                'Resist': f"{resist:,.0f}".replace(",", "."),
                'Pivot': f"{pivot:,.0f}".replace(",", "."), 
                'Recom Beli': f"{c:,.0f}".replace(",", "."), 
                'Recom Jual': f"{resist:,.0f}".replace(",", "."),
                'Jenis Rekomendasi': jenis_recom, 
                'Alasan Rekomendasi': alasan
            })
        except Exception:
            continue

    return pd.DataFrame(results), {'current': ihsg_current, 'chg': ihsg_chg}

# ============================================================
# HEADER & JAM REALTIME WIB
# ============================================================
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("""
        <h1 style="margin: 0; font-size: 2rem; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ⚡ JII70 SYARIAH PRO TERMINAL
        </h1>
    """, unsafe_allow_html=True)

with col_h2:
    waktu_wib = datetime.now(ZoneInfo("Asia/Jakarta"))
    waktu_str = waktu_wib.strftime("%d %b %Y | %H:%M:%S WIB")
    st.markdown(f'<div style="text-align: right;"><span class="clock-box">🕒 {waktu_str}</span></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Load Data
with st.spinner("Sinkronisasi real-time dengan server bursa..."):
    df, ihsg_info = download_market_data()

# ============================================================
# KARTU METRIK KOMPAK (UKURAN KECIL DENGAN WARNA BERBEDA)
# ============================================================
m1, m2, m3, m4, m5 = st.columns(5)

chg_color = "#4ade80" if ihsg_info['chg'] >= 0 else "#f87171"
with m1:
    st.markdown(f"""
        <div class="metric-ihsg">
            <div class="metric-label">IHSG Market</div>
            <div class="metric-value">{ihsg_info['current']:,.2f}</div>
            <div style="font-size: 0.8rem; color: {chg_color}; font-weight: bold; margin-top: 2px;">{ihsg_info['chg']:+.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
        <div class="metric-emiten">
            <div class="metric-label">Total Emiten</div>
            <div class="metric-value">{len(df)}</div>
            <div style="font-size: 0.8rem; color: #34d399; margin-top: 2px;">Aktif Terpantau</div>
        </div>
    """, unsafe_allow_html=True)

naik = len(df[df['Chg%'].str.contains(r"\+", na=False)]) if not df.empty else 0
with m3:
    st.markdown(f"""
        <div class="metric-naik">
            <div class="metric-label">Saham Naik</div>
            <div class="metric-value">{naik}</div>
            <div style="font-size: 0.8rem; color: #4ade80; margin-top: 2px;">Bullish Sesi</div>
        </div>
    """, unsafe_allow_html=True)

turun = len(df[df['Chg%'].str.contains(r"\-", na=False)]) if not df.empty else 0
with m4:
    st.markdown(f"""
        <div class="metric-turun">
            <div class="metric-label">Saham Turun</div>
            <div class="metric-value">{turun}</div>
            <div style="font-size: 0.8rem; color: #fca5a5; margin-top: 2px;">Bearish Sesi</div>
        </div>
    """, unsafe_allow_html=True)

layak = len(df[~df['Jenis Rekomendasi'].str.contains("Konsolidasi Normal", na=False)]) if not df.empty else 0
with m5:
    st.markdown(f"""
        <div class="metric-rekom">
            <div class="metric-label">Rekomendasi Aktif</div>
            <div class="metric-value">{layak}</div>
            <div style="font-size: 0.8rem; color: #c084fc; margin-top: 2px;">Setup Siap</div>
        </div>
    """, unsafe_allow_html=True)

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
    # PEWARNAAN BERBEDA DI SETIAP KOLOM ANGKA
    # ============================================================
    def color_columns(val):
        s_val = str(val)
        if "%" in s_val:
            color = '#4ade80' if "+" in s_val else '#f87171' if "-" in s_val else '#94a3b8'
            return f'color: {color}; font-weight: bold;'
        elif "Rebound" in s_val or "Scalping" in s_val:
            return 'color: #f43f5e; font-weight: bold;'
        elif "Swing" in s_val or "BOW" in s_val or "BSJP" in s_val or "BPJS" in s_val:
            return 'color: #38bdf8; font-weight: bold;'
        elif "Konsolidasi" in s_val:
            return 'color: #64748b;'
        return ''

    # Menerapkan styling warna dinamis ke kolom tabel
    styled_df = filtered_df.style.map(color_columns)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tampilkan Tabel Data Interaktif
    st.dataframe(styled_df, use_container_width=True, height=520)

    # ============================================================
    # TOMBOL DOWNLOAD
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
