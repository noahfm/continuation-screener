import unittest
import pandas as pd
import numpy as np
from continuation_screener.trend_screener import avg_volume, ema_bounce_score

class TestFilters(unittest.TestCase):

    def setUp(self):
        dates = pd.date_range(start="2023-01-01", periods=100)
        self.df = pd.DataFrame(index=dates)
        self.df['Close'] = 50.0
        self.df['Open'] = 49.0
        self.df['High'] = 51.0
        self.df['Low'] = 48.0
        self.df['Volume'] = 2_000_000 # High liquidity
        self.df['EMA_9'] = 47.0 # Price is above EMA_9

    def test_avg_volume_pass(self):
        self.df.loc[self.df.index[-1], 'Volume'] = 3_000_000 
        result = avg_volume(self.df)
        self.assertIsNotNone(result)

    def test_avg_volume_fail_price(self):
        self.df['Close'] = 15.0
        result = avg_volume(self.df)
        self.assertIsNone(result)

    def test_ema_bounce_no_score(self):
        result = ema_bounce_score(self.df)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
