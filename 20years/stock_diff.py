import yfinance as yf
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import platform
import matplotlib.font_manager as fm

# OS에 맞게 한글 폰트 설정
system_name = platform.system()
if system_name == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif system_name == 'Darwin': # Mac OS
    plt.rcParams['font.family'] = 'AppleGothic'
elif system_name == 'Linux':
    # 나눔고딕 폰트가 있는지 확인
    if fm.findfont('NanumGothic', fontext='ttf'):
        plt.rcParams['font.family'] = 'NanumGothic'
    else:
        print("나눔고딕 폰트가 설치되어 있지 않습니다. 'sudo apt-get install fonts-nanum*'으로 설치할 수 있습니다.")
        # 설치되어 있지 않으면 다른 사용 가능한 폰트를 사���하거나, 경고 메시지를 출력합니다.
        # 여기서는 sans-serif를 기본값으로 사용합니다.
        plt.rcParams['font.family'] = 'sans-serif'

plt.rcParams['axes.unicode_minus'] = False # 마이너스 폰트 깨짐 방지

def get_stock_data_with_diff_and_dividends(ticker1, ticker2, start_date, end_date, external_dividends=None):
    """
    두 주식의 일별 종가 차이, 비율, 배당금 및 배당 수익률을 계산하여 DataFrame으로 반환합니다.
    외부 배당금 데이터를 사용하여 배당금 정보를 통합할 수 있습니다.
    또한, Price_Diff_Ratio의 해당 날짜까지의 25% 및 75% 사분위수 값을 계산하여 추가합니다.

    Args:
        ticker1 (str): 첫 번째 주식의 티커 심볼 (예: '005930.KS' for 삼성전자)
        ticker2 (str): 두 번째 주식의 티커 심볼 (예: '005935.KS' for 삼성전자(우))
        start_date (str): 데이터 시작 날짜 (YYYY-MM-DD 형식)
        end_date (str): 데이터 종료 날짜 (YYYY-MM-DD 형식)
        external_dividends (pd.Series, optional): 외부에서 제공된 배당금 데이터 (인덱스는 날짜, 값은 배당금).
                                                  기본값은 None.

    Returns:
        pandas.DataFrame: 날짜, 종가 차이, 비율, 배당금, 배당 수익률, Price_Diff_Ratio 사분위수를 포함하는 DataFrame
    """
    try:
        # 주식 데이터 다운로드
        data1 = yf.download(ticker1, start=start_date, end=end_date)
        data2 = yf.download(ticker2, start=start_date, end=end_date)

        if data1.empty or data2.empty:
            print("Debug: One or both dataframes are empty after download.")
            return pd.DataFrame()

        # 종가(Close) 및 시가(Open) 데이터 추출 및 컬럼 이름 단순화
        close_prices1 = data1['Close']
        close_prices2 = data2['Close']
        open_prices1 = data1['Open']
        open_prices2 = data2['Open']

        # MultiIndex인 경우, 첫 번째 레벨의 'Close' 또는 'Open'을 선택
        if isinstance(close_prices1.columns, pd.MultiIndex):
            close_prices1 = close_prices1.xs('Close', level=0, axis=1)
            open_prices1 = open_prices1.xs('Open', level=0, axis=1)
        if isinstance(close_prices2.columns, pd.MultiIndex):
            close_prices2 = close_prices2.xs('Close', level=0, axis=1)
            open_prices2 = open_prices2.xs('Open', level=0, axis=1)

        # Series로 변환 (만약 DataFrame으로 남아있다면)
        if isinstance(close_prices1, pd.DataFrame):
            close_prices1 = close_prices1.iloc[:, 0]
            open_prices1 = open_prices1.iloc[:, 0]
        if isinstance(close_prices2, pd.DataFrame):
            close_prices2 = close_prices2.iloc[:, 0]
            open_prices2 = open_prices2.iloc[:, 0]

        # 배당금 데이터 처리
        if external_dividends is not None:
            # 외부 배당금 데이터를 사용
            dividends_to_use = external_dividends
        else:
            # yfinance에서 배당금 컬럼이 있다면 사용, 없으면 0으로 채움
            if 'Dividends' in data2.columns:
                dividends_to_use = data2['Dividends']
                if isinstance(dividends_to_use.columns, pd.MultiIndex):
                    dividends_to_use = dividends_to_use.xs('Dividends', level=0, axis=1)
                if isinstance(dividends_to_use, pd.DataFrame):
                    dividends_to_use = dividends_to_use.iloc[:, 0]
            else:
                dividends_to_use = pd.Series(0, index=data2.index, name='Dividends')
        
        # 모든 데이터를 날짜 기준으로 합치기
        combined_df = pd.concat([
            close_prices1.rename('Stock1_Close'),
            close_prices2.rename('Stock2_Close'),
            open_prices1.rename('Stock1_Open'),
            open_prices2.rename('Stock2_Open'),
            dividends_to_use.rename('Dividend_Amount_Raw') # 원본 배당금
        ], axis=1)

        combined_df = combined_df.dropna(subset=['Stock1_Close', 'Stock2_Close', 'Stock1_Open', 'Stock2_Open']) # 종가 및 시가 데이터가 있는 날짜만 사용
        
        combined_df['Dividend_Amount_Raw'] = combined_df['Dividend_Amount_Raw'].fillna(0)

        combined_df['Dividend_Amount'] = combined_df['Dividend_Amount_Raw'].replace(0, pd.NA).ffill().fillna(0)


        if combined_df.empty:
            print("Debug: combined_df is empty after dropna.")
            return pd.DataFrame()

        # 가격 차이 계산
        combined_df['Price_Difference'] = combined_df['Stock1_Close'] - combined_df['Stock2_Close']

        # diff * 100 / 삼성전자(우) Price 계산
        combined_df['Price_Diff_Ratio'] = combined_df.apply(
            lambda row: (row['Price_Difference'] * 100 / row['Stock2_Close']) if row['Stock2_Close'] != 0 else 0,
            axis=1
        )

        # 배당금액 * 100 / 삼성전자(우) price 계산 (채워진 배당금 사용)
        combined_df['Dividend_Yield_on_Preferred'] = combined_df.apply(
            lambda row: (row['Dividend_Amount'] * 100 / row['Stock2_Close']) if row['Stock2_Close'] != 0 else 0,
            axis=1
        )

        # 해당 날짜까지의 Price_Diff_Ratio 25% 및 75% 사분위수 계산
        combined_df['Price_Diff_Ratio_25th_Percentile'] = combined_df['Price_Diff_Ratio'].expanding().quantile(0.25)
        combined_df['Price_Diff_Ratio_75th_Percentile'] = combined_df['Price_Diff_Ratio'].expanding().quantile(0.75)


        # 필요한 컬럼만 선택
        result_df = combined_df[[
            'Price_Difference',
            'Price_Diff_Ratio',
            'Dividend_Amount',
            'Dividend_Yield_on_Preferred',
            'Stock1_Close',
            'Stock2_Close',
            'Stock1_Open',
            'Stock2_Open',
            'Price_Diff_Ratio_25th_Percentile',
            'Price_Diff_Ratio_75th_Percentile',
            'Dividend_Amount_Raw' # 추가
        ]]
        result_df.index.name = 'Date'
        return result_df

    except Exception as e:
        print(f"데이터를 가져오거나 처리하는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # 삼성전자와 삼성전자(우)의 티커 심볼
    samsung_elec_ticker = '005930.KS'
    samsung_elec_pref_ticker = '005935.KS'

    # 데이터 조회 기간 설정 (오늘 날짜 기준 5년 전부터 오늘까지)
    today = datetime(2025, 6, 29)
    five_years_ago = today - timedelta(days=20*365)
    
    start_date = five_years_ago.strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    print(f"{start_date}부터 {end_date}까지 삼성전자와 삼성전자(우)의 일별 가격 차이 계산 중...")

    # Investing.com에서 추출한 삼성전자(우) 배당금 데이터
    dividend_history_pref = [
        {"Ex-dividend Date": "6월 26, 2025", "Dividend": 361.00},
        {"Ex-dividend Date": "3월 27, 2025", "Dividend": 365.00},
        {"Ex-dividend Date": "12월 26, 2024", "Dividend": 364.00},
        {"Ex-dividend Date": "9월 26, 2024", "Dividend": 361.00},
        {"Ex-dividend Date": "6월 26, 2024", "Dividend": 361.00},
        {"Ex-dividend Date": "3월 27, 2024", "Dividend": 361.00},
        {"Ex-dividend Date": "12월 26, 2023", "Dividend": 362.00},
        {"Ex-dividend Date": "9월 25, 2023", "Dividend": 361.00},
        {"Ex-dividend Date": "6월 28, 2023", "Dividend": 361.00},
        {"Ex-dividend Date": "3월 29, 2023", "Dividend": 361.00},
        {"Ex-dividend Date": "12월 27, 2022", "Dividend": 362.00},
        {"Ex-dividend Date": "9월 28, 2022", "Dividend": 361.00},
        {"Ex-dividend Date": "6월 28, 2022", "Dividend": 361.00},
        {"Ex-dividend Date": "3월 29, 2022", "Dividend": 361.00},
        {"Ex-dividend Date": "12월 28, 2021", "Dividend": 362.00},
        {"Ex-dividend Date": "9월 28, 2021", "Dividend": 361.00},
        {"Ex-dividend Date": "6월 28, 2021", "Dividend": 361.00},
        {"Ex-dividend Date": "3월 29, 2021", "Dividend": 361.00},
        {"Ex-dividend Date": "12월 28, 2020", "Dividend": 1933.00},
        {"Ex-dividend Date": "9월 27, 2020", "Dividend": 354.00}
    ]

    # 배당금 데이터를 pandas Series로 변환
    external_dividends_series = pd.Series({
        pd.to_datetime(item["Ex-dividend Date"], format='%m월 %d, %Y'): item["Dividend"]
        for item in dividend_history_pref
    }).sort_index()

    price_data_df = get_stock_data_with_diff_and_dividends(
        samsung_elec_ticker, 
        samsung_elec_pref_ticker, 
        start_date, 
        end_date, 
        external_dividends=external_dividends_series
    )

    if not price_data_df.empty:
        # 날짜 형식을 YY-mm-dd로 변경
        price_data_df.index = price_data_df.index.strftime('%y-%m-%d')

        # 결과를 JSON 파일로 저장
        output_json_path = r'./samsung_stock_analysis.json'
        price_data_df.to_json(output_json_path, orient='index', indent=4)
        print(f"주식 분석 데이터가 {output_json_path}에 JSON 형식으로 저장되었습니다.")

        # Price_Diff_Ratio 히스토그램 및 박스 플롯 저장
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        sns.histplot(price_data_df['Price_Diff_Ratio'], kde=True)
        plt.title('Price_Diff_Ratio 히스토그램')
        plt.xlabel('Price_Diff_Ratio (%)')
        plt.ylabel('빈도')

        plt.subplot(1, 2, 2)
        sns.boxplot(y=price_data_df['Price_Diff_Ratio'])
        plt.title('Price_Diff_Ratio 박스 플롯')
        plt.ylabel('Price_Diff_Ratio (%)')

        plt.tight_layout()
        plot_output_path = r'./price_diff_ratio_distribution.png'
        plt.savefig(plot_output_path)
        print(f"Price_Diff_Ratio 분포 그래프가 {plot_output_path}에 저장되었습니다.")
    else:
        print("주식 분석 데이터를 생성할 수 없습니다.")

