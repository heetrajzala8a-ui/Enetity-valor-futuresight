import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ta
import yfinance as yf

# ==========================================
# 1. CONFIGURATION & DATA ENGINE
# ==========================================
class ValorFutureSightEngine:
    def __init__(self, ticker: str, start_date: str, end_date: str):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.data = None

    def fetch_market_data(self):
        """Fetches historical market data using yfinance."""
        print(f"[⚙️] Fetching data for {self.ticker}...")
        try:
            df = yf.download(self.ticker, start=self.start_date, end=self.end_date)
            if df.empty:
                raise ValueError("No data retrieved. Check the ticker symbol or dates.")
            
            # Clean up column multi-index if present in newer yfinance versions
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            self.data = df.dropna()
            print(f"[✓] Successfully loaded {len(self.data)} rows of data.")
            return self.data
        except Exception as e:
            print(f"[❌] Error fetching data: {e}")
            return None

# ==========================================
# 2. QUANTITATIVE & PREDICTIVE INDICATORS
# ==========================================
    def compute_indicators(self):
        """Calculates momentum and trend indicators for forward analysis."""
        print("[⚙️] Computing indicators (EMA, RSI, MACD)...")
        
        # Trend Indicators
        self.data['EMA_Fast'] = ta.trend.ema_indicator(self.data['Close'], window=12)
        self.data['EMA_Slow'] = ta.trend.ema_indicator(self.data['Close'], window=26)
        
        # Momentum Indicators
        self.data['RSI'] = ta.momentum.rsi(self.data['Close'], window=14)
        
        # MACD
        self.data['MACD'] = ta.trend.macd(self.data['Close'])
        self.data['MACD_Signal'] = ta.trend.macd_signal(self.data['Close'])
        
        self.data.dropna(inplace=True)
        return self.data

# ==========================================
# 3. VALOR SIGNAL GENERATION MATRIX
# ==========================================
    def generate_signals(self):
        """Executes rules engine to produce clear Buy/Sell triggers."""
        print("[⚙️] Generating predictive trading signals...")
        
        self.data['Signal'] = 0  # 0 = Hold, 1 = Buy, -1 = Sell
        
        # Logic Matrix
        # BUY: Fast EMA crosses above Slow EMA AND RSI is not overbought (< 65)
        buy_condition = (self.data['EMA_Fast'] > self.data['EMA_Slow']) & (self.data['RSI'] < 65)
        
        # SELL: Fast EMA crosses below Slow EMA OR RSI is overbought (> 75)
        sell_condition = (self.data['EMA_Fast'] < self.data['EMA_Slow']) | (self.data['RSI'] > 75)
        
        self.data.loc[buy_condition, 'Signal'] = 1
        self.data.loc[sell_condition, 'Signal'] = -1
        
        # Find execution steps (where signal changes)
        self.data['Position'] = self.data['Signal'].diff()
        return self.data

# ==========================================
# 4. VISUALIZATION DASHBOARD
# ==========================================
    def plot_dashboard(self):
        """Renders the performance and signal tracking chart."""
        print("[⚙️] Rendering visual analytics dashboard...")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        
        # Top Plot: Price and EMAs
        ax1.plot(self.data.index, self.data['Close'], label='Close Price', color='black', alpha=0.6)
        ax1.plot(self.data.index, self.data['EMA_Fast'], label='12-Period Fast EMA', color='blue', linestyle='--')
        ax1.plot(self.data.index, self.data['EMA_Slow'], label='26-Period Slow EMA', color='orange', linestyle='--')
        
        # Plot Buy Triggers
        ax1.plot(self.data[self.data['Position'] == 2].index, 
                 self.data['Close'][self.data['Position'] == 2], 
                 '^', markersize=10, color='green', label='VALOR BUY SIGNAL', lw=0)
        
        # Plot Sell Triggers
        ax1.plot(self.data[self.data['Position'] == -2].index, 
                 self.data['Close'][self.data['Position'] == -2], 
                 'v', markersize=10, color='red', label='VALOR SELL SIGNAL', lw=0)
        
        ax1.set_title(f"{self.ticker} - Future Sight Trading Dashboard", fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # Bottom Plot: RSI Momentum Matrix
        ax2.plot(self.data.index, self.data['RSI'], label='RSI (14)', color='purple')
        ax2.axhline(70, color='red', linestyle=':', alpha=0.7, label='Overbought (70)')
        ax2.axhline(30, color='green', linestyle=':', alpha=0.7, label='Oversold (30)')
        ax2.set_ylabel('RSI Range', fontsize=12)
        ax2.set_xlabel('Timeline', fontsize=12)
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

# ==========================================
# 5. MAIN EXECUTION PIPELINE
# ==========================================
if __name__ == "__main__":
    # Define Ticker (e.g., Apple stock 'AAPL' or E-mini S&P 500 Futures 'ES=F')
    TARGET_ASSET = "AAPL" 
    
    # Analyze the last 365 days of data
    end_date = datetime.date.today().strftime('%Y-%m-%d')
    start_date = (datetime.date.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    
    # Initialize the App Engine
    app = ValorFutureSightEngine(ticker=TARGET_ASSET, start_date=start_date, end_date=end_date)
    
    # Run Pipeline
    if app.fetch_market_data() is not None:
        app.compute_indicators()
        processed_data = app.generate_signals()
        
        # Output the most recent evaluations to the console
        print("\n=== RECENT TRADING SIGNALS SUMMARY ===")
        print(processed_data[['Close', 'EMA_Fast', 'EMA_Slow', 'RSI', 'Signal']].tail(10))
        print("=======================================\n")
        
        # Show Graphical Interface
        app.plot_dashboard()
