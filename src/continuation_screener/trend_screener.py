import pandas as pd
from continuation_screener.data.indicators import add_emas, add_atr, add_rsi

def stacked_emas(df, period=7, slope_thresh=0.012, dist_thresh=0.75, depth_thresh=-0.8, debug=False, bt=False):
    """
    Checks for 'Stacked EMA's' trend: Price > 200, EMAs 9 > 20 > 50,
    price respecting the 9 ema within ATR bounds.
    """

    if df is None or df.empty:
        if debug:
            print('stacked_emas: df is None or empty')
        return None if not bt else (df, pd.Series(True, index=[]))
    
    df = add_emas(df)
    df = add_atr(df)

    fail_marker = pd.Series(False, index=df.index)

    if len(df) < 210:
        if debug:
            print('stacked_emas: not enough rows', len(df))
        return None if not bt else (df, fail_marker)
    
    last = df.tail(period).copy()

    last14 = df.tail(14).copy()

    macro = last['Close'].iloc[-1] > last['EMA_200'].iloc[-1]
    
    slopequal = True
    ema_slope = (last14['EMA_9'].iloc[-1] - last14['EMA_9'].iloc[0]) / last14['EMA_9'].iloc[0]
    if ema_slope < slope_thresh:
        slopequal = False

    ema_stacked = (
        (last14['EMA_9'] > last14['EMA_20']) &
        (last14['EMA_20'] > last14['EMA_50'])
    ).all()

    dist_bool = True
    ema9_distance = ((last['Close'] - last['EMA_9']) / last['ATR_14']).iloc[-1]
    if ema9_distance > dist_thresh:
        dist_bool = False

    emarespectbool = True
    ema_respect = (last14['Close'] > last14['EMA_9']).mean()
    if ema_respect < (14/14):
        emarespectbool = False

    depthbool = True
    depth = ((last14['Low'] - last14['EMA_9']) / last14['ATR_14']).min()
    if depth < depth_thresh:
        depthbool = False

    passes = ema_stacked and slopequal and emarespectbool and depthbool and dist_bool and macro

    if bt:
        fail_marker[:] = not passes
        return df, fail_marker
    return df if passes else None

def balanced_atr(df, period=14, low_atr=0.009, high_atr=0.047, bt=False):
    """
    Filters stocks based on a specified ATR percentage range.
    """
    
    if df is None or df.empty:
        return None if not bt else (df, pd.Series(True, index=[]))
    
    if len(df) < period:
        return None if not bt else (df, pd.Series(True, index=[]))

    if 'ATR_14' not in df.columns:
        df = add_atr(df)

    last = df.tail(period).copy()
    
    last['ATR_pct'] = last['ATR_14'] / last['Close']

    atr_avg = last['ATR_pct'].tail(7).mean()

    passes = (atr_avg >= low_atr) and (atr_avg <= high_atr)
    
    if bt:
        fail_marker = pd.Series(not passes, index=df.index)
        return df, fail_marker
    else:
        return df if passes else None

def balanced_rsi(df, period=14, low_rsi=50, high_rsi=78, debug=False, bt=False):
    """
    Filters based on relative strength.
    """


    if df is None or df.empty:
        return None if not bt else (df, pd.Series(True, index=[]))

    df = add_rsi(df)
    if len(df) < period:
        return None if not bt else (df, pd.Series(True, index=df.index))

    last = df.tail(period).copy()

    rsi_avg = last['RSI_14'].tail(7).mean()

    if debug:
        print("----- balanced_rsi debug -----")
        print(last[['Close', 'RSI_14']])
        print("5-day average RSI:", rsi_avg)
        print("----------------------------")

    passes = (rsi_avg >= low_rsi) and (rsi_avg <= high_rsi)

    if bt:
        fail_marker = pd.Series(not passes, index=df.index)
        return df, fail_marker
    else:
        return df if passes else None

def ema_bounce_score(df, period=14, cushion=0.005, bt=False):
    """
    Returns score per EMA-9 'Bounce', Scoring based on EMA-9 Respect.
    """

    if df is None or df.empty or len(df) < period:
        return None if not bt else (df, pd.Series(True, index=df.index))

    last = df.tail(period)
    
    touch_bounce = (
        (last['Low'] >= last['EMA_9'] * (1 - cushion)) &
        (last['Low'] <= last['EMA_9'] * (1 + cushion)) &
        (last['Close'] > last['EMA_9']) &
        (last['Close'] > last['Open'])
        )
    
    scorecomp = touch_bounce.iloc[:-2].sum()
    passes = int(scorecomp) >= 2

    if bt:
        fail_marker = pd.Series(not passes, index=df.index)
        return df, fail_marker
    else:
        return int(scorecomp) if passes else None
    
def avg_volume(df, min_avg_vol=1000000, min_price=20.00, bt=False):
    """
    Ensuring sufficient liquidity and minimum price floor.
    """

    if df is None or df.empty:
        return None if not bt else (df, pd.Series(True, index=[]))

    current_p = df['Close'].iloc[-1]
    price_pass = current_p >= min_price

    last20vol = df['Volume'].tail(20)
    avg_vol = last20vol.mean()

    signal = df['Volume'].iloc[-1]

    liquidity = avg_vol >= min_avg_vol

    rvol = signal >= (avg_vol * 1.05)

    passes = liquidity and rvol and price_pass

    if bt:
        fail_marker = pd.Series(not passes, index=df.index)
        return df, fail_marker
    else:
        return df if passes else None

    

    
