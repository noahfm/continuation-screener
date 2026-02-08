import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm

from continuation_screener.screener.run_screener_bt import run_screener_bt
from continuation_screener.simulator.backtester_oneday import backtest_ticker

def run_backtester(start_date=None, end_date=None):
    """
    Simulates trades given a start and end date. Naturally, maximizes window
    possible under yfinance restrictions. See readme for backtest data for
    longer periods.
    """

    end_dt = pd.to_datetime(end_date) if end_date else datetime.now()
    cutoff = end_dt - timedelta(days=11)
    start_dt = pd.to_datetime(start_date) if start_date else datetime.now() - timedelta(days=59)  

    ticker_df = run_screener_bt(start_dt.strftime('%m-%d-%Y'), cutoff.strftime('%m-%d-%Y'))

    if ticker_df is None:
        print('run_screener_bt failed, ticker_df is empty.')
        return pd.DataFrame(), pd.DataFrame()

    trades = []

    traded_today = set()
    executed_trades = set()
    current_day = None

    for (day, ticker) in tqdm(ticker_df.index, desc='Processing Through Days...'):

        if current_day != day.date():
            traded_today.clear()
            current_day = day.date()

        base = ticker
        if ticker in ['GOOGL','GOOG']: base = 'GOOG'
        if ticker in ['FOXA', 'FOX']: base = 'FOX'

        trade_marker = (day.date(), base)

        if trade_marker in traded_today:
            continue
        
        bt_data = backtest_ticker(ticker, day)

        if bt_data is not None:
            trade_id = (bt_data['Ticker'], bt_data['Entry Time'])
            if trade_id in executed_trades:
                continue
            executed_trades.add(trade_id)

            trade_day = bt_data['Entry Time'].date()
            trade_marker = (trade_day, base)
            if trade_marker in traded_today:
                continue
            traded_today.add(trade_marker)
            
            bt_return = (bt_data['Exit Price'] / bt_data['Entry Price']) - 1
            bt_data['Return %'] = bt_return

            leverage = 10 #approximate
            option_return = bt_return * leverage
            bt_data['Option Net ($)'] = 1000 * option_return
            
            trades.append(bt_data)

    df_trades = pd.DataFrame(trades)

    if df_trades.empty:
        print('Error forming df_trades')
        return pd.DataFrame(), pd.DataFrame()

    win_rate = (df_trades['Return %'] > 0).mean()
    avg_win = df_trades[df_trades['Return %'] > 0]['Return %'].mean()
    avg_loss = df_trades[df_trades['Return %'] <= 0]['Return %'].mean()

    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

    gross_profit = df_trades[df_trades['Net'] > 0]['Net'].sum()
    gross_loss = abs(df_trades[df_trades['Net'] <= 0]['Net'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')

    bond_rt = 0.05
    days_total = max((end_dt - start_dt).days, 1)
    year_convert = days_total / 365.25
    trades_yearly = len(df_trades) / year_convert

    est_annual_return = expectancy * trades_yearly

    std = df_trades['Return %'].std()
    if std > 0 and len(df_trades) > 1:
        sharpe = (est_annual_return - bond_rt) / (std * np.sqrt(trades_yearly))
    else:
        sharpe = 0.0

    
    summary = {
        'Metric': [
            'Total Trades',
            'Win Rate',
            'Avg Win %',
            'Avg Loss %',
            'Profit Factor (Gross)',
            'Expectancy (Per Trade)',
            'Est. Annual Return',
            'Cumulative Net ($)',
            'Est. Option Gain($)',
            'Annualized Sharpe Ratio'
        ],
        'Value': [
            len(df_trades),
            f'{win_rate:.2%}',
            f'{avg_win:.2%}',
            f'{avg_loss:.2%}',
            f'{profit_factor:.2f}',
            f'{expectancy:.2%}',
            f'{est_annual_return:.2%}',
            f'{df_trades["Net"].sum():.2f}',
            f'${df_trades["Option Net ($)"].sum():.2f}',
            f'{sharpe:.2f}'
        ],
        'Note': [
            '', '', '', '', '', '',
            'Compare to 5% bond',
            'Total profit per 1 share traded',
            'Based on $1k pos, 0.5 delta, 10x leverage',
            'Sharpe Ratio(excess return per unit of risk vs. 5% bond'
        ]
            
    }

    summary_df = pd.DataFrame(summary)

    return df_trades, summary_df

if __name__ == '__main__':
    
    trades, summary = run_backtester()

    print('\n---BACKTEST SUMMARY---')
    print(summary)

    print('\n---TRADES INFO---')
    print(trades)
            
#'12/06/25', '01/22/26'
            
        

            
            
        

        
