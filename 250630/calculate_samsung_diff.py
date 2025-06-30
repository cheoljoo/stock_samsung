
import json
import numpy as np
from datetime import datetime, timedelta

# JSON 파일 읽기
with open('samsung_ltd_price.json', 'r') as f:
    ltd_price_data = json.load(f)

with open('samsung_pref_price.json', 'r') as f:
    pref_price_data = json.load(f)

with open('samsung_ltd_dividend.json', 'r') as f:
    ltd_dividend_data = json.load(f)

with open('samsung_pref_dividend.json', 'r') as f:
    pref_dividend_data = json.load(f)

diff_data = {}
diff_ratio_history = [] # diff_ratio를 저장할 리스트

# 오늘 날짜와 10년 전 날짜 계산
today = datetime.now()
ten_years_ago = today - timedelta(days=365 * 10) # 대략 10년

# 초기 주식 보유량 및 가치 설정
prev_ltd_count = 0
prev_pref_count = 0
prev_ltd_close = 0
prev_pref_close = 0
portfolio_value = 0 # 포트폴리오의 현재 가치 (전날 종가 기준)
prev_range = "normal" # 전날의 range 값 초기화
prev_balanced = 0 # 전날의 남은 현금
changed_total_dividend = 0 # 변경된 포트폴리오의 총 배당금
buy_and_hold_total_dividend = 0 # buy_and_hold 포트폴리오의 총 배당금

first_trading_day_processed = False

# 날짜를 기준으로 데이터 처리
for date_str in sorted(ltd_price_data.keys()):
    current_date = datetime.strptime(date_str, '%Y-%m-%d')

    # 10년 전 데이터부터 처리
    if current_date >= ten_years_ago:
        if date_str in pref_price_data:
            ltd_close = ltd_price_data[date_str]['close']
            pref_close = pref_price_data[date_str]['close']

            # 첫 번째 유효한 거래일 처리
            if not first_trading_day_processed:
                # 처음에 삼성전자 보통주 1000주를 가지고 있다고 가정
                prev_ltd_count = 1000
                prev_pref_count = 0
                portfolio_value = prev_ltd_count * ltd_close # 첫 날의 종가로 가치 계산
                prev_balanced = 0 # 초기 현금은 0
                first_trading_day_processed = True
            else:
                # 전날의 종가로 포트폴리오 가치 계산 (오늘 매매를 위한 자본) + 남은 현금
                portfolio_value = (prev_ltd_count * prev_ltd_close) + (prev_pref_count * prev_pref_close) + prev_balanced

            diff = ltd_close - pref_close
            diff_ratio = diff / pref_close if pref_close != 0 else 0
            diff_ratio_history.append(diff_ratio)

            # 현재까지의 diff_ratio 데이터로 사분위 계산
            q25 = np.percentile(diff_ratio_history, 25)
            q75 = np.percentile(diff_ratio_history, 75)

            # 현재 날짜의 range 계산
            current_range = "normal"
            if diff_ratio < q25:
                current_range = "q25"
            elif diff_ratio > q75:
                current_range = "q75"

            # 주식 매매 로직 (오늘의 종가로 매매)
            current_ltd_count = prev_ltd_count
            current_pref_count = prev_pref_count
            current_balanced = prev_balanced

            if prev_range == "normal" and current_range == "q25":
                # 삼성전자(우)를 팔고 삼성전자 보통주를 산다
                num_shares_to_buy = int(portfolio_value / ltd_close) if ltd_close != 0 else 0
                current_ltd_count = num_shares_to_buy
                current_pref_count = 0
                current_balanced = portfolio_value - (num_shares_to_buy * ltd_close)
            elif prev_range == "normal" and current_range == "q75":
                # 삼성전자를 팔고 삼성전자(우)를 산다
                num_shares_to_buy = int(portfolio_value / pref_close) if pref_close != 0 else 0
                current_ltd_count = 0
                current_pref_count = num_shares_to_buy
                current_balanced = portfolio_value - (num_shares_to_buy * pref_close)
            # else: 그 외의 경우에는 전날의 주식 보유량을 유지

            # 배당금 계산 및 추가
            if date_str in ltd_dividend_data:
                changed_total_dividend += current_ltd_count * ltd_dividend_data[date_str]
                buy_and_hold_total_dividend += 1000 * ltd_dividend_data[date_str] # buy_and_hold는 항상 삼성전자 보통주 1000주
            if date_str in pref_dividend_data:
                changed_total_dividend += current_pref_count * pref_dividend_data[date_str]
                # buy_and_hold는 삼성전자 보통주만 가지고 있으므로 우선주 배당은 계산하지 않음

            # total_value 계산
            changed_total_value = (current_ltd_count * ltd_close) + (current_pref_count * pref_close) + current_balanced
            buy_and_hold_total_value = 1000 * ltd_close # buy_and_hold는 항상 삼성전자 보통주 1000주로 가정

            diff_data[date_str] = {
                'diff': diff,
                'diff_ratio': diff_ratio,
                'samsung_ltd_close': ltd_close,
                'samsung_pref_close': pref_close,
                'q25': q25,
                'q75': q75,
                'buy_and_hold': 1000, # 이 값은 항상 1000으로 고정
                'samsung_ltd_count': current_ltd_count,
                'samsung_pref_count': current_pref_count,
                'range': current_range,
                'changed_total_value': changed_total_value,
                'buy_and_hold_total_value': buy_and_hold_total_value,
                'balanced': current_balanced,
                'changed_total_dividend': changed_total_dividend,
                'buy_and_hold_total_dividend': buy_and_hold_total_dividend
            }

            # 다음 날을 위한 현재 날짜의 종가와 주식 수, range, balanced 저장
            prev_ltd_count = current_ltd_count
            prev_pref_count = current_pref_count
            prev_ltd_close = ltd_close
            prev_pref_close = pref_close
            prev_range = current_range
            prev_balanced = current_balanced

# JSON 파일로 저장
with open('samsung_diff.json', 'w') as f:
    json.dump(diff_data, f, indent=4)

print("samsung_diff.json 파일이 생성되었습니다.")
