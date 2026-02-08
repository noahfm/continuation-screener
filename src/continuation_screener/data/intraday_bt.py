import yfinance as yf
import pandas as pd
import time
from continuation_screener.data.indicators import add_emas, add_atr

def intraday_bt(ticker, start, end, interval='15m', max_retries=2):
    """
    Fetches Intraday, 15m candles for trade execution simulation.
    Preloads 5 days of data to ensure ATR is stable.
    """

    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    preload_start = start - pd.Timedelta(days=5)
    
    attempt = 0
    while attempt <= max_retries:
        df = yf.download(
            ticker,
            start=preload_start,
            end=end,
            interval=interval,
            auto_adjust=False,
            progress=False
            )

        if not df.empty and not df.isnull().values.any():

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel('Ticker')
                
            df = df[['Open','High','Low','Close']].copy()
            df.sort_index(inplace=True)

            df.index = df.index.tz_localize(None)

            df = add_atr(df, period=14)

            df = df.loc[df.index >= start]
            
            return df

        attempt += 1
        time.sleep(0.2 + (0.5 * attempt))

    print(f'{ticker} 15m data failed to download after 3 attempts.')
    return None

def daily_bt(ticker, start, end, max_retries=2, interval='1d'):
    """
    Fetches Daily data for trade execution simulation.
    """

    start = pd.to_datetime(start)
    end = pd.to_datetime(end) + pd.Timedelta(days=1)

    attempt = 0
    while attempt <= max_retries:
        df = yf.download(
            ticker,
            start=start,
            end=end,
            interval=interval,
            auto_adjust=False,
            progress=False
            )

        if not df.empty and not df.isnull().values.any():

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
                
            df = df[['Open','High','Low','Close','Volume']].copy()
            df.sort_index(inplace=True)

            df = add_emas(df)
            df.index = df.index.tz_localize(None)
            df.index = df.index.normalize()

            if isinstance(df.index, pd.MultiIndex):
                df.index = df.index.droplevel('Ticker')
                

            return df

        attempt += 1
        time.sleep(0.5 + 0.5 * attempt)

    print(f'{ticker} daily data failed to download after 3 attempts.')
    return None


        
