import pandas as pd
import time

def entry(intraday_df, daily_df, debug=False, mode='backtest'):
    """
    Returns Entry markers based on EMA reclaim.
    Testing found that for this strategy, bounces tend to result
    in negative return expectancy, and subsequently are particularly avoided.
    """
    
    if intraday_df.empty or daily_df.empty:
        if debug: print('empty dataframes')
        return None, None, None

    if mode == 'backtest':
        today_date = intraday_df.index[0].normalize()
    else:  
        today_date = intraday_df.index[-1].normalize()

    intraday_df = intraday_df[intraday_df.index.normalize() == today_date].copy()

    if intraday_df.empty:
        if debug:
            print(f'No intraday data for {today_date}')
            return None, None, None

    entry_day = intraday_df.index[0].normalize()

    if entry_day not in daily_df.index:
        if debug: print('entry_day not in daily_df', entry_day)
        return None, None, None

    daily_ema9 = daily_df.loc[entry_day, 'EMA_9']

    if debug:
        print('Entry day:', entry_day)
        print('Daily EMA9:', daily_ema9)
        print('Intraday Row Count:', len(intraday_df))
        print(intraday_df[['Low','Close','ATR_14']].head())
        print(daily_df[['Low','Close','EMA_9']].head())

    if pd.isna(daily_ema9) or intraday_df[['Low','Close','ATR_14']].isnull().values.any():
        if debug: print('NaNs in Ema or intraday ATR or Prices')    
        return None, None, None

    ema_break = False

    for time, row in intraday_df.iterrows():
        low = row['Low']
        close = row['Close']
        atr = row['ATR_14']

        cushion = 0.2 * atr

        ema_touch = abs(low - daily_ema9) <= cushion

        if debug:
            print(time)
            print('Low', low, 'Close:', close, 'ATR:', atr)
            print('EMA9:', daily_ema9)
            print('Cushion:', cushion)
            print('ema_touch:', ema_touch)
            print('ema broken? (it shouldnt be yet):', ema_break)

        if not ema_break:
            if ema_touch and close > daily_ema9:
                if debug: print('Entry triggered - bounce')
                return None, None, None
            elif close < daily_ema9:
                if debug: print('Ema broken, watching for reclaim...')
                ema_break = True

        else:
            if close >= daily_ema9:
                if debug: print('Entry triggered, reclaimed')
                return time, close, 'reclaim'

    if debug: print('No entry found')
    return None, None, None

def exits(entry_time, entry_price, intraday_df, daily_df, max_hold=8, debug=False):
    """
    Returns Exit markers given a breach of stop loss, a hold period
    greater than max_hold, or take profit.
    """

    if intraday_df.empty or daily_df.empty or entry_time not in intraday_df.index:
        return None, None, None

    entry_loc = intraday_df.index.get_loc(entry_time)
    entry_day = entry_time.normalize()
    max_exit_day = (entry_day + pd.offsets.BDay(max_hold))

    for time in intraday_df.index[entry_loc + 1:]:
        row = intraday_df.loc[time]
        close = row['Close']
        atr = row['ATR_14']

        candle_day = time.normalize()

        if candle_day not in daily_df.index:
            continue

        daily_ema9 = daily_df.loc[candle_day, 'EMA_9']

        stop_level = daily_ema9 - (atr * 1.5)
        if close < stop_level:
            return time, close, 'stop'

        tp_level = entry_price * (1 + 0.04)
        if close >= tp_level:
            return time, close, 'take_profit'

        final_candles = intraday_df[intraday_df.index.normalize() == max_exit_day.normalize()]
        if not final_candles.empty and time == final_candles.index[-1]:
            return time, close, 'max_hold_exit'
        elif debug == True and final_candles.empty:
            print(f'Final_candles are empty for {max_exit_day}')
        

    last_time = intraday_df.index[-1]
    return last_time, intraday_df.loc[last_time, 'Close'], 'max_hold_exit'
