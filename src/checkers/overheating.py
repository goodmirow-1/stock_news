def check_overheating(df):
    """
    Checks for Short-term Overheating criteria.
    Returns: (is_triggered, details)
    
    Criteria (Composite):
    1. Closing Price >= MA(40) * 1.3
    2. Turnover Ratio (Volume/MA_VOL) >= 500% (5.0)
    3. Volatility >= MA_Volatility(40) * 1.5
    
    Note: Real criteria requires "2 out of 3" or specific sequences. 
    Here we check if the LATEST day matches these conditions.
    """
    if df is None or len(df) < 41:
        return False, "데이터 부족"
        
    latest = df.iloc[-1]
    
    # Thresholds
    price_cond = latest['Close'] >= (latest['MA_40'] * 1.3)
    vol_cond = latest['Vol_Ratio'] >= 5.0
    volatility_cond = latest['Volatility'] >= (latest['Volatility_MA_40'] * 1.5)
    
    details = {
        "주가요건": {
            "val": latest['Close'],
            "threshold": latest['MA_40'] * 1.3,
            "triggered": bool(price_cond)
        },
        "회전율요건": {
            "val": latest['Vol_Ratio'],
            "threshold": 5.0,
            "triggered": bool(vol_cond)
        },
        "변동성요건": {
            "val": latest['Volatility'],
            "threshold": latest['Volatility_MA_40'] * 1.5,
            "triggered": bool(volatility_cond)
        }
    }
    
    # Simplification: KRX 'Designation Alert' triggers if ANY of these happen repeatedly or combination.
    # For this tool, we flag if ANY single condition is met on the latest day as a 'Potential Signal'
    is_triggered = price_cond and vol_cond and volatility_cond 
    
    return is_triggered, details
