import pandas as pd

def add_ema(df, period, column='Close'):
    """
    Calculates Exponential Moving Average for a given period.
    """
    
    df[f'EMA_{period}'] = df[column].ewm(span=period, adjust=False).mean()
    return df

def add_emas(df):
    """
    Adds EMA 9/20/50/200 to given DataFrame.
    """
    
    df = add_ema(df, 9)
    df = add_ema(df, 20)
    df = add_ema(df, 50)
    df = add_ema(df, 200)
    return df

def add_atr(df, period=14):
    """
    Calculates Average True Range using Exponential Smoothing.
    """
    
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()

    truerange = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    df['TR'] = truerange
    df[f'ATR_{period}'] = df['TR'].ewm(span=period, adjust=False).mean()
    return df

def add_rsi(df, period=14):
    """
    Calculates Relative Strength Index using Wilder's Smoothing (alpha=1/period).
    """
    
    delta = df['Close'].diff()
    gains = delta.clip(lower = 0)
    losses = -delta.clip(upper = 0)

    avg_gain = gains.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    df[f'RSI_{period}'] = rsi

    return df
    
    
