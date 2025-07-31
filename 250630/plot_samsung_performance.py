import json
import matplotlib.pyplot as plt
from datetime import datetime
import platform

# 운영체제에 맞는 한글 폰트 설정
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Linux':
    # 리눅스에 나눔고딕 폰트가 설치되어 있어야 합니다.
    # 터미널에 다음 명령어를 입력하여 설치할 수 있습니다:
    # sudo apt-get update && sudo apt-get install -y fonts-nanum*
    plt.rc('font', family='NanumGothic')

# JSON 파일 읽기
with open('samsung_diff.json', 'r') as f:
    samsung_diff_data = json.load(f)

# 그래프를 그릴 데이터 준비
dates = []
changed_values = []
buy_and_hold_values = []

# 매월 14일, 29일 데이터만 추출
for date_str in sorted(samsung_diff_data.keys()):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    if date_obj.day in [14, 29]: # 14일, 29일 데이터만 선택
        dates.append(date_str)
        changed_values.append(samsung_diff_data[date_str]['changed_total_value'])
        buy_and_hold_values.append(samsung_diff_data[date_str]['buy_and_hold_total_value'])

# 그래프 그리기
plt.figure(figsize=(12, 6))
plt.plot(dates, changed_values, label='전략 적용 포트폴리오', marker='o')
plt.plot(dates, buy_and_hold_values, label='단순 보유 포트폴리오', marker='x')

plt.xlabel('날짜')
plt.ylabel('총 평가액')
plt.title('삼성전자 주식 포트폴리오 성과 비교 (매월 14, 29일 기준)')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()

# PNG 파일로 저장
plt.savefig('samsung_performance_comparison.png')
print("samsung_performance_comparison.png 파일이 생성되었습니다.")