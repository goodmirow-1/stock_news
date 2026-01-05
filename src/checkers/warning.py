def check_warning(df):
    """
    Checks for Investment Warning criteria.
    Returns: (is_triggered, details)
    """
    if df is None or len(df) < 15:
        return False, "데이터 부족"
        
    latest = df.iloc[-1]
    
    # Criteria:
    # 1. 5-day change > 60% ?? (Caution is lower, Warning is higher usually)
    # Actually, Warning often requires:
    # - 5-day rise > 60% AND Price > 15-day Max
    # - 15-day rise > 100% AND Price > 15-day Max
    
    # Let's implement stricter "Warning" thresholds
    
    change_3d = latest.get('Change_3d', 0)
    change_5d = latest.get('Change_5d', 0)
    change_15d = latest.get('Change_15d', 0)

    # 1. Ultra-Short-Term (3 days) > 100%
    cond_3d = change_3d >= 1.0
    
    # 2. Short-Term (5 days) > 60% (Reusing generic caution threshold but applied strictly here)
    cond_5d = change_5d >= 0.60
    
    # 3. Medium-Term (15 days) > 100%
    cond_15d = change_15d >= 1.0
    
    is_triggered = cond_3d or cond_5d or cond_15d
    
    details = {
        "초단기(3일)상승률": {
            "val": change_3d,
            "threshold": 1.0,
            "triggered": bool(cond_3d)
        },
        "단기(5일)상승률": {
            "val": change_5d,
            "threshold": 0.60,
            "triggered": bool(cond_5d)
        },
        "중기(15일)상승률": {
            "val": change_15d,
            "threshold": 1.0,
            "triggered": bool(cond_15d)
        }
    }
    
    return is_triggered, details
