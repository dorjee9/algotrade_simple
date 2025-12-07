import yfinance as yf         # To download historical stock data
import pandas as pd           # For handling tables (dataframes)
import numpy as np            # For math operations like floor or arrays
import matplotlib.pyplot as plt  # To plot charts


# PARAMETERS
symbol = "AAPL"       # Stock ticker
start = "2022-01-01"  # Start date for historical data
end = "2024-12-31"    # End date
fast_window = 20      # Fast moving average period
slow_window = 50      # Slow moving average period
initial_cash = 100000 # Starting money
fee_per_trade = 1.0   # Flat trading fee
slippage_pct = 0.0005 # Extra cost due to price changes while trading


# 1. DOWNLOAD DATA (avoid FutureWarning)
df = yf.download(symbol, start=start, end=end, progress=False, auto_adjust=False)

# 2. INDICATORS
df["fast_sma"] = df["Close"].rolling(fast_window).mean()
df["slow_sma"] = df["Close"].rolling(slow_window).mean()

# 3. SIGNAL (shift for next-day execution)
df["signal"] = np.where(df["fast_sma"] > df["slow_sma"], 1, 0)
df["signal"] = df["signal"].shift(1).fillna(0).astype(int)

# 4. BACKTEST LOOP
cash = initial_cash
position = 0
portfolio_values = []
positions = []

for idx in range(len(df)):
    sig = int(df["signal"].iloc[idx])       # ✅ Force scalar safely
    price = float(df["Open"].iloc[idx])     # ✅ Force scalar safely

    # BUY
    if sig == 1 and position == 0:
        shares = np.floor(cash / (price * (1 + slippage_pct)))
        if shares > 0:
            cost = shares * price * (1 + slippage_pct) + fee_per_trade
            cash -= cost
            position = shares

    # SELL
    elif sig == 0 and position > 0:
        proceeds = position * price * (1 - slippage_pct) - fee_per_trade
        cash += proceeds
        position = 0

    # Track portfolio value
    pv = cash + position * float(df["Close"].iloc[idx])
    portfolio_values.append(pv)
    positions.append(position)

df["portfolio_value"] = portfolio_values
df["position"] = positions

# 5. PERFORMANCE
ending_value = df["portfolio_value"].iloc[-1]
cumulative_return = (ending_value / initial_cash - 1) * 100

print("Ending Value:", round(ending_value, 2))
print("Cumulative Return:", round(cumulative_return, 2), "%")

# 6. PLOT
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["portfolio_value"], label="Portfolio Value")
plt.title("SMA Crossover Backtest")
plt.legend()
plt.grid(True)
plt.show()
