#!/usr/bin/env python3
"""
모든 우선주 보유 회사들에 대한 종합 분석 스크립트

이 스크립트는 stock_diff.py에서 생성된 데이터를 기반으로
모든 회사들의 Price_Diff_Ratio를 분석하고 비교합니다.
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import platform
import matplotlib.font_manager as fm
import numpy as np
from datetime import datetime
import os

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
        plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

def load_company_data(company_name, period='20년'):
    """
    특정 회사의 분석 데이터를 로드합니다.
    
    Args:
        company_name (str): 회사명
        period (str): 분석 기간 (기본값: '20년')
        
    Returns:
        pd.DataFrame: 로드된 데이터프레임, 실패 시 None
    """
    try:
        safe_company_name = company_name.replace('/', '_').replace('\\', '_')
        json_file = f'./{safe_company_name}_stock_analysis_{period}.json'
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index = pd.to_datetime(df.index, format='%y-%m-%d')
        df = df.sort_index()
        
        return df
        
    except FileNotFoundError:
        print(f"⚠️  {company_name} 데이터 파일을 찾을 수 없습니다: {json_file}")
        return None
    except Exception as e:
        print(f"❌ {company_name} 데이터 로드 실패: {e}")
        return None

def generate_company_comparison_report():
    """
    모든 회사들의 Price_Diff_Ratio 비교 리포트를 생성합니다.
    """
    from stock_diff import PREFERRED_STOCK_COMPANIES
    
    print("📊 회사별 Price_Diff_Ratio 비교 분석 시작")
    print("=" * 80)
    
    # 모든 회사 데이터 수집
    company_data = {}
    company_stats = {}
    
    for company_name in PREFERRED_STOCK_COMPANIES.keys():
        df = load_company_data(company_name)
        if df is not None and 'Price_Diff_Ratio' in df.columns:
            company_data[company_name] = df['Price_Diff_Ratio']
            
            # 기본 통계 계산
            stats = {
                'mean': df['Price_Diff_Ratio'].mean(),
                'median': df['Price_Diff_Ratio'].median(),
                'std': df['Price_Diff_Ratio'].std(),
                'min': df['Price_Diff_Ratio'].min(),
                'max': df['Price_Diff_Ratio'].max(),
                'q25': df['Price_Diff_Ratio'].quantile(0.25),
                'q75': df['Price_Diff_Ratio'].quantile(0.75),
                'current': df['Price_Diff_Ratio'].iloc[-1] if len(df) > 0 else None,
                'data_points': len(df),
                'sector': PREFERRED_STOCK_COMPANIES[company_name]['sector']
            }
            company_stats[company_name] = stats
            print(f"✅ {company_name}: {len(df)}일 데이터 로드 완료")
        else:
            print(f"❌ {company_name}: 데이터 로드 실패")
    
    if not company_data:
        print("❌ 분석할 수 있는 회사 데이터가 없습니다.")
        return
    
    # 1. 통계 요약 테이블 생성
    print(f"\n📋 회사별 Price_Diff_Ratio 통계 요약 ({len(company_data)}개 회사)")
    stats_df = pd.DataFrame(company_stats).T
    stats_df = stats_df.round(2)
    
    # 업종별로 정렬
    stats_df = stats_df.sort_values(['sector', 'mean'])
    
    print("\n" + "="*120)
    print(f"{'회사명':^12} {'업종':^12} {'평균':^8} {'중앙값':^8} {'표준편차':^8} {'최솟값':^8} {'최댓값':^8} {'현재값':^8} {'데이터수':^8}")
    print("="*120)
    
    for company, stats in stats_df.iterrows():
        print(f"{company:^12} {stats['sector']:^12} {stats['mean']:^8.2f} {stats['median']:^8.2f} {stats['std']:^8.2f} {stats['min']:^8.2f} {stats['max']:^8.2f} {stats['current']:^8.2f} {int(stats['data_points']):^8}")
    
    # 2. 박스플롯 비교
    plt.figure(figsize=(20, 10))
    
    # 업종별로 색상 구분
    sectors = list(set([stats['sector'] for stats in company_stats.values()]))
    colors = plt.cm.Set3(np.linspace(0, 1, len(sectors)))
    sector_colors = dict(zip(sectors, colors))
    
    box_data = []
    box_labels = []
    box_colors = []
    
    for company in stats_df.index:
        if company in company_data:
            box_data.append(company_data[company].values)
            box_labels.append(company)
            box_colors.append(sector_colors[stats_df.loc[company, 'sector']])
    
    bp = plt.boxplot(box_data, labels=box_labels, patch_artist=True)
    
    for patch, color in zip(bp['boxes'], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    plt.title('회사별 Price_Diff_Ratio 분포 비교', fontsize=16, fontweight='bold')
    plt.ylabel('Price_Diff_Ratio (%)', fontsize=12)
    plt.xlabel('회사명', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    
    # 범례 추가 (업종별)
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, alpha=0.7, label=sector) 
                      for sector, color in sector_colors.items()]
    plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
    
    plt.tight_layout()
    plt.savefig('company_comparison_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n📊 회사별 박스플롯 비교 저장: company_comparison_boxplot.png")
    
    # 3. 히트맵 (상관관계 분석)
    if len(company_data) >= 2:
        plt.figure(figsize=(12, 10))
        
        # 데이터 정렬 및 결합
        common_dates = None
        for company, data in company_data.items():
            if common_dates is None:
                common_dates = set(data.index)
            else:
                common_dates = common_dates.intersection(set(data.index))
        
        if common_dates:
            common_dates = sorted(list(common_dates))
            correlation_data = {}
            
            for company, data in company_data.items():
                correlation_data[company] = data.reindex(common_dates).fillna(method='ffill')
            
            corr_df = pd.DataFrame(correlation_data)
            correlation_matrix = corr_df.corr()
            
            # 히트맵 생성
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
            sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                       square=True, fmt='.2f', cbar_kws={"shrink": .8})
            plt.title('회사별 Price_Diff_Ratio 상관관계', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig('company_correlation_heatmap.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(f"📊 상관관계 히트맵 저장: company_correlation_heatmap.png")
    
    # 4. 시계열 비교 (대표 회사들)
    top_companies = stats_df.head(5).index.tolist()  # 평균이 낮은 상위 5개 회사
    
    plt.figure(figsize=(15, 10))
    for i, company in enumerate(top_companies):
        if company in company_data:
            data = company_data[company].rolling(window=30).mean()  # 30일 이동평균으로 스무딩
            plt.plot(data.index, data.values, label=company, linewidth=2, alpha=0.8)
    
    plt.title('주요 회사별 Price_Diff_Ratio 시계열 비교 (30일 이동평균)', fontsize=16, fontweight='bold')
    plt.ylabel('Price_Diff_Ratio (%)', fontsize=12)
    plt.xlabel('날짜', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('company_timeseries_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"📊 시계열 비교 그래프 저장: company_timeseries_comparison.png")
    
    # 5. 업종별 분석
    sector_stats = {}
    for company, stats in company_stats.items():
        sector = stats['sector']
        if sector not in sector_stats:
            sector_stats[sector] = {'companies': [], 'means': [], 'stds': []}
        sector_stats[sector]['companies'].append(company)
        sector_stats[sector]['means'].append(stats['mean'])
        sector_stats[sector]['stds'].append(stats['std'])
    
    print(f"\n🏭 업종별 Price_Diff_Ratio 분석")
    print("="*60)
    
    sector_summary = []
    for sector, data in sector_stats.items():
        avg_mean = np.mean(data['means'])
        avg_std = np.mean(data['stds'])
        company_count = len(data['companies'])
        
        sector_summary.append({
            'sector': sector,
            'avg_mean': avg_mean,
            'avg_std': avg_std,
            'company_count': company_count,
            'companies': ', '.join(data['companies'])
        })
        
        print(f"{sector:^15} | 평균: {avg_mean:^8.2f} | 변동성: {avg_std:^8.2f} | 회사수: {company_count:^3}")
    
    # 6. 리포트 파일 생성
    report_file = f'company_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 📊 우선주 가격차이 비율 종합 분석 리포트\n\n")
        f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 📈 분석 요약\n\n")
        f.write(f"- 분석 대상: {len(company_data)}개 회사\n")
        f.write(f"- 분석 기간: 20년\n")
        f.write(f"- 총 업종: {len(sectors)}개\n\n")
        
        f.write("## 📋 회사별 통계\n\n")
        f.write("| 회사명 | 업종 | 평균 | 중앙값 | 표준편차 | 최솟값 | 최댓값 | 현재값 |\n")
        f.write("|--------|------|------|--------|----------|--------|--------|--------|\n")
        
        for company, stats in stats_df.iterrows():
            f.write(f"| {company} | {stats['sector']} | {stats['mean']:.2f}% | {stats['median']:.2f}% | {stats['std']:.2f}% | {stats['min']:.2f}% | {stats['max']:.2f}% | {stats['current']:.2f}% |\n")
        
        f.write("\n## 🏭 업종별 분석\n\n")
        f.write("| 업종 | 평균 비율 | 평균 변동성 | 회사 수 | 포함 회사 |\n")
        f.write("|------|-----------|-------------|---------|----------|\n")
        
        for summary in sector_summary:
            f.write(f"| {summary['sector']} | {summary['avg_mean']:.2f}% | {summary['avg_std']:.2f}% | {summary['company_count']} | {summary['companies']} |\n")
        
        f.write("\n## 📊 생성된 차트\n\n")
        f.write("1. `company_comparison_boxplot.png`: 회사별 분포 비교\n")
        f.write("2. `company_correlation_heatmap.png`: 회사간 상관관계\n")
        f.write("3. `company_timeseries_comparison.png`: 시계열 비교\n\n")
        
        f.write("## 💡 주요 발견\n\n")
        
        # 가장 낮은/높은 평균을 가진 회사들
        lowest_company = stats_df.loc[stats_df['mean'].idxmin()]
        highest_company = stats_df.loc[stats_df['mean'].idxmax()]
        
        f.write(f"- **가장 낮은 평균 비율**: {lowest_company.name} ({lowest_company['mean']:.2f}%) - 보통주가 상대적으로 저평가\n")
        f.write(f"- **가장 높은 평균 비율**: {highest_company.name} ({highest_company['mean']:.2f}%) - 우선주가 상대적으로 저평가\n")
        
        # 가장 변동성이 큰/작은 회사들
        most_volatile = stats_df.loc[stats_df['std'].idxmax()]
        least_volatile = stats_df.loc[stats_df['std'].idxmin()]
        
        f.write(f"- **가장 높은 변동성**: {most_volatile.name} ({most_volatile['std']:.2f}%)\n")
        f.write(f"- **가장 낮은 변동성**: {least_volatile.name} ({least_volatile['std']:.2f}%)\n\n")
        
        f.write("---\n")
        f.write("*이 리포트는 자동으로 생성되었습니다.*\n")
    
    print(f"\n📄 종합 분석 리포트 생성: {report_file}")
    print(f"\n✅ 모든 회사 비교 분석 완료!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='우선주 가격차이 비율 종합 분석',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python analyze_all_companies.py                    # 모든 회사 분석 (기본값)
  python analyze_all_companies.py --company 삼성전자   # 특정 회사만 분석
  python analyze_all_companies.py --company LG화학    # 특정 회사만 분석
        """)
    
    parser.add_argument(
        '--company', '-c',
        type=str,
        help='분석할 특정 회사명 (예: 삼성전자, LG화학). 지정하지 않으면 모든 회사 분석'
    )
    
    args = parser.parse_args()
    
    if args.company:
        # 특정 회사만 분석
        from stock_diff import PREFERRED_STOCK_COMPANIES
        
        if args.company in PREFERRED_STOCK_COMPANIES:
            print(f"🎯 {args.company} 개별 분석 시작")
            print("=" * 60)
            
            df = load_company_data(args.company)
            if df is not None and 'Price_Diff_Ratio' in df.columns:
                # 개별 회사 통계 출력
                ratio_data = df['Price_Diff_Ratio']
                company_info = PREFERRED_STOCK_COMPANIES[args.company]
                
                print(f"\n📊 {args.company} Price_Diff_Ratio 통계")
                print("-" * 50)
                print(f"업종: {company_info['sector']}")
                print(f"데이터 기간: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
                print(f"데이터 수: {len(df)}일")
                print(f"평균: {ratio_data.mean():.2f}%")
                print(f"중앙값: {ratio_data.median():.2f}%")
                print(f"표준편차: {ratio_data.std():.2f}%")
                print(f"최솟값: {ratio_data.min():.2f}%")
                print(f"최댓값: {ratio_data.max():.2f}%")
                print(f"현재값: {ratio_data.iloc[-1]:.2f}%")
                print(f"25% 분위수: {ratio_data.quantile(0.25):.2f}%")
                print(f"75% 분위수: {ratio_data.quantile(0.75):.2f}%")
                
                print(f"\n✅ {args.company} 분석 완료")
            else:
                print(f"❌ {args.company} 데이터를 찾을 수 없습니다.")
        else:
            print(f"❌ '{args.company}'는 지원되지 않는 회사입니다.")
            print("\n📋 지원하는 회사 목록:")
            from stock_diff import print_available_companies
            print_available_companies()
    else:
        # 기본값: 모든 회사 분석
        generate_company_comparison_report()
