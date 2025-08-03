import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import platform
import matplotlib.font_manager as fm
import os

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

def analyze_price_diff_ratio(json_file_path, company_name="삼성전자"):
    """
    JSON 파일에서 Price_Diff_Ratio의 분포를 분석하고 해석 가이드를 제공합니다.

    Args:
        json_file_path (str): 분석할 JSON 파일의 경로.
        company_name (str): 분석할 회사명 (기본값: "삼성전자")
    """
    try:
        # 파일명에서 기간 정보 추출
        import os
        filename = os.path.basename(json_file_path)
        period = "기본"  # 기본값
        
        # 파일명 패턴: {회사명}_stock_analysis_{기간}.json
        if '_stock_analysis_' in filename:
            try:
                period = filename.split('_stock_analysis_')[1].replace('.json', '')
            except:
                period = "기본"
        
        print(f"\n=== {company_name} ({period}) Price_Diff_Ratio 분석 ===")
        
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
        plt.title(f'Price_Diff_Ratio 히스토그램 ({company_name})')
        plt.xlabel('Price_Diff_Ratio (%)')
        plt.ylabel('빈도')

        plt.subplot(1, 2, 2)
        sns.boxplot(y=price_diff_ratio)
        plt.title(f'Price_Diff_Ratio 박스 플롯 ({company_name})')
        plt.ylabel('Price_Diff_Ratio (%)')

        plt.tight_layout()
        # 회사명을 포함한 파일명으로 저장 (회사명이 먼저 오도록)
        safe_company_name = company_name.replace('/', '_').replace('\\', '_')
        distribution_filename = f'{safe_company_name}_price_diff_ratio_distribution_{period}.png'
        plt.savefig(distribution_filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"히스토그램과 박스플롯이 '{distribution_filename}'로 저장되었습니다.")

        # 추가 그래프: 시간에 따른 가격 및 비율 변화
        print("\n3. 시간에 따른 가격 및 비율 변화:")
        
        # 필요한 컬럼들이 있는지 확인 (실제 컬럼명에 맞게 수정)
        required_columns = ['Stock1_Close', 'Stock2_Close', 'Price_Difference', 'Price_Diff_Ratio']
        available_columns = [col for col in required_columns if col in df.columns]
        
        if len(available_columns) >= 2:
            # 첫 번째 그래프: 보통주 종가, 우선주 종가, 가격 차이
            print("첫 번째 그래프: 종가 및 가격 차이")
            fig, axes = plt.subplots(3, 1, figsize=(15, 12))
            fig.suptitle(f'{company_name} 보통주와 우선주 종가 및 가격 차이', fontsize=16)
            
            # 첫 번째 서브플롯: 보통주 종가
            if 'Stock1_Close' in df.columns:
                axes[0].plot(df.index, df['Stock1_Close'], label=f'{company_name} 보통주', color='blue', linewidth=1.5)
                axes[0].set_title(f'{company_name} 보통주 종가')
                axes[0].set_ylabel('가격 (원)')
                axes[0].grid(True, alpha=0.3)
                axes[0].tick_params(axis='x', rotation=45)
            
            # 두 번째 서브플롯: 우선주 종가
            if 'Stock2_Close' in df.columns:
                axes[1].plot(df.index, df['Stock2_Close'], label=f'{company_name} 우선주', color='red', linewidth=1.5)
                axes[1].set_title(f'{company_name} 우선주 종가')
                axes[1].set_ylabel('가격 (원)')
                axes[1].grid(True, alpha=0.3)
                axes[1].tick_params(axis='x', rotation=45)
            
            # 세 번째 서브플롯: 가격 차이
            if 'Price_Difference' in df.columns:
                axes[2].plot(df.index, df['Price_Difference'], label='가격 차이', color='green', linewidth=1.5)
                axes[2].set_title(f'가격 차이 ({company_name} 보통주 - 우선주)')
                axes[2].set_ylabel('가격 차이 (원)')
                axes[2].set_xlabel('날짜')
                axes[2].grid(True, alpha=0.3)
                axes[2].tick_params(axis='x', rotation=45)
                # 0선 표시
                axes[2].axhline(y=0, color='black', linestyle='--', alpha=0.5)
            
            plt.tight_layout()
            stock_prices_filename = f'{safe_company_name}_stock_prices_and_difference_{period}.png'
            plt.savefig(stock_prices_filename, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"종가 및 가격 차이 그래프가 '{stock_prices_filename}'로 저장되었습니다.")
            
            # 두 번째 그래프: 가격 차이 비율 (별도 그래프) - 모든 윈도우 사이즈별로 생성
            if 'Price_Diff_Ratio' in df.columns:
                print("두 번째 그래프: 가격 차이 비율 및 슬라이딩 윈도우 사분위수 (모든 윈도우 사이즈)")
                
                # 사용 가능한 윈도우 사이즈 확인
                available_windows = []
                for window in ['2year', '3year', '5year']:
                    q25_col = f'Price_Diff_Ratio_25th_Percentile_{window}'
                    q75_col = f'Price_Diff_Ratio_75th_Percentile_{window}'
                    if q25_col in df.columns and q75_col in df.columns:
                        available_windows.append(window)
                
                # 기본 윈도우가 있는 경우도 확인
                has_default_window = ('Price_Diff_Ratio_25th_Percentile' in df.columns and 
                                    'Price_Diff_Ratio_75th_Percentile' in df.columns)
                
                if has_default_window and not available_windows:
                    available_windows = ['2year']  # 기본 윈도우를 2year로 처리
                
                # 각 윈도우 사이즈별로 별도 그래프 생성
                for window_info in available_windows:
                    plt.figure(figsize=(15, 8))
                    plt.plot(df.index, df['Price_Diff_Ratio'], label='가격 차이 비율', color='purple', linewidth=1.5)
                    
                    plt.title(f'가격 차이 비율 (%) - {window_info} 슬라이딩 윈도우 사분위수 포함 ({company_name} {period})', fontsize=16)
                    plt.ylabel('비율 (%)')
                    plt.xlabel('날짜')
                    plt.grid(True, alpha=0.3)
                    plt.xticks(rotation=45)
                    
                    # 0선 표시
                    plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
                    
                    # 전체 기간 평균선 표시
                    mean_ratio = df['Price_Diff_Ratio'].mean()
                    plt.axhline(y=mean_ratio, color='orange', linestyle=':', alpha=0.7, label=f'전체기간 평균: {mean_ratio:.2f}%')
                    
                    # 전체 기간 25%, 75% 사분위수 선 표시
                    q25_overall = df['Price_Diff_Ratio'].quantile(0.25)
                    q75_overall = df['Price_Diff_Ratio'].quantile(0.75)
                    plt.axhline(y=q25_overall, color='gray', linestyle='-.', alpha=0.5, label=f'전체기간 25% 분위: {q25_overall:.2f}%')
                    plt.axhline(y=q75_overall, color='gray', linestyle='-.', alpha=0.5, label=f'전체기간 75% 분위: {q75_overall:.2f}%')
                    
                    # 해당 윈도우의 슬라이딩 윈도우 사분위수 선 표시
                    if window_info == '2year' and has_default_window and 'Price_Diff_Ratio_25th_Percentile_2year' not in df.columns:
                        # 기본 윈도우 사용 (컬럼명에 _2year 없는 경우)
                        plt.plot(df.index, df['Price_Diff_Ratio_25th_Percentile'], 
                                color='blue', linestyle='--', alpha=0.8, linewidth=1, 
                                label=f'{window_info} 슬라이딩 25% 분위')
                        plt.plot(df.index, df['Price_Diff_Ratio_75th_Percentile'], 
                                color='red', linestyle='--', alpha=0.8, linewidth=1, 
                                label=f'{window_info} 슬라이딩 75% 분위')
                    else:
                        # 명시적 윈도우 컬럼 사용
                        q25_col = f'Price_Diff_Ratio_25th_Percentile_{window_info}'
                        q75_col = f'Price_Diff_Ratio_75th_Percentile_{window_info}'
                        if q25_col in df.columns and q75_col in df.columns:
                            plt.plot(df.index, df[q25_col], 
                                    color='blue', linestyle='--', alpha=0.8, linewidth=1, 
                                    label=f'{window_info} 슬라이딩 25% 분위')
                            plt.plot(df.index, df[q75_col], 
                                    color='red', linestyle='--', alpha=0.8, linewidth=1, 
                                    label=f'{window_info} 슬라이딩 75% 분위')
                    
                    plt.legend()
                    plt.tight_layout()
                    timeseries_filename = f'{safe_company_name}_price_diff_ratio_timeseries_{period}_{window_info}.png'
                    plt.savefig(timeseries_filename, dpi=300, bbox_inches='tight')
                    plt.close()
                    print(f"  - {window_info} 윈도우 시계열 그래프: '{timeseries_filename}' 저장 완료")
                
                print(f"📈 총 {len(available_windows)}개 윈도우 사이즈 시계열 그래프 생성 완료")
            
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
                            'Stock1_Close': f'{company_name} 보통주 종가',
                            'Stock2_Close': f'{company_name} 우선주 종가',
                            'Price_Difference': '가격 차이',
                            'Price_Diff_Ratio': '가격 차이 비율'
                        }
                        display_name = col_name_map.get(col, col)
                        plt.plot(df.index, normalized_data, label=display_name, linewidth=1.5, alpha=0.8)
                
                plt.title(f'정규화된 시계열 데이터 비교 (0-1 범위) - {company_name}')
                plt.xlabel('날짜')
                plt.ylabel('정규화된 값 (0-1)')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                normalized_filename = f'{safe_company_name}_normalized_comparison_{period}.png'
                plt.savefig(normalized_filename, dpi=300, bbox_inches='tight')
                plt.close()
                print(f"정규화된 통합 그래프가 '{normalized_filename}'로 저장되었습니다.")
        else:
            print(f"필요한 컬럼들을 찾을 수 없습니다. 사용 가능한 컬럼: {list(df.columns)}")

        print("\n--- Price_Diff_Ratio 해석 가이드 ---")
        print(f"Price_Diff_Ratio = ({company_name} 보통주 종가 - {company_name} 우선주 종가) * 100 / {company_name} 우선주 종가")
        print(f"이 비율은 {company_name} 우선주 가격 대비 보통주와 우선주 간의 가격 차이를 백분율로 나타냅니다.")
        print("\n투자 관점:")
        print(f"  - 비율이 작을수록 (음수이거나 0에 가까울수록): {company_name} 우선주 대비 보통주의 가격이 상대적으로 낮다는 의미입니다.")
        print(f"    따라서, {company_name} 보통주를 매수하는 것이 유리할 수 있습니다 (상대적으로 저평가).")
        print(f"  - 비율이 클수록 (양수이고 값이 높을수록): {company_name} 우선주 대비 보통주의 가격이 상대적으로 높다는 의미입니다.")
        print(f"    따라서, {company_name} 우선주를 매수하는 것이 유리할 수 있습니다 (상대적으로 저평가).")
        print("\n'크다' 또는 '작다'의 기준:")
        print("  - **평균 (Mean) 및 중앙값 (Median):** 이 값들은 비율의 '중심'을 나타냅니다. 이보다 낮은 비율은 상대적으로 '작다'고 볼 수 있고, 높은 비율은 '크다'고 볼 수 있습니다.")
        print("  - **표준편차 (Standard Deviation):** 데이터가 평균으로부터 얼마나 퍼져 있는지를 나타냅니다. 표준편차 범위(예: 평균 ± 1 표준편차)를 벗어나는 값들은 상대적으로 극단적인 값으로 해석할 수 있습니다.")
        print("  - **사분위수 (Quartiles - 25%, 50%, 75%):** 박스 플롯에서 시각적으로 확인할 수 있으며, 데이터의 25%, 50%(중앙값), 75% 지점을 나타냅니다.")
        print("    - 25% 값보다 작으면 하위 25%에 해당하므로 '매우 작은' 비율로 볼 수 있습니다.")
        print("    - 75% 값보다 크면 상위 25%에 해당하므로 '매우 큰' 비율로 볼 수 있습니다.")
        print("  - **역사적 범위 (Min/Max):** 최소값과 최대값은 비율이 가질 수 있는 극단적인 범위를 보여줍니다. 현재 비율이 역사적 최소값에 가까우면 보통주가 유리하고, 최대값에 가까우면 우선주가 유리하다고 판단할 수 있습니다.")
        print("\n결론적으로, '크다' 또는 '작다'의 기준은 절대적인 것이 아니라, 해당 비율의 **역사적 분포**와 **평균, 중앙값, 사분위수**를 기준으로 상대적으로 판단해야 합니다. 히스토그램과 박스 플롯을 통해 시각적으로 분포를 확인하면 더욱 직관적인 이해를 얻을 수 있습니다.")

    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다. 경로를 확인해주세요: {json_file_path}")
    except json.JSONDecodeError:
        print(f"오류: JSON 파일을 디코딩할 수 없습니다. 파일 형식을 확인해주세요: {json_file_path}")
    except Exception as e:
        print(f"데이터 처리 중 오류가 발생했습니다: {e}")

def generate_timeseries_plots_for_all_periods(company_name="삼성전자"):
    """
    특정 회사의 모든 기간과 윈도우 사이즈에 대해 price_diff_ratio 시계열 그래프를 생성합니다.
    
    Args:
        company_name (str): 분석할 회사명 (기본값: "삼성전자")
    """
    periods = ['3년', '5년', '10년', '20년', '30년']
    window_sizes = ['2year', '3year', '5year']
    
    print(f"=== {company_name} 기간별 및 윈도우 사이즈별 시계열 그래프 생성 ===\n")
    
    safe_company_name = company_name.replace('/', '_').replace('\\', '_')
    
    for period in periods:
        json_file = f'./{safe_company_name}_stock_analysis_{period}.json'
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 딕셔너리를 DataFrame으로 변환
            df = pd.DataFrame.from_dict(data, orient='index')
            df.index = pd.to_datetime(df.index, format='%y-%m-%d')
            df = df.sort_index()
            
            if 'Price_Diff_Ratio' not in df.columns:
                print(f"경고: '{json_file}' 파일에 'Price_Diff_Ratio' 컬럼이 없습니다.")
                continue
            
            # 각 윈도우 사이즈별로 그래프 생성
            for window_size in window_sizes:
                plt.figure(figsize=(15, 8))
                
                # 기본 시계열 그래프
                plt.plot(df.index, df['Price_Diff_Ratio'], 
                        label='가격 차이 비율', color='purple', linewidth=1.5, alpha=0.8)
                
                # 0선 표시
                plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
                
                # 전체 기간 평균선 표시
                mean_ratio = df['Price_Diff_Ratio'].mean()
                plt.axhline(y=mean_ratio, color='orange', linestyle=':', alpha=0.7, 
                           label=f'전체기간 평균: {mean_ratio:.2f}%')
                
                # 전체 기간 25%, 75% 사분위수 선 표시
                q25_overall = df['Price_Diff_Ratio'].quantile(0.25)
                q75_overall = df['Price_Diff_Ratio'].quantile(0.75)
                plt.axhline(y=q25_overall, color='gray', linestyle='-.', alpha=0.5, 
                           label=f'전체기간 25% 분위: {q25_overall:.2f}%')
                plt.axhline(y=q75_overall, color='gray', linestyle='-.', alpha=0.5, 
                           label=f'전체기간 75% 분위: {q75_overall:.2f}%')
                
                # 윈도우 사이즈별 슬라이딩 윈도우 사분위수 선 표시
                q25_col = f'Price_Diff_Ratio_25th_Percentile_{window_size}'
                q75_col = f'Price_Diff_Ratio_75th_Percentile_{window_size}'
                
                if q25_col in df.columns and q75_col in df.columns:
                    plt.plot(df.index, df[q25_col], 
                            color='blue', linestyle='--', alpha=0.8, linewidth=1.5, 
                            label=f'{window_size} 슬라이딩 25% 분위')
                    plt.plot(df.index, df[q75_col], 
                            color='red', linestyle='--', alpha=0.8, linewidth=1.5, 
                            label=f'{window_size} 슬라이딩 75% 분위')
                else:
                    # 기본 2year 윈도우가 있는 경우
                    if 'Price_Diff_Ratio_25th_Percentile' in df.columns and 'Price_Diff_Ratio_75th_Percentile' in df.columns:
                        plt.plot(df.index, df['Price_Diff_Ratio_25th_Percentile'], 
                                color='blue', linestyle='--', alpha=0.8, linewidth=1.5, 
                                label='슬라이딩 25% 분위')
                        plt.plot(df.index, df['Price_Diff_Ratio_75th_Percentile'], 
                                color='red', linestyle='--', alpha=0.8, linewidth=1.5, 
                                label='슬라이딩 75% 분위')
                
                plt.title(f'가격 차이 비율 ({company_name} {period}, {window_size} 윈도우)', fontsize=16)
                plt.ylabel('비율 (%)')
                plt.xlabel('날짜')
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.legend()
                plt.tight_layout()
                
                # 파일명 생성 (회사명이 먼저 오도록)
                filename = f'{safe_company_name}_price_diff_ratio_timeseries_{period}_{window_size}.png'
                plt.savefig(filename, dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"✓ {filename} 저장 완료")
                
        except FileNotFoundError:
            print(f"⚠️  파일을 찾을 수 없습니다: {json_file}")
        except Exception as e:
            print(f"❌ {period} 데이터 처리 중 오류: {e}")
    
    print(f"\n=== {company_name} 모든 시계열 그래프 생성 완료 ===")

def analyze_all_companies():
    """
    모든 회사에 대해 다양한 기간 (3년, 5년, 10년, 20년, 30년)과 
    윈도우 사이즈 (2년, 3년, 5년)로 분석을 수행합니다.
    """
    from stock_diff import PREFERRED_STOCK_COMPANIES
    
    periods = ['3년', '5년', '10년', '20년', '30년']
    
    print("📊 모든 회사 종합 분석 시작")
    print("=" * 80)
    print(f"📈 분석 기간: {', '.join(periods)}")
    print(f"📊 윈도우 사이즈: 2년, 3년, 5년")
    print("=" * 80)
    
    total_companies = len(PREFERRED_STOCK_COMPANIES)
    current_company = 0
    
    for company_name in PREFERRED_STOCK_COMPANIES.keys():
        current_company += 1
        print(f"\n🏢 [{current_company}/{total_companies}] {company_name} 종합 분석 시작...")
        
        try:
            safe_company_name = company_name.replace('/', '_').replace('\\', '_')
            
            # 각 기간별로 분석 수행
            for period in periods:
                print(f"\n  📅 {period} 데이터 분석 중...")
                json_file = f'./{safe_company_name}_stock_analysis_{period}.json'
                
                try:
                    # 기본 분석 (분포, 시각화)
                    analyze_price_diff_ratio(json_file, company_name)
                    print(f"    ✅ {company_name} {period} 기본 분석 완료")
                except FileNotFoundError:
                    print(f"    ⚠️  {company_name} {period} 데이터 파일을 찾을 수 없습니다: {json_file}")
                except Exception as e:
                    print(f"    ❌ {company_name} {period} 분석 중 오류: {e}")
            
            # 모든 기간과 윈도우 사이즈에 대한 시계열 그래프 생성
            print(f"\n  📈 {company_name} 전체 시계열 그래프 생성 중...")
            try:
                generate_timeseries_plots_for_all_periods(company_name)
                print(f"    ✅ {company_name} 시계열 그래프 생성 완료")
            except Exception as e:
                print(f"    ❌ {company_name} 시계열 그래프 생성 중 오류: {e}")
            
            print(f"✅ {company_name} 전체 분석 완료!")
            
        except Exception as e:
            print(f"❌ {company_name} 처리 중 전체 오류: {e}")
    
    print(f"\n{'='*80}")
    print("=== 모든 회사 종합 분석 완료 ===")
    print(f"✅ 처리된 회사: {total_companies}개")
    print(f"📊 분석된 기간: {len(periods)}개 ({', '.join(periods)})")
    print(f"📈 생성된 윈도우 유형: 2년, 3년, 5년 슬라이딩 윈도우")
    print(f"📁 생성된 파일 유형:")
    print(f"   - 회사명_price_diff_ratio_distribution_기간.png (분포 차트)")
    print(f"   - 회사명_stock_prices_and_difference_기간.png (주가 차트)")
    print(f"   - 회사명_price_diff_ratio_timeseries_기간_윈도우.png (기본 시계열 차트)")
    print(f"   - 회사명_normalized_comparison_기간.png (정규화 비교)")
    print(f"   - 회사명_price_diff_ratio_timeseries_기간_윈도우.png (상세 시계열)")
    print(f"{'='*80}")

def analyze_all_companies_single_period(period='20년'):
    """
    모든 회사에 대해 특정 기간으로만 분석을 수행합니다. (기존 호환성을 위한 함수)
    
    Args:
        period (str): 분석할 기간 (기본값: '20년')
    """
    from stock_diff import PREFERRED_STOCK_COMPANIES
    
    print(f"📊 모든 회사 {period} 데이터 분석 시작")
    print("=" * 80)
    
    for company_name in PREFERRED_STOCK_COMPANIES.keys():
        try:
            print(f"\n🏢 {company_name} 분석 시작...")
            safe_company_name = company_name.replace('/', '_').replace('\\', '_')
            
            # 지정된 기간 데이터 기준으로 분석
            json_file = f'./{safe_company_name}_stock_analysis_{period}.json'
            
            try:
                analyze_price_diff_ratio(json_file, company_name)
                print(f"✅ {company_name} 분석 완료")
            except FileNotFoundError:
                print(f"⚠️  {company_name} 데이터 파일을 찾을 수 없습니다: {json_file}")
            except Exception as e:
                print(f"❌ {company_name} 분석 중 오류: {e}")
                
        except Exception as e:
            print(f"❌ {company_name} 처리 중 오류: {e}")
    
    print(f"\n{'='*80}")
    print(f"=== 모든 회사 {period} 분석 완료 ===")
    print(f"{'='*80}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='우선주 가격차이 비율 분석')
    parser.add_argument('--company', '-c', type=str, help='분석할 회사명 (지정하지 않으면 모든 회사 분석)')
    parser.add_argument('--timeseries', '-t', action='store_true', help='시계열 그래프 생성')
    parser.add_argument('--file', '-f', type=str, help='분석할 JSON 파일 경로')
    parser.add_argument('--period', '-p', type=str, 
                       choices=['3년', '5년', '10년', '20년', '30년'],
                       help='분석할 기간 (지정하지 않으면 모든 기간 분석)')
    
    args = parser.parse_args()
    
    # --period가 지정되지 않은 경우 모든 기간 분석
    if not args.period:
        if args.company:
            print(f"🎯 {args.company} 전체 기간 종합 분석...")
            try:
                safe_company_name = args.company.replace('/', '_').replace('\\', '_')
                periods = ['3년', '5년', '10년', '20년', '30년']
                
                # 각 기간별 기본 분석
                for period in periods:
                    json_file = f'./{safe_company_name}_stock_analysis_{period}.json'
                    try:
                        analyze_price_diff_ratio(json_file, args.company)
                        print(f"✅ {args.company} {period} 분석 완료")
                    except FileNotFoundError:
                        print(f"⚠️  {args.company} {period} 데이터 파일을 찾을 수 없습니다")
                    except Exception as e:
                        print(f"❌ {args.company} {period} 분석 중 오류: {e}")
                
                # 모든 기간 시계열 그래프 생성
                generate_timeseries_plots_for_all_periods(args.company)
                print(f"✅ {args.company} 전체 종합 분석 완료!")
                
            except Exception as e:
                print(f"❌ {args.company} 종합 분석 실패: {e}")
        else:
            # 모든 회사 종합 분석
            analyze_all_companies()
    elif args.company and args.timeseries:
        # 특정 회사의 시계열 그래프 생성
        if args.period:
            # 특정 기간만 시계열 그래프 생성
            safe_company_name = args.company.replace('/', '_').replace('\\', '_')
            json_file = f'./{safe_company_name}_stock_analysis_{args.period}.json'
            try:
                analyze_price_diff_ratio(json_file, args.company)
            except FileNotFoundError:
                print(f"⚠️  {args.company} {args.period} 데이터 파일을 찾을 수 없습니다")
            except Exception as e:
                print(f"❌ {args.company} {args.period} 분석 중 오류: {e}")
        else:
            # 모든 기간 시계열 그래프 생성
            generate_timeseries_plots_for_all_periods(args.company)
    elif args.company:
        # 특정 회사 분석
        safe_company_name = args.company.replace('/', '_').replace('\\', '_')
        if args.period:
            # 특정 기간 분석
            json_file = args.file or f'./{safe_company_name}_stock_analysis_{args.period}.json'
            analyze_price_diff_ratio(json_file, args.company)
        else:
            # 모든 기간 분석
            periods = ['3년', '5년', '10년', '20년', '30년']
            for period in periods:
                json_file = f'./{safe_company_name}_stock_analysis_{period}.json'
                try:
                    analyze_price_diff_ratio(json_file, args.company)
                    print(f"✅ {args.company} {period} 분석 완료")
                except FileNotFoundError:
                    print(f"⚠️  {args.company} {period} 데이터 파일을 찾을 수 없습니다")
                except Exception as e:
                    print(f"❌ {args.company} {period} 분석 중 오류: {e}")
            # 모든 기간 시계열 그래프 생성
            generate_timeseries_plots_for_all_periods(args.company)
    elif args.file:
        # 특정 파일 분석 (회사명 추출 시도)
        import os
        filename = os.path.basename(args.file)
        if '_stock_analysis_' in filename:
            company_name = filename.split('_stock_analysis_')[0]
            analyze_price_diff_ratio(args.file, company_name)
        else:
            analyze_price_diff_ratio(args.file)
    else:
        # 기본값: 모든 회사 종합 분석
        analyze_all_companies()
