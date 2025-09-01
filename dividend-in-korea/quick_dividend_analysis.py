# -*- coding: utf-8 -*-
"""
Quick Korean Dividend Analysis
Run this script for a focused analysis of Korean companies with 5+ consecutive dividend years
"""

from korean_dividend_analyzer import KoreanDividendAnalyzer
import pandas as pd

def main():
    print("🎯 한국 우수 배당주 간단 분석")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = KoreanDividendAnalyzer()
    
    # Run analysis
    results = analyzer.analyze_all_companies(min_consecutive_years=5)
    
    if not results:
        print("❌ 5년 이상 연속배당 기준을 만족하는 회사가 없습니다.")
        return
    
    # Create simplified comparison table
    table_data = []
    
    for company_name, result in results.items():
        common = result['common_stock']
        table_data.append({
            '순위': 0,  # Will be set after sorting
            '회사명': company_name,
            '섹터': result['sector'],
            '연속배당년수': f"{common['consecutive_years']}년",
            '현재주가': f"{common['price']:,.0f}원",
            '배당률': f"{common['dividend_yield']:.2f}%",
            '연간배당금': f"{common['annual_dividend']:,.0f}원",
            '시가총액': analyzer.format_market_cap(common['market_cap']),
            '투자등급': analyzer.get_investment_grade(result['investment_score']),
            '점수': f"{result['investment_score']:.1f}"
        })
    
    # Create DataFrame and sort by investment score
    df = pd.DataFrame(table_data)
    df = df.sort_values('점수', ascending=False, key=lambda x: x.str.replace('점', '').astype(float))
    df['순위'] = range(1, len(df) + 1)
    
    print(f"\n🏆 5년 이상 연속배당 한국 기업 TOP {len(df)}:")
    print("=" * 100)
    print(df.to_string(index=False))
    
    # Show top recommendations
    print(f"\n💡 투자 추천 TOP 5:")
    print("-" * 60)
    for i, (_, row) in enumerate(df.head(5).iterrows(), 1):
        print(f"  {i}. {row['회사명']} ({row['섹터']})")
        print(f"     📈 배당률: {row['배당률']} | 연속년수: {row['연속배당년수']} | 등급: {row['투자등급']}")
        print(f"     💰 현재주가: {row['현재주가']} | 시가총액: {row['시가총액']}")
        print()
    
    # Sector summary
    sector_summary = df.groupby('섹터').agg({
        '회사명': 'count',
        '점수': lambda x: x.str.replace('점', '').astype(float).mean()
    }).rename(columns={'회사명': '기업수', '점수': '평균점수'})
    sector_summary['평균점수'] = sector_summary['평균점수'].round(1)
    sector_summary = sector_summary.sort_values('평균점수', ascending=False)
    
    print("📊 섹터별 요약:")
    print("-" * 40)
    for sector, data in sector_summary.iterrows():
        print(f"  {sector:12s}: {int(data['기업수']):2d}개사 (평균 {data['평균점수']:.1f}점)")

if __name__ == "__main__":
    main()