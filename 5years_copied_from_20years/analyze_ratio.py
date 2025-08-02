import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import platform
import matplotlib.font_manager as fm
import warnings

# 한글 폰트 설정 함수
def setup_korean_font():
    """
    한글 폰트를 안정적으로 설정하는 함수
    """
    # matplotlib 폰트 관련 경고 메시지 억제
    warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
    warnings.filterwarnings("ignore", message="Glyph*missing from font*")
    warnings.filterwarnings("ignore", message="findfont: Font family*not found*")
    
    # 한글 폰트 직접 설정 (우선순위 순)
    korean_fonts = [
        'NanumGothic',
        'NanumBarunGothic', 
        'NanumMyeongjo',
        'DejaVu Sans'
    ]
    
    # 폰트 설정
    plt.rcParams['font.family'] = korean_fonts
    plt.rcParams['axes.unicode_minus'] = False
    
    print(f"폰트 설정 완료: {korean_fonts[0]} (fallback: {korean_fonts[1:]})")
    return True

# 폰트 설정 실행
setup_korean_font()

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
        plt.savefig('price_diff_ratio_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("히스토그램과 박스플롯이 'price_diff_ratio_distribution.png'로 저장되었습니다.")

        # 추가 그래프: 시간에 따른 가격 및 비율 변화
        print("\n3. 시간에 따른 가격 및 비율 변화:")
        
        # 필요한 컬럼들이 있는지 확인 (실제 컬럼명에 맞게 수정)
        required_columns = ['Stock1_Close', 'Stock2_Close', 'Price_Difference', 'Price_Diff_Ratio']
        available_columns = [col for col in required_columns if col in df.columns]
        
        if len(available_columns) >= 2:
            # 첫 번째 그래프: 삼성전자 종가, 삼성전자(우) 종가, 가격 차이
            print("첫 번째 그래프: 종가 및 가격 차이")
            fig, axes = plt.subplots(3, 1, figsize=(15, 12))
            fig.suptitle('삼성전자와 삼성전자(우) 종가 및 가격 차이', fontsize=16)
            
            # 첫 번째 서브플롯: 삼성전자 종가
            if 'Stock1_Close' in df.columns:
                axes[0].plot(df.index, df['Stock1_Close'], label='삼성전자', color='blue', linewidth=1.5)
                axes[0].set_title('삼성전자 종가')
                axes[0].set_ylabel('가격 (원)')
                axes[0].grid(True, alpha=0.3)
                axes[0].tick_params(axis='x', rotation=45)
            
            # 두 번째 서브플롯: 삼성전자(우) 종가
            if 'Stock2_Close' in df.columns:
                axes[1].plot(df.index, df['Stock2_Close'], label='삼성전자(우)', color='red', linewidth=1.5)
                axes[1].set_title('삼성전자(우) 종가')
                axes[1].set_ylabel('가격 (원)')
                axes[1].grid(True, alpha=0.3)
                axes[1].tick_params(axis='x', rotation=45)
            
            # 세 번째 서브플롯: 가격 차이
            if 'Price_Difference' in df.columns:
                axes[2].plot(df.index, df['Price_Difference'], label='가격 차이', color='green', linewidth=1.5)
                axes[2].set_title('가격 차이 (삼성전자 - 삼성전자(우))')
                axes[2].set_ylabel('가격 차이 (원)')
                axes[2].set_xlabel('날짜')
                axes[2].grid(True, alpha=0.3)
                axes[2].tick_params(axis='x', rotation=45)
                # 0선 표시
                axes[2].axhline(y=0, color='black', linestyle='--', alpha=0.5)
            
            plt.tight_layout()
            plt.savefig('stock_prices_and_difference.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("종가 및 가격 차이 그래프가 'stock_prices_and_difference.png'로 저장되었습니다.")
            
            # 두 번째 그래프: 가격 차이 비율 (별도 그래프)
            if 'Price_Diff_Ratio' in df.columns:
                print("두 번째 그래프: 가격 차이 비율")
                plt.figure(figsize=(15, 6))
                plt.plot(df.index, df['Price_Diff_Ratio'], label='가격 차이 비율', color='purple', linewidth=1.5)
                plt.title('가격 차이 비율 (%)', fontsize=16)
                plt.ylabel('비율 (%)')
                plt.xlabel('날짜')
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                
                # 0선 표시
                plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
                
                # 평균선 표시
                mean_ratio = df['Price_Diff_Ratio'].mean()
                plt.axhline(y=mean_ratio, color='orange', linestyle=':', alpha=0.7, label=f'평균: {mean_ratio:.2f}%')
                
                # 25%, 75% 사분위수 선 표시 (선택적)
                q25 = df['Price_Diff_Ratio'].quantile(0.25)
                q75 = df['Price_Diff_Ratio'].quantile(0.75)
                plt.axhline(y=q25, color='gray', linestyle='-.', alpha=0.5, label=f'25% 분위: {q25:.2f}%')
                plt.axhline(y=q75, color='gray', linestyle='-.', alpha=0.5, label=f'75% 분위: {q75:.2f}%')
                
                plt.legend()
                plt.tight_layout()
                plt.savefig('price_diff_ratio_timeseries.png', dpi=300, bbox_inches='tight')
                plt.close()
                print("가격 차이 비율 그래프가 'price_diff_ratio_timeseries.png'로 저장되었습니다.")
            
            # 통합 그래프: 모든 데이터를 한 번에 보기 (정규화)
            if len(available_columns) >= 2:
                print("\n4. 정규화된 통합 그래프:")
                plt.figure(figsize=(15, 8))
                
                # 각 데이터를 0-1 범위로 정규화
                for col in available_columns:
                    if col in df.columns:
                        data = df[col]
                        normalized_data = (data - data.min()) / (data.max() - data.min())
                        
                        # 컬럼명을 한글로 변환
                        col_name_map = {
                            'Stock1_Close': '삼성전자 종가',
                            'Stock2_Close': '삼성전자(우) 종가',
                            'Price_Difference': '가격 차이',
                            'Price_Diff_Ratio': '가격 차이 비율'
                        }
                        display_name = col_name_map.get(col, col)
                        plt.plot(df.index, normalized_data, label=display_name, linewidth=1.5, alpha=0.8)
                
                plt.title('정규화된 시계열 데이터 비교 (0-1 범위)')
                plt.xlabel('날짜')
                plt.ylabel('정규화된 값 (0-1)')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig('normalized_comparison.png', dpi=300, bbox_inches='tight')
                plt.close()
                print("정규화된 통합 그래프가 'normalized_comparison.png'로 저장되었습니다.")
        else:
            print(f"필요한 컬럼들을 찾을 수 없습니다. 사용 가능한 컬럼: {list(df.columns)}")

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
