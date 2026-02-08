import pandas as pd
import yfinance as yf
from tqdm import tqdm

from continuation_screener.utils.get_iwv import get_iwv_tickers
from continuation_screener.data.dailydata import get_daily_data
from continuation_screener.trend_screener import stacked_emas, balanced_atr, balanced_rsi, ema_bounce_score, avg_volume

def run_screener_bt(start_date, end_date):
    """
    Simulates the screening process over a historical date range.
    Generates a list of tickers to be processed by the simulator.
    """

    spy = yf.download('SPY', period='300d', interval='1d', progress=False)
    spy['SMA200'] = spy['Close'].rolling(window=200).mean()

    current_spy = spy['Close'].iloc[-1].item()
    current_sma = spy['SMA200'].iloc[-1].item()

    if current_spy < current_sma:
        print('Market is not suitable for continuation trading, buy some gold.')
        return pd.DataFrame()

    window = 300

    start_day = pd.to_datetime(start_date).normalize()
    end_day = pd.to_datetime(end_date).normalize()

    tickers = get_iwv_tickers()
    
    raw_data_full = get_daily_data(tickers, end_day, bt_mode=True)

    available = raw_data_full.columns.get_level_values(1).unique()
    
    section = raw_data_full.xs(available[0], axis=1, level=1)
    eval_days = section.loc[
        (section.index >= start_day) & (section.index <= end_day)
        ].index.normalize()
    
    passes = []   
    print('Rolling-window ticker evaluation...')

    for ticker in tqdm(available, desc='Precomputing...'):
        df = raw_data_full.xs(ticker, axis=1, level=1).copy()
        df.index = df.index.normalize()

        for day in eval_days:
            df_slice = df.loc[df.index <= day].tail(window).copy()

            if len(df_slice) < 210 or df_slice.isna().any().any():
                continue

            if avg_volume(df_slice) is None:
                continue
            if stacked_emas(df_slice) is None:
                continue
            if balanced_atr(df_slice) is None:
                continue
            if balanced_rsi(df_slice) is None:
                continue

            score = ema_bounce_score(df_slice)
            if score is None:
                continue

            passes.append({
                'date': day,
                'Ticker': ticker,
                '# of EMA BOUNCES': score,
            })

    if not passes:
        return None

    df_final = pd.DataFrame(passes)
    df_final = df_final.sort_values(
        ['date', '# of EMA BOUNCES'],
        ascending = [True,False]
    ).set_index(['date', 'Ticker'])

    return df_final


        
