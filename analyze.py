import sys
import argparse
from tabulate import tabulate
from src.data_fetcher import get_stock_data
from src.indicators import calculate_indicators
from src.checkers.overheating import check_overheating
from src.checkers.caution import check_caution
from src.checkers.warning import check_warning

def main():
    parser = argparse.ArgumentParser(description="KRX 종목 지정 요건 검사기")
    parser.add_argument("code", type=str, help="종목코드 (예: 삼성전자 005930)")
    args = parser.parse_args()
    
    print(f"{args.code} 데이터 조회 중...")
    df = get_stock_data(args.code)
    
    if df is None:
        print("데이터 조회 실패. 종목코드를 확인해주세요.")
        sys.exit(1)
        
    print("지표 계산 중...")
    df = calculate_indicators(df)
    
    # Run Checks
    oh_triggered, oh_details = check_overheating(df)
    ca_triggered, ca_details = check_caution(df)
    wa_triggered, wa_details = check_warning(df)
    
    # Print Report
    print("\n" + "="*40)
    print(f" 검사 결과: {args.code}")
    print("="*40)
    
    latest_close = df.iloc[-1]['Close']
    print(f"최근 종가: {latest_close:,.0f} KRW")
    print(f"기준일: {df.index[-1].strftime('%Y-%m-%d')}")
    print("-" * 40)
    
    # Overheating
    print(f"[단기과열종목]: {'지정예상' if oh_triggered else '해당없음'}")
    if isinstance(oh_details, str):
        print(f"  {oh_details}")
    else:
        for k, v in oh_details.items():
            if isinstance(v, dict):
                # Using '미충족' for Safe (PASS), '충족' for Triggered (FAIL)
                status = "충족" if v.get('triggered') else "미충족"
                val = v.get('val')
                thresh = v.get('threshold')
                print(f"  - {k}: {val:.2f} >= {thresh:.2f} ? [{status}]")
    
    print("-" * 40)
    
    # Caution
    print(f"[투자주의종목]: {'지정예상' if ca_triggered else '해당없음'}")
    if isinstance(ca_details, str):
        print(f"  {ca_details}")
    else:
        for k, v in ca_details.items():
            if isinstance(v, dict):
                status = "충족" if v.get('triggered') else "미충족"
                val = v.get('val')
                thresh = v.get('threshold')
                print(f"  - {k}: {val:.2%} >= {thresh:.2%} ? [{status}]")
            
    print("-" * 40)
    
    # Warning
    print(f"[투자경고종목]: {'지정예상' if wa_triggered else '해당없음'}")
    if isinstance(wa_details, str):
        print(f"  {wa_details}")
    else:
        for k, v in wa_details.items():
            if isinstance(v, dict):
                status = "충족" if v.get('triggered') else "미충족"
                val = v.get('val')
                thresh = v.get('threshold')
                print(f"  - {k}: {val:.2%} >= {thresh:.2%} ? [{status}]")

if __name__ == "__main__":
    main()
