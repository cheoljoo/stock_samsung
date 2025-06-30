
import json
import matplotlib.pyplot as plt
from datetime import datetime

# JSON 파일 읽기
with open('samsung_diff.json', 'r') as f:
    samsung_diff_data = json.load(f)

# 그래프를 그릴 데이터 준비
dates = []
changed_values = []
buy_and_hold_values = []

# 매년 1월 데이터만 추출
for date_str in sorted(samsung_diff_data.keys()):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    if date_obj.month == 1: # 1월 데이터만 선택
        dates.append(date_str)
        changed_values.append(samsung_diff_data[date_str]['changed_total_value'])
        buy_and_hold_values.append(samsung_diff_data[date_str]['buy_and_hold_total_value'])

# 그래프 그리기
plt.figure(figsize=(12, 6))
plt.plot(dates, changed_values, label='Changed Portfolio Value', marker='o')
plt.plot(dates, buy_and_hold_values, label='Buy & Hold Portfolio Value', marker='x')

plt.xlabel('Date')
plt.ylabel('Total Value')
plt.title('Samsung Stock Performance Comparison (January Data)')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()

# PNG 파일로 저장
plt.savefig('samsung_performance_comparison.png')
print("samsung_performance_comparison.png 파일이 생성되었습니다.")
