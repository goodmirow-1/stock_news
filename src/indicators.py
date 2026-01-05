import pandas as pd
import numpy as np

def calculate_indicators(df):
    """
    Calculates necessary indicators for warning checks.
    Adds columns to the dataframe in-place.
    """
    if df is None or df.empty:
        return df

    # Closing Price Changes
    df['Change_3d'] = df['Close'].pct_change(periods=3)
    df['Change_5d'] = df['Close'].pct_change(periods=5)
    df['Change_15d'] = df['Close'].pct_change(periods=15)
    
    # Moving Averages
    df['MA_40'] = df['Close'].rolling(window=40).mean()
    
    # Turnover (Rotation) Rate
    # Turnover Ratio = Volume / Outstanding Shares
    # Since we don't have outstanding shares readily available in simple OHLCV, 
    # we will use Volume comparison as a proxy or if FDR provides shares.
    # FDR's KRX data often doesn't give shares easily in daily. 
    # Workaround: Use Volume ratio relative to 40-day average volume directly 
    # as the criteria "volume turnover increases 500%" is equivalent to "volume increases 500%" 
    # if shares outstanding is constant.
    df['Vol_MA_40'] = df['Volume'].rolling(window=40).mean()
    df['Vol_Ratio'] = df['Volume'] / df['Vol_MA_40'] 
    
    # Volatility (Daily Fluctuation)
    # Formula: (High - Low) / Close (or similar variation)
    # The KRX rule: "Daily Volatility" often defined as (High-Low)/Close or (High-Low)/((High+Low)/2)
    # We will use (High - Low) / Close for simplicity unless specified otherwise.
    df['Volatility'] = (df['High'] - df['Low']) / df['Close']
    df['Volatility_MA_40'] = df['Volatility'].rolling(window=40).mean()
    
    return df
