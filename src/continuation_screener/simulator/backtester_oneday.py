import pandas as pd
import time
from continuation_screener.simulator.entry_exit import entry, exits
from continuation_screener.data.intraday_bt import intraday_bt, daily_bt

def backtest_ticker(ticker, eval_date, debug=False):
    """
    Simulates Trade for single ticker based on entry/exit markers.
    """

    day_of = pd.to_datetime(eval_date)

    daily_start = day_of - pd.Timedelta(days=60)
    daily_end = day_of + pd.Timedelta(days=11)

    intraday_start = day_of
    intraday_end = day_of + pd.Timedelta(days=11)

    daily_df = daily_bt(ticker, daily_start, daily_end)
    intraday_df = intraday_bt(ticker, intraday_start, intraday_end)

    if daily_df is None or intraday_df is None:
        if debug == True:
            print(f'{ticker} chart data failed to download.')
        return None

    entry_time, entry_price, entry_method = entry(intraday_df, daily_df)
    if entry_time is None:
        if debug == True:
            print(f'{ticker}, no valid entry.')
        return None

    exit_time, exit_price, exit_method = exits(
        entry_time,
        entry_price,
        intraday_df,
        daily_df,
        debug=False
        )

    return {
        'Ticker' : ticker,
        'Entry Time' : entry_time,
        'Entry Price' : round(float(entry_price), 2),
        'Entry Method' : entry_method,
        'Exit Time' : exit_time,
        'Exit Price' : round(float(exit_price), 2),
        'Exit Type' : exit_method,
        'Net' : round(float(exit_price - entry_price), 2), 
        }
        
    
        
        
