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
            # Filter Likuiditas: Value transaksi >= 5 Miliar / Volume Relatif >= 1.5x
            # Filter Volatilitas & Momentum: Harga Rp 100 - Rp 2.000, Chg% +2% s.d +8%, Rentang Intraday >= 3%
            # Filter Teknikal: Harga di atas VWAP, EMA 9 > EMA 20, RSI di rentang 50 - 70
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
                recom_jual = c * 1.02  # Target profit ketat 1-2%
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

    return pd.DataFrame(results), {'current': ihsg_current, '
