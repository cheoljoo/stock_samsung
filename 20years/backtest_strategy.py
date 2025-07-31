import pandas as pd
import json
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
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
        # 설치되어 있지 않으면 다른 사용 가능한 폰트를 사용하거나, 경고 메시지를 출력합니다.
        # 여기서는 sans-serif를 기본값으로 사용합니다.
        plt.rcParams['font.family'] = 'sans-serif'

plt.rcParams['axes.unicode_minus'] = False # 마이너스 폰트 깨짐 방지

def run_backtest(json_file_path, initial_stock_type, initial_shares, start_date_str):
    """
    주어진 전략에 따라 백테스트를 수행하고 투자 결과를 분석합니다.
    또한, 각 전략의 월별 평가 금액 그래프를 생성하여 PNG 파일로 저장합니다.

    Args:
        json_file_path (str): 주식 데이터가 포함된 JSON 파일 경로.
        initial_stock_type (str): 초기 보유 주식 유형 ('삼성전자' 또는 '삼성전자(우)').
        initial_shares (int): 초기 보유 주식 수.
        start_date_str (str): 백테스트 시작 날짜 (YY-mm-dd 형식).
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        df = pd.DataFrame.from_dict(data, orient='index')
        df.index = pd.to_datetime(df.index, format='%y-%m-%d')
        df = df.sort_index()

        # 백테스트 시작 날짜 이후의 데이터만 사용
        start_date = datetime.strptime(start_date_str, '%y-%m-%d')
        df_backtest = df[df.index >= start_date].copy()

        if df_backtest.empty:
            print(f"오류: 백테스트 시작 날짜({start_date_str}) 이후의 데이터가 없습니다.")
            return

        # --- 전략 백테스트 ---
        current_stock_type = initial_stock_type
        current_shares = initial_shares
        cash = 0.0 # 배당금 및 매매 후 남은 현금
        
        strategy_portfolio_values = [] # 일별 전략 포트폴리오 가치 저장
        
        first_day_data = df_backtest.iloc[0]
        if current_stock_type == '삼성전자':
            initial_value = current_shares * first_day_data['Stock1_Open']
        else: # 삼성전자(우)
            initial_value = current_shares * first_day_data['Stock2_Open']
        
        print(f"백테스트 시작: {start_date_str}")
        print(f"초기 보유: {initial_shares}주 {initial_stock_type} (시가 기준 초기 가치: {initial_value:,.2f}원)")

        for i, (date, row) in enumerate(df_backtest.iterrows()):
            # 첫 날의 평가 금액 기록
            if i == 0:
                current_portfolio_value = initial_value
            else:
                prev_date = df_backtest.index[i-1]
                prev_row = df_backtest.loc[prev_date]

                current_ratio = prev_row['Price_Diff_Ratio']
                q25 = prev_row['Price_Diff_Ratio_25th_Percentile']
                q75 = prev_row['Price_Diff_Ratio_75th_Percentile']

                # 매매 조건 확인
                if current_ratio < q25 and current_stock_type != '삼성전자':
                    action = "삼성전자(우) -> 삼성전자"
                    sell_value = current_shares * row['Stock2_Open']
                    cash += sell_value
                    buy_shares = cash / row['Stock1_Open']
                    cash -= buy_shares * row['Stock1_Open']
                    current_shares = buy_shares
                    current_stock_type = '삼성전자'

                elif current_ratio > q75 and current_stock_type != '삼성전자(우)':
                    action = "삼성전자 -> 삼성전자(우)"
                    sell_value = current_shares * row['Stock1_Open']
                    cash += sell_value
                    buy_shares = cash / row['Stock2_Open']
                    cash -= buy_shares * row['Stock2_Open']
                    current_shares = buy_shares
                    current_stock_type = '삼성전자(우)'
                
                # 배당금 처리
                if row['Dividend_Amount_Raw'] > 0: # 원본 배당금 사용
                    dividend_income = current_shares * row['Dividend_Amount_Raw']
                    cash += dividend_income

            # 현재 포트폴리오 가치 계산 (종가 기준)
            if current_stock_type == '삼성전자':
                current_portfolio_value = current_shares * row['Stock1_Close'] + cash
            else:
                current_portfolio_value = current_shares * row['Stock2_Close'] + cash
            
            strategy_portfolio_values.append({'Date': date, 'Value': current_portfolio_value})

        last_day_data = df_backtest.iloc[-1]
        final_stock_value_strategy = 0.0
        if current_stock_type == '삼성전자':
            final_stock_value_strategy = current_shares * last_day_data['Stock1_Close']
        else:
            final_stock_value_strategy = current_shares * last_day_data['Stock2_Close']
        
        # 최종 총 자산 가치 (주식 + 현금) - 출력용
        final_total_value_strategy = final_stock_value_strategy + cash
        # 배당금을 제외한 수익률 계산
        return_without_dividends_strategy = ((final_stock_value_strategy - initial_value) / initial_value) * 100

        print("\n--- 전략 백테스트 결과 ---")
        print(f"백테스트 종료: {df_backtest.index[-1].strftime('%y-%m-%d')}")
        print(f"최종 보유: {current_shares:,.2f}주 {current_stock_type}")
        print(f"최종 현금 (배당금 포함): {cash:,.2f}원")
        print(f"최종 총 자산 가치 (주식 + 현금): {final_total_value_strategy:,.2f}원")
        print(f"초기 자산 가치: {initial_value:,.2f}원")
        print(f"총 수익률 (배당금 제외): {return_without_dividends_strategy:,.2f}%")

        # --- 삼성전자 Buy & Hold 전략 ---
        print("\n--- 삼성전자 Buy & Hold 결과 ---")
        buy_hold_initial_shares = 1000
        buy_hold_initial_value = buy_hold_initial_shares * first_day_data['Stock1_Open']
        
        buy_hold_portfolio_values = [] # 일별 Buy & Hold 포트폴리오 가치 저장
        accumulated_buy_hold_dividends = 0.0 # 누적 배당금

        # 삼성전자 보통주 배당금 데이터 (Investing.com에서 추출)
        dividend_history_elec = [
            {"Ex-dividend Date": "6월 26, 2025", "Dividend": 361.00},
            {"Ex-dividend Date": "3월 27, 2025", "Dividend": 365.00},
            {"Ex-dividend Date": "12월 26, 2024", "Dividend": 363.00},
            {"Ex-dividend Date": "9월 26, 2024", "Dividend": 361.00},
            {"Ex-dividend Date": "6월 26, 2024", "Dividend": 361.00},
            {"Ex-dividend Date": "3월 27, 2024", "Dividend": 361.00},
            {"Ex-dividend Date": "12월 26, 2023", "Dividend": 361.00},
            {"Ex-dividend Date": "9월 25, 2023", "Dividend": 361.00},
            {"Ex-dividend Date": "6월 28, 2023", "Dividend": 361.00},
            {"Ex-dividend Date": "3월 29, 2023", "Dividend": 361.00},
            {"Ex-dividend Date": "12월 27, 2022", "Dividend": 361.00},
            {"Ex-dividend Date": "9월 28, 2022", "Dividend": 361.00},
            {"Ex-dividend Date": "6월 28, 2022", "Dividend": 361.00},
            {"Ex-dividend Date": "3월 29, 2022", "Dividend": 361.00},
            {"Ex-dividend Date": "12월 28, 2021", "Dividend": 361.00},
            {"Ex-dividend Date": "9월 28, 2021", "Dividend": 361.00},
            {"Ex-dividend Date": "6월 28, 2021", "Dividend": 361.00},
            {"Ex-dividend Date": "3월 29, 2021", "Dividend": 361.00},
            {"Ex-dividend Date": "12월 28, 2020", "Dividend": 1932.00},
            {"Ex-dividend Date": "9월 27, 2020", "Dividend": 354.00}
        ]

        external_dividends_elec_series = pd.Series({
            pd.to_datetime(item["Ex-dividend Date"], format='%m월 %d, %Y'): item["Dividend"]
            for item in dividend_history_elec
        }).sort_index()

        for date, row in df_backtest.iterrows():
            # 배당금 누적
            if date in external_dividends_elec_series.index:
                accumulated_buy_hold_dividends += external_dividends_elec_series.loc[date] * buy_hold_initial_shares
            
            buy_hold_daily_value = buy_hold_initial_shares * row['Stock1_Close'] + accumulated_buy_hold_dividends
            buy_hold_portfolio_values.append({'Date': date, 'Value': buy_hold_daily_value})

        buy_hold_final_value = buy_hold_initial_shares * last_day_data['Stock1_Close']
        buy_hold_final_total_value = buy_hold_final_value + accumulated_buy_hold_dividends
        # 배당금을 제외한 수익률 계산
        return_without_dividends_buy_hold = ((buy_hold_final_value - buy_hold_initial_value) / buy_hold_initial_value) * 100

        print(f"초기 보유: {buy_hold_initial_shares}주 삼성전자 (시가 기준 초기 가치: {buy_hold_initial_value:,.2f}원)")
        print(f"최종 보유: {buy_hold_initial_shares}주 삼성전자")
        print(f"최종 주식 가치: {buy_hold_final_value:,.2f}원")
        print(f"총 배당금 수령: {accumulated_buy_hold_dividends:,.2f}원")
        print(f"최종 총 자산 가치 (주식 + 배당금): {buy_hold_final_total_value:,.2f}원")
        print(f"총 수익률 (배당금 제외): {return_without_dividends_buy_hold:,.2f}%")

        # --- 그래프 생성 및 저장 ---
        strategy_df = pd.DataFrame(strategy_portfolio_values).set_index('Date')
        buy_hold_df = pd.DataFrame(buy_hold_portfolio_values).set_index('Date')

        # 월별 1일 데이터 추출
        monthly_strategy_df = strategy_df.resample('MS').first()
        monthly_buy_hold_df = buy_hold_df.resample('MS').first()

        plt.figure(figsize=(15, 8))
        plt.plot(monthly_strategy_df.index, monthly_strategy_df['Value'], label='전략 백테스트', marker='o', markersize=4)
        plt.plot(monthly_buy_hold_df.index, monthly_buy_hold_df['Value'], label='삼성전자 Buy & Hold', marker='x', markersize=4)

        plt.title('월별 포트폴리오 평가 금액 비교 (배당금 포함)')
        plt.xlabel('날짜')
        plt.ylabel('평가 금액 (원)')
        plt.grid(True)
        plt.legend()

        # X축 날짜 포맷 및 세로로 표시
        plt.xticks(rotation=90)
        plt.tight_layout() # 레이블이 잘리지 않도록 조정

        plot_output_path = r'./portfolio_comparison.png'
        plt.savefig(plot_output_path)
        print(f"\n월별 포트폴리오 평가 금액 그래프가 {plot_output_path}에 저장되었습니다.")
        # plt.show() # 화면에 표시하지 않음

    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다. 경로를 확인해주세요: {json_file_path}")
    except json.JSONDecodeError:
        print(f"오류: JSON 파일을 디코딩할 수 없습니다. 파일 형식을 확인해주세요: {json_file_path}")
    except Exception as e:
        print(f"데이터 처리 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    json_file = r'./samsung_stock_analysis.json'
    initial_stock = '삼성전자'
    initial_shares = 1000
    start_date_backtest = '05-01-03' # 2022년 1월 첫 거래일

    run_backtest(json_file, initial_stock, initial_shares, start_date_backtest)

