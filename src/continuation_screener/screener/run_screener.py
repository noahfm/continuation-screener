import pandas as pd
import numpy as np
import yfinance as yf
import pytz
from tqdm import tqdm
from datetime import datetime, timedelta

from continuation_screener.utils.get_iwv import get_iwv_tickers
from continuation_screener.data.dailydata import get_daily_data
from continuation_screener.trend_screener import stacked_emas, balanced_atr, balanced_rsi, ema_bounce_score, avg_volume

def run_screener(as_of_date=None):
    """
    Macro filter -> Data fetching -> Strategy filters.
    Returns DataFrame of passed tickers.
    """
    
    spy = yf.download('SPY', period='300d', interval='1d', progress=False)
    spy['SMA200'] = spy['Close'].rolling(window=200).mean()

    current_spy = spy['Close'].iloc[-1].item()
    current_sma = spy['SMA200'].iloc[-1].item()

    if current_spy < current_sma:
        print('Market is not suitable for continuation trading, buy some gold.')
        return pd.DataFrame()

    if as_of_date is None:
        now_ny = datetime.now(pytz.timezone('US/Eastern'))
                              
        if now_ny.hour < 16:
            as_of_date = (pd.Timestamp(now_ny.date()) - pd.offsets.BusinessDay(1)).normalize()
        else:
            as_of_date = pd.Timestamp(now_ny.date()).normalize()

    else:
        as_of_date = pd.to_datetime(as_of_date).normalize()

    tickers = get_iwv_tickers()
    
    raw_data = get_daily_data(tickers, as_of_date=as_of_date)

    available = raw_data.columns.get_level_values(1).unique()

    strong = []

    fail_nan = 0
    fail_vol = 0
    fail_ema = 0
    fail_atr = 0
    fail_rsi = 0

    max_retries = 5
    retrydelay = 0.5

    for ticker in tqdm(available, desc='Screening tickers...'):
        
        df = raw_data.xs(ticker, axis=1, level=1).copy()

        if int(df.shape[0]) < 210:
            continue

        df = df.loc[df.index <= as_of_date].copy()
        if df.empty or df.isna().any().any():
            fail_nan += 1
            continue

        if df.isna().any().any():
            fail_nan += 1
            continue

        df = avg_volume(df)
        if df is None:
            fail_vol += 1
            continue

        df = stacked_emas(df)
        if df is None:
            fail_ema += 1
            continue

        df = balanced_atr(df)
        if df is None:
            fail_atr += 1
            continue

        df = balanced_rsi(df)
        if df is None:
            fail_rsi += 1
            continue

        score = ema_bounce_score(df)
        if score is None:
            continue

        strong.append({
            'Ticker': ticker,
            '# of EMA BOUNCES': score
        })

    final_df = pd.DataFrame(strong)

    print('~'*30)
    print("TOTAL:", len(tickers))
    print("FAIL NAN TEST:", fail_nan)
    print("FAIL VOL TEST:", fail_vol)
    print("FAIL EMA TEST:", fail_ema)
    print("FAIL ATR TEST:", fail_atr)
    print("FAIL RSI TEST:", fail_rsi)
    print('~'*30)

    if final_df.empty:
        print("No tickers met criteria.")
        return final_df

    if "# of EMA BOUNCES" in final_df.columns:
        final_df = final_df.sort_values("# of EMA BOUNCES", ascending=False).set_index('Ticker')

    return final_df

if __name__ == '__main__':
    final_df = run_screener()
    print(final_df)

    
    
