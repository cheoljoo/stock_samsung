
import yfinance as yf
import json

# 삼성전자 우선주 티커는 005935.KS 입니다.
ticker = "005935.KS"
samsung_pref = yf.Ticker(ticker)

# 배당금 정보 가져오기
dividends = samsung_pref.dividends

# 딕셔너리로 변환
dividend_dict = {}
for date, dividend in dividends.items():
    date_str = date.strftime('%Y-%m-%d')
    dividend_dict[date_str] = float(dividend)

# JSON 파일로 저장
with open("samsung_pref_dividend.json", "w") as f:
    json.dump(dividend_dict, f, indent=4)

print("samsung_pref_dividend.json 파일이 생성되었습니다.")
