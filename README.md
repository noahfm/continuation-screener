# Russell 3000 Trend Continuation Screener

A quantitative toolset for identifying high-probability trend continuation setups within the Russell 3000 universe. The system automates ticker selection using multi-level technical filters to provide daily **strong** candidates. It also includes backtesting capabilities using both intraday (15m) and daily data.

## Logic
The screener focuses on **quality over quantity**, seeking strong trends and entry signals based on short-term mean reversions.

## Macro Filter
In order to avoid applying the method in incompatible markets, SPY's current price is compared against its 200-day SMA, effectively halting trading during heavy bear markets to protect capital.

## Stacked EMAs
A primary trend is only confirmed when the Exponential Moving Averages are perfectly aligned in a “stacked” formation:

$$
EMA_{9} > EMA_{20} > EMA_{50} > EMA_{200}
$$

## Momentum and Volatility
- **RSI (14):** Filters for assets with bullish momentum that are not yet overextended.
- **ATR (14):** Uses Average True Range to ensure the asset has sufficient volatility for trading, while filtering out hyper-volatile outliers.

## Key Features
- **Dynamic Universe Management:** Scrapes iShares Russell 3000 (IWV) holdings directly to ensure the ticker candidate list is always up to date.
- **Data Pipeline:** Implements batch-downloading with exponential backoff and retry logic to overcome `yfinance` rate-limiting.
- **Backtest Simulator:** A dual-engine backtester identifies entry and exit signals on both daily and 15m timeframes, returning a summary of historical trades.
- **Vectorized Indicators:** All technical calculations (EMA, RSI, ATR) are implemented using vectorized Pandas operations for maximum performance.

## A Note on Backtesting **IMPORTANT**
As this project, or rather the part of the project being released to GitHub uses yfinance, there are inherent limits to data downloads. Specifically, 15m data has a short period of time from which candle data can be downloaded. Therefore using the integrated backtester script will always result in a limited lookback (approximately 35 trading days), which is unavoidable using yfinance.

Separately, I have build very similar scripts, retaining all data screening methods and trading criteria, which uses **Massive's API**. Running longer tests, I have saved results in **backtest_results**. Please take a look to see the quality that this screener produces.

## Performance Analysis

The strategy was backtested across the Russell 3000 universe using a dual-timeframe (Daily/15m) simulation. The results demonstrate a strong edge in trend-following, with significant out performance during the recent market regime.

### Strategy Metrics Comparison

| Metric | 2023 - 2026 (Full) | 2025 - 2026 (Recent) |
| :--- | :--- | :--- |
| **Total Trades** | 116 | 39 |
| **Win Rate** | 37.07% | 38.46% |
| **Avg Win %** | 4.03% | 3.65% |
| **Profit Factor** | 2.78 | 1.61 |
| **Expectancy (Per Trade)** | **0.92%** | 0.67% |
| **Est. Annual Return** | **36.22%** | 27.72% |
| **Annualized Sharpe Ratio** | **1.91** | 1.32 |



---

### Tactical Observations

* **Positive Skew:** The strategy maintains an elite 4.4-to-1 Reward-to-Risk ratio. By entering on the EMA reclaim and capping losses at $\approx 1\%$, the average win (4.03%) dwarfing the average loss (0.91%) ensures a robust, upward-sloping equity curve even with an approximately **37% win rate**.
* **Momentum Efficiency:** A 1.91 Sharpe Ratio over the verified 3-year backtest significantly exceeds the professional benchmark of 1.0. This suggests the "Stacked EMA" filter and Macro SPY filter successfully side-step choppy regimes, providing high returns relative to the volatility taken.
* **Risk-Adjusted Outperformance:** Clearing a Sharpe of 1.0 as the industry benchmark for a professional-grade strategy, the verified results are exceptional. Reaching a Sharpe of 1.91 indicates that the strategy provides high returns relative to the volatility taken. This long-term consistency, paired with a Profit Factor of 2.78, proves the strategy is not just lucky but structurally sound. It successfully capitalized on the sustained momentum of 2023 and the V-shaped recovery periods of 2025, maintaining an upward-sloping equity curve across multiple market regimes.
### Audit Logs
The full trade-by-trade execution logs for these periods are available for review in the root directory:
* `backtest_trades_2023_to_2026.csv`
* `backtest_trades_2025_to_2026.csv`

## Structure
- `src/continuation_screener/data/`: Technical indicator logic and data fetching wrappers.
- `src/continuation_screener/screener/`: The core scanning engine for daily use and historical backtesting.
- `src/continuation_screener/simulator/`: Tools for intraday execution simulation and trade tracking.
- `src/continuation_screener/utils/`: Ticker scraping and other general helper functions.

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/noahfm/continuation-screener.git
```

### 2. Install requirements
```bash
pip install -r requirements.txt
```

### 3. Run the Screener
```python
from continuation_screener.screener.run_screener import run_screener

# Execute the scan
candidates = run_screener()
print(candidates)
```

## Testing and Quality Assurance
This project includes a small suite of unit tests to verify strategy math and filter behavior. Testing is critical to prevent silent failures.

### Key Test Coverage
- **Indicator Accuracy:** Validates that EMAs, RSI, and ATR calculate correctly across various trend regimes.
- **Filter Logic:** Ensures the system correctly rejects low-liquidity stocks (Volume < 1M) and overextended momentum (RSI > 78).
- **Trend Stability:** Verifies that the stacked EMA logic handles indicator warm-up periods (500+ days) for the 200 EMA.
- **Edge Case Resilience:** Confirms the code handles empty DataFrames and delisted tickers without crashing.

### Running Tests
To run the full suite of indicator and screening tests from the project root:
```bash
python -m unittest discover tests
```

#### Disclaimer
This software is for educational and demonstrational purposes only. Past performance is not indicative of future results. Trading involves significant risk of capital loss.
