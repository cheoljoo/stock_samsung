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
        trading_log = [] # 매매 기록 저장
        
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
                q25 = prev_row['Price_Diff_Ratio_25th_Percentile']
                q75 = prev_row['Price_Diff_Ratio_75th_Percentile']

                # 매매 조건 확인
                if current_ratio < q25 and current_stock_type != '삼성전자':
                    # 삼성전자(우) -> 삼성전자
                    sell_price = row['Stock2_Open']
                    sell_value = current_shares * sell_price
                    cash += sell_value
                    
                    buy_price = row['Stock1_Open']
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

                elif current_ratio > q75 and current_stock_type != '삼성전자(우)':
                    # 삼성전자 -> 삼성전자(우)
                    sell_price = row['Stock1_Open']
                    sell_value = current_shares * sell_price
                    cash += sell_value
                    
                    buy_price = row['Stock2_Open']
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

        print("\n--- 전략 백테스트 결과 ---")
        print(f"백테스트 종료: {df_backtest.index[-1].strftime('%y-%m-%d')}")
        print(f"최종 보유: {current_shares:,.2f}주 {current_stock_type}")
        print(f"최종 현금 (배당금 포함): {cash:,.2f}원")
        print(f"최종 총 자산 가치 (주식 + 현금): {final_total_value_strategy:,.2f}원")
        print(f"초기 자산 가치: {initial_value:,.2f}원")
        print(f"총 수익률 (배당금 제외): {return_without_dividends_strategy:,.2f}%")

        # 매매 기록 출력 및 저장
        print(f"\n--- 매매 기록 (총 {len(trading_log)}건) ---")
        trading_df = pd.DataFrame(trading_log)
        
        # 매매 관련 기록만 필터링 (초기보유 제외)
        actual_trades = trading_df[trading_df['Action'].isin(['매도->매수', '배당금수령'])]
        
        if not actual_trades.empty:
            print("주요 매매 기록:")
            for idx, trade in actual_trades.head(10).iterrows():  # 최근 10건만 출력
                print(f"  {trade['Date']}: {trade['Action']} - {trade['Stock_Type']}")
                print(f"    거래내용: {trade['Shares_Traded']}")
                print(f"    가격: {trade['Price_Per_Share']}")
                print(f"    금액: {trade['Total_Amount']}")
                print(f"    보유현황: {trade['Current_Shares']:.2f}주 ({trade['Current_Stock_Type']})")
                print(f"    현금잔액: {trade['Cash_Balance']:,.0f}원")
                print(f"    포트폴리오가치: {trade['Portfolio_Value']:,.0f}원")
                if trade['Action'] == '매도->매수':
                    print(f"    Price_Diff_Ratio: {trade['Price_Diff_Ratio']:.2f}% (Q25: {trade['Q25']:.2f}%, Q75: {trade['Q75']:.2f}%)")
                print()
            
            if len(actual_trades) > 10:
                print(f"... 총 {len(actual_trades)}건 중 최근 10건만 표시")
        
        # 매매 기록을 CSV 파일로 저장
        trading_df.to_csv('trading_log.csv', index=False, encoding='utf-8-sig')
        print(f"전체 매매 기록이 'trading_log.csv' 파일로 저장되었습니다.")
        
        # 매매 통계
        trades_only = trading_df[trading_df['Action'] == '매도->매수']
        dividends_only = trading_df[trading_df['Action'] == '배당금수령']
        
        print(f"\n--- 매매 통계 ---")
        print(f"총 매매 횟수: {len(trades_only)}회")
        print(f"배당금 수령 횟수: {len(dividends_only)}회")
        
        if not trades_only.empty:
            samsung_to_pref = len(trades_only[trades_only['Stock_Type'].str.contains('삼성전자 -> 삼성전자(우)')])
            pref_to_samsung = len(trades_only[trades_only['Stock_Type'].str.contains('삼성전자(우) -> 삼성전자')])
            print(f"삼성전자 -> 삼성전자(우): {samsung_to_pref}회")
            print(f"삼성전자(우) -> 삼성전자: {pref_to_samsung}회")

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
        
        # --- 추가 그래프: 시간에 따른 주식 보유 현황 ---
        print("\n주식 보유 현황 그래프 생성 중...")
        
        # 일별 보유 현황 데이터 준비
        holding_data = []
        for log_entry in trading_log:
            date = pd.to_datetime(log_entry['Date'])
            stock_type = log_entry['Current_Stock_Type']
            shares = log_entry['Current_Shares']
            
            if stock_type == '삼성전자':
                samsung_shares = shares
                samsung_pref_shares = 0
            else:  # 삼성전자(우)
                samsung_shares = 0
                samsung_pref_shares = shares
            
            holding_data.append({
                'Date': date,
                'Samsung_Shares': samsung_shares,
                'Samsung_Pref_Shares': samsung_pref_shares,
                'Total_Shares': shares,
                'Stock_Type': stock_type
            })
        
        # DataFrame으로 변환
        holding_df = pd.DataFrame(holding_data)
        
        # 전체 백테스트 기간의 일별 데이터로 확장 (forward fill)
        all_dates = pd.date_range(start=df_backtest.index.min(), end=df_backtest.index.max(), freq='D')
        holding_df_expanded = holding_df.set_index('Date').reindex(all_dates, method='ffill').fillna(0)
        
        # 그래프 생성
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        fig.suptitle('시간에 따른 주식 보유 현황 (전략 백테스트)', fontsize=16)
        
        # 첫 번째 그래프: 보유 주식 수
        ax1.fill_between(holding_df_expanded.index, 0, holding_df_expanded['Samsung_Shares'], 
                        alpha=0.7, label='삼성전자 보유 주식 수', color='blue')
        ax1.fill_between(holding_df_expanded.index, 0, holding_df_expanded['Samsung_Pref_Shares'], 
                        alpha=0.7, label='삼성전자(우) 보유 주식 수', color='red')
        
        ax1.set_title('보유 주식 수 변화')
        ax1.set_ylabel('주식 수 (주)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 두 번째 그래프: 보유 주식 유형 (0/1로 표시)
        stock_type_numeric = holding_df_expanded['Stock_Type'].map({'삼성전자': 1, '삼성전자(우)': 0})
        
        ax2.fill_between(holding_df_expanded.index, 0, stock_type_numeric, 
                        alpha=0.7, step='pre', color='green')
        ax2.set_title('보유 주식 유형 (1: 삼성전자, 0: 삼성전자(우))')
        ax2.set_ylabel('주식 유형')
        ax2.set_xlabel('날짜')
        ax2.set_ylim(-0.1, 1.1)
        ax2.set_yticks([0, 1])
        ax2.set_yticklabels(['삼성전자(우)', '삼성전자'])
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        holding_plot_path = r'./stock_holding_timeline.png'
        plt.savefig(holding_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"주식 보유 현황 그래프가 {holding_plot_path}에 저장되었습니다.")
        
        # --- 추가 그래프: 매매 시점 표시가 포함된 상세 그래프 ---
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # 보유 주식 수 그래프
        ax.plot(holding_df_expanded.index, holding_df_expanded['Total_Shares'], 
               linewidth=2, color='black', label='총 보유 주식 수')
        
        # 삼성전자 보유 구간
        samsung_mask = holding_df_expanded['Samsung_Shares'] > 0
        ax.fill_between(holding_df_expanded.index, 0, holding_df_expanded['Total_Shares'], 
                       where=samsung_mask, alpha=0.3, color='blue', label='삼성전자 보유 구간')
        
        # 삼성전자(우) 보유 구간  
        pref_mask = holding_df_expanded['Samsung_Pref_Shares'] > 0
        ax.fill_between(holding_df_expanded.index, 0, holding_df_expanded['Total_Shares'], 
                       where=pref_mask, alpha=0.3, color='red', label='삼성전자(우) 보유 구간')
        
        # 매매 시점 표시
        trade_dates = []
        trade_shares = []
        for log_entry in trading_log:
            if log_entry['Action'] == '매도->매수':
                trade_dates.append(pd.to_datetime(log_entry['Date']))
                trade_shares.append(log_entry['Current_Shares'])
        
        if trade_dates:
            ax.scatter(trade_dates, trade_shares, color='orange', s=50, zorder=5, 
                      label=f'매매 시점 ({len(trade_dates)}회)')
        
        ax.set_title('시간에 따른 주식 보유 현황 및 매매 시점')
        ax.set_xlabel('날짜')
        ax.set_ylabel('보유 주식 수 (주)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        detailed_holding_plot_path = r'./detailed_stock_holding_timeline.png'
        plt.savefig(detailed_holding_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"상세 주식 보유 현황 그래프가 {detailed_holding_plot_path}에 저장되었습니다.")
        
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
    start_date_backtest = '20-01-02' # 2020년 1월 2일 (1월 1일이 휴일이므로 첫 거래일)

    run_backtest(json_file, initial_stock, initial_shares, start_date_backtest)

