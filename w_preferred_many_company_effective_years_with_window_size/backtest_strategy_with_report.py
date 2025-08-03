# -*- coding: utf-8 -*-
import pandas as pd
import json
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import platform
import matplotlib.font_manager as fm
import os
import shutil
import argparse

# stock_diff.py에서 회사 정보 가져오기
try:
    from stock_diff import PREFERRED_STOCK_COMPANIES
except ImportError:
    # 기본값으로 삼성전자만 설정
    PREFERRED_STOCK_COMPANIES = {
        "삼성전자": {
            "common_symbol": "005930.KS",
            "preferred_symbol": "005935.KS"
        }
    }

# 나눔고딕 폰트 설정 (경고 메시지 제거)
nanum_font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

# 폰트 경로가 존재하는지 확인하고 설정
if os.path.exists(nanum_font_path):
    print(f"✅ 나눔고딕 폰트 발견: {nanum_font_path}")
    # 폰트를 matplotlib에 등록
    font_prop = fm.FontProperties(fname=nanum_font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    print(f"✅ 나눔고딕 폰트 설정 완료: {font_prop.get_name()}")
else:
    print("⚠️ 나눔고딕 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
    # OS별 기본 한글 폰트 설정
    system_name = platform.system()
    if system_name == 'Windows':
        plt.rcParams['font.family'] = 'Malgun Gothic'
    elif system_name == 'Darwin':  # Mac OS
        plt.rcParams['font.family'] = 'AppleGothic'
    else:  # Linux 기본
        plt.rcParams['font.family'] = 'sans-serif'

plt.rcParams['axes.unicode_minus'] = False  # 마이너스 폰트 깨짐 방지

# matplotlib 폰트 캐시 새로고침 (경고 메시지 제거)
try:
    fm._get_font.cache_clear()
except AttributeError:
    pass  # 오래된 matplotlib 버전에서는 이 메서드가 없을 수 있음

def ensure_backup_directory():
    """
    백업 디렉토리를 생성합니다.
    """
    backup_dir = './report_backup'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"📁 백업 디렉토리 생성: {backup_dir}")
    return backup_dir

def save_report_files(content, base_filename, period_name=""):
    """
    리포트 파일을 기본 디렉토리와 백업 디렉토리에 저장합니다.
    
    Args:
        content (str): 리포트 내용
        base_filename (str): 기본 파일명 (확장자 제외)
        period_name (str): 기간 이름 (선택사항)
    
    Returns:
        tuple: (기본 파일 경로, 백업 파일 경로)
    """
    backup_dir = ensure_backup_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 기본 디렉토리에 저장할 파일 (날짜/시간 없음)
    if period_name:
        main_filename = f'{base_filename}_{period_name}.md'
    else:
        main_filename = f'{base_filename}.md'
    
    # 백업 디렉토리에 저장할 파일 (날짜/시간 포함)
    if period_name:
        backup_filename = f'{base_filename}_{period_name}_{timestamp}.md'
    else:
        backup_filename = f'{base_filename}_{timestamp}.md'
    
    main_path = f'./{main_filename}'
    backup_path = f'{backup_dir}/{backup_filename}'
    
    # 파일 저장
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📋 리포트 저장: {main_filename}")
    print(f"💾 백업 저장: {backup_path}")
    
    return main_path, backup_path

def run_single_strategy(df_backtest, initial_stock_type, initial_shares, initial_value, company_name, reverse_strategy=False, strategy_name="", window_suffix="2year"):
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
        company_name: 회사명
    
    Returns:
        dict: 전략 실행 결과
    """
    current_stock_type = initial_stock_type
    current_shares = initial_shares
    cash = 0.0 # 배당금 및 매매 후 남은 현금
    
    # 회사명을 기반으로 주식 유형명 설정
    common_stock_name = f"{company_name} 보통주"
    preferred_stock_name = f"{company_name} 우선주"
    
    strategy_portfolio_values = [] # 일별 전략 포트폴리오 가치 저장
    trading_log = [] # 매매 기록 저장

    # 윈도우 크기에 따른 분위수 컬럼명 설정
    q25_col = f'Price_Diff_Ratio_25th_Percentile_{window_suffix}'
    q75_col = f'Price_Diff_Ratio_75th_Percentile_{window_suffix}'

    for i, (date, row) in enumerate(df_backtest.iterrows()):
        # 첫 날의 평가 금액 기록 - 종가 기준으로 수정
        if i == 0:
            # 첫날 종가 기준으로 포트폴리오 가치 계산
            if current_stock_type == common_stock_name:
                current_portfolio_value = current_shares * row['Stock1_Close'] + cash
            else:
                current_portfolio_value = current_shares * row['Stock2_Close'] + cash
            
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
                # 기본 전략: 25% 이하 -> 보통주, 75% 이상 -> 우선주
                should_buy_common = current_ratio < q25 and current_stock_type != common_stock_name
                should_buy_preferred = current_ratio > q75 and current_stock_type != preferred_stock_name
            else:
                # 반대 전략: 25% 이하 -> 우선주, 75% 이상 -> 보통주
                should_buy_common = current_ratio > q75 and current_stock_type != common_stock_name
                should_buy_preferred = current_ratio < q25 and current_stock_type != preferred_stock_name

            if should_buy_common:
                # 현재 보유주 -> 보통주
                if current_stock_type == preferred_stock_name:
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
                        'Stock_Type': f'{current_stock_type} -> {common_stock_name}',
                        'Shares_Traded': f'매도 {current_shares:.2f}주 -> 매수 {buy_shares:.2f}주',
                        'Price_Per_Share': f'매도가 {sell_price:,.0f}원 -> 매수가 {buy_price:,.0f}원',
                        'Total_Amount': f'매도금 {sell_value:,.0f}원 -> 매수금 {buy_shares * buy_price:,.0f}원',
                        'Current_Shares': buy_shares,
                        'Current_Stock_Type': common_stock_name,
                        'Cash_Balance': cash,
                        'Portfolio_Value': 0,  # 아래에서 계산
                        'Price_Diff_Ratio': current_ratio,
                        'Q25': q25,
                        'Q75': q75
                    })
                    
                    current_shares = buy_shares
                    current_stock_type = common_stock_name

            elif should_buy_preferred:
                # 현재 보유주 -> 우선주
                if current_stock_type == common_stock_name:
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
                        'Stock_Type': f'{current_stock_type} -> {preferred_stock_name}',
                        'Shares_Traded': f'매도 {current_shares:.2f}주 -> 매수 {buy_shares:.2f}주',
                        'Price_Per_Share': f'매도가 {sell_price:,.0f}원 -> 매수가 {buy_price:,.0f}원',
                        'Total_Amount': f'매도금 {sell_value:,.0f}원 -> 매수금 {buy_shares * buy_price:,.0f}원',
                        'Current_Shares': buy_shares,
                        'Current_Stock_Type': preferred_stock_name,
                        'Cash_Balance': cash,
                        'Portfolio_Value': 0,  # 아래에서 계산
                        'Price_Diff_Ratio': current_ratio,
                        'Q25': q25,
                        'Q75': q75
                    })
                    
                    current_shares = buy_shares
                    current_stock_type = preferred_stock_name
            
            # 배당금 처리 - stock_diff.py에서 처리된 배당 데이터 활용
            dividend_income = 0.0
            dividend_per_share = 0.0
            
            # 현재 보유 주식 유형에 따른 배당 처리
            if current_stock_type == common_stock_name:
                # 보통주 보유 시 - Stock1 배당 (일반적으로 보통주와 우선주 배당이 동일)
                if 'Dividend_Amount_Raw' in row and row['Dividend_Amount_Raw'] > 0:
                    dividend_per_share = row['Dividend_Amount_Raw']
                    dividend_income = current_shares * dividend_per_share
                    cash += dividend_income
            else:  # preferred_stock_name
                # 우선주 보유 시 - Stock2 배당 또는 동일 배당
                if 'Dividend_Amount_Raw' in row and row['Dividend_Amount_Raw'] > 0:
                    dividend_per_share = row['Dividend_Amount_Raw']
                    dividend_income = current_shares * dividend_per_share
                    cash += dividend_income
            
            # 배당금 수령 기록
            if dividend_income > 0:
                trading_log.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Action': '배당금수령',
                    'Stock_Type': current_stock_type,
                    'Shares_Traded': f'{current_shares:.2f}주',
                    'Price_Per_Share': f'{dividend_per_share:,.0f}원/주',
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
        if current_stock_type == common_stock_name:
            current_portfolio_value = current_shares * row['Stock1_Close'] + cash
        else:
            current_portfolio_value = current_shares * row['Stock2_Close'] + cash
        
        # 매매 기록이 있으면 포트폴리오 가치 업데이트
        if trading_log and trading_log[-1]['Date'] == date.strftime('%Y-%m-%d'):
            trading_log[-1]['Portfolio_Value'] = current_portfolio_value
        
        strategy_portfolio_values.append({'Date': date, 'Value': current_portfolio_value})

    last_day_data = df_backtest.iloc[-1]
    final_stock_value_strategy = 0.0
    if current_stock_type == common_stock_name:
        final_stock_value_strategy = current_shares * last_day_data['Stock1_Close']
    else:
        final_stock_value_strategy = current_shares * last_day_data['Stock2_Close']
    
    # 최종 총 자산 가치 (주식 + 현금) - 출력용
    final_total_value_strategy = final_stock_value_strategy + cash
    
    # 첫날 종가 기준 초기 가치 계산
    first_day_data = df_backtest.iloc[0]
    if initial_stock_type == common_stock_name:
        actual_initial_value = initial_shares * first_day_data['Stock1_Close']
    else:
        actual_initial_value = initial_shares * first_day_data['Stock2_Close']
    
    # 배당금을 제외한 수익률 계산 - 첫날 종가 기준으로 수정
    # 초기 투자금 1억원 기준 수익률 계산
    initial_capital = 100_000_000  # 1억원
    return_without_dividends_strategy = ((final_total_value_strategy - cash - initial_capital) / initial_capital) * 100

    print(f"\n--- {strategy_name} 백테스트 결과 ---")
    print(f"백테스트 종료: {df_backtest.index[-1].strftime('%y-%m-%d')}")
    print(f"최종 보유: {current_shares:,.2f}주 {current_stock_type}")
    print(f"최종 현금 (배당금 포함): {cash:,.2f}원")
    print(f"최종 총 자산 가치 (주식 + 현금): {final_total_value_strategy:,.2f}원")
    print(f"초기 자산 가치 (시가 기준): {initial_value:,.2f}원")
    print(f"초기 자산 가치 (종가 기준): {actual_initial_value:,.2f}원")
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
        common_to_pref = len(trades_only[trades_only['Stock_Type'].str.contains(f'{company_name} -> {company_name}\\(우\\)', regex=True)])
        pref_to_common = len(trades_only[trades_only['Stock_Type'].str.contains(f'{company_name}\\(우\\) -> {company_name}', regex=True)])
        print(f"{company_name} -> {company_name}(우): {common_to_pref}회")
        print(f"{company_name}(우) -> {company_name}: {pref_to_common}회")
        
        # 평균 매매 간격 계산
        if len(trades_only) > 1:
            trade_dates = pd.to_datetime(trades_only['Date'])
            avg_interval = (trade_dates.max() - trade_dates.min()).days / len(trades_only)
            print(f"평균 매매 간격: {avg_interval:.1f}일")

    return {
        'portfolio_values': strategy_portfolio_values,
        'trading_log': trading_log,
        'final_value': final_total_value_strategy,
        'final_stock_value': final_stock_value_strategy,
        'return_rate': return_without_dividends_strategy,
        'current_shares': current_shares,
        'current_stock_type': current_stock_type,
        'cash': cash
    }

def generate_analysis_report(strategy_results, buy_hold_final_value, buy_hold_return_rate, 
                           start_date, end_date, initial_value, company_name, period_name="20년",
                           pref_buy_hold_final_value=None, pref_buy_hold_return_rate=None):
    """
    윈도우 크기별 전략 성과 분석 리포트를 마크다운 형식으로 생성합니다.
    
    Args:
        strategy_results: 전략별 결과
        buy_hold_final_value: 보통주 Buy & Hold 최종 값
        buy_hold_return_rate: 보통주 Buy & Hold 수익률
        pref_buy_hold_final_value: 우선주 Buy & Hold 최종 값
        pref_buy_hold_return_rate: 우선주 Buy & Hold 수익률
        buy_hold_final_value: Buy & Hold 최종 가치
        buy_hold_return_rate: Buy & Hold 수익률
        start_date: 시작 날짜
        end_date: 종료 날짜
        initial_value: 초기 투자금
        period_name: 기간명
        company_name: 회사명
    """
    from datetime import datetime
    
    safe_company_name = company_name.replace('/', '_').replace('\\', '_')
    
    report_content = f"""# {company_name} {period_name} 백테스트 전략 성과 분석 리포트

**분석 날짜**: {datetime.now().strftime('%Y년 %m월 %d일')}  
**백테스트 기간**: {start_date} ~ {end_date}  
**초기 투자금**: {initial_value:,.0f}원

---

## 📊 **수익률 계산 기준**

### 💡 **수익률 산정 방식**
- **분자 (수익)**: (최종 총자산 - 현금배당금 - 초기투자금 1억원)
- **분모 (기준)**: 초기투자금 1억원
- **공식**: 수익률(%) = ((최종총자산 - 배당금 - 100,000,000원) / 100,000,000원) × 100
- **특징**: 모든 전략이 동일한 1억원 기준으로 수익률을 계산하여 공정한 비교 가능

### 📋 **자산 구성 요소**
- **총자산**: 주식자산 + 배당금(현금)
- **주식자산**: 최종 보유 주식의 시장가치 (종가 기준)
- **배당금**: 백테스트 기간 중 수령한 모든 배당금의 누적액

---

## 📊 **전략 성과 요약**

### 🥇 **기본전략 (25%↓→{company_name}, 75%↑→{company_name}(우)) 성과**

| 윈도우 크기 | 수익률 | 최종 자산 | 주식자산 | 배당금 | 순위 |
|------------|--------|-----------|----------|--------|------|
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
                'final_stock_value': result['final_stock_value'],
                'final_dividend_value': result['cash'],
                'trades': len([log for log in result['trading_log'] if log['Action'] == '매도->매수'])
            })
    
    # 수익률 기준으로 정렬
    basic_strategies.sort(key=lambda x: x['return_rate'], reverse=True)
    
    # 기본전략 표 작성
    medals = ['🏆', '🥈', '🥉']
    for i, strategy in enumerate(basic_strategies):
        medal = medals[i] if i < 3 else ''
        report_content += f"| {strategy['window']} 윈도우 | **{strategy['return_rate']:,.2f}%** | {strategy['final_value']:,.0f}원 | {strategy['final_stock_value']:,.0f}원 | {strategy['final_dividend_value']:,.0f}원 | {medal} |\n"

    report_content += f"""

### 📉 **반대전략 (25%↓→{company_name}(우), 75%↑→{company_name}) 성과**

| 윈도우 크기 | 수익률 | 최종 자산 | 주식자산 | 배당금 | 순위 |
|------------|--------|-----------|----------|--------|------|
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
                'final_stock_value': result['final_stock_value'],
                'final_dividend_value': result['cash'],
                'trades': len([log for log in result['trading_log'] if log['Action'] == '매도->매수'])
            })
    
    # 수익률 기준으로 정렬
    reverse_strategies.sort(key=lambda x: x['return_rate'], reverse=True)
    
    # 반대전략 표 작성
    for i, strategy in enumerate(reverse_strategies):
        medal = medals[i] if i < 3 else ''
        report_content += f"| {strategy['window']} 윈도우 | **{strategy['return_rate']:,.2f}%** | {strategy['final_value']:,.0f}원 | {strategy['final_stock_value']:,.0f}원 | {strategy['final_dividend_value']:,.0f}원 | {medal} |\n"

    # 최고 성과 전략 찾기
    best_basic = max(basic_strategies, key=lambda x: x['return_rate']) if basic_strategies else None
    best_reverse = max(reverse_strategies, key=lambda x: x['return_rate']) if reverse_strategies else None

    # Buy & Hold 구성 요소 계산
    buy_hold_cash = 0
    buy_hold_stock_value = buy_hold_final_value
    
    # 기본전략의 배당금을 Buy & Hold 배당금으로 사용 (동일한 기간, 동일한 배당)
    if strategy_results and '기본전략_2년' in strategy_results:
        buy_hold_cash = strategy_results['기본전략_2년'].get('cash', 0)
        buy_hold_stock_value = buy_hold_final_value - buy_hold_cash

    report_content += f"""

### 📈 **Buy & Hold 참고**

#### 🔵 **{company_name} 보통주 Buy & Hold**
- **수익률**: {buy_hold_return_rate:,.2f}% (1억원 기준)
- **총자산**: {buy_hold_final_value:,.0f}원
- **주식자산**: {buy_hold_stock_value:,.0f}원
- **배당금**: {buy_hold_cash:,.0f}원"""

    if pref_buy_hold_final_value and pref_buy_hold_return_rate:
        # 우선주 Buy & Hold 구성 요소 계산
        pref_buy_hold_cash = 0
        pref_buy_hold_stock_value = pref_buy_hold_final_value
        
        # 기본전략의 배당금을 우선주 Buy & Hold 배당금으로 사용 (동일한 기간, 비슷한 배당)
        if strategy_results and '기본전략_2년' in strategy_results:
            # 우선주는 보통주보다 약간 높은 배당을 받으므로 추정값 사용
            pref_buy_hold_cash = strategy_results['기본전략_2년'].get('cash', 0) * 1.05  # 약 5% 더 높은 배당 추정
            pref_buy_hold_stock_value = pref_buy_hold_final_value - pref_buy_hold_cash
        
        report_content += f"""

#### 🔶 **{company_name} 우선주 Buy & Hold**
- **수익률**: {pref_buy_hold_return_rate:,.2f}% (1억원 기준)
- **총자산**: {pref_buy_hold_final_value:,.0f}원
- **주식자산**: {pref_buy_hold_stock_value:,.0f}원
- **배당금**: {pref_buy_hold_cash:,.0f}원"""

    report_content += f"""

---

## 💡 **핵심 발견사항**

### 1. **최적 윈도우 크기**"""

    if best_basic:
        report_content += f"""
- **{best_basic['window']} 윈도우**가 기본전략에서 가장 우수한 성과를 보임
- 수익률: **{best_basic['return_rate']:,.2f}%**
- 최종 자산: **{best_basic['final_value']:,.0f}원**"""

    report_content += f"""

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

    if best_basic and best_reverse:
        report_content += f"""

### 3. **전략 우위성**
- {'기본전략' if best_basic['return_rate'] > best_reverse['return_rate'] else '반대전략'}이 더 우수한 성과
- 기본전략은 Buy & Hold보다 **{best_basic['return_rate']/buy_hold_return_rate:.1f}배** 높은 수익률"""

    report_content += f"""

### 4. **윈도우 크기의 영향**
- **윈도우가 클수록 매매 빈도 감소** (안정성 증가)
- **{period_name} 기간**에서는 {"장기" if best_basic and best_basic['window'] == '5년' else "중기" if best_basic and best_basic['window'] == '3년' else "단기"} 윈도우가 최적

---

## 🎯 **투자 전략 권고사항**

### ✅ **추천 전략**"""

    if best_basic:
        report_content += f"""
1. **{best_basic['window']} 슬라이딩 윈도우를 사용한 기본전략** (최고 성과)
   - 가격차이비율 < {best_basic['window']} 슬라이딩 25% 분위 → {company_name} 매수
   - 가격차이비율 > {best_basic['window']} 슬라이딩 75% 분위 → {company_name}(우) 매수"""

    report_content += f"""

### ❌ **비추천 전략**
- 반대전략: Buy & Hold보다 저조한 성과
- 가격차이비율의 기본 논리에 반하는 매매는 비효율적

### 📝 **실행 가이드라인**
1. **시작 자본**: 최소 {initial_value:,.0f}원 이상 권장 (분석 기준: 1억원)
2. **수익률 해석**: 모든 수익률은 1억원 투자 기준으로 계산됨
   - 예: 500% 수익률 = 1억원 투자 시 5억원 수익 = 최종 6억원
3. **리밸런싱 주기**: 일일 모니터링, 신호 발생시 즉시 실행
4. **수수료 고려**: 실제 거래시 매매 수수료 및 세금 고려 필요
5. **리스크 관리**: 과도한 집중 투자 지양, 포트폴리오 분산 권장

---

## 📋 **상세 데이터**

### 💰 **자산 구성 요소 분석 (상세)**

**⚠️ 수익률 계산 기준**: 모든 수익률은 **초기투자금 1억원 대비** 계산됩니다.  
**📊 총자산 구성**: 총자산 = 주식자산 + 배당금(현금)  
**🔍 비교 기준**: 모든 전략이 동일한 1억원으로 시작하여 공정한 성과 비교가 가능합니다.

#### 📈 **전체 전략 자산 구성 비교**
"""

    # 자산 구성 요소 계산 (기본전략과 반대전략의 첫 번째 윈도우 결과 사용)
    if basic_strategies and reverse_strategies:
        basic_final_value = basic_strategies[0]['final_value']
        reverse_final_value = reverse_strategies[0]['final_value']
        
        # 주식 가치와 배당금(현금) 분리
        basic_stock_value = basic_strategies[0].get('final_stock_value', basic_final_value)
        reverse_stock_value = reverse_strategies[0].get('final_stock_value', reverse_final_value)
        basic_cash = basic_strategies[0].get('cash', 0)
        reverse_cash = reverse_strategies[0].get('cash', 0)
        
        # Buy & Hold의 주식 가치 계산 (배당금은 동일하므로 기본전략 배당금 사용)
        buy_hold_stock_value = buy_hold_final_value - basic_cash
        
        # 배당금 비율 계산
        basic_dividend_ratio = (basic_cash / basic_final_value) * 100 if basic_final_value > 0 else 0
        reverse_dividend_ratio = (reverse_cash / reverse_final_value) * 100 if reverse_final_value > 0 else 0
        buy_hold_dividend_ratio = (basic_cash / buy_hold_final_value) * 100 if buy_hold_final_value > 0 else 0
        
        # 우선주 Buy & Hold의 구성 요소 계산
        pref_buy_hold_cash_for_table = 0
        pref_buy_hold_stock_value_for_table = pref_buy_hold_final_value if pref_buy_hold_final_value else 0
        pref_buy_hold_dividend_ratio = 0
        
        if pref_buy_hold_final_value and strategy_results and '기본전략_2년' in strategy_results:
            # 우선주 배당금 추정 (보통주보다 약간 높음)
            pref_buy_hold_cash_for_table = strategy_results['기본전략_2년'].get('cash', 0) * 1.05
            pref_buy_hold_stock_value_for_table = pref_buy_hold_final_value - pref_buy_hold_cash_for_table
            pref_buy_hold_dividend_ratio = (pref_buy_hold_cash_for_table / pref_buy_hold_final_value) * 100 if pref_buy_hold_final_value > 0 else 0
        
        report_content += f"""
| 구분 | 수익률 (1억원 기준) | 총자산 | 주식자산 | 배당금 | 배당금 비율 |
|------|------------------|--------|----------|--------|------------|
| **보통주 Buy & Hold** | {buy_hold_return_rate:,.2f}% | {buy_hold_final_value:,.0f}원 | {buy_hold_stock_value:,.0f}원 | {basic_cash:,.0f}원 | {buy_hold_dividend_ratio:.1f}% |"""
        
        if pref_buy_hold_final_value and pref_buy_hold_return_rate:
            report_content += f"""
| **우선주 Buy & Hold** | {pref_buy_hold_return_rate:,.2f}% | {pref_buy_hold_final_value:,.0f}원 | {pref_buy_hold_stock_value_for_table:,.0f}원 | {pref_buy_hold_cash_for_table:,.0f}원 | {pref_buy_hold_dividend_ratio:.1f}% |"""
        
        report_content += f"""
| **기본전략 (최고성과)** | {basic_strategies[0]['return_rate']:,.2f}% | {basic_final_value:,.0f}원 | {basic_stock_value:,.0f}원 | {basic_cash:,.0f}원 | {basic_dividend_ratio:.1f}% |
| **반대전략 (최고성과)** | {reverse_strategies[0]['return_rate']:,.2f}% | {reverse_final_value:,.0f}원 | {reverse_stock_value:,.0f}원 | {reverse_cash:,.0f}원 | {reverse_dividend_ratio:.1f}% |

#### 📊 **구성 요소 상세 분석**

1. **수익률 계산**: 모든 수익률은 1억원 초기투자 기준으로 계산
   - 공식: (총자산 - 배당금 - 1억원) ÷ 1억원 × 100
2. **배당금 특성**: {'동일한 주식 수량 보유 시 배당금은 유사' if basic_cash == reverse_cash else '전략별로 보유 주식과 수량이 달라 배당금 차이 발생'}
3. **주식자산 차이**: 전략별로 보유 주식 종류(보통주/우선주)와 수량이 달라 주식자산 가치에 차이 발생
4. **공정한 비교**: 모든 전략이 동일한 1억원으로 시작하여 공정한 성과 비교 가능

### 🔄 **Buy & Hold 기준 성과 비교**

"""
        
        # Buy & Hold 기준 성과 비교 계산
        basic_vs_buyhold_ratio = basic_final_value / buy_hold_final_value
        reverse_vs_buyhold_ratio = reverse_final_value / buy_hold_final_value
        basic_absolute_diff = basic_final_value - buy_hold_final_value
        reverse_absolute_diff = reverse_final_value - buy_hold_final_value
        basic_relative_perf = ((basic_final_value - buy_hold_final_value) / buy_hold_final_value) * 100
        reverse_relative_perf = ((reverse_final_value - buy_hold_final_value) / buy_hold_final_value) * 100
        
        report_content += f"""| 전략 | Buy & Hold 대비 | 절대 차이 | 상대 성과 |
|------|----------------|-----------|----------|
| **기본전략** | **{basic_vs_buyhold_ratio:.2f}배** | {basic_absolute_diff:+,.0f}원 | {'✅ **' + f'{basic_relative_perf:.0f}% 더 좋음**' if basic_relative_perf > 0 else '❌ **' + f'{abs(basic_relative_perf):.0f}% 더 나쁨**'} |
| **반대전략** | **{reverse_vs_buyhold_ratio:.2f}배** | {reverse_absolute_diff:+,.0f}원 | {'✅ **' + f'{reverse_relative_perf:.0f}% 더 좋음**' if reverse_relative_perf > 0 else '❌ **' + f'{abs(reverse_relative_perf):.0f}% 더 나쁨**'} |

"""

    report_content += f"""### 기본전략 상세 성과

| 윈도우 | 수익률 (1억원 기준) | 총자산 | 주식자산 | 배당금 | 매매횟수 | Buy&Hold 대비 |
|--------|------------------|--------|----------|--------|----------|---------------|
"""

    for strategy in basic_strategies:
        buy_hold_ratio = strategy['final_value'] / buy_hold_final_value
        strategy_name = f"기본전략_{strategy['window']}"
        strategy_data = strategy_results.get(strategy_name, {})
        stock_value = strategy_data.get('final_stock_value', strategy['final_value'])
        cash_value = strategy_data.get('cash', 0)
        report_content += f"| {strategy['window']} | {strategy['return_rate']:,.2f}% | {strategy['final_value']:,.0f}원 | {stock_value:,.0f}원 | {cash_value:,.0f}원 | {strategy['trades']}회 | **{buy_hold_ratio:.2f}배** |\n"

    report_content += f"""

### 반대전략 상세 성과

| 윈도우 | 수익률 (1억원 기준) | 총자산 | 주식자산 | 배당금 | 매매횟수 | Buy&Hold 대비 |
|--------|------------------|--------|----------|--------|----------|---------------|
"""

    for strategy in reverse_strategies:
        buy_hold_ratio = strategy['final_value'] / buy_hold_final_value
        strategy_name = f"반대전략_{strategy['window']}"
        strategy_data = strategy_results.get(strategy_name, {})
        stock_value = strategy_data.get('final_stock_value', strategy['final_value'])
        cash_value = strategy_data.get('cash', 0)
        report_content += f"| {strategy['window']} | {strategy['return_rate']:,.2f}% | {strategy['final_value']:,.0f}원 | {stock_value:,.0f}원 | {cash_value:,.0f}원 | {strategy['trades']}회 | **{buy_hold_ratio:.2f}배** |\n"

    report_content += f"""

---

## 📊 **생성된 파일들**

1. **그래프**: `strategy_comparison_{period_name}.png`
2. **매매 기록**: 각 전략별 CSV 파일
   - `trading_log_{period_name}_기본전략_2년.csv`
   - `trading_log_{period_name}_기본전략_3년.csv`
   - `trading_log_{period_name}_기본전략_5년.csv`
   - `trading_log_{period_name}_반대전략_2년.csv`
   - `trading_log_{period_name}_반대전략_3년.csv`
   - `trading_log_{period_name}_반대전략_5년.csv`

---

**📊 수익률 계산 요약**: 본 분석의 모든 수익률은 1억원 초기투자 기준으로 계산되었습니다. 공식: (최종총자산 - 배당금 - 1억원) ÷ 1억원 × 100

**면책조항**: 본 분석은 과거 데이터에 기반한 백테스트 결과이며, 미래 수익을 보장하지 않습니다. 실제 투자시에는 시장 상황, 거래 비용, 세금 등을 종합적으로 고려하시기 바랍니다.
"""

    # 리포트 파일 저장
    main_path, backup_path = save_report_files(report_content, f'{safe_company_name}_strategy_analysis_report', period_name)
    
    print(f"\n📋 {company_name} {period_name} 전략 분석 리포트 저장 완료")

def run_comprehensive_backtest(company_name):
    """
    다양한 기간(3년, 5년, 10년, 20년, 30년)에 대해 백테스트를 수행합니다.
    각 기간별로 2년, 3년, 5년 윈도우 크기를 사용하여 전략을 비교분석합니다.
    
    Args:
        company_name (str): 분석할 회사명
    """
    print(f"\n🏢 {company_name} 백테스트 분석 시작")
    
    # 회사가 지원되는지 확인
    if company_name not in PREFERRED_STOCK_COMPANIES:
        print(f"❌ 지원되지 않는 회사입니다: {company_name}")
        print(f"지원되는 회사: {list(PREFERRED_STOCK_COMPANIES.keys())}")
        return
    
    periods = ['3년', '5년', '10년', '20년', '30년']
    window_configs = {
        '2year': '2년',
        '3year': '3년',
        '5year': '5년'
    }
    
    all_results = {}
    safe_company_name = company_name.replace('/', '_').replace('\\', '_')
    
    for period in periods:
        print(f"\n{'='*80}")
        print(f"=== {company_name} {period} 백테스트 시작 ===")
        print(f"{'='*80}")
        
        json_file = f'./{safe_company_name}_stock_analysis_{period}.json'
        
        try:
            # JSON 파일 읽기
            print(f"📁 run_comprehensive_backtest JSON 파일 로딩 중: {json_file}")
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ run_comprehensive_backtest JSON 파일 로딩 완료: {json_file}")

            df = pd.DataFrame.from_dict(data, orient='index')
            df.index = pd.to_datetime(df.index, format='%y-%m-%d')
            df = df.sort_index()

            if df.empty:
                print(f"{period} 데이터가 비어있습니다.")
                continue

            print(f"데이터 기간: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
            print(f"총 데이터 포인트: {len(df)}")

            # 초기 설정 (1억원 초기 자본)
            initial_capital = 100_000_000  # 1억원
            initial_stock_type = f"{company_name} 보통주"  # 정확한 보통주 명칭 사용
            start_date_str = df.index[0].strftime('%y-%m-%d')
            
            # 백테스트 시작 날짜 설정 (첫 날 다음날부터)
            if len(df) > 1:
                df_backtest = df.iloc[1:].copy()
            else:
                print(f"{period} 백테스트에 충분한 데이터가 없습니다.")
                continue

            first_day_data = df.iloc[0]
            # 1억원으로 살 수 있는 주식 수 계산
            initial_shares = int(initial_capital / first_day_data['Stock1_Open'])
            initial_value = initial_shares * first_day_data['Stock1_Open']

            print(f"초기 설정:")
            print(f"  - 보유주식: {initial_shares}주 {initial_stock_type}")
            print(f"  - 초기 가치: {initial_value:,.2f}원")
            print(f"  - 백테스트 시작: {df_backtest.index[0].strftime('%y-%m-%d')}")

            strategy_results = {}

            # 각 윈도우 크기별로 전략 실행
            for window_suffix, window_name in window_configs.items():
                print(f"\n{'*'*50}")
                print(f"*** {window_name} 윈도우 분석 ***")
                print(f"{'*'*50}")
                
                # 기본 전략
                print(f"\n--- {window_name} 기본 전략 ---")
                print(f"- 가격차이비율 < {window_name} 슬라이딩 25% 분위: {company_name} 보통주 매수 (상대적 저평가)")
                print(f"- 가격차이비율 > {window_name} 슬라이딩 75% 분위: {company_name} 우선주 매수 (상대적 저평가)")

                basic_strategy_name = f"기본전략_{window_name}"
                strategy_results[basic_strategy_name] = run_single_strategy(
                    df_backtest, initial_stock_type, initial_shares, initial_value, company_name,
                    False, basic_strategy_name, window_suffix
                )
                
                # 반대 전략
                print(f"\n--- {window_name} 반대 전략 ---")
                print(f"- 가격차이비율 < {window_name} 슬라이딩 25% 분위: {company_name} 우선주 매수")
                print(f"- 가격차이비율 > {window_name} 슬라이딩 75% 분위: {company_name} 보통주 매수")

                reverse_strategy_name = f"반대전략_{window_name}"
                strategy_results[reverse_strategy_name] = run_single_strategy(
                    df_backtest, initial_stock_type, initial_shares, initial_value, company_name,
                    True, reverse_strategy_name, window_suffix
                )

            # Buy & Hold 전략 (1억원 기준)
            print("\n" + "="*60)
            print(f"=== {company_name} 보통주 Buy & Hold 결과 ===")
            buy_hold_initial_shares = int(initial_capital / first_day_data['Stock1_Open'])
            buy_hold_initial_value = buy_hold_initial_shares * first_day_data['Stock1_Open']
            
            buy_hold_portfolio_values = []
            accumulated_buy_hold_dividends = 0.0

            # stock_diff.py에서 처리된 배당 데이터를 활용한 Buy & Hold 전략
            print(f"📈 {company_name} 보통주 Buy & Hold 전략 (stock_diff.py 배당 데이터 활용)")
            
            for date, row in df_backtest.iterrows():
                # stock_diff.py에서 처리된 배당 데이터 활용
                if 'Dividend_Amount_Raw' in row and row['Dividend_Amount_Raw'] > 0:
                    daily_dividend = row['Dividend_Amount_Raw'] * buy_hold_initial_shares
                    accumulated_buy_hold_dividends += daily_dividend
                    print(f"  📅 {date.strftime('%Y-%m-%d')}: 배당 {row['Dividend_Amount_Raw']:,.0f}원/주 → 총 {daily_dividend:,.0f}원")
                
                buy_hold_daily_value = buy_hold_initial_shares * row['Stock1_Close'] + accumulated_buy_hold_dividends
                buy_hold_portfolio_values.append({'Date': date, 'Value': buy_hold_daily_value})

            buy_hold_final_value = buy_hold_initial_shares * df_backtest.iloc[-1]['Stock1_Close']
            buy_hold_final_total_value = buy_hold_final_value + accumulated_buy_hold_dividends
            # 초기 투자금 1억원 기준 수익률 계산
            return_without_dividends_buy_hold = ((buy_hold_final_value - initial_capital) / initial_capital) * 100

            print(f"초기 보유: {buy_hold_initial_shares}주 {company_name} 보통주 (시가 기준 초기 가치: {buy_hold_initial_value:,.2f}원)")
            print(f"최종 보유: {buy_hold_initial_shares}주 {company_name} 보통주")
            print(f"최종 주식 가치: {buy_hold_final_value:,.2f}원")
            print(f"총 배당금 수령: {accumulated_buy_hold_dividends:,.2f}원")
            print(f"최종 총 자산 가치 (주식 + 배당금): {buy_hold_final_total_value:,.2f}원")
            print(f"총 수익률 (배당금 제외): {return_without_dividends_buy_hold:,.2f}%")

            # 우선주 Buy & Hold 전략 (1억원 기준)
            print("\n" + "="*60)
            print(f"=== {company_name} 우선주 Buy & Hold 결과 ===")
            pref_buy_hold_initial_shares = int(initial_capital / first_day_data['Stock2_Open'])
            pref_buy_hold_initial_value = pref_buy_hold_initial_shares * first_day_data['Stock2_Open']
            
            pref_buy_hold_portfolio_values = []
            accumulated_pref_buy_hold_dividends = 0.0

            # stock_diff.py에서 처리된 배당 데이터를 활용한 우선주 Buy & Hold 전략
            print(f"📈 {company_name} 우선주 Buy & Hold 전략 (stock_diff.py 배당 데이터 활용)")
            
            for date, row in df_backtest.iterrows():
                # 우선주 배당금은 보통주보다 높을 수 있음 (일반적으로 추가 배당 있음)
                if 'Dividend_Amount_Raw' in row and row['Dividend_Amount_Raw'] > 0:
                    # 우선주는 보통주 배당 + 추가 배당 (일반적으로 1% 정도 추가)
                    pref_dividend_per_share = row['Dividend_Amount_Raw'] * 1.01  # 우선주 추가 배당 가정
                    daily_pref_dividend = pref_dividend_per_share * pref_buy_hold_initial_shares
                    accumulated_pref_buy_hold_dividends += daily_pref_dividend
                    print(f"  📅 {date.strftime('%Y-%m-%d')}: 우선주 배당 {pref_dividend_per_share:,.0f}원/주 → 총 {daily_pref_dividend:,.0f}원")
                
                pref_buy_hold_daily_value = pref_buy_hold_initial_shares * row['Stock2_Close'] + accumulated_pref_buy_hold_dividends
                pref_buy_hold_portfolio_values.append({'Date': date, 'Value': pref_buy_hold_daily_value})

            pref_buy_hold_final_value = pref_buy_hold_initial_shares * df_backtest.iloc[-1]['Stock2_Close']
            pref_buy_hold_final_total_value = pref_buy_hold_final_value + accumulated_pref_buy_hold_dividends
            # 초기 투자금 1억원 기준 수익률 계산
            return_without_dividends_pref_buy_hold = ((pref_buy_hold_final_value - initial_capital) / initial_capital) * 100

            print(f"초기 보유: {pref_buy_hold_initial_shares}주 {company_name} 우선주 (시가 기준 초기 가치: {pref_buy_hold_initial_value:,.2f}원)")
            print(f"최종 보유: {pref_buy_hold_initial_shares}주 {company_name} 우선주")
            print(f"최종 주식 가치: {pref_buy_hold_final_value:,.2f}원")
            print(f"총 배당금 수령: {accumulated_pref_buy_hold_dividends:,.2f}원")
            print(f"최종 총 자산 가치 (주식 + 배당금): {pref_buy_hold_final_total_value:,.2f}원")
            print(f"총 수익률 (배당금 제외): {return_without_dividends_pref_buy_hold:,.2f}%")

            # 매매 기록 저장
            for strategy_name, result in strategy_results.items():
                trading_df = pd.DataFrame(result['trading_log'])
                filename = f'{safe_company_name}_trading_log_{period}_{strategy_name.replace(" ", "_")}.csv'
                trading_df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"\n{strategy_name} 매매 기록이 '{filename}' 파일로 저장되었습니다.")

            # 전략 비교 요약
            print(f"\n{'='*80}")
            print(f"=== {company_name} {period} 전략 비교 요약 ===")
            
            print(f"\n--- 기본전략 (25%↓→{company_name} 보통주, 75%↑→{company_name} 우선주) ---")
            for window_name in ['2년', '3년', '5년']:
                strategy_name = f"기본전략_{window_name}"
                if strategy_name in strategy_results:
                    result = strategy_results[strategy_name]
                    stock_value = result['final_stock_value']
                    dividend_value = result['cash']
                    print(f"{window_name} 윈도우: {result['return_rate']:,.2f}% (최종자산: {result['final_value']:,.0f}원, 주식자산: {stock_value:,.0f}원, 배당금: {dividend_value:,.0f}원)")
            
            print(f"\n--- 반대전략 (25%↓→{company_name} 우선주, 75%↑→{company_name} 보통주) ---")
            for window_name in ['2년', '3년', '5년']:
                strategy_name = f"반대전략_{window_name}"
                if strategy_name in strategy_results:
                    result = strategy_results[strategy_name]
                    stock_value = result['final_stock_value']
                    dividend_value = result['cash']
                    print(f"{window_name} 윈도우: {result['return_rate']:,.2f}% (최종자산: {result['final_value']:,.0f}원, 주식자산: {stock_value:,.0f}원, 배당금: {dividend_value:,.0f}원)")
            
            print(f"\n--- Buy & Hold 참고 ---")
            # 보통주 Buy & Hold 구성 요소 계산
            buy_hold_stock_value = buy_hold_final_value
            buy_hold_dividend_value = buy_hold_final_total_value - buy_hold_final_value
            print(f"{company_name} 보통주 Buy & Hold: {return_without_dividends_buy_hold:,.2f}% (최종자산: {buy_hold_final_total_value:,.0f}원, 주식자산: {buy_hold_stock_value:,.0f}원, 배당금: {buy_hold_dividend_value:,.0f}원)")
            
            # 우선주 Buy & Hold 구성 요소 계산
            pref_buy_hold_stock_value = pref_buy_hold_final_value
            pref_buy_hold_dividend_value = pref_buy_hold_final_total_value - pref_buy_hold_final_value
            print(f"{company_name} 우선주 Buy & Hold: {return_without_dividends_pref_buy_hold:,.2f}% (최종자산: {pref_buy_hold_final_total_value:,.0f}원, 주식자산: {pref_buy_hold_stock_value:,.0f}원, 배당금: {pref_buy_hold_dividend_value:,.0f}원)")

            # Buy&Hold 구성 요소 계산 (기본전략의 배당금을 사용)
            basic_cash = 0
            if strategy_results and '기본전략_2년' in strategy_results:
                basic_cash = strategy_results['기본전략_2년'].get('cash', 0)
            buy_hold_stock_value = buy_hold_final_total_value - basic_cash
            
            # 결과 저장
            all_results[period] = {
                'strategy_results': strategy_results,
                'buy_hold_final_value': buy_hold_final_total_value,
                'buy_hold_stock_value': buy_hold_stock_value,  # Buy&Hold 주식자산
                'buy_hold_dividends': basic_cash,  # Buy&Hold 배당금
                'buy_hold_return_rate': return_without_dividends_buy_hold,
                'pref_buy_hold_final_value': pref_buy_hold_final_total_value,  # 우선주 Buy&Hold
                'pref_buy_hold_return_rate': return_without_dividends_pref_buy_hold,  # 우선주 수익률
                'start_date': start_date_str,
                'end_date': df_backtest.index[-1].strftime('%y-%m-%d'),
                'initial_value': initial_value,
                'initial_capital': initial_capital,  # 초기 자본 추가
                'buy_hold_portfolio_values': buy_hold_portfolio_values,
                'pref_buy_hold_portfolio_values': pref_buy_hold_portfolio_values  # 우선주 포트폴리오 값들
            }

            # 그래프 생성
            generate_period_comparison_chart(period, strategy_results, buy_hold_portfolio_values, pref_buy_hold_portfolio_values, company_name)

            # 개별 기간 리포트 생성
            generate_analysis_report(strategy_results, buy_hold_final_total_value, return_without_dividends_buy_hold, 
                                   start_date_str, df_backtest.index[-1].strftime('%y-%m-%d'), initial_value, company_name, period,
                                   pref_buy_hold_final_total_value, return_without_dividends_pref_buy_hold)

        except FileNotFoundError:
            print(f"오류: {json_file} 파일을 찾을 수 없습니다.")
            continue
        except Exception as e:
            print(f"{period} 백테스트 중 오류 발생: {e}")
            continue

    # 전체 기간 비교 리포트 생성
    if all_results:
        generate_comprehensive_report(all_results, company_name)
        generate_summary_report(all_results, company_name)

def generate_period_comparison_chart(period, strategy_results, buy_hold_portfolio_values, pref_buy_hold_portfolio_values, company_name):
    """
    특정 기간에 대한 전략 비교 차트를 생성합니다.
    
    Args:
        period: 분석 기간
        strategy_results: 전략별 결과
        buy_hold_portfolio_values: 보통주 Buy & Hold 포트폴리오 값들
        pref_buy_hold_portfolio_values: 우선주 Buy & Hold 포트폴리오 값들
        company_name (str): 분석 대상 회사명
    """
    safe_company_name = company_name.replace('/', '_').replace('\\', '_')
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # 기본전략 비교 그래프
    ax1.set_title(f'{period} 기본전략: 윈도우 크기별 월별 포트폴리오 평가 금액 비교', fontsize=14)
    for window_name in ['2년', '3년', '5년']:
        strategy_name = f"기본전략_{window_name}"
        if strategy_name in strategy_results:
            strategy_df = pd.DataFrame(strategy_results[strategy_name]['portfolio_values']).set_index('Date')
            monthly_df = strategy_df.resample('MS').first()
            ax1.plot(monthly_df.index, monthly_df['Value'], label=f'{window_name} 윈도우', marker='o', markersize=3)
    
    # Buy & Hold 추가
    buy_hold_df = pd.DataFrame(buy_hold_portfolio_values).set_index('Date')
    monthly_buy_hold_df = buy_hold_df.resample('MS').first()
    ax1.plot(monthly_buy_hold_df.index, monthly_buy_hold_df['Value'], label=f'{company_name} 보통주 Buy & Hold', marker='x', markersize=3, linestyle='--')
    
    # 우선주 Buy & Hold 추가
    pref_buy_hold_df = pd.DataFrame(pref_buy_hold_portfolio_values).set_index('Date')
    monthly_pref_buy_hold_df = pref_buy_hold_df.resample('MS').first()
    ax1.plot(monthly_pref_buy_hold_df.index, monthly_pref_buy_hold_df['Value'], label=f'{company_name} 우선주 Buy & Hold', marker='o', markersize=3, linestyle=':')
    
    ax1.set_ylabel('평가 금액 (원)')
    ax1.grid(True)
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)
    
    # 반대전략 비교 그래프
    ax2.set_title(f'{period} 반대전략: 윈도우 크기별 월별 포트폴리오 평가 금액 비교', fontsize=14)
    for window_name in ['2년', '3년', '5년']:
        strategy_name = f"반대전략_{window_name}"
        if strategy_name in strategy_results:
            strategy_df = pd.DataFrame(strategy_results[strategy_name]['portfolio_values']).set_index('Date')
            monthly_df = strategy_df.resample('MS').first()
            ax2.plot(monthly_df.index, monthly_df['Value'], label=f'{window_name} 윈도우', marker='s', markersize=3)
    
    # Buy & Hold 추가
    buy_hold_df = pd.DataFrame(buy_hold_portfolio_values).set_index('Date')
    monthly_buy_hold_df = buy_hold_df.resample('MS').first()
    ax2.plot(monthly_buy_hold_df.index, monthly_buy_hold_df['Value'], label=f'{company_name} 보통주 Buy & Hold', marker='x', markersize=3, linestyle='--')
    
    # 우선주 Buy & Hold 추가
    pref_buy_hold_df = pd.DataFrame(pref_buy_hold_portfolio_values).set_index('Date')
    monthly_pref_buy_hold_df = pref_buy_hold_df.resample('MS').first()
    ax2.plot(monthly_pref_buy_hold_df.index, monthly_pref_buy_hold_df['Value'], label=f'{company_name} 우선주 Buy & Hold', marker='o', markersize=3, linestyle=':')
    
    ax2.set_xlabel('날짜')
    ax2.set_ylabel('평가 금액 (원)')
    ax2.grid(True)
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plot_output_path = f'./{safe_company_name}_strategy_comparison_{period}.png'
    plt.savefig(plot_output_path, dpi=300, bbox_inches='tight')
    print(f"\n{company_name} {period} 전략 비교 그래프가 {plot_output_path}에 저장되었습니다.")
    
    plt.close()

def generate_comprehensive_report(all_results, company_name):
    """
    모든 기간에 대한 종합 비교 리포트를 생성합니다.
    
    Args:
        all_results: 모든 기간의 결과 데이터
        company_name (str): 분석 대상 회사명
    """
    from datetime import datetime
    
    safe_company_name = company_name.replace('/', '_').replace('\\', '_')
    
    report_content = f"""# {company_name} 종합 기간별 전략 성과 분석

**분석 날짜**: {datetime.now().strftime('%Y년 %m월 %d일')}  
**분석 기간**: 3년, 5년, 10년, 20년, 30년 백테스트 종합 비교

---

## 📊 **기간별 최고 성과 전략 요약**

| 기간 | 최고 성과 전략 | 수익률 | 최종 자산 | Buy&Hold 수익률 | Buy&Hold 자산 | 대비 비율 |
|------|---------------|--------|-----------|-----------------|------------|-----------|
"""

    # 각 기간별 최고 성과 전략 찾기
    best_strategies = {}
    for period, result in all_results.items():
        strategy_results = result['strategy_results']
        buy_hold_return = result['buy_hold_return_rate']
        buy_hold_final_value = result['buy_hold_final_value']
        
        best_strategy = None
        best_return = -float('inf')
        
        for strategy_name, strategy_result in strategy_results.items():
            if strategy_result['return_rate'] > best_return:
                best_return = strategy_result['return_rate']
                best_strategy = {
                    'name': strategy_name,
                    'return_rate': strategy_result['return_rate'],
                    'final_value': strategy_result['final_value']
                }
        
        best_strategies[period] = best_strategy
        
        if best_strategy:
            # Buy&Hold 대비 비율을 최종 자산 기준으로 계산
            vs_buyhold_ratio = best_strategy['final_value'] / buy_hold_final_value if buy_hold_final_value > 0 else 0
            report_content += f"| {period} | {best_strategy['name']} | **{best_strategy['return_rate']:,.2f}%** | {best_strategy['final_value']:,.0f}원 | {buy_hold_return:,.2f}% | {buy_hold_final_value:,.0f}원 | {vs_buyhold_ratio:.2f}배 |\n"

    report_content += f"""

## 📈 **기간별 상세 성과 비교**

"""

    # 각 기간별 상세 성과 표
    for period, result in all_results.items():
        strategy_results = result['strategy_results']
        buy_hold_return = result['buy_hold_return_rate']
        buy_hold_final = result['buy_hold_final_value']
        
        report_content += f"""
### {period} 백테스트 결과

**기간**: {result['start_date']} ~ {result['end_date']}  
**초기 투자금**: {result['initial_value']:,.0f}원

| 전략 | 수익률 | 최종 자산 | Buy&Hold 대비(자산) | Buy&Hold 대비(수익률) |
|------|--------|-----------|-------------------|-------------------|
"""
        
        # 기본전략들
        for window_name in ['2년', '3년', '5년']:
            strategy_name = f"기본전략_{window_name}"
            if strategy_name in strategy_results:
                result_data = strategy_results[strategy_name]
                # 최종 자산 기준 대비 계산
                asset_ratio = result_data['final_value'] / buy_hold_final if buy_hold_final > 0 else 0
                # 수익률 기준 대비 계산
                return_ratio = result_data['return_rate'] / buy_hold_return if buy_hold_return > 0 else 0
                report_content += f"| 기본전략 {window_name} | {result_data['return_rate']:,.2f}% | {result_data['final_value']:,.0f}원 | {asset_ratio:.2f}배 | {return_ratio:.2f}배 |\n"
        
        # 반대전략들
        for window_name in ['2년', '3년', '5년']:
            strategy_name = f"반대전략_{window_name}"
            if strategy_name in strategy_results:
                result_data = strategy_results[strategy_name]
                # 최종 자산 기준 대비 계산
                asset_ratio = result_data['final_value'] / buy_hold_final if buy_hold_final > 0 else 0
                # 수익률 기준 대비 계산
                return_ratio = result_data['return_rate'] / buy_hold_return if buy_hold_return > 0 else 0
                report_content += f"| 반대전략 {window_name} | {result_data['return_rate']:,.2f}% | {result_data['final_value']:,.0f}원 | {asset_ratio:.2f}배 | {return_ratio:.2f}배 |\n"
        
        # Buy & Hold
        buy_hold_stock_value = result.get('buy_hold_stock_value', buy_hold_final)
        buy_hold_dividends = result.get('buy_hold_dividends', 0)
        report_content += f"| **Buy & Hold** | **{buy_hold_return:,.2f}%** | **{buy_hold_final:,.0f}원** | **1.00배** | **1.00배** |\n"
        report_content += f"| └─ 주식자산 | - | {buy_hold_stock_value:,.0f}원 | - | - |\n"
        report_content += f"| └─ 배당금 | - | {buy_hold_dividends:,.0f}원 | - | - |\n"

    report_content += f"""

## 💡 **핵심 발견사항**

### 1. **기간별 최적 전략**
"""
    
    # 기간별 최적 전략 분석
    basic_wins = 0
    reverse_wins = 0
    
    for period, best in best_strategies.items():
        if best and '기본전략' in best['name']:
            basic_wins += 1
        elif best and '반대전략' in best['name']:
            reverse_wins += 1
    
    report_content += f"""
- **기본전략**이 {basic_wins}개 기간에서 최고 성과
- **반대전략**이 {reverse_wins}개 기간에서 최고 성과
- 전반적으로 {'기본전략' if basic_wins > reverse_wins else '반대전략'}이 우세

### 2. **기간별 특성**
"""

    # 가장 좋은 성과와 나쁜 성과 찾기
    if best_strategies:
        best_overall = max(best_strategies.items(), key=lambda x: x[1]['return_rate'] if x[1] else 0)
        worst_overall = min(best_strategies.items(), key=lambda x: x[1]['return_rate'] if x[1] else float('inf'))

        report_content += f"""
- **최고 성과 기간**: {best_overall[0]} ({best_overall[1]['return_rate']:,.2f}%)
- **최저 성과 기간**: {worst_overall[0]} ({worst_overall[1]['return_rate']:,.2f}%)
- **장기 vs 단기**: {"장기 투자가 더 유리" if best_overall[0] in ['20년', '30년'] else "단기 투자가 더 유리"}

### 3. **Buy&Hold 대비 계산 방법 설명**

**중요**: 본 분석에서는 Buy&Hold 대비를 두 가지 방식으로 계산합니다.

#### 📊 **최종 자산 기준 대비 (Buy&Hold 대비(자산))**
```
대비 비율 = 전략의 최종 자산 ÷ Buy&Hold 최종 자산
```
- **의미**: 같은 초기 투자금으로 시작했을 때 최종적으로 얼마나 더 많은 자산을 확보했는지
- **예시**: 전략 최종자산 1,200만원, Buy&Hold 최종자산 1,000만원 → 1.20배
- **장점**: 실제 투자 결과를 직관적으로 비교 가능

#### 📈 **수익률 기준 대비 (Buy&Hold 대비(수익률))**
```
대비 비율 = 전략의 수익률 ÷ Buy&Hold 수익률
```
- **의미**: 수익률의 상대적 성과를 비교
- **예시**: 전략 수익률 20%, Buy&Hold 수익률 15% → 1.33배
- **주의**: 음수 수익률이 포함될 경우 해석에 주의 필요

#### ⚠️ **해석 시 주의사항**
1. **수익률 대비가 1보다 작아도 최종 자산이 더 클 수 있음**
   - Buy&Hold 수익률이 음수이고 전략 수익률이 양수인 경우
   - 또는 두 수익률 모두 음수이지만 전략의 손실이 더 적은 경우

2. **권장 해석 방법**
   - **최종 자산 기준 대비**를 우선적으로 참고
   - 수익률 대비는 보조 지표로 활용
   - 절대적인 최종 자산 금액을 함께 고려

### 3. **투자 기간 권고사항**

#### ✅ **추천**
1. **{best_overall[0]} 투자**: 최고 수익률 {best_overall[1]['return_rate']:,.2f}%
2. **전략**: {best_overall[1]['name']}

#### ⚠️ **주의**
- 기간이 짧을수록 변동성이 클 수 있음
- 시장 상황에 따라 결과가 달라질 수 있음"""

    report_content += f"""

---

## 📋 **생성된 파일들**

### 그래프 파일
"""

    for period in all_results.keys():
        report_content += f"- `strategy_comparison_{period}.png`\n"

    report_content += f"""

### 매매 기록 파일
"""

    for period in all_results.keys():
        for window_name in ['2년', '3년', '5년']:
            report_content += f"- `trading_log_{period}_기본전략_{window_name}.csv`\n"
            report_content += f"- `trading_log_{period}_반대전략_{window_name}.csv`\n"

    report_content += f"""

---

**면책조항**: 본 분석은 과거 데이터에 기반한 백테스트 결과이며, 미래 수익을 보장하지 않습니다. 실제 투자시에는 시장 상황, 거래 비용, 세금 등을 종합적으로 고려하시기 바랍니다.
"""

    # 종합 리포트 파일 저장
    main_path, backup_path = save_report_files(report_content, f'{safe_company_name}_comprehensive_analysis_report')
    
    print(f"\n📋 종합 분석 리포트 저장 완료")

def generate_summary_report(all_results, company_name):
    """
    모든 기간의 백테스트 결과를 요약한 종합 리포트를 생성합니다.
    
    Args:
        all_results: 모든 기간의 결과 데이터
        company_name (str): 분석 대상 회사명
    """
    from datetime import datetime
    
    safe_company_name = company_name.replace('/', '_').replace('\\', '_')
    
    report_content = f"""# {company_name} 백테스트 종합 요약 리포트

**분석 날짜**: {datetime.now().strftime('%Y년 %m월 %d일')}  
**분석 기간**: 3년, 5년, 10년, 20년, 30년 백테스트  
**윈도우**: 2년, 3년, 5년 슬라이딩 윈도우  
**전략**: 기본전략 vs 반대전략

---

## 🏆 **최고 성과 TOP 5**

"""

    # 모든 전략 결과를 하나의 리스트로 수집
    all_strategies = []
    for period, result in all_results.items():
        for strategy_name, strategy_result in result['strategy_results'].items():
            all_strategies.append({
                'period': period,
                'strategy': strategy_name,
                'return_rate': strategy_result['return_rate'],
                'final_value': strategy_result['final_value'],
                'buy_hold_ratio': strategy_result['return_rate'] / result['buy_hold_return_rate']
            })
    
    # 수익률 기준으로 정렬
    all_strategies.sort(key=lambda x: x['return_rate'], reverse=True)
    
    report_content += "| 순위 | 기간 | 전략 | 수익률 | 최종 자산 | Buy&Hold 대비 |\n"
    report_content += "|------|------|------|--------|-----------|---------------|\n"
    
    medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
    for i, strategy in enumerate(all_strategies[:5]):
        medal = medals[i] if i < 5 else ''
        report_content += f"| {medal} | {strategy['period']} | {strategy['strategy']} | **{strategy['return_rate']:,.2f}%** | {strategy['final_value']:,.0f}원 | {strategy['buy_hold_ratio']:.1f}배 |\n"

    report_content += f"""

## 📊 **기간별 베스트 전략**

| 기간 | 최고 성과 전략 | 수익률 | 최종 자산 |
|------|---------------|--------|-----------|
"""

    # 각 기간별 최고 성과 전략
    period_best = {}
    for period, result in all_results.items():
        best_strategy = None
        best_return = -float('inf')
        
        for strategy_name, strategy_result in result['strategy_results'].items():
            if strategy_result['return_rate'] > best_return:
                best_return = strategy_result['return_rate']
                best_strategy = {
                    'name': strategy_name,
                    'return_rate': strategy_result['return_rate'],
                    'final_value': strategy_result['final_value']
                }
        
        period_best[period] = best_strategy
        
        if best_strategy:
            report_content += f"| {period} | {best_strategy['name']} | {best_strategy['return_rate']:,.2f}% | {best_strategy['final_value']:,.0f}원 |\n"

    report_content += f"""

## 🎯 **전략별 성과 분석**

### 기본전략 성과 (25%↓→{company_name}, 75%↑→{company_name}(우))

| 기간 | 2년 윈도우 | 3년 윈도우 | 5년 윈도우 | 최고 성과 |
|------|-----------|-----------|-----------|----------|
"""

    for period in ['3년', '5년', '10년', '20년', '30년']:
        if period in all_results:
            result = all_results[period]
            basic_2 = result['strategy_results'].get('기본전략_2년', {}).get('return_rate', 0)
            basic_3 = result['strategy_results'].get('기본전략_3년', {}).get('return_rate', 0)
            basic_5 = result['strategy_results'].get('기본전략_5년', {}).get('return_rate', 0)
            best_basic = max(basic_2, basic_3, basic_5)
            
            best_window = '2년' if best_basic == basic_2 else ('3년' if best_basic == basic_3 else '5년')
            
            report_content += f"| {period} | {basic_2:,.1f}% | {basic_3:,.1f}% | {basic_5:,.1f}% | **{best_basic:,.1f}%** ({best_window}) |\n"

    report_content += f"""

### 반대전략 성과 (25%↓→{company_name}(우), 75%↑→{company_name})

| 기간 | 2년 윈도우 | 3년 윈도우 | 5년 윈도우 | 최고 성과 |
|------|-----------|-----------|-----------|----------|
"""

    for period in ['3년', '5년', '10년', '20년', '30년']:
        if period in all_results:
            result = all_results[period]
            reverse_2 = result['strategy_results'].get('반대전략_2년', {}).get('return_rate', 0)
            reverse_3 = result['strategy_results'].get('반대전략_3년', {}).get('return_rate', 0)
            reverse_5 = result['strategy_results'].get('반대전략_5년', {}).get('return_rate', 0)
            best_reverse = max(reverse_2, reverse_3, reverse_5)
            
            best_window = '2년' if best_reverse == reverse_2 else ('3년' if best_reverse == reverse_3 else '5년')
            
            report_content += f"| {period} | {reverse_2:,.1f}% | {reverse_3:,.1f}% | {reverse_5:,.1f}% | **{best_reverse:,.1f}%** ({best_window}) |\n"

    report_content += f"""

## � **기간별 전략 상세 성과표**

"""

    # 각 기간별 상세 성과표 생성
    for period in ['3년', '5년', '10년', '20년', '30년']:
        if period in all_results:
            result = all_results[period]
            buy_hold_final = result['buy_hold_final_value']
            
            report_content += f"""
### {period} 백테스트 결과

| 전략 | 최종 자산 | Buy&Hold 대비 | 매매 횟수 |
|------|-----------|---------------|----------|
"""
            
            # 기본전략들
            for window_name in ['2년', '3년', '5년']:
                strategy_name = f"기본전략_{window_name}"
                if strategy_name in result['strategy_results']:
                    final_value = result['strategy_results'][strategy_name]['final_value']
                    ratio = (final_value / buy_hold_final) * 100
                    trades = len([log for log in result['strategy_results'][strategy_name]['trading_log'] if log['Action'] == '매도->매수'])
                    report_content += f"| **기본전략_{window_name}** | {final_value:,.0f}원 | {ratio:.1f}% | {trades}회 |\n"
            
            # 반대전략들
            for window_name in ['2년', '3년', '5년']:
                strategy_name = f"반대전략_{window_name}"
                if strategy_name in result['strategy_results']:
                    final_value = result['strategy_results'][strategy_name]['final_value']
                    ratio = (final_value / buy_hold_final) * 100
                    trades = len([log for log in result['strategy_results'][strategy_name]['trading_log'] if log['Action'] == '매도->매수'])
                    report_content += f"| **반대전략_{window_name}** | {final_value:,.0f}원 | {ratio:.1f}% | {trades}회 |\n"
            
            # Buy & Hold
            report_content += f"| **Buy & Hold** | {buy_hold_final:,.0f}원 | 100.0% | 0회 |\n"

    report_content += f"""

## �💡 **핵심 인사이트**

### 1. **투자 기간의 중요성**
"""

    # 기간별 성과 분석
    if all_strategies:
        best_period = all_strategies[0]['period']
        worst_period_strategies = [s for s in all_strategies if s['period'] == '3년']
        worst_period_best = max(worst_period_strategies, key=lambda x: x['return_rate']) if worst_period_strategies else None
        
        long_term_strategies = [s for s in all_strategies if s['period'] in ['20년', '30년']]
        short_term_strategies = [s for s in all_strategies if s['period'] in ['3년', '5년']]
        
        long_term_avg = sum(s['return_rate'] for s in long_term_strategies) / len(long_term_strategies) if long_term_strategies else 0
        short_term_avg = sum(s['return_rate'] for s in short_term_strategies) / len(short_term_strategies) if short_term_strategies else 0
        
        report_content += f"""
- **최고 성과 기간**: {best_period} ({all_strategies[0]['return_rate']:,.2f}%)
- **장기 투자 평균**: {long_term_avg:,.1f}% (20년, 30년)
- **단기 투자 평균**: {short_term_avg:,.1f}% (3년, 5년)
- **장기 vs 단기**: {"장기 투자가 " + f"{long_term_avg/short_term_avg:.1f}배 더 유리" if long_term_avg > short_term_avg else "단기 투자가 더 유리"}

### 2. **윈도우 크기 선택**
"""

    # 윈도우별 승률 계산
    window_wins = {'2년': 0, '3년': 0, '5년': 0}
    for period in ['3년', '5년', '10년', '20년', '30년']:
        if period in all_results:
            result = all_results[period]
            period_strategies = []
            for strategy_name, strategy_result in result['strategy_results'].items():
                window = strategy_name.split('_')[1] if '_' in strategy_name else 'unknown'
                period_strategies.append({
                    'window': window,
                    'return_rate': strategy_result['return_rate']
                })
            
            if period_strategies:
                best_strategy = max(period_strategies, key=lambda x: x['return_rate'])
                if best_strategy['window'] in window_wins:
                    window_wins[best_strategy['window']] += 1

    best_window = max(window_wins.items(), key=lambda x: x[1])
    
    report_content += f"""
- **가장 자주 최고 성과를 낸 윈도우**: {best_window[0]} ({best_window[1]}번 승리)
- **윈도우별 승률**: 2년 {window_wins['2년']}회, 3년 {window_wins['3년']}회, 5년 {window_wins['5년']}회

### 3. **전략 선택 가이드**
"""

    # 기본전략 vs 반대전략 승률
    basic_wins = 0
    reverse_wins = 0
    
    for strategy in all_strategies[:10]:  # 상위 10개 전략
        if '기본전략' in strategy['strategy']:
            basic_wins += 1
        else:
            reverse_wins += 1
    
    report_content += f"""
- **상위 10개 전략 중**: 기본전략 {basic_wins}개, 반대전략 {reverse_wins}개
- **추천 전략**: {'기본전략' if basic_wins > reverse_wins else '반대전략'}
- **핵심 원리**: 가격차이비율이 {'낮을 때 ' + company_name + ', 높을 때 ' + company_name + '(우)' if basic_wins > reverse_wins else '낮을 때 ' + company_name + '(우), 높을 때 ' + company_name}

---

## 🎯 **투자 권고사항**

### ✅ **최적 포트폴리오**

1. **{all_strategies[0]['period']} 투자 + {all_strategies[0]['strategy']}**
   - 예상 수익률: **{all_strategies[0]['return_rate']:,.2f}%**
   - Buy & Hold 대비: **{all_strategies[0]['buy_hold_ratio']:.1f}배**

2. **안정적 선택: {best_window[0]} 윈도우 전략**
   - 가장 일관성 있는 성과
   - 리스크 대비 안정적 수익

### ⚠️ **주의사항**

- 과거 성과가 미래 수익을 보장하지 않음
- 실제 거래 비용 및 세금 고려 필요
- 시장 상황 변화에 따른 전략 조정 권장

---

## 📁 **관련 파일**

### 📈 **그래프**
"""

    for period in ['3년', '5년', '10년', '20년', '30년']:
        if period in all_results:
            report_content += f"- `strategy_comparison_{period}.png`\n"

    report_content += f"""

### 📊 **개별 분석 리포트**
"""

    for period in ['3년', '5년', '10년', '20년', '30년']:
        if period in all_results:
            report_content += f"- `strategy_analysis_report_{period}_[날짜].md`\n"

    report_content += f"""

### 📋 **매매 기록**
- 각 기간별, 전략별 CSV 파일 (총 30개 파일)
- 파일명: `trading_log_[기간]_[전략]_[윈도우].csv`

---

**📝 분석 완료**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}  
**💼 면책조항**: 본 분석은 과거 데이터 기반 백테스트 결과이며, 실제 투자 시 다양한 요인을 종합적으로 고려하시기 바랍니다.
"""

    # 종합 요약 리포트 파일 저장
    main_path, backup_path = save_report_files(report_content, f'{safe_company_name}_summary_backtest_report')
    
    print(f"\n📋 종합 요약 리포트 저장 완료")

def run_backtest(json_file_path, initial_stock_type, initial_shares, start_date_str, company_name):
    """
    2년 슬라이딩 윈도우 사분위 기반 전략에 따라 백테스트를 수행하고 투자 결과를 분석합니다.
    
    기본 전략:
    - 가격차이비율이 2년 슬라이딩 윈도우 25% 분위 이하: 보통주(상대적 저평가) 매수
    - 가격차이비율이 2년 슬라이딩 윈도우 75% 분위 이상: 우선주(상대적 저평가) 매수
    
    반대 전략:
    - 가격차이비율이 2년 슬라이딩 윈도우 25% 분위 이하: 우선주 매수
    - 가격차이비율이 2년 슬라이딩 윈도우 75% 분위 이상: 보통주 매수
    
    또한, 각 전략의 월별 평가 금액 그래프를 생성하여 PNG 파일로 저장합니다.

    Args:
        json_file_path (str): 주식 데이터가 포함된 JSON 파일 경로.
        initial_stock_type (str): 초기 보유 주식 유형 (회사명 또는 '회사명(우)').
        initial_shares (int): 초기 보유 주식 수.
        start_date_str (str): 백테스트 시작 날짜 (YY-mm-dd 형식).
        company_name (str): 분석할 회사명.
    """
    try:
        print(f"📁 파일 로딩: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ 파일 로딩 완료: {len(data)}개 데이터 포인트")

        df = pd.DataFrame.from_dict(data, orient='index')
        df.index = pd.to_datetime(df.index, format='%y-%m-%d')
        df = df.sort_index()

        # 백테스트 시작 날짜 이후의 데이터만 사용
        start_date = datetime.strptime(start_date_str, '%y-%m-%d')
        df_backtest = df[df.index >= start_date].copy()

        if df_backtest.empty:
            print(f"오류: 백테스트 시작 날짜({start_date_str}) 이후의 데이터가 없습니다.")
            return

        # 초기 자산 가치 계산 (동적 회사명 지원)
        first_day_data = df_backtest.iloc[0]
        # 회사명에 따른 주식 유형명 설정
        common_stock_name = company_name
        preferred_stock_name = f"{company_name}(우)"
        
        if initial_stock_type == common_stock_name:
            initial_value = initial_shares * first_day_data['Stock1_Open']
        else: # preferred_stock_name
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
            print(f"- 가격차이비율 < {window_name} 슬라이딩 25% 분위: {common_stock_name} 매수 (상대적 저평가)")
            print(f"- 가격차이비율 > {window_name} 슬라이딩 75% 분위: {preferred_stock_name} 매수 (상대적 저평가)")

            basic_strategy_name = f"기본전략_{window_name}"
            strategy_results[basic_strategy_name] = run_single_strategy(
                df_backtest, initial_stock_type, initial_shares, initial_value, company_name,
                False, basic_strategy_name, window_suffix
            )
            
            # 반대 전략
            print(f"\n--- {window_name} 반대 전략 ---")
            print(f"- 가격차이비율 < {window_name} 슬라이딩 25% 분위: {preferred_stock_name} 매수")
            print(f"- 가격차이비율 > {window_name} 슬라이딩 75% 분위: {common_stock_name} 매수")

            reverse_strategy_name = f"반대전략_{window_name}"
            strategy_results[reverse_strategy_name] = run_single_strategy(
                df_backtest, initial_stock_type, initial_shares, initial_value, company_name,
                True, reverse_strategy_name, window_suffix
            )

        # --- Buy & Hold 전략 (stock_diff.py 배당 데이터 활용) ---
        print("\n" + "="*60)
        print(f"=== {common_stock_name} Buy & Hold 결과 ===")
        buy_hold_initial_shares = 1000
        buy_hold_initial_value = buy_hold_initial_shares * first_day_data['Stock1_Open']
        
        buy_hold_portfolio_values = [] # 일별 Buy & Hold 포트폴리오 가치 저장
        accumulated_buy_hold_dividends = 0.0 # 누적 배당금

        # stock_diff.py에서 처리된 배당 데이터 활용 (하드코딩 제거)
        print(f"📈 {common_stock_name} Buy & Hold 전략 (stock_diff.py 배당 데이터 활용)")
        
        for date, row in df_backtest.iterrows():
            # stock_diff.py에서 처리된 배당 데이터 활용
            if 'Dividend_Amount_Raw' in row and row['Dividend_Amount_Raw'] > 0:
                daily_dividend = row['Dividend_Amount_Raw'] * buy_hold_initial_shares
                accumulated_buy_hold_dividends += daily_dividend
                print(f"  📅 {date.strftime('%Y-%m-%d')}: 배당 {row['Dividend_Amount_Raw']:,.0f}원/주 → 총 {daily_dividend:,.0f}원")
            
            buy_hold_daily_value = buy_hold_initial_shares * row['Stock1_Close'] + accumulated_buy_hold_dividends
            buy_hold_portfolio_values.append({'Date': date, 'Value': buy_hold_daily_value})

        buy_hold_final_value = buy_hold_initial_shares * df_backtest.iloc[-1]['Stock1_Close']
        buy_hold_final_total_value = buy_hold_final_value + accumulated_buy_hold_dividends
        # 배당금을 제외한 수익률 계산 (초기 투자금 1억원 기준)
        initial_capital = 100_000_000  # 1억원
        return_without_dividends_buy_hold = ((buy_hold_final_value - initial_capital) / initial_capital) * 100

        print(f"초기 보유: {buy_hold_initial_shares}주 {common_stock_name} (시가 기준 초기 가치: {buy_hold_initial_value:,.2f}원)")
        print(f"최종 보유: {buy_hold_initial_shares}주 {common_stock_name}")
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
        print(f"\n--- 기본전략 (25%↓→{common_stock_name}, 75%↑→{preferred_stock_name}) ---")
        for window_name in ['2년', '3년', '5년']:
            strategy_name = f"기본전략_{window_name}"
            if strategy_name in strategy_results:
                result = strategy_results[strategy_name]
                print(f"{window_name} 윈도우: {result['return_rate']:,.2f}% (자산: {result['final_value']:,.0f}원)")
        
        # 윈도우별 반대전략 비교
        print(f"\n--- 반대전략 (25%↓→{preferred_stock_name}, 75%↑→{common_stock_name}) ---")
        for window_name in ['2년', '3년', '5년']:
            strategy_name = f"반대전략_{window_name}"
            if strategy_name in strategy_results:
                result = strategy_results[strategy_name]
                print(f"{window_name} 윈도우: {result['return_rate']:,.2f}% (자산: {result['final_value']:,.0f}원)")
        
        print(f"\n--- Buy & Hold 참고 ---")
        print(f"{common_stock_name} Buy & Hold: {return_without_dividends_buy_hold:,.2f}% (자산: {buy_hold_final_total_value:,.0f}원)")

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
        ax1.plot(monthly_buy_hold_df.index, monthly_buy_hold_df['Value'], label=f'{common_stock_name} Buy & Hold', marker='x', markersize=3, linestyle='--')
        
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
        ax2.plot(monthly_buy_hold_df.index, monthly_buy_hold_df['Value'], label=f'{common_stock_name} Buy & Hold', marker='x', markersize=3, linestyle='--')
        
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
                                start_date_str, df_backtest.index[-1].strftime('%y-%m-%d'), initial_value, company_name, "기본")

    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다. 경로를 확인해주세요: {json_file_path}")
    except json.JSONDecodeError:
        print(f"오류: JSON 파일을 디코딩할 수 없습니다. 파일 형식을 확인해주세요: {json_file_path}")
    except Exception as e:
        print(f"데이터 처리 중 오류가 발생했습니다: {e}")

def run_all_companies_backtest():
    """
    모든 지원되는 회사에 대해 백테스트를 수행합니다.
    """
    print("🌐 모든 회사 백테스트 분석 시작")
    print("=" * 80)
    
    for company_name in PREFERRED_STOCK_COMPANIES.keys():
        try:
            print(f"\n🏢 {company_name} 백테스트 시작...")
            run_comprehensive_backtest(company_name)
            print(f"✅ {company_name} 백테스트 완료")
        except Exception as e:
            print(f"❌ {company_name} 백테스트 중 오류: {e}")
    
    print(f"\n{'='*80}")
    print("=== 모든 회사 백테스트 완료 ===")
    print(f"{'='*80}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='우선주 백테스트 분석')
    parser.add_argument('--company', '-c', type=str, help='분석할 회사명 (지정하지 않으면 모든 회사 분석)')
    
    args = parser.parse_args()
    
    print("="*80)
    print("우선주 차익거래 백테스트 시스템")
    print("="*80)
    print("💰 초기 자본: 1억원 (100,000,000원)")
    print("📊 분석 기간: 3년, 5년, 10년, 20년, 30년")
    print("⏰ 윈도우 크기: 2년, 3년, 5년 슬라이딩 윈도우")
    print("📈 전략:")
    print("   - 기본전략 (25%↓→보통주, 75%↑→우선주)")
    print("   - 반대전략 (25%↓→우선주, 75%↑→보통주)")
    print("   - 보통주 Buy & Hold")
    print("   - 우선주 Buy & Hold")
    print("="*80)
    
    if args.company:
        # 특정 회사 백테스트
        if args.company in PREFERRED_STOCK_COMPANIES:
            run_comprehensive_backtest(args.company)
        else:
            print(f"❌ 지원되지 않는 회사입니다: {args.company}")
            print(f"지원되는 회사: {list(PREFERRED_STOCK_COMPANIES.keys())}")
    else:
        # 모든 회사 백테스트
        run_all_companies_backtest()
