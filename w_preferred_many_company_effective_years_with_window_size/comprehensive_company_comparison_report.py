# -*- coding: utf-8 -*-
"""
종합 회사 비교 리포트 생성기
4개 회사의 우선주 가격차이 분석 데이터를 종합 비교하여 마크다운 리포트를 생성합니다.
"""

import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import os

# 한글 폰트 설정
import platform
import matplotlib.font_manager as fm

system_name = platform.system()
if system_name == 'Linux':
    if fm.findfont('NanumGothic', fontext='ttf'):
        plt.rcParams['font.family'] = 'NanumGothic'
    else:
        plt.rcParams['font.family'] = 'sans-serif'
elif system_name == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
elif system_name == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'

plt.rcParams['axes.unicode_minus'] = False

# 현재 지원되는 4개 회사
COMPANIES = {
    '삼성전자': {
        'common': '005930.KS',
        'preferred': '005935.KS',
        'sector': '전자/반도체',
        'color': '#1f77b4'
    },
    'LG화학': {
        'common': '051910.KS',
        'preferred': '051915.KS',
        'sector': '화학',
        'color': '#ff7f0e'
    },
    'LG전자': {
        'common': '066570.KS',
        'preferred': '066575.KS',
        'sector': '전자',
        'color': '#2ca02c'
    },
    '현대자동차': {
        'common': '005380.KS',
        'preferred': '005385.KS',
        'sector': '자동차',
        'color': '#d62728'
    }
}

def load_company_data(company_name, period='20년'):
    """특정 회사의 데이터를 로드합니다."""
    try:
        file_path = f'./{company_name}_stock_analysis_{period}.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index = pd.to_datetime(df.index, format='%y-%m-%d')
        df = df.sort_index()
        
        return df
    except FileNotFoundError:
        print(f"⚠️ {company_name} 데이터 파일을 찾을 수 없습니다: {file_path}")
        return None
    except Exception as e:
        print(f"❌ {company_name} 데이터 로드 오류: {e}")
        return None

def calculate_statistics(df):
    """데이터프레임에서 주요 통계를 계산합니다."""
    if df is None or df.empty:
        return None
    
    stats = {
        'total_days': len(df),
        'price_diff_ratio': {
            'mean': df['Price_Diff_Ratio'].mean(),
            'std': df['Price_Diff_Ratio'].std(),
            'min': df['Price_Diff_Ratio'].min(),
            'max': df['Price_Diff_Ratio'].max(),
            'q25': df['Price_Diff_Ratio'].quantile(0.25),
            'q50': df['Price_Diff_Ratio'].median(),
            'q75': df['Price_Diff_Ratio'].quantile(0.75)
        },
        'price_difference': {
            'mean': df['Price_Difference'].mean(),
            'std': df['Price_Difference'].std(),
            'min': df['Price_Difference'].min(),
            'max': df['Price_Difference'].max()
        },
        'dividend_yield': {
            'mean': df['Dividend_Yield_on_Preferred'].mean(),
            'std': df['Dividend_Yield_on_Preferred'].std(),
            'max': df['Dividend_Yield_on_Preferred'].max()
        },
        'latest_data': {
            'date': df.index[-1].strftime('%Y-%m-%d'),
            'price_diff_ratio': df['Price_Diff_Ratio'].iloc[-1],
            'price_difference': df['Price_Difference'].iloc[-1],
            'common_price': df['Stock1_Close'].iloc[-1],
            'preferred_price': df['Stock2_Close'].iloc[-1]
        }
    }
    
    return stats

def create_comparison_charts():
    """회사 간 비교 차트를 생성합니다."""
    
    # 1. Price Diff Ratio 분포 비교
    plt.figure(figsize=(15, 10))
    
    # 서브플롯 1: 히스토그램 비교
    plt.subplot(2, 2, 1)
    for company_name, company_info in COMPANIES.items():
        df = load_company_data(company_name)
        if df is not None:
            plt.hist(df['Price_Diff_Ratio'], bins=50, alpha=0.6, 
                    label=company_name, color=company_info['color'])
    
    plt.title('Price Diff Ratio 분포 비교', fontsize=14, fontweight='bold')
    plt.xlabel('Price Diff Ratio (%)')
    plt.ylabel('빈도')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 서브플롯 2: 박스플롯 비교
    plt.subplot(2, 2, 2)
    box_data = []
    labels = []
    colors = []
    
    for company_name, company_info in COMPANIES.items():
        df = load_company_data(company_name)
        if df is not None:
            box_data.append(df['Price_Diff_Ratio'])
            labels.append(company_name)
            colors.append(company_info['color'])
    
    box_plot = plt.boxplot(box_data, labels=labels, patch_artist=True)
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    plt.title('Price Diff Ratio 박스플롯 비교', fontsize=14, fontweight='bold')
    plt.ylabel('Price Diff Ratio (%)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 서브플롯 3: 시계열 비교 (최근 1년)
    plt.subplot(2, 2, 3)
    cutoff_date = datetime.now() - pd.Timedelta(days=365)
    
    for company_name, company_info in COMPANIES.items():
        df = load_company_data(company_name)
        if df is not None:
            recent_df = df[df.index >= cutoff_date]
            plt.plot(recent_df.index, recent_df['Price_Diff_Ratio'], 
                    label=company_name, color=company_info['color'], linewidth=2)
    
    plt.title('Price Diff Ratio 시계열 비교 (최근 1년)', fontsize=14, fontweight='bold')
    plt.xlabel('날짜')
    plt.ylabel('Price Diff Ratio (%)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # 서브플롯 4: 평균값 비교 바차트
    plt.subplot(2, 2, 4)
    means = []
    stds = []
    company_names = []
    colors_list = []
    
    for company_name, company_info in COMPANIES.items():
        df = load_company_data(company_name)
        if df is not None:
            means.append(df['Price_Diff_Ratio'].mean())
            stds.append(df['Price_Diff_Ratio'].std())
            company_names.append(company_name)
            colors_list.append(company_info['color'])
    
    bars = plt.bar(company_names, means, yerr=stds, capsize=5, 
                   color=colors_list, alpha=0.7, edgecolor='black')
    
    plt.title('Price Diff Ratio 평균값 비교', fontsize=14, fontweight='bold')
    plt.ylabel('평균 Price Diff Ratio (%)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    
    # 값 표시
    for bar, mean, std in zip(bars, means, stds):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + std + 0.1,
                f'{mean:.2f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('./comprehensive_company_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. 상관관계 분석
    plt.figure(figsize=(12, 8))
    
    # 모든 회사의 Price_Diff_Ratio를 하나의 데이터프레임으로 결합
    correlation_data = {}
    
    for company_name in COMPANIES.keys():
        df = load_company_data(company_name)
        if df is not None:
            correlation_data[company_name] = df['Price_Diff_Ratio']
    
    if correlation_data:
        corr_df = pd.DataFrame(correlation_data)
        corr_df = corr_df.dropna()  # 결측값 제거
        
        # 상관관계 행렬 계산
        correlation_matrix = corr_df.corr()
        
        # 히트맵 생성
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm',
                   center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
        
        plt.title('회사간 Price Diff Ratio 상관관계', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('./company_correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()

def generate_markdown_report():
    """종합 비교 리포트를 마크다운으로 생성합니다."""
    
    # 차트 생성
    create_comparison_charts()
    
    # 모든 회사 데이터 로드 및 통계 계산
    all_stats = {}
    for company_name in COMPANIES.keys():
        df = load_company_data(company_name)
        stats = calculate_statistics(df)
        if stats:
            all_stats[company_name] = stats
    
    # 마크다운 리포트 생성
    report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    markdown_content = f"""# 📊 우선주 가격차이 종합 비교 리포트

**생성일시:** {report_date}  
**분석 대상:** {len(all_stats)}개 회사  
**분석 기간:** 20년 데이터 기준  

---

## 🎯 Executive Summary

이 리포트는 한국 주식시장에서 우선주를 보유한 4개 주요 기업의 보통주-우선주 가격차이 패턴을 종합 분석한 결과입니다.

### 📈 주요 발견사항

"""

    if all_stats:
        # 평균 Price Diff Ratio 순위
        sorted_companies = sorted(all_stats.items(), 
                                key=lambda x: x[1]['price_diff_ratio']['mean'], 
                                reverse=True)
        
        markdown_content += f"""
**1. 평균 가격차이율 순위:**
"""
        for i, (company, stats) in enumerate(sorted_companies, 1):
            sector = COMPANIES[company]['sector']
            mean_ratio = stats['price_diff_ratio']['mean']
            markdown_content += f"   {i}. **{company}** ({sector}): {mean_ratio:.2f}%\n"
        
        # 변동성 순위
        sorted_by_volatility = sorted(all_stats.items(), 
                                    key=lambda x: x[1]['price_diff_ratio']['std'], 
                                    reverse=True)
        
        markdown_content += f"""
**2. 변동성 순위 (표준편차 기준):**
"""
        for i, (company, stats) in enumerate(sorted_by_volatility, 1):
            std = stats['price_diff_ratio']['std']
            markdown_content += f"   {i}. **{company}**: {std:.2f}%\n"

    markdown_content += f"""

---

## 📊 회사별 상세 분석

"""

    # 각 회사별 상세 정보
    for company_name, company_info in COMPANIES.items():
        if company_name in all_stats:
            stats = all_stats[company_name]
            sector = company_info['sector']
            common_ticker = company_info['common']
            preferred_ticker = company_info['preferred']
            
            markdown_content += f"""
### 🏢 {company_name} ({sector})

**기본 정보:**
- 보통주: {common_ticker}
- 우선주: {preferred_ticker}
- 분석 기간: {stats['total_days']:,}일

**가격차이율 통계:**
- 평균: {stats['price_diff_ratio']['mean']:.2f}%
- 표준편차: {stats['price_diff_ratio']['std']:.2f}%
- 최솟값: {stats['price_diff_ratio']['min']:.2f}%
- 최댓값: {stats['price_diff_ratio']['max']:.2f}%
- 중앙값: {stats['price_diff_ratio']['q50']:.2f}%
- 25% 분위수: {stats['price_diff_ratio']['q25']:.2f}%
- 75% 분위수: {stats['price_diff_ratio']['q75']:.2f}%

**최근 현황 ({stats['latest_data']['date']}):**
- 가격차이율: {stats['latest_data']['price_diff_ratio']:.2f}%
- 가격차이: {stats['latest_data']['price_difference']:,.0f}원
- 보통주 가격: {stats['latest_data']['common_price']:,.0f}원
- 우선주 가격: {stats['latest_data']['preferred_price']:,.0f}원

**배당 수익률:**
- 평균: {stats['dividend_yield']['mean']:.3f}%
- 최대: {stats['dividend_yield']['max']:.3f}%

---
"""

    # 비교 분석 섹션
    markdown_content += f"""
## 🔍 종합 비교 분석

### 📈 시각화 차트

![종합 비교 차트](./comprehensive_company_comparison.png)

![상관관계 히트맵](./company_correlation_heatmap.png)

### 💡 인사이트 분석

"""

    if all_stats:
        # 인사이트 생성
        highest_avg = max(all_stats.items(), key=lambda x: x[1]['price_diff_ratio']['mean'])
        lowest_avg = min(all_stats.items(), key=lambda x: x[1]['price_diff_ratio']['mean'])
        highest_vol = max(all_stats.items(), key=lambda x: x[1]['price_diff_ratio']['std'])
        lowest_vol = min(all_stats.items(), key=lambda x: x[1]['price_diff_ratio']['std'])
        
        markdown_content += f"""
**1. 가격차이율 특성:**
- **{highest_avg[0]}**가 평균 가격차이율이 가장 높음 ({highest_avg[1]['price_diff_ratio']['mean']:.2f}%)
- **{lowest_avg[0]}**가 평균 가격차이율이 가장 낮음 ({lowest_avg[1]['price_diff_ratio']['mean']:.2f}%)
- 최고-최저 간 차이: {highest_avg[1]['price_diff_ratio']['mean'] - lowest_avg[1]['price_diff_ratio']['mean']:.2f}%p

**2. 변동성 특성:**
- **{highest_vol[0]}**가 가장 높은 변동성을 보임 (표준편차: {highest_vol[1]['price_diff_ratio']['std']:.2f}%)
- **{lowest_vol[0]}**가 가장 안정적임 (표준편차: {lowest_vol[1]['price_diff_ratio']['std']:.2f}%)

**3. 업종별 특성:**
"""
        
        # 업종별 분석
        sector_analysis = {}
        for company_name, stats in all_stats.items():
            sector = COMPANIES[company_name]['sector']
            if sector not in sector_analysis:
                sector_analysis[sector] = []
            sector_analysis[sector].append((company_name, stats['price_diff_ratio']['mean']))
        
        for sector, companies in sector_analysis.items():
            avg_by_sector = sum([mean for _, mean in companies]) / len(companies)
            company_list = ', '.join([name for name, _ in companies])
            markdown_content += f"- **{sector}**: 평균 {avg_by_sector:.2f}% ({company_list})\n"

    markdown_content += f"""

### 🎯 투자 전략 시사점

**1. 차익거래 관점:**
- 평균 가격차이율이 높은 종목일수록 차익거래 기회가 많을 수 있음
- 변동성이 높은 종목은 리스크가 크지만 수익 기회도 큼

**2. 안정성 관점:**
- 낮은 변동성을 보이는 종목은 상대적으로 안정적인 투자 대상
- 업종별 특성을 고려한 포트폴리오 구성 필요

**3. 시장 효율성:**
- 지속적인 가격차이는 시장의 비효율성을 시사
- 우선주 특성(배당, 의결권 등)이 가격차이에 영향

---

## 📝 분석 방법론

**데이터 소스:** yfinance API  
**분석 기간:** 20년 (약 {max([stats['total_days'] for stats in all_stats.values()]) if all_stats else 0:,}일)  
**지표:** 
- Price_Diff_Ratio = (보통주가격 - 우선주가격) / 우선주가격 × 100
- 통계적 지표: 평균, 표준편차, 분위수
- 상관관계 분석

**한계점:**
- 과거 데이터 기반 분석으로 미래 예측 한계
- 거래량, 유동성 등 기타 요인 미고려
- 시장 상황 변화에 따른 패턴 변화 가능성

---

## 📞 문의 및 추가 분석

이 리포트에 대한 문의사항이나 추가 분석이 필요한 경우 언제든 연락 바랍니다.

**생성 도구:** Python 자동화 분석 시스템  
**업데이트:** 매일 자동 업데이트 가능  

---

*본 리포트는 투자 참고용이며, 투자 결정은 개인의 책임입니다.*
"""

    # 파일 저장
    report_filename = f'comprehensive_company_comparison_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"📊 종합 비교 리포트 생성 완료: {report_filename}")
    print(f"📈 차트 파일: comprehensive_company_comparison.png")
    print(f"🔗 상관관계 히트맵: company_correlation_heatmap.png")
    
    return report_filename

if __name__ == "__main__":
    print("🚀 종합 회사 비교 리포트 생성 시작...")
    print("=" * 60)
    
    report_file = generate_markdown_report()
    
    print(f"\n✅ 리포트 생성 완료!")
    print(f"📁 파일 확인: {report_file}")
