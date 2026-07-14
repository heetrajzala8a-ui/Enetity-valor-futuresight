import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from datetime import datetime

# Institutional System Configuration
st.set_page_config(page_title="ENTITY VALOR FUTURE SIGHT", layout="wide")
st.title("🛡️ ENTITY VALOR FUTURE SIGHT")
st.subheader("Institutional Derivatives Analytics & Level Projection Engine")
st.markdown("---")

# 1. SIDEBAR CONFIGURATION MATRIX
st.sidebar.header("🎯 System Risk Parameters")

asset_class = st.sidebar.selectbox(
    "Select Target Market", 
    ["NSE Stock Futures (India)", "Crypto Perpetual Futures"]
)

current_month = datetime.now().strftime("%b").upper()

if asset_class == "NSE Stock Futures (India)":
    st.sidebar.info(f"Format: Stock + Month + F. Example: SBIN{current_month}F")
    ticker_input = st.sidebar.text_input("Enter NSE Futures Ticker", f"SBIN{current_month}F").strip().upper()
    ticker = f"{ticker_input}.NS"
else:
    st.sidebar.info("Continuous perpetual contract swap data valuation mapping.")
    ticker_input = st.sidebar.text_input("Enter Crypto Pair", "BTC").strip().upper()
    ticker = f"{ticker_input}-USD"

interval = st.sidebar.selectbox("Timeframe Analyzer", ["15m", "1h", "1d"], index=0)

st.sidebar.markdown("---")
st.sidebar.header("💰 Capital Allocation Math")
account_balance = st.sidebar.number_input("Total Trading Capital", value=100000, step=1000)
risk_per_trade = st.sidebar.slider("Max Capital Risk Per Trade (%)", 0.5, 3.0, 1.0, step=0.1)
reward_ratio = st.sidebar.slider("Risk-to-Reward Ratio (1 : X)", 2.0, 4.0, 2.5, step=0.5)

# 2. DATA PIPELINE WRAPPER
@st.cache_data(ttl=15) 
def load_market_data(symbol, timeframe):
    period_map = {"15m": "5d", "1h": "1mo", "1d": "6mo"}
    df = yf.download(symbol, period=period_map[timeframe], interval=timeframe)
    return df

try:
    with st.spinner("Streaming mathematical telemetry feeds..."):
        data = load_market_data(ticker, interval)
    
    if data.empty:
        st.error(f"Symbol verification failure. For NSE Futures, ensure format matches current active month (e.g., SBIN{current_month}F).")
        st.stop()

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col for col in data.columns]

    # 3. MATHEMATICAL ALGORITHM ENGINE
    data['EMA_fast'] = ta.trend.ema_indicator(data['Close'], window=9)
    data['EMA_slow'] = ta.trend.ema_indicator(data['Close'], window=21)
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
    data['ATR'] = ta.volatility.average_true_range(data['High'], data['Low'], data['Close'], window=14)

    latest_row = data.iloc[-1]
    prev_row = data.iloc[-2]
    
    current_price = float(latest_row['Close'])
    rsi_val = float(latest_row['RSI'])
    atr_val = float(latest_row['ATR'])

    bullish_cross = (prev_row['EMA_fast'] <= prev_row['EMA_slow']) and (latest_row['EMA_fast'] > latest_row['EMA_slow'])
    bearish_cross = (prev_row['EMA_fast'] >= prev_row['EMA_slow']) and (latest_row['EMA_fast'] < latest_row['EMA_slow'])

    # 4. SIGNAL FILTERS & EXECUTIONS
    signal = "NEUTRAL / MARKET CONSOLIDATION"
    entry_level = current_price
    stop_loss = 0.0
    target_profit = 0.0
    max_loss_allowed = account_balance * (risk_per_trade / 100)

    if bullish_cross and rsi_val < 65:
        signal = "🚀 LONG ENTRY SETUP (BUY)"
        stop_loss = entry_level - (1.5 * atr_val) 
        target_profit = entry_level + ((entry_level - stop_loss) * reward_ratio)
    elif bearish_cross and rsi_val > 35:
        signal = "🚨 SHORT ENTRY SETUP (SELL)"
        stop_loss = entry_level + (1.5 * atr_val) 
        target_profit = entry_level - ((stop_loss - entry_level) * reward_ratio)

    if stop_loss != 0.0 and entry_level != stop_loss:
        risk_per_unit = abs(entry_level - stop_loss)
        optimal_position_size = max_loss_allowed / risk_per_unit
    else:
        optimal_position_size = 0.0

    # 5. STREAMLIT INTERFACE METRICS
    st.header(f"Live Market Feed: {ticker}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Price", f"₹ {current_price:,.2f}" if ".NS" in ticker else f"$ {current_price:,.2f}")
    c2.metric("RSI Momentum", f"{rsi_val:.1f}")
    c3.metric("Volatility Index (ATR)", f"{atr_val:.2f}")
    
    if "LONG" in signal:
        st.success(signal)
    elif "SHORT" in signal:
        st.error(signal)
    else:
        st.info(signal)

    st.markdown("---")

    # Math-Based Execution Levels Section
    st.subheader("🎯 Future Sight Projections")
    if signal != "NEUTRAL / MARKET CONSOLIDATION":
        l_col1, l_col2, l_col3, l_col4 = st.columns(4)
        l_col1.markdown(f"**Execution Entry Level:** {entry_level:,.2f}")
        l_col2.markdown(f"**🔴 Volatility Stop Loss (SL):** {stop_loss:,.2f}")
        l_col3.markdown(f"**🟢 Target Take Profit (TP):** {target_profit:,.2f}")
        
        currency_symbol = "₹" if ".NS" in ticker else "$"
        l_col4.markdown(f"**📦 Strategic Allocation Unit Size:** {optimal_position_size:.2f} Units (Max Trade Risk: {currency_symbol}{max_loss_allowed:,.2f})")
    else:
        st.warning("⏳ Market Consolidation. No high-probability crossover detected. Stand down and protect your capital base.")

    # 6. CHART VISUALIZATION
    st.markdown("---")
    st.subheader("📈 Interactive Mathematical Projection Layout")
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price Matrix"
    ))
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA_fast'], line=dict(color='#FFA500', width=1.5), name="9 EMA (Fast)"))
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA_slow'], line=dict(color='#00FFFF', width=1.5), name="21 EMA (Slow)"))
    
    if signal != "NEUTRAL / MARKET CONSOLIDATION":
        fig.add_hline(y=entry_level, line_dash="dash", line_color="blue", annotation_text="Sight Entry")
        fig.add_hline(y=stop_loss, line_dash="dash", line_color="red", annotation_text="Sight SL Zone")
        fig.add_hline(y=target_profit, line_dash="dash", line_color="green", annotation_text="Sight TP Target")

    fig.update_layout(xaxis_rangeslider_visible=False, height=550, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Live Engine Core Sync Loop Exception:
