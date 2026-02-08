import pandas as pd
import requests
from io import StringIO
import re

def get_iwv_tickers():
    """
    Scrapes the IShares Russell 3000 ETF holdings to get a current list
    of the 3000 largest publicly traded US companies.
    """
    
    url = "https://www.ishares.com/us/products/239714/ishares-russell-3000-etf/1467271812596.ajax?fileType=csv&fileName=IWV_holdings&dataType=fund"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
    try:
        response = requests.get(url, headers=headers)
        csv_data = response.text
        lines = csv_data.splitlines()


        start = [i for i,l in enumerate(lines) if l.strip().startswith('Ticker,')][0]

        if not start:
            print('could not find ticker header in ishares csv.')
            return []

        csv_clean = '\n'.join(lines[start:])
    
        table = pd.read_csv(StringIO(csv_clean))

        tickeridentify = re.compile(r'^[A-Z0-9\.\-]{1,6}$')
    
        tickers = (
            table['Ticker']
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
            )
        tickers = [t for t in tickers if tickeridentify.match(t)]

        return tickers
    except Exception as e:
        print(f'error fetchin tickers: {e}')
        return []
             

    
    
