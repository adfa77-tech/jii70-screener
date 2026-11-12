import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from zoneinfo import ZoneInfo

# ============================================================
# KONFIGURASI HALAMAN STREAMLIT (FUTURISTIC TERMINAL V6)
# ============================================================
st.set_page_config(
    page_title="JII70 Syariah Futuristic Pro Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling CSS - Tema Futuristik, Menawan, & Background Pemandangan Tajam
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(3, 7, 18, 0.72), rgba(15, 23, 42, 0.82)), 
                    url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f8fafc;
    }
    
    /* Warna Teks & Label Futuristik */
    h1, h2, h3, p, span, label {
        color: #f8fafc !important;
    }
    
    div.row-widget.stRadio > div {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    div.row-widget.stRadio label {
        color: #e2e8f0 !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
    }
    
    /* Kartu Metrik Glassmorphism Futuristik */
    .metric-ihsg { background: rgba(30, 27, 75, 0.75); border: 1px solid #6366f1; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 0 20px rgba(99, 102, 241, 0.3); backdrop-filter: blur(8px); }
    .metric-emiten { background: rgba(6, 78, 59, 0.75); border: 1px solid #10b981; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 0 20px rgba(16, 185, 129, 0.3); backdrop-filter: blur(8px); }
    .metric-naik { background: rgba(20, 83, 45, 0.75); border: 1px solid #22c55e; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 0 20px rgba(34, 197, 94, 0.3); backdrop-filter: blur(8px); }
    .metric-turun { background: rgba(127, 29, 29, 0.75); border: 1px solid #ef4444; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); backdrop-filter: blur(8px); }
    .metric-rekom { background: rgba(59, 7, 100, 0.75); border: 1px solid #c084fc; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 0 20px rgba(192, 132, 252, 0.3); backdrop-filter: blur(8px); }
    
    .metric-label { font-size: 0.75rem; color: #94a3b8; font-weight: 800; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 1px; }
    .metric-value { font-size: 1.35rem; font-weight: 900; color: #ffffff; text-shadow: 0 0 10px rgba(56, 189, 248, 0.5); }
    
    /* Jam Realtime WIB Box */
    .clock-box {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #38bdf8;
        padding: 8px 16px;
        border-radius: 8px;
        color: #38bdf8;
        font-weight: 800;
        font-size: 0.9rem;
        display: inline-block;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }
    
    /* Styling Header Tabel Futuristik */
    thead tr th {
        background-color: #0f172a !important;
        color: #38bdf8 !important;
        font-weight: 900 !important;
        font-size: 0.95rem !important;
        text-align: center !important;
        border-bottom: 2px solid #38bdf8 !important;
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
            hist = yf.download(symbol, period="2mo", interval="1d", progress=False, auto_adjust=False, timeout=10)
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            
            if hist is None or hist.empty or len(hist) < 20:
                continue

            def get_s(col):
                if col not in hist.columns:
                    return pd.Series(dtype=float)
                d = hist[col]
                if isinstance(d, pd.DataFrame):
                    d = d.iloc[:, 0]
                return pd.to_numeric(d, errors="coerce").dropna()

            o_s, h_s, l_s, c_s, v_s = get_s("Open"), get_s("High"), get_s("Low"), get_s("Close"), get_s("Volume")
            if len(c_s) < 20:
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
            val_transaksi = c * v
            
            pivot = (h + l + c) / 3.0
            support = (2.0 * pivot) - h
            resist = (2.0 * pivot) - l
            vwap = ((pivot * v) / v) if v > 0 else pivot

            ma5 = float(c_s.rolling(window=5).mean().iloc[-1])
            ema9 = float(c_s.ewm(span=9, adjust=False).mean().iloc[-1])
            ema20 = float(c_s.ewm(span=20, adjust=False).mean().iloc[-1])
            ma50 = float(c_s.rolling(window=50).mean().iloc[-1]) if len(c_s) >= 50 else ema20
            vol_sma5 = float(v_s.rolling(window=5).mean().iloc[-1]) if len(v_s) >= 5 else 0.0

            # RSI 14 Calculation
            delta = c_s.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_val = float((100 - (100 / (1 + rs))).iloc[-1])

            intraday_drop = ((l - h) / h) * 100.0
            rebound_low = ((c - l) / l) * 100.0
            is_rebound = (intraday_drop <= -2.5) and (rebound_low >= 2.0) and (v > vol_sma5 * 1.5) and (c >= vwap)

            jenis_recom = "Konsolidasi Normal"
            alasan = "Pergerakan harga stabil dalam rentang konsolidasi wajar."
            waktu_jual = "Sesi 2 Mendatang / Target Tercapai"
            recom_beli = c
            recom_jual = resist

            # ==========================================================
            # PENERAPAN STRATEGI SCALPING BARU
            # ==========================================================
            intraday_range_pct = ((h - l) / l) * 100.0
            is_scalping_new = (
                (100 <= c <= 2000) and
                (val_transaksi >= 5_000_000_000) and
                (2.0 <= chg_pct <= 8.0) and
                (intraday_range_pct >= 3.0) and
                (c >= vwap) and
                (ema9 > ema20) and
                (50 <= rsi_val <= 70) and
                (v >= vol_sma5 * 1.5)
            )

            if is_scalping_new:
                jenis_recom = "Saham Scalping"
                alasan = "Setup Scalping Sempurna: Value >5M, Range >=3%, %Chg +2%-+8%, VWAP & EMA 9>20 Bullish, RSI Momentum (50-70)."
                waktu_jual = "Intraday (30-60 Min / Cepat)"
                recom_beli = c
                recom_jual = c * 1.02
            elif is_rebound:
                jenis_recom = "Saham Rebound"
                alasan = "Shakeout Rebound: Tekanan jual diredam buyer besar dengan lonjakan volume."
                waktu_jual = "Intraday / 1-3 Hari ke Depan"
                recom_beli = support * 1.005
                recom_jual = resist
            elif c <= support * 1.015 and c >= support * 0.985:
                jenis_recom = "Saham BOW"
                alasan = "Buy on Weakness: Harga terkoreksi sehat menguji area Support Pivot kuat."
                waktu_jual = "Swing 3-7 Hari"
                recom_beli = support
                recom_jual = pivot
            elif c > ema20 and ema20 > ma50 and chg_pct > 0:
                jenis_recom = "Saham Swing"
                alasan = "Swing Trend Following: Struktur tren bullish mapan (EMA 20 > MA 50)."
                waktu_jual = "1-2 Minggu (Trailing Stop)"
                recom_beli = ema20
                recom_jual = resist * 1.02
            elif c > ma5 and 0.3 < chg_pct < 3.0 and c >= o:
                jenis_recom = "Saham BSJP"
                alasan = "Beli Sore Jual Pagi: Akumulasi institusi menjelang penutupan."
                waktu_jual = "Besok Pagi (09:00 - 09:30 WIB)"
                recom_beli = c
                recom_jual = c * 1.02
            elif 0.0 < chg_pct <= 1.2:
                jenis_recom = "Saham BPJS"
                alasan = "Beli Pagi Jual Siang: Stabilitas harga di sesi pertama aman."
                waktu_jual = "Siang Hari Ini (11:30 WIB)"
                recom_beli = o
                recom_jual = o * 1.015

            results.append({
                'Ticker': t, 
                'Open': f"{o:,.0f}".replace(",", "."), 
                'Preview': f"{p:,.0f}".replace(",", "."), 
                'High': f"{h:,.0f}".replace(",", "."),
                'Low': f"{l:,.0f}".replace(",", "."), 
                'Close': f"{c:,.0f}".replace(",", "."), 
                'Chg%': f"{chg_pct:+.2f}%",  
                'Volume': f"{v:,.0f}".replace(",", "."),
                'Frekuensi': f"{freq:,.0f}".replace(",", "."), 
                'Support': f"{support:,.0f}".replace(",", "."), 
                'Resist': f"{resist:,.0f}".replace(",", "."),
                'Pivot': f"{pivot:,.0f}".replace(",", "."), 
                'Harga Beli': f"{recom_beli:,.0f}".replace(",", "."), 
                'Harga Jual': f"{recom_jual:,.0f}".replace(",", "."),
                'Waktu Jual': waktu_jual,
                'Jenis Rekomendasi': jenis_recom, 
                'Alasan': alasan
            })
        except Exception:
            continue

    return pd.DataFrame(results), {'current': ihsg_current, 'chg': ihsg_chg}

# ============================================================
# HEADER, AUTHOR & JAM REALTIME WIB
# ============================================================
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("""
        <h1 style="margin: 0; font-size: 2.2rem; background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ⚡ JII70 SYARIAH FUTURISTIC TERMINAL
        </h1>
        <p style="margin: 4px 0 0 0; font-size: 0.95rem; color: #94a3b8; font-weight: 700; letter-spacing: 1px;">
            MADE BY : ADI CANDRA, S.HI, MM
        </p>
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
# KARTU METRIK KOMPAK
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
# PANEL KONTROL & NAVIGASI STRATEGI (DI HALAMAN DEPAN)
# ============================================================
st.markdown("### 🔍 Terminal Filter & Analisis Strategi")

tab_labels = [
    "Semua Saham 🌐", "Top Gainer 🚀", "Top Loser 🔻", 
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

    def color_by_column(val, col_name):
        s_val = str(val)
        if col_name == 'Chg%':
            if "+" in s_val:
                return 'background-color: rgba(20, 83, 45, 0.85); color: #4ade80; font-weight: bold;'
            elif "-" in s_val:
                return 'background-color: rgba(127, 29, 29, 0.85); color: #f87171; font-weight: bold;'
        elif col_name == 'Jenis Rekomendasi':
            if "Konsolidasi" in s_val:
                return 'background-color: rgba(15, 23, 42, 0.85); color: #94a3b8;'
            return 'background-color: rgba(49, 46, 129, 0.85); color: #38bdf8; font-weight: bold;'
        
        col_colors = {
            'Ticker': 'background-color: rgba(15, 23, 42, 0.9); color: #f8fafc; font-weight: bold;',
            'Open': 'background-color: rgba(30, 41, 59, 0.85); color: #fbbf24;',
            'Preview': 'background-color: rgba(30, 41, 59, 0.85); color: #34d399;',
            'High': 'background-color: rgba(12, 74, 110, 0.85); color: #38bdf8;',
            'Low': 'background-color: rgba(76, 29, 149, 0.85); color: #c084fc;',
            'Close': 'background-color: rgba(20, 83, 45, 0.85); color: #4ade80; font-weight: bold;',
            'Volume': 'background-color: rgba(30, 27, 75, 0.85); color: #818cf8;',
            'Frekuensi': 'background-color: rgba(49, 46, 129, 0.85); color: #a5b4fc;',
            'Support': 'background-color: rgba(112, 26, 117, 0.85); color: #f472b6;',
            'Resist': 'background-color: rgba(131, 24, 67, 0.85); color: #fb7185;',
            'Pivot': 'background-color: rgba(120, 53, 15, 0.85); color: #fcd34d;',
            'Harga Beli': 'background-color: rgba(20, 83, 45, 0.85); color: #6ee7b7; font-weight: bold;',
            'Harga Jual': 'background-color: rgba(88, 28, 135, 0.85); color: #d8b4fe; font-weight: bold;',
            'Waktu Jual': 'background-color: rgba(30, 41, 59, 0.85); color: #38bdf8;',
            'Alasan': 'background-color: rgba(15, 23, 42, 0.85); color: #e2e8f0;'
        }
        return col_colors.get(col_name, '')

    styled_df = filtered_df.style.apply(lambda col: [color_by_column(v, col.name) for v in col], axis=0)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tampilkan Tabel Data Interaktif
    st.dataframe(styled_df, use_container_width=True, height=520)

    # ============================================================
    # PANEL PILIHAN EMITEN & GRAFIK CANDLESTICK
    # ============================================================
    st.markdown("---")
    st.markdown("### 📊 Analisis Detail Candlestick, Indikator & Stockbit")
    
    available_tickers = filtered_df['Ticker'].tolist() if not filtered_df.empty else JII70_TICKERS
    
    col_sel1, col_sel2 = st.columns([2, 2])
    with col_sel1:
        selected_ticker = st.selectbox("👇 Klik / Pilih Kode Emiten untuk Memunculkan Grafik:", available_tickers, index=0)

    stockbit_url = f"https://stockbit.com/symbol/{selected_ticker}"
    with col_sel2:
        st.markdown(f"""
            <div style="padding-top: 28px;">
                <a href="{stockbit_url}" target="_blank" style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; box-shadow: 0 0 15px rgba(2, 132, 199, 0.4);">
                    🔗 Buka Analisis {selected_ticker} di Stockbit
                </a>
            </div>
        """, unsafe_allow_html=True)

    @st.cache_data(ttl=300)
    def get_chart_data(ticker):
        df_chart = yf.download(f"{ticker}.JK", period="3mo", interval="1d", progress=False, auto_adjust=False)
        if isinstance(df_chart.columns, pd.MultiIndex):
            df_chart.columns = df_chart.columns.get_level_values(0)
        return df_chart

    if selected_ticker:
        chart_df = get_chart_data(selected_ticker)
        if not chart_df.empty and len(chart_df) > 20:
            chart_df['EMA9'] = chart_df['Close'].ewm(span=9, adjust=False).mean()
            chart_df['EMA20'] = chart_df['Close'].ewm(span=20, adjust=False).mean()
            chart_df['MA50'] = chart_df['Close'].rolling(window=50).mean()

            delta = chart_df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            chart_df['RSI'] = 100 - (100 / (1 + rs))

            exp12 = chart_df['Close'].ewm(span=12, adjust=False).mean()
            exp26 = chart_df['Close'].ewm(span=26, adjust=False).mean()
            chart_df['MACD'] = exp12 - exp26
            chart_df['Signal_Line'] = chart_df['MACD'].ewm(span=9, adjust=False).mean()
            chart_df['MACD_Hist'] = chart_df['MACD'] - chart_df['Signal_Line']

            low14 = chart_df['Low'].rolling(window=14).min()
            high14 = chart_df['High'].rolling(window=14).max()
            chart_df['%K'] = (chart_df['Close'] - low14) * 100 / (high14 - low14)
            chart_df['%D'] = chart_df['%K'].rolling(window=3).mean()

            fig = make_subplots(rows=4, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.03, 
                                row_heights=[0.45, 0.15, 0.2, 0.2],
                                subplot_titles=(f"Candlestick & EMA (9, 20) - {selected_ticker}", "Volume", "MACD & Signal", "RSI (14) & Stochastic"))

            fig.add_trace(go.Candlestick(
                x=chart_df.index, open=chart_df['Open'], high=chart_df['High'],
                low=chart_df['Low'], close=chart_df['Close'], name='Candlestick'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA9'], line=dict(color='#fbbf24', width=1.5), name='EMA 9'), row=1, col=1)
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['EMA20'], line=dict(color='#38bdf8', width=1.5), name='EMA 20'), row=1, col=1)
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['MA50'], line=dict(color='#c084fc', width=1.5), name='MA 50'), row=1, col=1)

            colors = ['#22c55e' if c >= o else '#ef4444' for c, o in zip(chart_df['Close'], chart_df['Open'])]
            fig.add_trace(go.Bar(x=chart_df.index, y=chart_df['Volume'], marker_color=colors, name='Volume'), row=2, col=1)

            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['MACD'], line=dict(color='#38bdf8', width=1), name='MACD'), row=3, col=1)
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['Signal_Line'], line=dict(color='#f97316', width=1), name='Signal'), row=3, col=1)
            fig.add_trace(go.Bar(x=chart_df.index, y=chart_df['MACD_Hist'], marker_color='#64748b', name='Histogram'), row=3, col=1)

            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['RSI'], line=dict(color='#a855f7', width=1.5), name='RSI (14)'), row=4, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=4, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="#38bdf8", row=4, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#22c55e", row=4, col=1)
            
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['%K'], line=dict(color='#22c55e', width=1), name='%K Stoch'), row=4, col=1)
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['%D'], line=dict(color='#ef4444', width=1), name='%D Stoch'), row=4, col=1)

            fig.update_layout(
                template='plotly_dark',
                height=850,
                margin=dict(l=10, r=10, t=30, b=10),
                paper_bgcolor='rgba(15, 23, 42, 0.85)',
                plot_bgcolor='rgba(15, 23, 42, 0.85)',
                xaxis_rangeslider_visible=False,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # KALKULATOR SAHAM FUTURISTIK
    # ============================================================
    st.markdown("---")
    st.markdown("### 🧮 Kalkulator Trading & Investasi Saham")
    
    with st.container():
        calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)
        
        with calc_col1:
            calc_ticker = st.selectbox("Pilih Saham", available_tickers, key="calc_ticker")
        with calc_col2:
            default_buy_p = float(df[df['Ticker'] == calc_ticker]['Close'].values[0].replace('.', '').replace(',', '.')) if not df[df['Ticker'] == calc_ticker].empty else 1000.0
            buy_price = st.number_input("Harga Beli (Rp)", value=default_buy_p, step=10.0)
        with calc_col3:
            lot_count = st.number_input("Jumlah Lot", min_value=1, value=10, step=1)
        with calc_col4:
            sell_price = st.number_input("Target Harga Jual (Rp)", value=round(buy_price * 1.02, 2), step=10.0)

        calc_fee1, calc_fee2 = st.columns(2)
        with calc_fee1:
            fee_beli_pct = st.number_input("Fee Beli (%)", value=0.15, step=0.01)
        with calc_fee2:
            fee_jual_pct = st.number_input("Fee Jual (%)", value=0.25, step=0.01)

        shares = lot_count * 100
        total_modal_kotor = buy_price * shares
        fee_beli_val = total_modal_kotor * (fee_beli_pct / 100)
        total_modal_bersih = total_modal_kotor + fee_beli_val

        total_jual_kotor = sell_price * shares
        fee_jual_val = total_jual_kotor * (fee_jual_pct / 100)
        total_jual_bersih = total_jual_kotor - fee_jual_val

        net_profit = total_jual_bersih - total_modal_bersih
        roi_pct = (net_profit / total_modal_bersih) * 100 if total_modal_bersih > 0 else 0

        st.markdown("<br>", unsafe_allow_html=True)
        res_c1, res_c2, res_c3, res_c4 = st.columns(4)
        
        with res_c1:
            st.metric("Total Modal Bersih", f"Rp {total_modal_bersih:,.0f}".replace(",", "."))
        with res_c2:
            st.metric("Total Nilai Jual", f"Rp {total_jual_bersih:,.0f}".replace(",", "."))
        with res_c3:
            profit_color_label = "🟢 Profit Bersih" if net_profit >= 0 else "🔴 Loss Bersih"
            st.metric(profit_color_label, f"Rp {net_profit:,.0f}".replace(",", "."))
        with res_c4:
            st.metric("Estimasi Return (ROI)", f"{roi_pct:+.2f}%")

    # ============================================================
    # TOMBOL DOWNLOAD
    # ============================================================
    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns([1, 4])
    with b1:
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export to CSV",
            data=csv_data,
            file_name="jii70_futuristic_terminal_report.csv",
            mime="text/css"
        )
else:
    st.warning("⚠️ Tidak ada data emiten yang cocok dengan filter atau kriteria pencarian.")
