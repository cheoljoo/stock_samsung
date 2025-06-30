
import yfinance as yf
import json
from datetime import datetime

# 삼성전자 티커는 005930.KS 입니다.
ticker = "005930.KS"

# 데이터 가져오기 (현재 날짜까지)
data = yf.download(ticker, start="2015-01-01", end=datetime.now().strftime('%Y-%m-%d'))

# 필요한 데이터만 추출하여 딕셔너리로 변환
price_dict = {}
for index, row in data.iterrows():
    date_str = index.strftime('%Y-%m-%d')
    price_dict[date_str] = {
        'open': float(row['Open']),
        'close': float(row['Close'])
    }

# JSON 파일로 저장
with open("samsung_ltd_price.json", "w") as f:
    json.dump(price_dict, f, indent=4)

print("samsung_ltd_price.json 파일이 생성되었습니다.")
