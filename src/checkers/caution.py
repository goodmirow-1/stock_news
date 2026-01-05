def check_caution(df):
    """
    Checks for Investment Caution criteria.
    Returns: (is_triggered, details)
    """
    if df is None or len(df) < 15:
        return False, "데이터 부족"
        
    latest = df.iloc[-1]
    
    # Criteria 1: Price Explosion (Generic proxy for "Rapid Rise")
    # e.g. Close > Highest of last 15 days (excluding today? no, including)
    # Actually, "Close is highest in 15 days" is a weak signal.
    # Let's use: 5-day increase > 60% (Common Caution/Warning boundary)
    
    change_5d = latest.get('Change_5d', 0)
    change_15d = latest.get('Change_15d', 0)
    
    # 1. Spam/Excessive Rise
    cond_rise_5d = change_5d >= 0.60  # 60% rise in 5 days
    cond_rise_15d = change_15d >= 1.00 # 100% rise in 15 days
    
    is_triggered = cond_rise_5d or cond_rise_15d
    
    details = {
        "5일상승률": {
            "val": change_5d,
            "threshold": 0.60,
            "triggered": bool(cond_rise_5d)
        },
        "15일상승률": {
            "val": change_15d,
            "threshold": 1.00,
            "triggered": bool(cond_rise_15d)
        }
    }
    
    return is_triggered, details
