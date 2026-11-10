import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from zoneinfo import ZoneInfo

# ============================================================
# KONFIGURASI HALAMAN STREAMLIT (PRO TERMINAL V5 - LIGHT MODE)
# ============================================================
st.set_page_config(
    page_title="JII70 Syariah Pro Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling CSS & Desain Terang agar Background Pemandangan Terlihat Jelas & Estetik
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(241, 245, 249, 0.82), rgba(226, 232, 240, 0.88)), 
                    url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #0f172a;
    }
    
    /* Warna Teks & Label Utama */
    h1, h2, h3, p, span, label {
        color: #0f172a !important;
    }
    
    div.row-widget.stRadio > div {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    div.row-widget.stRadio label {
        color: #1e293b !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
    }
    
    /* Ukuran Kotak Kartu Metrik Terang & Elegan */
    .metric-ihsg { background: linear-gradient(145deg, #e0e7ff 0%, #c7d2fe 100%); border: 1px solid #818cf8; padding: 12px; border-radius: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .metric-emiten { background: linear-gradient(145deg, #d1fae5 0%, #a7f3d0 100%); border: 1px solid #34d399; padding: 12px; border-radius: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .metric-naik { background: linear-gradient(145deg, #dcfce7 0%, #bbf7d0 100%); border: 1px solid #4ade80; padding: 12px; border-radius: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .metric-turun { background: linear-gradient(145deg, #fee2e2 0%, #fecaca 100%); border: 1px solid #f87171; padding: 12px; border-radius: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .metric-rekom { background: linear-gradient(145deg, #fae8ff 0%, #f5d0fe 100%); border: 1px solid #e879f9; padding: 12px; border-radius: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    
    .metric-label { font-size: 0.75rem; color: #475569; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
    .metric-value { font-size: 1.25rem; font-weight: 900; color: #0f172a; }
    
    /* Jam Realtime WIB Box */
    .clock-box {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #0284c7;
        padding: 8px 16px;
        border-radius: 8px;
        color: #0369a1;
        font-weight: 800;
        font-size: 0.9rem;
        display: inline-block;
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.2);
    }
    
    /* Styling Header Tabel agar Jelas & Profesional */
    thead tr th {
        background-color: #0f172a !important;
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
            
            pivot = (h + l + c) / 3.0
            support = (2.0 * pivot) - h
            resist = (2.0 * pivot) - l
            vwap = ((pivot * v) / v) if v > 0 else pivot

            ma5 = float(c_s.rolling(window=5).mean().iloc[-1])
            ma20 = float(c_s.rolling(window=20).mean().iloc[-1])
            ma50 = float(c_s.rolling(window=50).mean().iloc[-1]) if len(c_s) >= 50 else ma20
            
            vol_sma5 = float(v_s.rolling(window=5).mean().iloc[-1]) if len(v_s) >= 5 else 0.0

            intraday_drop = ((l - h) / h) * 100.0
            rebound_low = ((c - l) / l) * 100.0
            is_rebound = (intraday_drop <= -2.5) and (rebound_low >= 2.0) and (v > vol_sma5 * 1.5) and (c >= vwap)

            jenis_recom = "Konsolidasi Normal"
            alasan = "Pergerakan harga dan volume stabil dalam rentang konsolidasi wajar."

            if is_rebound:
                jenis_recom = "Saham Rebound"
                alasan = "Shakeout Rebound: Tekanan jual diredam buyer besar dengan lonjakan volume."
            elif c <= support * 1.015 and c >= support * 0.985:
                jenis_recom = "Saham BOW"
                alasan = "Buy on Weakness: Harga terkoreksi sehat menguji area Support Pivot kuat."
            elif c > ma20 and ma20 > ma50 and chg_pct > 0:
                jenis_recom = "Saham Swing"
                alasan = "Swing Trend Following Akurat: Struktur tren bullish mapan (MA20 > MA50) + Higher High."
            elif chg_pct > 2.5 and v > (vol_sma5 * 1.5) and c >= h * 0.98:
                jenis_recom = "Saham Scalping"
                alasan = "Momentum Scalping Akurat: Lonjakan harga impulsif menembus resistance intraday + volume masif."
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
                'Chg%': f"{chg_pct:+.2f}%",  
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
# HEADER, AUTHOR & JAM REALTIME WIB
# ============================================================
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("""
        <h1 style="margin: 0; font-size: 2rem; background: linear-gradient(90deg, #0284c7, #4f46e5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ⚡ JII70 SYARIAH PRO TERMINAL
        </h1>
        <p style="margin: 4px 0 0 0; font-size: 0.9rem; color: #1e293b; font-weight: 700; letter-spacing: 0.5px;">
            Made By : ADI CANDRA, S.HI, MM
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

chg_color = "#15803d" if ihsg_info['chg'] >= 0 else "#b91c1c"
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
            <div style="font-size: 0.8rem; color: #047857; margin-top: 2px;">Aktif Terpantau</div>
        </div>
    """, unsafe_allow_html=True)

naik = len(df[df['Chg%'].str.contains(r"\+", na=False)]) if not df.empty else 0
with m3:
    st.markdown(f"""
        <div class="metric-naik">
            <div class="metric-label">Saham Naik</div>
            <div class="metric-value">{naik}</div>
            <div style="font-size: 0.8rem; color: #15803d; margin-top: 2px;">Bullish Sesi</div>
        </div>
    """, unsafe_allow_html=True)

turun = len(df[df['Chg%'].str.contains(r"\-", na=False)]) if not df.empty else 0
with m4:
    st.markdown(f"""
        <div class="metric-turun">
            <div class="metric-label">Saham Turun</div>
            <div class="metric-value">{turun}</div>
            <div style="font-size: 0.8rem; color: #b91c1c; margin-top: 2px;">Bearish Sesi</div>
        </div>
    """, unsafe_allow_html=True)

layak = len(df[~df['Jenis Rekomendasi'].str.contains("Konsolidasi Normal", na=False)]) if not df.empty else 0
with m5:
    st.markdown(f"""
        <div class="metric-rekom">
            <div class="metric-label">Rekomendasi Aktif</div>
            <div class="metric-value">{layak}</div>
            <div style="font-size: 0.8rem; color: #7e22ce; margin-top: 2px;">Setup Siap</div>
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

    def color_by_column(val, col_name):
        s_val = str(val)
        if col_name == 'Chg%':
            if "+" in s_val:
                return 'background-color: #dcfce7; color: #15803d; font-weight: bold;'
            elif "-" in s_val:
                return 'background-color: #fee2e2; color: #b91c1c; font-weight: bold;'
        elif col_name == 'Jenis Rekomendasi':
            if "Konsolidasi" in s_val:
                return 'background-color: #f1f5f9; color: #64748b;'
            return 'background-color: #e0e7ff; color: #3730a3; font-weight: bold;'
        
        col_colors = {
            'Ticker': 'background-color: #f8fafc; color: #0f172a; font-weight: bold;',
            'Open': 'background-color: #fef3c7; color: #b45309;',
            'Preview': 'background-color: #f1f5f9; color: #334155;',
            'High': 'background-color: #e0f2fe; color: #0369a1;',
            'Low': 'background-color: #f3e8ff; color: #6b21a8;',
            'Close': 'background-color: #dcfce7; color: #15803d; font-weight: bold;',
            'Volume': 'background-color: #e0e7ff; color: #3730a3;',
            'Frekuensi': 'background-color: #ede9fe; color: #5b21b6;',
            'Support': 'background-color: #fce7f3; color: #9d174d;',
            'Resist': 'background-color: #ffe4e6; color: #be123c;',
            'Pivot': 'background-color: #fef9c3; color: #854d0e;',
            'Recom Beli': 'background-color: #dcfce7; color: #166534;',
            'Recom Jual': 'background-color: #fae8ff; color: #86198f;'
        }
        return col_colors.get(col_name, '')

    styled_df = filtered_df.style.apply(lambda col: [color_by_column(v, col.name) for v in col], axis=0)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tampilkan Tabel Data Interaktif
    st.dataframe(styled_df, use_container_width=True, height=520)

    # ============================================================
    # PANEL PILIHAN EMITEN & GRAFIK CANDLESTICK (MUNCUL KETIKA DIKLIK)
    # ============================================================
    st.markdown("---")
    st.markdown("### 📊 Analisis Detail, Grafik Candlestick & Stockbit")
    
    available_tickers = filtered_df['Ticker'].tolist() if not filtered_df.empty else JII70_TICKERS
    
    col_sel1, col_sel2 = st.columns([2, 2])
    with col_sel1:
        selected_ticker = st.selectbox("👇 Klik / Pilih Kode Emiten untuk Memunculkan Grafik Candlestick:", available_tickers, index=0)

    stockbit_url = f"https://stockbit.com/symbol/{selected_ticker}"
    with col_sel2:
        st.markdown(f"""
            <div style="padding-top: 28px;">
                <a href="{stockbit_url}" target="_blank" style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
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

    # Grafik Candlestick & Indikator Lengkap Muncul Interaktif Saat Dipilih
    if selected_ticker:
        chart_df = get_chart_data(selected_ticker)
        if not chart_df.empty and len(chart_df) > 20:
            chart_df['MA5'] = chart_df['Close'].rolling(window=5).mean()
            chart_df['MA10'] = chart_df['Close'].rolling(window=10).mean()
            chart_df['MA20'] = chart_df['Close'].rolling(window=20).mean()

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
                                subplot_titles=(f"Candlestick & MA (5, 10, 20) - {selected_ticker}", "Volume", "MACD & Signal", "RSI (14) & Stochastic"))

            fig.add_trace(go.Candlestick(
                x=chart_df.index, open=chart_df['Open'], high=chart_df['High'],
                low=chart_df['Low'], close=chart_df['Close'], name='Candlestick'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['MA5'], line=dict(color='#d97706', width=1.5), name='MA 5'), row=1, col=1)
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['MA10'], line=dict(color='#0284c7', width=1.5), name='MA 10'), row=1, col=1)
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['MA20'], line=dict(color='#9333ea', width=1.5), name='MA 20'), row=1, col=1)

            colors = ['#16a34a' if c >= o else '#dc2626' for c, o in zip(chart_df['Close'], chart_df['Open'])]
            fig.add_trace(go.Bar(x=chart_df.index, y=chart_df['Volume'], marker_color=colors, name='Volume'), row=2, col=1)

            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['MACD'], line=dict(color='#0284c7', width=1), name='MACD'), row=3, col=1)
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['Signal_Line'], line=dict(color='#ea580c', width=1), name='Signal'), row=3, col=1)
            fig.add_trace(go.Bar(x=chart_df.index, y=chart_df['MACD_Hist'], marker_color='#64748b', name='Histogram'), row=3, col=1)

            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['RSI'], line=dict(color='#9333ea', width=1.5), name='RSI (14)'), row=4, col=1)
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['%K'], line=dict(color='#16a34a', width=1), name='%K Stoch'), row=4, col=1)
            fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df['%D'], line=dict(color='#dc2626', width=1), name='%D Stoch'), row=4, col=1)

            fig.update_layout(
                template='plotly_white',
                height=850,
                margin=dict(l=10, r=10, t=30, b=10),
                paper_bgcolor='rgba(255, 255, 255, 0.9)',
                plot_bgcolor='rgba(255, 255, 255, 0.9)',
                xaxis_rangeslider_visible=False,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # TOMBOL DOWNLOAD
    # ============================================================
    b1, b2 = st.columns([1, 4])
    with b1:
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export to CSV
