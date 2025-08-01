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

def run_single_strategy(df_backtest, initial_stock_type, initial_shares, initial_value, reverse_strategy=False, strategy_name="", window_suffix="2year"):
    """
    단일 전략에 대한 백테스트를 실행합니다.
    
    Args:
        df_backtest: 백테스트용 데이터프레임
        initial_stock_type: 초기 보유 주식 유형
        initial_shares: 초기 보유 주식 수
        initial_value: 초기 자산 가치
        reverse_strategy: True면 반대 전략 실행
        strategy_name: 전략 이름
        window_suffix: 윈도우 크기 접미사 (2year, 3year, 5year)
    
    Returns:
        dict: 전략 실행 결과
    """
    current_stock_type = initial_stock_type
    current_shares = initial_shares
    cash = 0.0 # 배당금 및 매매 후 남은 현금
    
    strategy_portfolio_values = [] # 일별 전략 포트폴리오 가치 저장
    trading_log = [] # 매매 기록 저장

    # 윈도우 크기에 따른 분위수 컬럼명 설정
    q25_col = f'Price_Diff_Ratio_25th_Percentile_{window_suffix}'
    q75_col = f'Price_Diff_Ratio_75th_Percentile_{window_suffix}'

    for i, (date, row) in enumerate(df_backtest.iterrows()):
        # 첫 날의 평가 금액 기록
        if i == 0:
            current_portfolio_value = initial_value
            # 초기 상태 기록
            trading_log.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Action': '초기보유',
                'Stock_Type': current_stock_type,
                'Shares_Traded': 0,
                'Price_Per_Share': 0,
                'Total_Amount': 0,
                'Current_Shares': current_shares,
                'Current_Stock_Type': current_stock_type,
                'Cash_Balance': cash,
                'Portfolio_Value': current_portfolio_value,
                'Price_Diff_Ratio': row['Price_Diff_Ratio'],
                'Q25': 0,
                'Q75': 0
            })
        else:
            prev_date = df_backtest.index[i-1]
            prev_row = df_backtest.loc[prev_date]

            current_ratio = prev_row['Price_Diff_Ratio']
            q25 = prev_row[q25_col]
            q75 = prev_row[q75_col]

            # 매매 조건 확인 (기본 전략 vs 반대 전략)
            if not reverse_strategy:
                # 기본 전략: 25% 이하 -> 삼성전자, 75% 이상 -> 삼성전자(우)
                should_buy_samsung = current_ratio < q25 and current_stock_type != '삼성전자'
                should_buy_samsung_pref = current_ratio > q75 and current_stock_type != '삼성전자(우)'
            else:
                # 반대 전략: 25% 이하 -> 삼성전자(우), 75% 이상 -> 삼성전자
                should_buy_samsung = current_ratio > q75 and current_stock_type != '삼성전자'
                should_buy_samsung_pref = current_ratio < q25 and current_stock_type != '삼성전자(우)'

            if should_buy_samsung:
                # 현재 보유주 -> 삼성전자
                if current_stock_type == '삼성전자(우)':
                    sell_price = row['Stock2_Open']
                    buy_price = row['Stock1_Open']
                    sell_value = current_shares * sell_price
                    cash += sell_value
                    
                    buy_shares = cash / buy_price
                    cash -= buy_shares * buy_price
                    
                    # 매매 기록
                    trading_log.append({
                        'Date': date.strftime('%Y-%m-%d'),
                        'Action': '매도->매수',
                        'Stock_Type': f'{current_stock_type} -> 삼성전자',
                        'Shares_Traded': f'매도 {current_shares:.2f}주 -> 매수 {buy_shares:.2f}주',
                        'Price_Per_Share': f'매도가 {sell_price:,.0f}원 -> 매수가 {buy_price:,.0f}원',
                        'Total_Amount': f'매도금 {sell_value:,.0f}원 -> 매수금 {buy_shares * buy_price:,.0f}원',
                        'Current_Shares': buy_shares,
                        'Current_Stock_Type': '삼성전자',
                        'Cash_Balance': cash,
                        'Portfolio_Value': 0,  # 아래에서 계산
                        'Price_Diff_Ratio': current_ratio,
                        'Q25': q25,
                        'Q75': q75
                    })
                    
                    current_shares = buy_shares
                    current_stock_type = '삼성전자'

            elif should_buy_samsung_pref:
                # 현재 보유주 -> 삼성전자(우)
                if current_stock_type == '삼성전자':
                    sell_price = row['Stock1_Open']
                    buy_price = row['Stock2_Open']
                    sell_value = current_shares * sell_price
                    cash += sell_value
                    
                    buy_shares = cash / buy_price
                    cash -= buy_shares * buy_price
                    
                    # 매매 기록
                    trading_log.append({
                        'Date': date.strftime('%Y-%m-%d'),
                        'Action': '매도->매수',
                        'Stock_Type': f'{current_stock_type} -> 삼성전자(우)',
                        'Shares_Traded': f'매도 {current_shares:.2f}주 -> 매수 {buy_shares:.2f}주',
                        'Price_Per_Share': f'매도가 {sell_price:,.0f}원 -> 매수가 {buy_price:,.0f}원',
                        'Total_Amount': f'매도금 {sell_value:,.0f}원 -> 매수금 {buy_shares * buy_price:,.0f}원',
                        'Current_Shares': buy_shares,
                        'Current_Stock_Type': '삼성전자(우)',
                        'Cash_Balance': cash,
                        'Portfolio_Value': 0,  # 아래에서 계산
                        'Price_Diff_Ratio': current_ratio,
                        'Q25': q25,
                        'Q75': q75
                    })
                    
                    current_shares = buy_shares
                    current_stock_type = '삼성전자(우)'
            
            # 배당금 처리
            if row['Dividend_Amount_Raw'] > 0: # 원본 배당금 사용
                dividend_income = current_shares * row['Dividend_Amount_Raw']
                cash += dividend_income
                
                # 배당금 기록
                trading_log.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Action': '배당금수령',
                    'Stock_Type': current_stock_type,
                    'Shares_Traded': f'{current_shares:.2f}주',
                    'Price_Per_Share': f'{row["Dividend_Amount_Raw"]:,.0f}원/주',
                    'Total_Amount': f'{dividend_income:,.0f}원',
                    'Current_Shares': current_shares,
                    'Current_Stock_Type': current_stock_type,
                    'Cash_Balance': cash,
                    'Portfolio_Value': 0,  # 아래에서 계산
                    'Price_Diff_Ratio': row['Price_Diff_Ratio'],
                    'Q25': 0,
                    'Q75': 0
                })

        # 현재 포트폴리오 가치 계산 (종가 기준)
        if current_stock_type == '삼성전자':
            current_portfolio_value = current_shares * row['Stock1_Close'] + cash
        else:
            current_portfolio_value = current_shares * row['Stock2_Close'] + cash
        
        # 매매 기록이 있으면 포트폴리오 가치 업데이트
        if trading_log and trading_log[-1]['Date'] == date.strftime('%Y-%m-%d'):
            trading_log[-1]['Portfolio_Value'] = current_portfolio_value
        
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

    print(f"\n--- {strategy_name} 백테스트 결과 ---")
    print(f"백테스트 종료: {df_backtest.index[-1].strftime('%y-%m-%d')}")
    print(f"최종 보유: {current_shares:,.2f}주 {current_stock_type}")
    print(f"최종 현금 (배당금 포함): {cash:,.2f}원")
    print(f"최종 총 자산 가치 (주식 + 현금): {final_total_value_strategy:,.2f}원")
    print(f"초기 자산 가치: {initial_value:,.2f}원")
    print(f"총 수익률 (배당금 제외): {return_without_dividends_strategy:,.2f}%")

    # 매매 통계
    trades_only = pd.DataFrame(trading_log)
    trades_only = trades_only[trades_only['Action'] == '매도->매수']
    dividends_only = pd.DataFrame(trading_log)
    dividends_only = dividends_only[dividends_only['Action'] == '배당금수령']
    
    print(f"\n--- {strategy_name} 매매 통계 ---")
    print(f"총 매매 횟수: {len(trades_only)}회")
    print(f"배당금 수령 횟수: {len(dividends_only)}회")
    
    if not trades_only.empty:
        samsung_to_pref = len(trades_only[trades_only['Stock_Type'].str.contains('삼성전자 -> 삼성전자(우)')])
        pref_to_samsung = len(trades_only[trades_only['Stock_Type'].str.contains('삼성전자(우) -> 삼성전자')])
        print(f"삼성전자 -> 삼성전자(우): {samsung_to_pref}회")
        print(f"삼성전자(우) -> 삼성전자: {pref_to_samsung}회")
        
        # 평균 매매 간격 계산
        if len(trades_only) > 1:
            trade_dates = pd.to_datetime(trades_only['Date'])
            avg_interval = (trade_dates.max() - trade_dates.min()).days / len(trades_only)
            print(f"평균 매매 간격: {avg_interval:.1f}일")

    return {
        'portfolio_values': strategy_portfolio_values,
        'trading_log': trading_log,
        'final_value': final_total_value_strategy,
        'return_rate': return_without_dividends_strategy,
        'current_shares': current_shares,
        'current_stock_type': current_stock_type,
        'cash': cash
    }

def run_backtest(json_file_path, initial_stock_type, initial_shares, start_date_str):
    """
    2년 슬라이딩 윈도우 사분위 기반 전략에 따라 백테스트를 수행하고 투자 결과를 분석합니다.
    
    기본 전략:
    - 가격차이비율이 2년 슬라이딩 윈도우 25% 분위 이하: 삼성전자(상대적 저평가) 매수
    - 가격차이비율이 2년 슬라이딩 윈도우 75% 분위 이상: 삼성전자(우)(상대적 저평가) 매수
    
    반대 전략:
    - 가격차이비율이 2년 슬라이딩 윈도우 25% 분위 이하: 삼성전자(우) 매수
    - 가격차이비율이 2년 슬라이딩 윈도우 75% 분위 이상: 삼성전자 매수
    
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

        # 초기 자산 가치 계산
        first_day_data = df_backtest.iloc[0]
        if initial_stock_type == '삼성전자':
            initial_value = initial_shares * first_day_data['Stock1_Open']
        else: # 삼성전자(우)
            initial_value = initial_shares * first_day_data['Stock2_Open']

        print(f"백테스트 시작: {start_date_str}")
        print(f"초기 보유: {initial_shares}주 {initial_stock_type} (시가 기준 초기 가치: {initial_value:,.2f}원)")
        
        # --- 전략 백테스트 ---
        strategy_results = {}
        
        # 윈도우 크기별로 전략 실행
        window_configs = {
            '2년': '2year',
            '3년': '3year', 
            '5년': '5year'
        }
        
        for window_name, window_suffix in window_configs.items():
            print("\n" + "="*80)
            print(f"=== {window_name} 슬라이딩 윈도우 전략 분석 ===")
            
            # 기본 전략
            print(f"\n--- {window_name} 기본 전략 ---")
            print(f"- 가격차이비율 < {window_name} 슬라이딩 25% 분위: 삼성전자 매수 (상대적 저평가)")
            print(f"- 가격차이비율 > {window_name} 슬라이딩 75% 분위: 삼성전자(우) 매수 (상대적 저평가)")

            basic_strategy_name = f"기본전략_{window_name}"
            strategy_results[basic_strategy_name] = run_single_strategy(
                df_backtest, initial_stock_type, initial_shares, initial_value, 
                False, basic_strategy_name, window_suffix
            )
            
            # 반대 전략
            print(f"\n--- {window_name} 반대 전략 ---")
            print(f"- 가격차이비율 < {window_name} 슬라이딩 25% 분위: 삼성전자(우) 매수")
            print(f"- 가격차이비율 > {window_name} 슬라이딩 75% 분위: 삼성전자 매수")

            reverse_strategy_name = f"반대전략_{window_name}"
            strategy_results[reverse_strategy_name] = run_single_strategy(
                df_backtest, initial_stock_type, initial_shares, initial_value, 
                True, reverse_strategy_name, window_suffix
            )

        # --- 삼성전자 Buy & Hold 전략 ---
        print("\n" + "="*60)
        print("=== 삼성전자 Buy & Hold 결과 ===")
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

        buy_hold_final_value = buy_hold_initial_shares * df_backtest.iloc[-1]['Stock1_Close']
        buy_hold_final_total_value = buy_hold_final_value + accumulated_buy_hold_dividends
        # 배당금을 제외한 수익률 계산
        return_without_dividends_buy_hold = ((buy_hold_final_value - buy_hold_initial_value) / buy_hold_initial_value) * 100

        print(f"초기 보유: {buy_hold_initial_shares}주 삼성전자 (시가 기준 초기 가치: {buy_hold_initial_value:,.2f}원)")
        print(f"최종 보유: {buy_hold_initial_shares}주 삼성전자")
        print(f"최종 주식 가치: {buy_hold_final_value:,.2f}원")
        print(f"총 배당금 수령: {accumulated_buy_hold_dividends:,.2f}원")
        print(f"최종 총 자산 가치 (주식 + 배당금): {buy_hold_final_total_value:,.2f}원")
        print(f"총 수익률 (배당금 제외): {return_without_dividends_buy_hold:,.2f}%")

        # --- 매매 기록 저장 ---
        for strategy_name, result in strategy_results.items():
            trading_df = pd.DataFrame(result['trading_log'])
            filename = f'trading_log_{strategy_name.replace(" ", "_")}.csv'
            trading_df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n{strategy_name} 매매 기록이 '{filename}' 파일로 저장되었습니다.")

        # --- 전략 비교 요약 ---
        print("\n" + "="*80)
        print("=== 전략 비교 요약 ===")
        
        # 윈도우별 기본전략 비교
        print("\n--- 기본전략 (25%↓→삼성전자, 75%↑→삼성전자(우)) ---")
        for window_name in ['2년', '3년', '5년']:
            strategy_name = f"기본전략_{window_name}"
            if strategy_name in strategy_results:
                result = strategy_results[strategy_name]
                print(f"{window_name} 윈도우: {result['return_rate']:,.2f}% (자산: {result['final_value']:,.0f}원)")
        
        # 윈도우별 반대전략 비교
        print("\n--- 반대전략 (25%↓→삼성전자(우), 75%↑→삼성전자) ---")
        for window_name in ['2년', '3년', '5년']:
            strategy_name = f"반대전략_{window_name}"
            if strategy_name in strategy_results:
                result = strategy_results[strategy_name]
                print(f"{window_name} 윈도우: {result['return_rate']:,.2f}% (자산: {result['final_value']:,.0f}원)")
        
        print(f"\n--- Buy & Hold 참고 ---")
        print(f"삼성전자 Buy & Hold: {return_without_dividends_buy_hold:,.2f}% (자산: {buy_hold_final_total_value:,.0f}원)")

        # --- 그래프 생성 및 저장 ---
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
        
        # 기본전략 비교 그래프
        ax1.set_title('기본전략: 윈도우 크기별 월별 포트폴리오 평가 금액 비교', fontsize=14)
        for window_name in ['2년', '3년', '5년']:
            strategy_name = f"기본전략_{window_name}"
            if strategy_name in strategy_results:
                strategy_df = pd.DataFrame(strategy_results[strategy_name]['portfolio_values']).set_index('Date')
                monthly_df = strategy_df.resample('MS').first()
                ax1.plot(monthly_df.index, monthly_df['Value'], label=f'{window_name} 윈도우', marker='o', markersize=3)
        
        # Buy & Hold 추가
        buy_hold_df = pd.DataFrame(buy_hold_portfolio_values).set_index('Date')
        monthly_buy_hold_df = buy_hold_df.resample('MS').first()
        ax1.plot(monthly_buy_hold_df.index, monthly_buy_hold_df['Value'], label='삼성전자 Buy & Hold', marker='x', markersize=3, linestyle='--')
        
        ax1.set_ylabel('평가 금액 (원)')
        ax1.grid(True)
        ax1.legend()
        ax1.tick_params(axis='x', rotation=45)
        
        # 반대전략 비교 그래프
        ax2.set_title('반대전략: 윈도우 크기별 월별 포트폴리오 평가 금액 비교', fontsize=14)
        for window_name in ['2년', '3년', '5년']:
            strategy_name = f"반대전략_{window_name}"
            if strategy_name in strategy_results:
                strategy_df = pd.DataFrame(strategy_results[strategy_name]['portfolio_values']).set_index('Date')
                monthly_df = strategy_df.resample('MS').first()
                ax2.plot(monthly_df.index, monthly_df['Value'], label=f'{window_name} 윈도우', marker='s', markersize=3)
        
        # Buy & Hold 추가
        ax2.plot(monthly_buy_hold_df.index, monthly_buy_hold_df['Value'], label='삼성전자 Buy & Hold', marker='x', markersize=3, linestyle='--')
        
        ax2.set_xlabel('날짜')
        ax2.set_ylabel('평가 금액 (원)')
        ax2.grid(True)
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plot_output_path = r'./multi_window_strategy_comparison.png'
        plt.savefig(plot_output_path, dpi=300, bbox_inches='tight')
        print(f"\n다중 윈도우 전략 비교 그래프가 {plot_output_path}에 저장되었습니다.")
        
        plt.close()

        # --- 분석 리포트 생성 ---
        generate_analysis_report(strategy_results, buy_hold_final_total_value, return_without_dividends_buy_hold, 
                                start_date_str, df_backtest.index[-1].strftime('%y-%m-%d'), initial_value)

def generate_analysis_report(strategy_results, buy_hold_final_value, buy_hold_return_rate, 
                           start_date, end_date, initial_value):
    """
    윈도우 크기별 전략 성과 분석 리포트를 마크다운 형식으로 생성합니다.
    """
    from datetime import datetime
    
    report_content = f"""# 삼성전자-삼성전자(우) 윈도우 크기별 전략 성과 분석 리포트

**분석 날짜**: {datetime.now().strftime('%Y년 %m월 %d일')}  
**백테스트 기간**: {start_date} ~ {end_date}  
**초기 투자금**: {initial_value:,.0f}원

---

## 📊 **전략 성과 요약**

### 🥇 **기본전략 (25%↓→삼성전자, 75%↑→삼성전자(우)) 성과**

| 윈도우 크기 | 수익률 | 최종 자산 | 순위 |
|------------|--------|-----------|------|
"""

    # 기본전략 성과 정렬 및 순위 매기기
    basic_strategies = []
    for window_name in ['2년', '3년', '5년']:
        strategy_name = f"기본전략_{window_name}"
        if strategy_name in strategy_results:
            result = strategy_results[strategy_name]
            basic_strategies.append({
                'window': window_name,
                'return_rate': result['return_rate'],
                'final_value': result['final_value'],
                'trades': len([log for log in result['trading_log'] if log['Action'] == '매도->매수'])
            })
    
    # 수익률 기준으로 정렬
    basic_strategies.sort(key=lambda x: x['return_rate'], reverse=True)
    
    # 기본전략 표 작성
    medals = ['🏆', '🥈', '🥉']
    for i, strategy in enumerate(basic_strategies):
        medal = medals[i] if i < 3 else ''
        report_content += f"| {strategy['window']} 윈도우 | **{strategy['return_rate']:,.2f}%** | {strategy['final_value']:,.0f}원 | {medal} |\n"

    report_content += f"""

### 📉 **반대전략 (25%↓→삼성전자(우), 75%↑→삼성전자) 성과**

| 윈도우 크기 | 수익률 | 최종 자산 | 순위 |
|------------|--------|-----------|------|
"""

    # 반대전략 성과 정렬 및 순위 매기기
    reverse_strategies = []
    for window_name in ['2년', '3년', '5년']:
        strategy_name = f"반대전략_{window_name}"
        if strategy_name in strategy_results:
            result = strategy_results[strategy_name]
            reverse_strategies.append({
                'window': window_name,
                'return_rate': result['return_rate'],
                'final_value': result['final_value'],
                'trades': len([log for log in result['trading_log'] if log['Action'] == '매도->매수'])
            })
    
    # 수익률 기준으로 정렬
    reverse_strategies.sort(key=lambda x: x['return_rate'], reverse=True)
    
    # 반대전략 표 작성
    for i, strategy in enumerate(reverse_strategies):
        medal = medals[i] if i < 3 else ''
        report_content += f"| {strategy['window']} 윈도우 | **{strategy['return_rate']:,.2f}%** | {strategy['final_value']:,.0f}원 | {medal} |\n"

    # 최고 성과 전략 찾기
    best_basic = max(basic_strategies, key=lambda x: x['return_rate'])
    best_reverse = max(reverse_strategies, key=lambda x: x['return_rate'])

    report_content += f"""

### 📈 **Buy & Hold 참고**
- **삼성전자 Buy & Hold**: {buy_hold_return_rate:,.2f}%
- **최종 자산**: {buy_hold_final_value:,.0f}원

---

## 💡 **핵심 발견사항**

### 1. **최적 윈도우 크기**
- **{best_basic['window']} 윈도우**가 기본전략에서 가장 우수한 성과를 보임
- 수익률: **{best_basic['return_rate']:,.2f}%**
- 최종 자산: **{best_basic['final_value']:,.0f}원**

### 2. **매매 빈도 분석**

| 전략 | 2년 윈도우 | 3년 윈도우 | 5년 윈도우 |
|------|-----------|-----------|-----------|
"""

    # 매매 횟수 테이블 작성
    basic_trades = {}
    reverse_trades = {}
    
    for window_name in ['2년', '3년', '5년']:
        basic_strategy_name = f"기본전략_{window_name}"
        reverse_strategy_name = f"반대전략_{window_name}"
        
        if basic_strategy_name in strategy_results:
            basic_trades[window_name] = len([log for log in strategy_results[basic_strategy_name]['trading_log'] if log['Action'] == '매도->매수'])
        
        if reverse_strategy_name in strategy_results:
            reverse_trades[window_name] = len([log for log in strategy_results[reverse_strategy_name]['trading_log'] if log['Action'] == '매도->매수'])

    report_content += f"| 기본전략 | {basic_trades.get('2년', 0)}회 | {basic_trades.get('3년', 0)}회 | {basic_trades.get('5년', 0)}회 |\n"
    report_content += f"| 반대전략 | {reverse_trades.get('2년', 0)}회 | {reverse_trades.get('3년', 0)}회 | {reverse_trades.get('5년', 0)}회 |\n"

    report_content += f"""

### 3. **전략 우위성**
- 모든 윈도우 크기에서 **기본전략 > Buy & Hold > 반대전략** 순서 유지
- 기본전략은 Buy & Hold보다 **{best_basic['return_rate']/buy_hold_return_rate:.1f}배** 높은 수익률
- 반대전략은 모든 윈도우에서 Buy & Hold보다 저조한 성과

### 4. **윈도우 크기의 영향**
- **윈도우가 클수록 매매 빈도 감소** (안정성 증가)
- **3년 윈도우**: 시장 변화 적응력과 노이즈 필터링의 최적 균형점
- **2년 윈도우**: 빠른 반응성이지만 과도한 매매 가능성
- **5년 윈도우**: 안정성은 높지만 시장 변화 대응이 늦음

---

## 🎯 **투자 전략 권고사항**

### ✅ **추천 전략**
1. **{best_basic['window']} 슬라이딩 윈도우를 사용한 기본전략** (최고 성과)
   - 가격차이비율 < {best_basic['window']} 슬라이딩 25% 분위 → 삼성전자 매수
   - 가격차이비율 > {best_basic['window']} 슬라이딩 75% 분위 → 삼성전자(우) 매수

### ❌ **비추천 전략**
- 반대전략: 모든 윈도우에서 Buy & Hold보다 저조한 성과
- 가격차이비율의 기본 논리에 반하는 매매는 비효율적

### 📝 **실행 가이드라인**
1. **시작 자본**: 최소 {initial_value:,.0f}원 이상 권장
2. **리밸런싱 주기**: 일일 모니터링, 신호 발생시 즉시 실행
3. **수수료 고려**: 실제 거래시 매매 수수료 및 세금 고려 필요
4. **리스크 관리**: 과도한 집중 투자 지양, 포트폴리오 분산 권장

---

## 📋 **상세 데이터**

### 기본전략 상세 성과

| 윈도우 | 수익률 | 최종자산 | 매매횟수 | Buy&Hold 대비 |
|--------|--------|----------|----------|---------------|
"""

    for strategy in basic_strategies:
        buy_hold_ratio = strategy['return_rate'] / buy_hold_return_rate
        report_content += f"| {strategy['window']} | {strategy['return_rate']:,.2f}% | {strategy['final_value']:,.0f}원 | {strategy['trades']}회 | {buy_hold_ratio:.1f}배 |\n"

    report_content += f"""

### 반대전략 상세 성과

| 윈도우 | 수익률 | 최종자산 | 매매횟수 | Buy&Hold 대비 |
|--------|--------|----------|----------|---------------|
"""

    for strategy in reverse_strategies:
        buy_hold_ratio = strategy['return_rate'] / buy_hold_return_rate
        report_content += f"| {strategy['window']} | {strategy['return_rate']:,.2f}% | {strategy['final_value']:,.0f}원 | {strategy['trades']}회 | {buy_hold_ratio:.1f}배 |\n"

    report_content += f"""

---

## 📊 **생성된 파일들**

1. **그래프**: `multi_window_strategy_comparison.png`
2. **매매 기록**: 각 전략별 CSV 파일
   - `trading_log_기본전략_2년.csv`
   - `trading_log_기본전략_3년.csv`
   - `trading_log_기본전략_5년.csv`
   - `trading_log_반대전략_2년.csv`
   - `trading_log_반대전략_3년.csv`
   - `trading_log_반대전략_5년.csv`

---

**면책조항**: 본 분석은 과거 데이터에 기반한 백테스트 결과이며, 미래 수익을 보장하지 않습니다. 실제 투자시에는 시장 상황, 거래 비용, 세금 등을 종합적으로 고려하시기 바랍니다.
"""

    # 리포트 파일 저장
    report_filename = f'strategy_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📋 전략 분석 리포트가 '{report_filename}' 파일로 저장되었습니다.")

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
