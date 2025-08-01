import yfinance as yf
import pandas as pd
from datetime import datetime

def get_and_save_dividends(ticker, start_date, end_date, output_filename):
    """
    주어진 티커에 대한 배당금 데이터를 가져와 JSON 파일로 저장합니다.

    Args:
        ticker (str): 주식 티커 심볼.
        start_date (str): 데이터 조회 시작 날짜 (YYYY-MM-DD).
        end_date (str): 데이터 조회 종료 날짜 (YYYY-MM-DD).
        output_filename (str): 저장할 JSON 파일 경로.
    """
    try:
        stock = yf.Ticker(ticker)
        
        # yfinance는 전체 기간의 배당금을 반환하므로, 날짜로 필터링합니다.
        dividends = stock.dividends
        dividends.index = pd.to_datetime(dividends.index.date) # 타임존 정보 제거
        
        mask = (dividends.index >= start_date) & (dividends.index <= end_date)
        filtered_dividends = dividends.loc[mask]

        if filtered_dividends.empty:
            print(f"{ticker}에 대해 해당 기간 내에 배당금 데이터가 없습니다.")
            return

        print(f"--- {ticker} 배당금 내역 ({start_date} ~ {end_date}) ---")
        print(filtered_dividends)

        # JSON ���일로 저장하기 위해 인덱스를 컬럼으로 변환
        output_df = filtered_dividends.reset_index()
        output_df.columns = ['Date', 'Dividend']
        output_df['Date'] = output_df['Date'].dt.strftime('%Y-%m-%d')
        
        output_df.to_json(output_filename, orient='records', indent=4, force_ascii=False)
        print(f"\n배당금 데이터가 {output_filename} 파일로 저장되었습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    samsung_ltd_ticker = '005930.KS' # 삼성전자 보통주 티커
    
    # 다른 스크립트와 기간을 통일합니다.
    today = datetime(2025, 6, 29)
    five_years_ago = today - pd.DateOffset(years=20)
    
    start = five_years_ago.strftime('%Y-%m-%d')
    end = today.strftime('%Y-%m-%d')
    
    output_file = 'samsung_ltd_dividends.json'
    
    get_and_save_dividends(samsung_ltd_ticker, start, end, output_file)
