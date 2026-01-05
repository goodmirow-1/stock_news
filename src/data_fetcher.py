import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(code, days=120):
    """
    Fetches OHLCV data for the given stock code.
    Fetches enough data to calculate moving averages (approx 120 days).
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)
    
    # fdr uses 'code' which can be KRX stock code
    # e.g. '005930' for Samsung Electronics
    try:
        df = fdr.DataReader(code, start_date, end_date)
        return df
    except Exception as e:
        print(f"Error fetching data for {code}: {e}")
        return None
