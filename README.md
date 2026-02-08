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
| **Total Trades** | 289 | 94 |
| **Win Rate** | 33.56% | 34.04% |
| **Avg Win %** | 3.20% | 3.80% |
| **Profit Factor** | 1.61 | 1.52 |
| **Expectancy (Per Trade)** | 0.32% | **0.49%** |
| **Est. Annual Return** | 31.80% | **49.53%** |
| **Annualized Sharpe Ratio** | 1.09 | **1.69** |



---

### Tactical Observations

* **Positive Skew:** A key to the strategy is prioritizing quality wins. Consequently, the strategy maintains a 'Fat Tail' distribution. While the win rate sits at ~34%, the average winning trade is significantly larger than the average loss, ensuring the equity curve remains upward-sloping. Notice that this is ensured by entry near EMA 9, and therefore an entry near the Stop.
* **Momentum Efficiency:** The jump in **Sharpe Ratio (1.69)** during the 2025–2026 period suggests that the "Stacked EMA" filter is highly effective at capturing alpha in the current high-volatility environment, although the strategy maintains outperformance compared with SPY over the same period.
* **Risk-Adjusted Outperformance:** Clearing a Sharpe of 1.0 being the industry benchmark for a professional-grade strategy, I am more than pleased with the results. Reaching 1.69 indicates that the strategy provides high returns relative to the risk (volatility) taken. The longer term 1.09 indicates a more consistent return over a more steady growth period. This insinuates that the strategy in fact benefitted from the V-shaped dip and recovery of early to mid 2025.

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
