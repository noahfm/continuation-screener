import yfinance as yf
import logging
import time
import random
import pandas as pd
from tqdm import tqdm

logging.getLogger('yfinance').setLevel(logging.CRITICAL)
logging.getLogger('yfinance.shared').setLevel(logging.CRITICAL)

def complete(df, min_rows=15):
    """
    Checks if dataframe has enough historical data and no missing values.
    """
    
    return (df is not None and
            not df.empty and
            not df.isna().any().any() and
            len(df) >= min_rows)


def get_daily_data(tickers, as_of_date, batch_size=500, retries=3, bt_mode=False):
    """
    Downloads historical daily data for a given list of tickers.
    Uses batching and retry logic to bypass rate limiting issues.
    """
    
    as_of_date = pd.to_datetime(as_of_date).normalize()

    lookback = 350

    start_date = as_of_date - pd.Timedelta(days=lookback)

    complete_data = []
    incomplete_data = []

    delay = random.random()
    retry_delay = delay + 2

    yf_tickers = [t.replace('.', '-') for t in tickers]

    pbar = tqdm(total=len(yf_tickers), desc='Downloading Russell 3k Chart Data...')

    for i in range(0, len(yf_tickers), batch_size):
        
        batch = yf_tickers[i:i + batch_size]
        
        data = yf.download(
            batch,
            start=start_date,
            end=as_of_date + pd.Timedelta(days=1),
            interval='1d',
            progress=False,
            threads=True,
            auto_adjust=False,
            back_adjust=False
            )

        for ticker in batch:
            
            pbar.update(1)
            
            try:
                ticker_df = data.xs(ticker, level=1, axis=1)
            except Exception:
                incomplete_data.append(ticker)
                continue

            if complete(ticker_df):
                ticker_df.columns = pd.MultiIndex.from_product(
                    [ticker_df.columns, [ticker]]
                )
                complete_data.append(ticker_df)
            else:
                incomplete_data.append(ticker)

        time.sleep(delay)
    
    pbar.close()

    print('Retrying failed tickers...')

    retry_batch_count = 50
    
    for i in range(retries):
        
        if not incomplete_data:
            break

        retrybatch = incomplete_data[:retry_batch_count]
        incomplete_data = incomplete_data[retry_batch_count:]

        retrydata = yf.download(
            retrybatch,
            start=start_date,
            end=as_of_date + pd.Timedelta(days=1),
            interval='1d',
            progress=False,
            threads=False,
            auto_adjust=False,
            back_adjust=False
        )

        if retrydata is None or retrydata.empty:
            incomplete_data.extend(retrybatch)
            time.sleep(retry_delay)
            continue

        for ticker in retrybatch:

            try:
                ticker_df = retrydata.xs(ticker, level=1, axis=1)
            except Exception:
                incomplete_data.append(ticker)
                continue

            if complete(ticker_df):
                ticker_df.columns = pd.MultiIndex.from_product(
                    [ticker_df.columns, [ticker]]
                )
                complete_data.append(ticker_df)
            else:
                incomplete_data.append(ticker)

        time.sleep(retry_delay)
        retry_delay *= 1.5

    if incomplete_data:
        print(f'{len(incomplete_data)} tickers failed after retries.')

    return pd.concat(complete_data, axis=1)
