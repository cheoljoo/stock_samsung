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

def load_existing_data(json_file_path):
    """
    기존 JSON 파일에서 데이터를 로드합니다.
    
    Args:
        json_file_path (str): 기존 JSON 파일 경로
        
    Returns:
        tuple: (DataFrame, 마지막 날짜) 또는 (None, None)
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            return None, None
            
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index = pd.to_datetime(df.index, format='%y-%m-%d')
        df = df.sort_index()
        
        last_date = df.index[-1]
        print(f"✓ 기존 데이터 로드 완료: {df.index[0].strftime('%Y-%m-%d')} ~ {last_date.strftime('%Y-%m-%d')} ({len(df)}일)")
        
        return df, last_date
        
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"기존 데이터 파일을 찾을 수 없거나 로드할 수 없습니다: {e}")
        return None, None

def get_stock_data_with_diff_and_dividends(ticker1, ticker2, start_date, end_date, external_dividends=None, existing_df=None):
    """
    두 주식의 일별 종가 차이, 비율, 배당금 및 배당 수익률을 계산하여 DataFrame으로 반환합니다.
    외부 배당금 데이터를 사용하여 배당금 정보를 통합할 수 있습니다.
    또한, Price_Diff_Ratio의 해당 날짜까지의 25% 및 75% 사분위수 값을 계산하여 추가합니다.
    
    기존 데이터가 있는 경우 증분 업데이트를 수행합니다.

    Args:
        ticker1 (str): 첫 번째 주식의 티커 심볼 (예: '005930.KS' for 삼성전자)
        ticker2 (str): 두 번째 주식의 티커 심볼 (예: '005935.KS' for 삼성전자(우))
        start_date (str): 데이터 시작 날짜 (YYYY-MM-DD 형식)
        end_date (str): 데이터 종료 날짜 (YYYY-MM-DD 형식)
        external_dividends (pd.Series, optional): 외부에서 제공된 배당금 데이터 (인덱스는 날짜, 값은 배당금).
                                                  기본값은 None.
        existing_df (pd.DataFrame, optional): 기존 데이터프레임 (증분 업데이트용)

    Returns:
        pandas.DataFrame: 날짜, 종가 차이, 비율, 배당금, 배당 수익률, Price_Diff_Ratio 사분위수를 포함하는 DataFrame
    """
    try:
        # 기존 데이터가 있는 경우 증분 업데이트 처리
        if existing_df is not None and not existing_df.empty:
            print("🔄 증분 업데이트 모드: 기존 데이터 활용")
            
            # 기존 데이터의 마지막 날짜 이후부터 새 데이터 다운로드
            last_date = existing_df.index[-1]
            next_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # 새 데이터가 필요한지 확인
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if last_date.date() >= end_date_dt.date():
                print(f"✓ 기존 데이터가 최신입니다. 마지막 날짜: {last_date.strftime('%Y-%m-%d')}")
                return existing_df
            
            print(f"📅 새 데이터 다운로드: {next_date} ~ {end_date}")
            
            # 새 데이터만 다운로드
            new_data1 = yf.download(ticker1, start=next_date, end=end_date)
            new_data2 = yf.download(ticker2, start=next_date, end=end_date)
            
            if new_data1.empty and new_data2.empty:
                print("✓ 다운로드할 새 데이터가 없습니다.")
                return existing_df
                
        else:
            print("🆕 전체 데이터 다운로드 모드")
            # 전체 데이터 다운로드
            new_data1 = yf.download(ticker1, start=start_date, end=end_date)
            new_data2 = yf.download(ticker2, start=start_date, end=end_date)
        
        # 주식 데이터 다운로드
        data1 = yf.download(ticker1, start=start_date, end=end_date)
        data2 = yf.download(ticker2, start=start_date, end=end_date)

        # 증분 업데이트의 경우 새 데이터만 처리
        if existing_df is not None and not existing_df.empty:
            # 새 데이터 처리
            data1 = new_data1
            data2 = new_data2
        
        if data1.empty or data2.empty:
            if existing_df is not None and not existing_df.empty:
                print("새 데이터가 없으므로 기존 데이터를 반환합니다.")
                return existing_df
            else:
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
            if existing_df is not None and not existing_df.empty:
                # 새 데이터 기간에 해당하는 배당금만 필터링
                dividends_to_use = external_dividends[external_dividends.index.isin(data2.index)]
            else:
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
        new_combined_df = pd.concat([
            close_prices1.rename('Stock1_Close'),
            close_prices2.rename('Stock2_Close'),
            open_prices1.rename('Stock1_Open'),
            open_prices2.rename('Stock2_Open'),
            dividends_to_use.rename('Dividend_Amount_Raw') # 원본 배당금
        ], axis=1)

        new_combined_df = new_combined_df.dropna(subset=['Stock1_Close', 'Stock2_Close', 'Stock1_Open', 'Stock2_Open']) # 종가 및 시가 데이터가 있는 날짜만 사용
        
        new_combined_df['Dividend_Amount_Raw'] = new_combined_df['Dividend_Amount_Raw'].fillna(0)
        new_combined_df['Dividend_Amount'] = new_combined_df['Dividend_Amount_Raw'].replace(0, pd.NA).ffill().fillna(0)

        if new_combined_df.empty:
            if existing_df is not None and not existing_df.empty:
                print("새 데이터가 비어있으므로 기존 데이터를 반환합니다.")
                return existing_df
            else:
                print("Debug: new_combined_df is empty after dropna.")
                return pd.DataFrame()

        # 기존 데이터와 병합
        if existing_df is not None and not existing_df.empty:
            # 기존 데이터와 새 데이터 결합
            combined_df = pd.concat([existing_df, new_combined_df])
            combined_df = combined_df[~combined_df.index.duplicated(keep='last')]  # 중복 제거 (최신 데이터 유지)
            combined_df = combined_df.sort_index()
            print(f"✓ 데이터 병합 완료: 기존 {len(existing_df)}일 + 새로운 {len(new_combined_df)}일 = 총 {len(combined_df)}일")
        else:
            combined_df = new_combined_df

        # 가격 차이 계산 (새로 추가된 부분만 또는 전체)
        if existing_df is not None and not existing_df.empty:
            # 새로 추가된 행에 대해서만 계산
            new_rows_mask = ~combined_df.index.isin(existing_df.index)
            if new_rows_mask.any():
                combined_df.loc[new_rows_mask, 'Price_Difference'] = (
                    combined_df.loc[new_rows_mask, 'Stock1_Close'] - 
                    combined_df.loc[new_rows_mask, 'Stock2_Close']
                )
                combined_df.loc[new_rows_mask, 'Price_Diff_Ratio'] = combined_df.loc[new_rows_mask].apply(
                    lambda row: (row['Price_Difference'] * 100 / row['Stock2_Close']) if row['Stock2_Close'] != 0 else 0,
                    axis=1
                )
                combined_df.loc[new_rows_mask, 'Dividend_Yield_on_Preferred'] = combined_df.loc[new_rows_mask].apply(
                    lambda row: (row['Dividend_Amount'] * 100 / row['Stock2_Close']) if row['Stock2_Close'] != 0 else 0,
                    axis=1
                )
        else:
            # 전체 계산
            combined_df['Price_Difference'] = combined_df['Stock1_Close'] - combined_df['Stock2_Close']
            combined_df['Price_Diff_Ratio'] = combined_df.apply(
                lambda row: (row['Price_Difference'] * 100 / row['Stock2_Close']) if row['Stock2_Close'] != 0 else 0,
                axis=1
            )
            combined_df['Dividend_Yield_on_Preferred'] = combined_df.apply(
                lambda row: (row['Dividend_Amount'] * 100 / row['Stock2_Close']) if row['Stock2_Close'] != 0 else 0,
                axis=1
            )

        # 해당 날짜 이전 2년, 3년, 5년 데이터를 기준으로 한 Price_Diff_Ratio 25% 및 75% 사분위수 계산
        # 2년 = 약 730일, 3년 = 약 1095일, 5년 = 약 1825일 (365일 * 년수 + 윤년 고려)
        window_configs = {
            '2year': 730,
            '3year': 1095,
            '5year': 1825
        }
        
        def calculate_rolling_quantile_optimized(series, window_size, quantile, existing_df=None):
            """슬라이딩 윈도우로 분위수 계산 (최적화된 버전)"""
            if existing_df is not None and not existing_df.empty:
                # 증분 업데이트: 기존 계산된 값들을 활용
                existing_col_25 = f'Price_Diff_Ratio_25th_Percentile_{list(window_configs.keys())[0] if quantile == 0.25 else ""}'
                existing_col_75 = f'Price_Diff_Ratio_75th_Percentile_{list(window_configs.keys())[0] if quantile == 0.75 else ""}'
                
                # 새로 계산해야 할 인덱스 찾기
                new_indices = series.index[~series.index.isin(existing_df.index)]
                
                if len(new_indices) == 0:
                    # 새 데이터가 없으면 기존 값 반환
                    return existing_df[existing_col_25 if quantile == 0.25 else existing_col_75].tolist()
                
                # 기존 결과를 리스트로 변환
                result = existing_df[existing_col_25 if quantile == 0.25 else existing_col_75].tolist()
                
                # 새 데이터에 대해서만 계산
                series_array = series.values
                start_idx = len(existing_df)
                
                for i in range(start_idx, len(series)):
                    if i < window_size:
                        window_data = series_array[:i+1]
                    else:
                        window_data = series_array[i-window_size+1:i+1]
                    
                    if len(window_data) > 0:
                        result.append(pd.Series(window_data).quantile(quantile))
                    else:
                        result.append(0)
                
                return result
            else:
                # 전체 계산
                result = []
                series_array = series.values
                for i in range(len(series)):
                    if i < window_size:
                        window_data = series_array[:i+1]
                    else:
                        window_data = series_array[i-window_size+1:i+1]
                    
                    if len(window_data) > 0:
                        result.append(pd.Series(window_data).quantile(quantile))
                    else:
                        result.append(0)
                return result
        
        # 2년, 3년, 5년 각각에 대해 분위수 계산
        for window_name, window_days in window_configs.items():
            if existing_df is not None and not existing_df.empty:
                print(f"🔄 {window_name} 슬라이딩 윈도우 분위수 증분 계산 중...")
            else:
                print(f"🆕 {window_name} 슬라이딩 윈도우로 25% 및 75% 분위수 계산 중...")
                
            combined_df[f'Price_Diff_Ratio_25th_Percentile_{window_name}'] = calculate_rolling_quantile_optimized(
                combined_df['Price_Diff_Ratio'], window_days, 0.25, existing_df
            )
            combined_df[f'Price_Diff_Ratio_75th_Percentile_{window_name}'] = calculate_rolling_quantile_optimized(
                combined_df['Price_Diff_Ratio'], window_days, 0.75, existing_df
            )
        
        # 기존 컬럼명 유지를 위해 2년 데이터를 기본으로 설정
        combined_df['Price_Diff_Ratio_25th_Percentile'] = combined_df['Price_Diff_Ratio_25th_Percentile_2year']
        combined_df['Price_Diff_Ratio_75th_Percentile'] = combined_df['Price_Diff_Ratio_75th_Percentile_2year']


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
            'Price_Diff_Ratio_25th_Percentile_2year',
            'Price_Diff_Ratio_75th_Percentile_2year',
            'Price_Diff_Ratio_25th_Percentile_3year',
            'Price_Diff_Ratio_75th_Percentile_3year',
            'Price_Diff_Ratio_25th_Percentile_5year',
            'Price_Diff_Ratio_75th_Percentile_5year',
            'Dividend_Amount_Raw' # 추가
        ]]
        result_df.index.name = 'Date'
        return result_df

    except Exception as e:
        print(f"데이터를 가져오거나 처리하는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

def generate_stock_data_for_periods():
    """
    다양한 기간(3년, 5년, 10년, 20년, 30년)에 대한 주식 데이터를 생성합니다.
    기존 데이터가 있는 경우 증분 업데이트를 수행합니다.
    """
    # 삼성전자와 삼성전자(우)의 티커 심볼
    samsung_elec_ticker = '005930.KS'
    samsung_elec_pref_ticker = '005935.KS'
    
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
    
    # 다양한 기간 설정 (3년, 5년, 10년, 20년, 30년)
    today = datetime.now()
    periods = {
        '3년': 3*365,
        '5년': 5*365,
        '10년': 10*365,
        '20년': 20*365,
        '30년': 30*365
    }
    
    results = {}
    
    for period_name, days in periods.items():
        print(f"\n{'='*80}")
        print(f"=== {period_name} 데이터 처리 중 ===")
        print(f"{'='*80}")
        
        start_date = (today - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        output_json_path = f'./samsung_stock_analysis_{period_name}.json'
        
        print(f"📅 대상 기간: {start_date} ~ {end_date}")
        
        # 기존 데이터 로드 시도
        existing_df, last_date = load_existing_data(output_json_path)
        
        if existing_df is not None:
            print(f"📊 기존 데이터 활용: {len(existing_df)}일의 데이터")
        else:
            print("🆕 새로운 데이터 생성")
        
        price_data_df = get_stock_data_with_diff_and_dividends(
            samsung_elec_ticker, 
            samsung_elec_pref_ticker, 
            start_date, 
            end_date, 
            external_dividends=external_dividends_series,
            existing_df=existing_df
        )
        
        if not price_data_df.empty:
            # 날짜 형식을 YY-mm-dd로 변경
            price_data_df.index = price_data_df.index.strftime('%y-%m-%d')
            
            # 결과를 JSON 파일로 저장
            price_data_df.to_json(output_json_path, orient='index', indent=4)
            
            if existing_df is not None:
                new_days = len(price_data_df) - len(existing_df) if len(price_data_df) > len(existing_df) else 0
                print(f"💾 업데이트 완료: {output_json_path} ({new_days}일 추가, 총 {len(price_data_df)}일)")
            else:
                print(f"💾 저장 완료: {output_json_path} (총 {len(price_data_df)}일)")
            
            results[period_name] = {
                'data': price_data_df,
                'file_path': output_json_path,
                'start_date': start_date,
                'end_date': end_date,
                'is_updated': existing_df is not None
            }
        else:
            print(f"❌ {period_name} 주식 분석 데이터를 생성할 수 없습니다.")
    
    print(f"\n{'='*80}")
    print("=== 데이터 처리 요약 ===")
    print(f"{'='*80}")
    
    updated_count = sum(1 for r in results.values() if r.get('is_updated', False))
    new_count = len(results) - updated_count
    
    print(f"📊 처리 완료: 총 {len(results)}개 기간")
    print(f"🔄 업데이트: {updated_count}개 기간")
    print(f"🆕 신규 생성: {new_count}개 기간")
    
    return results

if __name__ == "__main__":
    # 다양한 기간에 대한 데이터 생성
    results = generate_stock_data_for_periods()
    
    # 기본 20년 데이터도 생성 (기존 호환성 유지)
    if '20년' in results:
        price_data_df = results['20년']['data']
        
        # 기존 파일명으로도 저장
        output_json_path = r'./samsung_stock_analysis.json'
        price_data_df.to_json(output_json_path, orient='index', indent=4)
        print(f"\n기본 주식 분석 데이터가 {output_json_path}에도 저장되었습니다.")

        # Price_Diff_Ratio 히스토그램 및 박스 플롯 저장
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        sns.histplot(price_data_df['Price_Diff_Ratio'], kde=True)
        plt.title('Price_Diff_Ratio 히스토그램 (20년)')
        plt.xlabel('Price_Diff_Ratio (%)')
        plt.ylabel('빈도')

        plt.subplot(1, 2, 2)
        sns.boxplot(y=price_data_df['Price_Diff_Ratio'])
        plt.title('Price_Diff_Ratio 박스 플롯 (20년)')
        plt.ylabel('Price_Diff_Ratio (%)')

        plt.tight_layout()
        plot_output_path = r'./price_diff_ratio_distribution.png'
        plt.savefig(plot_output_path)
        print(f"Price_Diff_Ratio 분포 그래프가 {plot_output_path}에 저장되었습니다.")
    
    print(f"\n=== 데이터 생성 완료 ===")
    print(f"생성된 기간: {', '.join(results.keys())}")
    print("각 기간별 JSON 파일이 생성되었습니다.")

