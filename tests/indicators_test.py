import unittest
import pandas as pd
import numpy as np
from continuation_screener.trend_screener import stacked_emas

class TestIndicators(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range(start="2022-01-01", periods=500)
        self.df_up = pd.DataFrame(index=dates)
        
        trend = np.geomspace(100, 500, 500)
        
        self.df_up['Open'] = trend * 0.99
        self.df_up['High'] = trend * 1.02
        self.df_up['Low'] = trend * 0.98
        self.df_up['Close'] = trend
        self.df_up['Volume'] = 1_000_000

    def test_stacked_emas_true(self):
        
        result = stacked_emas(self.df_up)
        self.assertTrue(result is not None)

    def test_empty_dataframe(self):
        empty_df = pd.DataFrame()
        result = stacked_emas(empty_df)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
