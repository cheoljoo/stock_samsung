# -*- coding: utf-8 -*-
"""
Korean Dividend Analysis System
A comprehensive system to identify and analyze Korean companies with 
consistent dividend payments (5+ consecutive years).
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import platform
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings('ignore')

# Font setup for Korean text - Enhanced version
def setup_korean_font():
    """Setup Korean fonts with fallback options"""
    system_name = platform.system()
    
    # Get available fonts
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # Korean font candidates by system
    if system_name == 'Windows':
        font_candidates = ['Malgun Gothic', 'NanumGothic', 'Gulim', 'Dotum']
    elif system_name == 'Darwin':
        font_candidates = ['AppleGothic', 'AppleSDGothicNeo', 'NanumGothic']
    else:  # Linux and others
        font_candidates = ['NanumGothic', 'NanumBarunGothic', 'DejaVu Sans']
    
    # Find first available Korean font
    selected_font = None
    for font in font_candidates:
        if font in available_fonts:
            selected_font = font
            break
        # Case-insensitive search
        for available in available_fonts:
            if font.lower() in available.lower():
                selected_font = available
                break
        if selected_font:
            break
    
    # Set font
    if selected_font:
        plt.rcParams['font.family'] = selected_font
        print(f"✅ Korean font set: {selected_font}")
    else:
        plt.rcParams['font.family'] = ['sans-serif']
        print("⚠️  No Korean font found. Korean text may display as boxes.")
    
    plt.rcParams['axes.unicode_minus'] = False
    return selected_font is not None

# Initialize Korean font
setup_korean_font()

# Extended Korean companies database
KOREAN_DIVIDEND_COMPANIES = {
    '삼성전자': {'common': '005930.KS', 'preferred': '005935.KS', 'name': '삼성전자', 'sector': '전자/반도체'},
    'LG화학': {'common': '051910.KS', 'preferred': '051915.KS', 'name': 'LG화학', 'sector': '화학'},
    'LG전자': {'common': '066570.KS', 'preferred': '066575.KS', 'name': 'LG전자', 'sector': '전자'},
    '현대자동차': {'common': '005380.KS', 'preferred': '005385.KS', 'name': '현대자동차', 'sector': '자동차'},
    'SK하이닉스': {'common': '000660.KS', 'name': 'SK하이닉스', 'sector': '반도체'},
    'NAVER': {'common': '035420.KS', 'name': 'NAVER', 'sector': 'IT서비스'},
    'KT&G': {'common': '033780.KS', 'name': 'KT&G', 'sector': '담배'},
    '한국전력공사': {'common': '015760.KS', 'name': '한국전력공사', 'sector': '전력'},
    'S-Oil': {'common': '010950.KS', 'name': 'S-Oil', 'sector': '정유'},
    '기아': {'common': '000270.KS', 'name': '기아', 'sector': '자동차'},
    'LG': {'common': '003550.KS', 'name': 'LG', 'sector': '지주회사'},
    '포스코홀딩스': {'common': '005490.KS', 'name': '포스코홀딩스', 'sector': '철강'},
    'LG생활건강': {'common': '051900.KS', 'name': 'LG생활건강', 'sector': '생활용품'},
    '아모레퍼시픽': {'common': '090430.KS', 'name': '아모레퍼시픽', 'sector': '화장품'},
    'SK텔레콤': {'common': '017670.KS', 'name': 'SK텔레콤', 'sector': '통신'},
    'KT': {'common': '030200.KS', 'name': 'KT', 'sector': '통신'},
    'LG유플러스': {'common': '032640.KS', 'name': 'LG유플러스', 'sector': '통신'},
    '한국가스공사': {'common': '036460.KS', 'name': '한국가스공사', 'sector': '가스'},
    'CJ제일제당': {'common': '097950.KS', 'name': 'CJ제일제당', 'sector': '식품'},
    '롯데케미칼': {'common': '011170.KS', 'name': '롯데케미칼', 'sector': '화학'},
    'SK이노베이션': {'common': '096770.KS', 'name': 'SK이노베이션', 'sector': '에너지/화학'}
}

class KoreanDividendAnalyzer:
    """Korean Dividend Analysis System"""
    
    def __init__(self):
        self.companies = KOREAN_DIVIDEND_COMPANIES
        self.analysis_results = {}
        
    def get_dividend_history(self, ticker, years=10):
        """Get dividend history for a specific ticker"""
        try:
            stock = yf.Ticker(ticker)
            start_date = (datetime.now() - timedelta(days=years*365)).strftime('%Y-%m-%d')
            dividends = stock.dividends[start_date:]
            
            if not dividends.empty and hasattr(dividends.index, 'tz') and dividends.index.tz is not None:
                dividends.index = dividends.index.tz_localize(None)
                
            return dividends
        except Exception as e:
            print(f"❌ Error getting dividend data for {ticker}: {e}")
            return pd.Series(dtype=float)
    
    def check_consecutive_dividend_years(self, dividends, min_years=5):
        """Check if a company has paid dividends for consecutive years"""
        if dividends.empty:
            return 0, False
            
        yearly_dividends = dividends.groupby(dividends.index.year).sum()
        yearly_dividends = yearly_dividends[yearly_dividends > 0]
        
        if len(yearly_dividends) == 0:
            return 0, False
        
        years = sorted(yearly_dividends.index)
        consecutive_count = 1
        max_consecutive = 1
        
        for i in range(1, len(years)):
            if years[i] == years[i-1] + 1:
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                consecutive_count = 1
        
        current_year = datetime.now().year
        recent_consecutive = 0
        
        for year in range(current_year - max_consecutive, current_year + 1):
            if year in years:
                recent_consecutive += 1
            else:
                break
                
        final_consecutive = max(max_consecutive, recent_consecutive)
        is_qualified = final_consecutive >= min_years
        
        return final_consecutive, is_qualified
    
    def get_stock_info(self, ticker):
        """Get current stock information including price and market cap"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period='5d')
            
            if hist.empty:
                return None
                
            current_price = hist['Close'].iloc[-1]
            market_cap = info.get('marketCap', 0)
            shares_outstanding = info.get('sharesOutstanding', 0)
            
            if market_cap == 0 and shares_outstanding > 0:
                market_cap = current_price * shares_outstanding
            
            return {
                'price': current_price,
                'market_cap': market_cap,
                'shares_outstanding': shares_outstanding,
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown')
            }
        except Exception as e:
            print(f"❌ Error getting stock info for {ticker}: {e}")
            return None
    
    def calculate_dividend_metrics(self, ticker, stock_info):
        """Calculate dividend metrics for a stock"""
        dividends = self.get_dividend_history(ticker, years=10)
        consecutive_years, is_qualified = self.check_consecutive_dividend_years(dividends)
        
        if dividends.empty or not is_qualified:
            return {
                'consecutive_years': consecutive_years,
                'is_qualified': is_qualified,
                'annual_dividend': 0,
                'dividend_yield': 0,
                'dividend_growth_rate': 0,
                'total_dividends': 0
            }
        
        one_year_ago = datetime.now() - timedelta(days=365)
        recent_dividends = dividends[dividends.index >= one_year_ago]
        annual_dividend = recent_dividends.sum() if not recent_dividends.empty else 0
        
        current_price = stock_info['price'] if stock_info else 0
        dividend_yield = (annual_dividend / current_price * 100) if current_price > 0 else 0
        
        yearly_dividends = dividends.groupby(dividends.index.year).sum()
        if len(yearly_dividends) >= 3:
            recent_years = yearly_dividends.tail(3)
            growth_rates = []
            for i in range(1, len(recent_years)):
                if recent_years.iloc[i-1] > 0:
                    growth_rate = (recent_years.iloc[i] - recent_years.iloc[i-1]) / recent_years.iloc[i-1] * 100
                    growth_rates.append(growth_rate)
            dividend_growth_rate = np.mean(growth_rates) if growth_rates else 0
        else:
            dividend_growth_rate = 0
        
        return {
            'consecutive_years': consecutive_years,
            'is_qualified': is_qualified,
            'annual_dividend': annual_dividend,
            'dividend_yield': dividend_yield,
            'dividend_growth_rate': dividend_growth_rate,
            'total_dividends': dividends.sum()
        }
    
    def analyze_single_company(self, company_name):
        """Analyze a single company for dividend consistency and metrics"""
        if company_name not in self.companies:
            return None
        
        company_info = self.companies[company_name]
        results = {
            'company_name': company_name,
            'sector': company_info['sector'],
            'has_preferred': 'preferred' in company_info,
            'common_stock': {},
            'preferred_stock': {},
            'investment_score': 0
        }
        
        print(f"\n🔍 분석 중: {company_name} ({company_info['sector']})")
        
        # Analyze common stock
        common_ticker = company_info['common']
        common_stock_info = self.get_stock_info(common_ticker)
        
        if common_stock_info:
            common_dividend_metrics = self.calculate_dividend_metrics(common_ticker, common_stock_info)
            results['common_stock'] = {
                'ticker': common_ticker,
                **common_stock_info,
                **common_dividend_metrics
            }
            print(f"  ✓ 보통주 ({common_ticker}): {common_dividend_metrics['consecutive_years']}년 연속배당")
        else:
            print(f"  ❌ 보통주 ({common_ticker}): 데이터 수집 실패")
            
        # Analyze preferred stock if available
        if 'preferred' in company_info:
            preferred_ticker = company_info['preferred']
            preferred_stock_info = self.get_stock_info(preferred_ticker)
            
            if preferred_stock_info:
                preferred_dividend_metrics = self.calculate_dividend_metrics(preferred_ticker, preferred_stock_info)
                results['preferred_stock'] = {
                    'ticker': preferred_ticker,
                    **preferred_stock_info,
                    **preferred_dividend_metrics
                }
                print(f"  ✓ 우선주 ({preferred_ticker}): {preferred_dividend_metrics['consecutive_years']}년 연속배당")
            else:
                print(f"  ❌ 우선주 ({preferred_ticker}): 데이터 수집 실패")
        
        results['investment_score'] = self.calculate_investment_score(results)
        return results
    
    def calculate_investment_score(self, company_results):
        """Calculate investment score based on multiple criteria"""
        score = 0
        common_stock = company_results.get('common_stock', {})
        
        if not common_stock or not common_stock.get('is_qualified', False):
            return 0
        
        # Dividend reliability (40% weight)
        consecutive_years = common_stock.get('consecutive_years', 0)
        score += min(consecutive_years * 4, 40)
        
        # Dividend yield (30% weight)
        dividend_yield = common_stock.get('dividend_yield', 0)
        yield_score = min(dividend_yield * 6, 30)
        score += yield_score
        
        # Market cap stability (20% weight)
        market_cap = common_stock.get('market_cap', 0)
        if market_cap > 10_000_000_000_000:  # 10조원 이상
            score += 20
        elif market_cap > 1_000_000_000_000:  # 1조원 이상
            score += 15
        elif market_cap > 100_000_000_000:  # 1000억원 이상
            score += 10
        else:
            score += 5
        
        # Dividend growth (10% weight)
        growth_rate = common_stock.get('dividend_growth_rate', 0)
        if growth_rate > 5:
            score += 10
        elif growth_rate > 0:
            score += 5
        elif growth_rate > -5:
            score += 2
        
        return min(score, 100)
    
    def analyze_all_companies(self, min_consecutive_years=5):
        """Analyze all companies in the database"""
        print("🚀 한국 배당주 종합 분석 시작")
        print(f"📊 총 {len(self.companies)}개 회사 분석 예정")
        print("=" * 60)
        
        qualified_companies = {}
        
        for company_name in self.companies:
            try:
                result = self.analyze_single_company(company_name)
                if result and result['common_stock'].get('is_qualified', False):
                    consecutive_years = result['common_stock']['consecutive_years']
                    if consecutive_years >= min_consecutive_years:
                        qualified_companies[company_name] = result
                        print(f"✅ {company_name}: {consecutive_years}년 연속배당 (점수: {result['investment_score']:.1f})")
                    else:
                        print(f"○ {company_name}: {consecutive_years}년 연속배당 (기준 미달)")
                else:
                    print(f"❌ {company_name}: 배당 기준 미달 또는 데이터 없음")
            except Exception as e:
                print(f"❌ {company_name}: 분석 실패 - {e}")
        
        self.analysis_results = qualified_companies
        print(f"\n🎯 분석 완료: {len(qualified_companies)}개 회사가 {min_consecutive_years}년 이상 연속배당 기준 충족")
        
        return qualified_companies
    
    def create_comparison_table(self):
        """Create a comprehensive comparison table"""
        if not self.analysis_results:
            print("❌ 분석 결과가 없습니다. analyze_all_companies()를 먼저 실행하세요.")
            return pd.DataFrame()
        
        table_data = []
        
        for company_name, results in self.analysis_results.items():
            common_stock = results['common_stock']
            preferred_stock = results.get('preferred_stock', {})
            
            row = {
                '회사명': company_name,
                '섹터': results['sector'],
                '연속배당년수': common_stock['consecutive_years'],
                '보통주가격': f"{common_stock['price']:,.0f}원",
                '보통주배당률': f"{common_stock['dividend_yield']:.2f}%",
                '연간배당금': f"{common_stock['annual_dividend']:,.0f}원",
                '시가총액': self.format_market_cap(common_stock['market_cap']),
                '배당성장률': f"{common_stock['dividend_growth_rate']:.1f}%",
                '투자점수': f"{results['investment_score']:.1f}",
                '등급': self.get_investment_grade(results['investment_score'])
            }
            
            if preferred_stock and preferred_stock.get('is_qualified', False):
                row['우선주가격'] = f"{preferred_stock['price']:,.0f}원"
                row['우선주배당률'] = f"{preferred_stock['dividend_yield']:.2f}%"
            else:
                row['우선주가격'] = '-'
                row['우선주배당률'] = '-'
            
            table_data.append(row)
        
        df = pd.DataFrame(table_data)
        df = df.sort_values('투자점수', ascending=False, key=lambda x: x.str.replace('점', '').astype(float))
        df = df.reset_index(drop=True)
        df.index = df.index + 1
        
        return df
    
    def format_market_cap(self, market_cap):
        """Format market capitalization in Korean units"""
        if market_cap >= 1_000_000_000_000:
            return f"{market_cap/1_000_000_000_000:.1f}조원"
        elif market_cap >= 100_000_000_000:
            return f"{market_cap/100_000_000_000:.1f}천억원"
        elif market_cap >= 10_000_000_000:
            return f"{market_cap/10_000_000_000:.0f}백억원"
        else:
            return f"{market_cap/100_000_000:.0f}억원"
    
    def get_investment_grade(self, score):
        """Get investment grade based on score"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C+'
        else:
            return 'C'
    
    def generate_visualizations(self):
        """Generate visualization charts"""
        if not self.analysis_results:
            return
        
        companies = list(self.analysis_results.keys())
        dividend_yields = [results['common_stock']['dividend_yield'] for results in self.analysis_results.values()]
        consecutive_years = [results['common_stock']['consecutive_years'] for results in self.analysis_results.values()]
        investment_scores = [results['investment_score'] for results in self.analysis_results.values()]
        sectors = [results['sector'] for results in self.analysis_results.values()]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Dividend Yield by Company
        ax1.barh(companies, dividend_yields, color='steelblue')
        ax1.set_xlabel('배당률 (%)')
        ax1.set_title('🏆 회사별 배당률 비교')
        ax1.grid(axis='x', alpha=0.3)
        
        # 2. Investment Score vs Dividend Yield
        scatter = ax2.scatter(dividend_yields, investment_scores, 
                             c=consecutive_years, cmap='viridis', s=100, alpha=0.7)
        ax2.set_xlabel('배당률 (%)')
        ax2.set_ylabel('투자점수')
        ax2.set_title('📊 배당률 vs 투자점수')
        ax2.grid(alpha=0.3)
        plt.colorbar(scatter, ax=ax2, label='연속배당년수')
        
        # 3. Sector Distribution
        sector_counts = pd.Series(sectors).value_counts()
        ax3.pie(sector_counts.values, labels=sector_counts.index, autopct='%1.1f%%')
        ax3.set_title('🏭 섹터별 분포')
        
        # 4. Consecutive Years Distribution
        ax4.hist(consecutive_years, bins=range(5, max(consecutive_years)+2), 
                 color='lightcoral', alpha=0.7, edgecolor='black')
        ax4.set_xlabel('연속배당년수')
        ax4.set_ylabel('회사 수')
        ax4.set_title('📈 연속배당년수 분포')
        ax4.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('korean_dividend_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("📊 차트가 'korean_dividend_analysis.png'로 저장되었습니다.")
    
    def save_results(self, filename='korean_dividend_analysis_results.json'):
        """Save analysis results to JSON file"""
        if not self.analysis_results:
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 분석 결과가 '{filename}'에 저장되었습니다.")
    
    def print_summary_report(self):
        """Print a comprehensive summary report"""
        if not self.analysis_results:
            print("❌ 분석 결과가 없습니다.")
            return
        
        print("\n" + "="*80)
        print("🏆 한국 우수 배당주 분석 리포트")
        print("="*80)
        
        sorted_companies = sorted(self.analysis_results.items(), 
                                key=lambda x: x[1]['investment_score'], reverse=True)
        
        print(f"\n💎 투자점수 TOP 5:")
        for i, (company, results) in enumerate(sorted_companies[:5], 1):
            common = results['common_stock']
            print(f"  {i}. {company:12s}: {results['investment_score']:5.1f}점 "
                  f"(배당률: {common['dividend_yield']:5.2f}%, "
                  f"연속년수: {common['consecutive_years']:2d}년)")
        
        high_yield_companies = sorted(self.analysis_results.items(),
                                    key=lambda x: x[1]['common_stock']['dividend_yield'], reverse=True)
        
        print(f"\n💰 고배당률 TOP 5:")
        for i, (company, results) in enumerate(high_yield_companies[:5], 1):
            common = results['common_stock']
            print(f"  {i}. {company:12s}: {common['dividend_yield']:5.2f}% "
                  f"(점수: {results['investment_score']:5.1f}점, "
                  f"연속년수: {common['consecutive_years']:2d}년)")
        
        long_history_companies = sorted(self.analysis_results.items(),
                                      key=lambda x: x[1]['common_stock']['consecutive_years'], reverse=True)
        
        print(f"\n🗓️ 장기 연속배당 TOP 5:")
        for i, (company, results) in enumerate(long_history_companies[:5], 1):
            common = results['common_stock']
            print(f"  {i}. {company:12s}: {common['consecutive_years']:2d}년 "
                  f"(배당률: {common['dividend_yield']:5.2f}%, "
                  f"점수: {results['investment_score']:5.1f}점)")
        
        print("\n" + "="*80)


def main():
    """Main function to run the Korean dividend analysis"""
    analyzer = KoreanDividendAnalyzer()
    
    print("🚀 한국 배당주 분석을 시작합니다...")
    results = analyzer.analyze_all_companies(min_consecutive_years=5)
    
    if not results:
        print("❌ 5년 이상 연속배당 기준을 만족하는 회사가 없습니다.")
        return
    
    print("\n📊 비교표 생성 중...")
    comparison_table = analyzer.create_comparison_table()
    
    if not comparison_table.empty:
        print("\n🏆 한국 우수 배당주 비교표")
        print("="*120)
        print(comparison_table.to_string(index=True))
    
    print("\n📈 차트 생성 중...")
    analyzer.generate_visualizations()
    
    analyzer.print_summary_report()
    analyzer.save_results()

if __name__ == "__main__":
    main()