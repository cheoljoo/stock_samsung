import pandas as pd
import json
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
        print("나눔고딕 폰트가 설치되어 있지 않습니다. 'sudo apt-get install fonts-nanum*'으로 설치할 수 있습니다.")
        # 설치되어 있지 않으면 다른 사용 가능한 폰트를 사���하거나, 경고 메시지를 출력합니다.
        # 여기서는 sans-serif를 기본값으로 사용합니다.
        plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False # 마이너스 폰트 깨짐 방지

def analyze_price_diff_ratio(json_file_path):
    """
    JSON 파일에서 Price_Diff_Ratio의 분포를 분석하고 해석 가이드를 제공합니다.

    Args:
        json_file_path (str): 분석할 JSON 파일의 경로.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 딕셔너리를 DataFrame으로 변환
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index = pd.to_datetime(df.index, format='%y-%m-%d') # 인덱스를 datetime 객체로 변환
        df = df.sort_index() # 날짜 기준으로 정렬

        if 'Price_Diff_Ratio' not in df.columns:
            print(f"오류: '{json_file_path}' 파일에 'Price_Diff_Ratio' 컬럼이 없습니다.")
            return

        price_diff_ratio = df['Price_Diff_Ratio']

        print("--- Price_Diff_Ratio 분포 분석 ---")
        print("\n1. 기술 통계량:")
        print(price_diff_ratio.describe())

        print("\n2. 분포 시각화 (히스토그램 및 박스 플롯):")
        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        sns.histplot(price_diff_ratio, kde=True)
        plt.title('Price_Diff_Ratio 히스토그램')
        plt.xlabel('Price_Diff_Ratio (%)')
        plt.ylabel('빈도')

        plt.subplot(1, 2, 2)
        sns.boxplot(y=price_diff_ratio)
        plt.title('Price_Diff_Ratio 박스 플롯')
        plt.ylabel('Price_Diff_Ratio (%)')

        plt.tight_layout()
        plt.show()

        print("\n--- Price_Diff_Ratio 해석 가이드 ---")
        print("Price_Diff_Ratio = (삼성전자 종가 - 삼성전자(우) 종가) * 100 / 삼성전자(우) 종가")
        print("이 비율은 삼성전자(우) 가격 대비 삼성전자와 삼성전자(우) 간의 가격 차이를 백분율로 나타냅니다.")
        print("\n투자 관점:")
        print("  - 비율이 작을수록 (음수이거나 0에 가까울수록): 삼성전자(우) 대비 삼성전자의 가격이 상대적으로 낮다는 의미입니다.")
        print("    따라서, 삼성전자를 매수하는 것이 유리할 수 있습니다 (상대적으로 저평가).")
        print("  - 비율이 클수록 (양수이고 값이 높을수록): 삼성전자(우) 대비 삼성전자의 가격이 상대적으로 높다는 의미입니다.")
        print("    따라서, 삼성전자(우)를 매수하는 것이 유리할 수 있습니다 (상대적으로 저평가).")
        print("\n'크다' 또는 '작다'의 기준:")
        print("  - **평균 (Mean) 및 중앙값 (Median):** 이 값들은 비율의 '중심'을 나타냅니다. 이보다 낮은 비율은 상대적으로 '작다'고 볼 수 있고, 높은 비율은 '크다'고 볼 수 있습니다.")
        print("  - **표준편차 (Standard Deviation):** 데이터가 평균으로부터 얼마나 퍼져 있는지를 나타냅니다. 표준편차 범위(예: 평균 ± 1 표준편차)를 벗어나는 값들은 상대적으로 극단적인 값으로 해석할 수 있습니다.")
        print("  - **사분위수 (Quartiles - 25%, 50%, 75%):** 박스 플롯에서 시각적으로 확인할 수 있으며, 데이터의 25%, 50%(중앙값), 75% 지점을 나타냅니다.")
        print("    - 25% 값보다 작으면 하위 25%에 해당하므로 '매우 작은' 비율로 볼 수 있습니다.")
        print("    - 75% 값보다 크면 상위 25%에 해당하므로 '매우 큰' 비율로 볼 수 있습니다.")
        print("  - **역사적 범위 (Min/Max):** 최소값과 최대값은 비율이 가질 수 있는 극단적인 범위를 보여줍니다. 현재 비율이 역사적 최소값에 가까우면 삼성전자가 유리하고, 최대값에 가까우면 삼성전자(우)가 유리하다고 판단할 수 있습니다.")
        print("\n결론적으로, '크다' 또는 '작다'의 기준은 절대적인 것이 아니라, 해당 비율의 **역사적 분포**와 **평균, 중앙값, 사분위수**를 기준으로 상대적으로 판단해야 합니다. 히스토그램과 박스 플롯을 통해 시각적으로 분포를 확인하면 더욱 직관적인 이해를 얻을 수 있습니다.")

    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다. 경로를 확인해주세요: {json_file_path}")
    except json.JSONDecodeError:
        print(f"오류: JSON 파일을 디코딩할 수 없습니다. 파일 형식을 확인해주세요: {json_file_path}")
    except Exception as e:
        print(f"데이터 처리 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    json_file = r'./samsung_stock_analysis.json'
    analyze_price_diff_ratio(json_file)
