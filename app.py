import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import ta
import yfinance as yf

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="ENTITY VALOR // FUTURE SIGHT",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme Custom Styling Patch
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #38bdf8; }
    div[data-testid="stMetricLabel"] { color: #94a3b8; font-weight: 600; }
    </style>
""", unsafe_allowed_html=True)

# ==========================================
# 2. SIDEBAR CONFIGURATION MATRIX
# ==========================================
st.sidebar.title("🔮 FUTURE SIGHT CORE")
st.sidebar.markdown("---")

# User Asset & Window Parameters
ticker = st.sidebar.text_input("TARGET TICKER", value="AAPL").upper()
lookback_days = st.sidebar.slider("ANALYSIS LOOKBACK WINDOW (DAYS)", min_value=30, max_value=730, value=365)

st.sidebar.markdown("### Algorithmic Thresholds")
fast_window = st.sidebar.slider("Fast EMA Window", min_value=5, max_value=50, value=12)
slow_window = st.sidebar.slider("Slow EMA Window", min_value=20, max_value=100, value=26)
rsi_window = st.sidebar.slider("RSI Window", min_value=5, max_value=30, value=14)

# Calculate dynamic dates
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=lookback_days)

# ==========================================
# 3. VALOR QUANT ENGINE ENGINE FUNCTIONS
# ==========================================
@st.cache_data(ttl=600)  # Cache data for 10 minutes to minimize API throttling
def load_and_process_data(symbol, start, end):
    try:
        df = yf.download(symbol, start=start, end=end)
        if df.empty:
            return None
        
        # Clean multi-index headers from newer yfinance outputs if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df.dropna()
        
        # Compute Quantitative Vectors
        df['EMA_Fast'] = ta.trend.ema_indicator(df['Close'], window=fast_window)
        df['EMA_Slow'] = ta.trend.ema_indicator(df['Close'], window=slow_window)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=rsi_window)
        
        # Signal Rules Matrix (1 = Buy, -1 = Sell, 0 = Neutral/Hold)
        df['Signal'] = 0
        buy_cond = (df['EMA_Fast'] > df['EMA_Slow']) & (df['RSI'] < 65)
        sell_cond = (df['EMA_Fast'] < df['EMA_Slow']) | (df['RSI'] > 75)
        
        df.loc[buy_cond, 'Signal'] = 1
        df.loc[sell_cond, 'Signal'] = -1
        
        # Capture precise cross-over/state change execution moments
        df['Trigger'] = df['Signal'].diff()
        
        return df.dropna()
    except Exception as e:
        st.error(f"Engine Core Failure during Data Pipeline: {e}")
        return None

# Execute Quantitative Pipeline
data = load_and_process_data(ticker, start_date, end_date)

# ==========================================
# 4. MAIN USER INTERFACE DASHBOARD
# ==========================================
st.title("ENTITY VALOR // FUTURE SIGHT")
st.caption(f"Real-Time Analytics Matrix Pipeline Active • Asset Target: {ticker}")
st.markdown("---")

if data is not None and not data.empty:
    # Extract structural state data
    latest_row = data.iloc[-1]
    latest_price = round(float(latest_row['Close']), 2)
    latest_rsi = round(float(latest_row['RSI']), 2)
    latest_signal = int(latest_row['Signal'])
    
    # Determine Status Display Specs
    if latest_signal == 1:
        status_text = "▲ VALOR BUY TRIGGER"
        status_color = "inverse"
    elif latest_signal == -1:
        status_text = "▼ VALOR SELL TRIGGER"
        status_color = "normal"
    else:
        status_text = "◼ NEUTRAL / HOLD"
        status_color = "off"

    # Display Top Metrics Matrix
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label=f"LAST CAPTURED PRICE ({ticker})", value=f"${latest_price}")
    with m2:
        st.metric(label="VALOR MOMENTUM MATRIX (RSI)", value=f"{latest_rsi}")
    with m3:
        st.subheader("PREDICTIVE STATE VECTOR")
        if latest_signal == 1:
            st.success(status_text)
        elif latest_signal == -1:
            st.error(status_text)
        else:
            st.info(status_text)

    st.markdown("---")

    # ==========================================
    # 5. GRAPHICAL LOGIC DISPLAY (PLOTLY)
    # ==========================================
    st.subheader("Asset Velocity & Moving Windows Tracking")
    
    # Primary Trend Figure
    fig = go.Figure()
    
    # Price Line
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price', line=dict(color='#f8fafc', width=2)))
    # EMAs Lines
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA_Fast'], name='Fast Threshold Line', line=dict(color='#22c55e', width=1.5, dash='dash')))
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA_Slow'], name='Slow Threshold Line', line=dict(color='#ea580c', width=1.5, dash='dash')))
    
    # Superimpose execution execution arrows 
    buy_signals = data[data['Trigger'] == 2]
    sell_signals = data[data['Trigger'] == -2]
    
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers', name='VALOR BUY EXECUTION',
                             marker=dict(symbol='triangle-up', size=12, color='#22c55e', line=dict(width=2, color='white'))))
                             
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers', name='VALOR SELL EXECUTION',
                             marker=dict(symbol='triangle-down', size=12, color='#ef4444', line=dict(width=2, color='white'))))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        margin=dict(l=20, r=20, t=20, b=20),
        height=500,
        xaxis=dict(gridcolor='#334155'),
        yaxis=dict(gridcolor='#334155', title="Value ($)")
    )
    st.plotly_chart(fig, use_container_width=True)

    # Historical Evaluation Data Block Terminal
    with st.expander("VIEW HISTORICAL ENGINE EVALUATION STREAM LOGS"):
        st.dataframe(
            data[['Close', 'EMA_Fast', 'EMA_Slow', 'RSI', 'Signal']].tail(50),
            use_container_width=True
        )
else:
    st.error("Matrix Processing Blocked: Asset Ticker Invalid or Data Window Unreachable.")
