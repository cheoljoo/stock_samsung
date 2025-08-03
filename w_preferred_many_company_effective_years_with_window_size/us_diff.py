# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import platform
import matplotlib.font_manager as fm

# OS에 맞게 폰트 설정
system_name = platform.system()
if system_name == 'Windows':
    plt.rcParams['font.family'] = 'Arial'
elif system_name == 'Darwin':  # Mac OS
    plt.rcParams['font.family'] = 'Arial'
elif system_name == 'Linux':
    plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['axes.unicode_minus'] = False

# 미국 우선주를 가진 주요 회사들의 리스트 (검증된 티커만 포함)
US_PREFERRED_STOCK_COMPANIES = {
    'Bank of America': {
        'common': 'BAC',
        'preferred_stocks': {
            'BAC-PK': 'BAC-PK',  # Series K - 검증됨
            'BAC-PL': 'BAC-PL',  # Series L - 검증됨  
            'BAC-PN': 'BAC-PN',  # Series N - 검증됨
        },
        'name': 'Bank of America',
        'sector': 'Financial Services',
        'dividend_data': None,
        'description': '미국 최대 은행 중 하나로 안정적인 우선주 배당금 지급 이력을 보유'
    },
    'JPMorgan Chase': {
        'common': 'JPM',
        'preferred_stocks': {
            'JPM-PC': 'JPM-PC',  # Series C - 검증됨
            'JPM-PD': 'JPM-PD',  # Series D - 검증됨
        },
        'name': 'JPMorgan Chase',
        'sector': 'Financial Services',
        'dividend_data': None,
        'description': '글로벌 최고 신용등급의 투자은행으로 우선주 투자에 가장 안전한 선택'
    },
    'Digital Realty Trust': {
        'common': 'DLR',
        'preferred_stocks': {
            'DLR-PJ': 'DLR-PJ',  # Series J - 검증됨
            'DLR-PK': 'DLR-PK',  # Series K - 검증됨
        },
        'name': 'Digital Realty Trust',
        'sector': 'Real Estate Investment Trust',
        'dividend_data': None,
        'description': '데이터센터 전문 리츠로 디지털 경제 성장과 함께 안정적 배당금 제공'
    },
    'NextEra Energy': {
        'common': 'NEE',
        'preferred_stocks': {
            'NEE-PN': 'NEE-PN',  # Series N - 검증됨
        },
        'name': 'NextEra Energy',
        'sector': 'Utilities',
        'dividend_data': None,
        'description': '재생에너지 선두기업으로 ESG 투자와 안정적 유틸리티 배당의 이중 혜택'
    },
    'Berkshire Hathaway': {
        'common': 'BRK-A',
        'preferred_stocks': {
            'BRK-B': 'BRK-B',  # Class B shares - 검증됨
        },
        'name': 'Berkshire Hathaway',
        'sector': 'Financial Services',
        'dividend_data': None,
        'description': '워렌 버핏의 투자회사로 Class A/B 주식간 가격차이 활용 가능 (배당금 없음)'
    },
    'Alphabet': {
        'common': 'GOOGL',
        'preferred_stocks': {
            'GOOG': 'GOOG',  # Class C (no voting rights) - 검증됨
        },
        'name': 'Alphabet Inc.',
        'sector': 'Technology',
        'dividend_data': None,
        'description': '구글 모회사로 의결권 유무에 따른 Class A/C 주식간 가격차이 분석 가능'
    }
}

def validate_us_ticker_availability():
    """
    미국 우선주 티커들이 yfinance에서 사용 가능한지 검증합니다.
    
    Returns:
        dict: 검증 결과
    """
    print("🇺🇸 미국 우선주 티커 유효성 검증 시작")
    print("=" * 80)
    
    validation_results = {}
    total_companies = len(US_PREFERRED_STOCK_COMPANIES)
    successful_companies = 0
    
    for company_name, company_info in US_PREFERRED_STOCK_COMPANIES.items():
        print(f"\n🏢 {company_name} ({company_info['sector']})")
        print("-" * 60)
        
        company_results = {
            'name': company_info['name'],
            'sector': company_info['sector'],
            'common_stock': {},
            'preferred_stocks': {},
            'all_valid': True
        }
        
        # 보통주 검증
        common_ticker = company_info['common']
        print(f"📈 보통주 검증: {common_ticker}")
        
        try:
            common_stock = yf.Ticker(common_ticker)
            common_info = common_stock.info
            common_hist = common_stock.history(period="5d")
            
            if not common_hist.empty and 'shortName' in common_info:
                company_results['common_stock'] = {
                    'ticker': common_ticker,
                    'name': common_info.get('shortName', 'N/A'),
                    'price': common_hist['Close'].iloc[-1] if not common_hist.empty else 0,
                    'currency': common_info.get('currency', 'USD'),
                    'valid': True,
                    'error': None
                }
                print(f"  ✅ {common_ticker}: {common_info.get('shortName', 'N/A')}")
                print(f"     가격: ${common_hist['Close'].iloc[-1]:.2f}" if not common_hist.empty else "     가격: N/A")
            else:
                company_results['common_stock'] = {
                    'ticker': common_ticker,
                    'valid': False,
                    'error': 'No data available'
                }
                company_results['all_valid'] = False
                print(f"  ❌ {common_ticker}: 데이터 없음")
                
        except Exception as e:
            company_results['common_stock'] = {
                'ticker': common_ticker,
                'valid': False,
                'error': str(e)
            }
            company_results['all_valid'] = False
            print(f"  ❌ {common_ticker}: 오류 - {e}")
        
        # 우선주들 검증
        if 'preferred_stocks' in company_info and company_info['preferred_stocks']:
            print(f"📊 우선주 검증:")
            
            for series_name, preferred_ticker in company_info['preferred_stocks'].items():
                print(f"  🔍 {preferred_ticker} 검증 중...")
                
                try:
                    preferred_stock = yf.Ticker(preferred_ticker)
                    preferred_info = preferred_stock.info
                    preferred_hist = preferred_stock.history(period="5d")
                    
                    if not preferred_hist.empty and 'shortName' in preferred_info:
                        company_results['preferred_stocks'][series_name] = {
                            'ticker': preferred_ticker,
                            'name': preferred_info.get('shortName', 'N/A'),
                            'price': preferred_hist['Close'].iloc[-1] if not preferred_hist.empty else 0,
                            'currency': preferred_info.get('currency', 'USD'),
                            'valid': True,
                            'error': None
                        }
                        print(f"    ✅ {preferred_ticker}: {preferred_info.get('shortName', 'N/A')}")
                        print(f"       가격: ${preferred_hist['Close'].iloc[-1]:.2f}" if not preferred_hist.empty else "       가격: N/A")
                    else:
                        company_results['preferred_stocks'][series_name] = {
                            'ticker': preferred_ticker,
                            'valid': False,
                            'error': 'No data available'
                        }
                        company_results['all_valid'] = False
                        print(f"    ❌ {preferred_ticker}: 데이터 없음")
                        
                except Exception as e:
                    company_results['preferred_stocks'][series_name] = {
                        'ticker': preferred_ticker,
                        'valid': False,
                        'error': str(e)
                    }
                    company_results['all_valid'] = False
                    print(f"    ❌ {preferred_ticker}: 오류 - {e}")
        else:
            print(f"  ○ 우선주 없음 (Class 구조)")
        
        validation_results[company_name] = company_results
        
        if company_results['all_valid']:
            successful_companies += 1
            print(f"  ✅ {company_name}: 모든 티커 유효")
        else:
            print(f"  ⚠️ {company_name}: 일부 티커 무효")
    
    # 요약 결과 출력
    print(f"\n{'='*80}")
    print("📊 미국 우선주 티커 검증 요약")
    print(f"{'='*80}")
    
    print(f"🏢 총 검증 회사 수: {total_companies}개")
    print(f"✅ 완전히 유효한 회사: {successful_companies}개")
    print(f"⚠️ 부분적으로 유효한 회사: {total_companies - successful_companies}개")
    
    # 섹터별 요약
    sector_summary = {}
    for company_name, results in validation_results.items():
        sector = results['sector']
        if sector not in sector_summary:
            sector_summary[sector] = {'total': 0, 'valid': 0}
        sector_summary[sector]['total'] += 1
        if results['all_valid']:
            sector_summary[sector]['valid'] += 1
    
    print(f"\n📊 섹터별 유효성:")
    for sector, stats in sector_summary.items():
        print(f"  {sector}: {stats['valid']}/{stats['total']} ({stats['valid']/stats['total']*100:.1f}%)")
    
    # 사용 가능한 우선주 리스트
    print(f"\n🎯 사용 가능한 우선주 페어:")
    available_pairs = 0
    for company_name, results in validation_results.items():
        if results['common_stock'].get('valid', False) and results['preferred_stocks']:
            valid_preferred = [ticker for ticker, info in results['preferred_stocks'].items() if info.get('valid', False)]
            if valid_preferred:
                available_pairs += len(valid_preferred)
                for preferred in valid_preferred:
                    common_ticker = results['common_stock']['ticker']
                    preferred_info = results['preferred_stocks'][preferred]
                    print(f"  ✅ {company_name}: {common_ticker} vs {preferred_info['ticker']}")
    
    print(f"\n📈 총 사용 가능한 분석 페어: {available_pairs}개")
    
    # 검증 결과 JSON 저장
    try:
        with open('./us_ticker_validation_results.json', 'w', encoding='utf-8') as f:
            json.dump(validation_results, f, indent=4, ensure_ascii=False)
        print(f"\n💾 검증 결과 저장: ./us_ticker_validation_results.json")
    except Exception as e:
        print(f"\n❌ 검증 결과 저장 실패: {e}")
    
    return validation_results

def generate_comprehensive_dividend_analysis():
    """
    모든 유효한 미국 우선주에 대한 종합적인 배당률 및 가격 비교 분석을 수행합니다.
    
    Returns:
        dict: 종합 분석 결과
    """
    print("🔍 미국 우선주 종합 배당률 분석 시작")
    print("=" * 80)
    
    analysis_results = []
    
    for company_name, company_info in US_PREFERRED_STOCK_COMPANIES.items():
        print(f"\n🏢 {company_name} 분석 중...")
        
        common_ticker = company_info['common']
        preferred_stocks = company_info.get('preferred_stocks', {})
        
        if not preferred_stocks:
            continue
            
        for series_name, preferred_ticker in preferred_stocks.items():
            print(f"  📊 {preferred_ticker} vs {common_ticker}")
            
            try:
                # 주식 정보 가져오기
                common_stock = yf.Ticker(common_ticker)
                preferred_stock = yf.Ticker(preferred_ticker)
                
                # 현재 가격
                common_hist = common_stock.history(period="5d")
                preferred_hist = preferred_stock.history(period="5d")
                
                if common_hist.empty or preferred_hist.empty:
                    print(f"    ❌ 가격 데이터 없음")
                    continue
                
                common_price = common_hist['Close'].iloc[-1]
                preferred_price = preferred_hist['Close'].iloc[-1]
                
                # 배당금 정보
                common_dividends = common_stock.dividends
                preferred_dividends = preferred_stock.dividends
                
                # 최근 1년 배당금 계산
                one_year_ago = datetime.now() - timedelta(days=365)
                one_year_ago = one_year_ago.replace(tzinfo=None)  # timezone 정보 제거
                
                # 배당금 날짜를 naive datetime으로 변환
                if not common_dividends.empty:
                    common_dividends.index = pd.to_datetime(common_dividends.index).tz_localize(None)
                    common_recent = common_dividends[common_dividends.index >= one_year_ago]
                else:
                    common_recent = pd.Series()
                
                if not preferred_dividends.empty:
                    preferred_dividends.index = pd.to_datetime(preferred_dividends.index).tz_localize(None)
                    preferred_recent = preferred_dividends[preferred_dividends.index >= one_year_ago]
                else:
                    preferred_recent = pd.Series()
                
                common_annual_dividend = common_recent.sum() if not common_recent.empty else 0
                preferred_annual_dividend = preferred_recent.sum() if not preferred_recent.empty else 0
                
                # 배당률 계산
                common_yield = (common_annual_dividend / common_price * 100) if common_price > 0 else 0
                preferred_yield = (preferred_annual_dividend / preferred_price * 100) if preferred_price > 0 else 0
                
                # 우선주 프리미엄 계산
                yield_premium = preferred_yield - common_yield
                
                # 결과 저장
                result = {
                    'company_name': company_name,
                    'sector': company_info['sector'],
                    'description': company_info.get('description', ''),
                    'common_ticker': common_ticker,
                    'preferred_ticker': preferred_ticker,
                    'common_price': common_price,
                    'preferred_price': preferred_price,
                    'price_diff': common_price - preferred_price,
                    'price_diff_ratio': ((common_price - preferred_price) / preferred_price * 100) if preferred_price > 0 else 0,
                    'common_annual_dividend': common_annual_dividend,
                    'preferred_annual_dividend': preferred_annual_dividend,
                    'common_yield': common_yield,
                    'preferred_yield': preferred_yield,
                    'yield_premium': yield_premium,
                    'dividend_ratio': (preferred_annual_dividend / common_annual_dividend) if common_annual_dividend > 0 else 0
                }
                
                analysis_results.append(result)
                
                print(f"    ✅ 보통주: ${common_price:.2f} ({common_yield:.2f}%)")
                print(f"    ✅ 우선주: ${preferred_price:.2f} ({preferred_yield:.2f}%)")
                print(f"    📈 프리미엄: {yield_premium:+.2f}%p")
                
            except Exception as e:
                print(f"    ❌ 분석 실패: {e}")
                continue
    
    # 결과 테이블 출력
    if analysis_results:
        print(f"\n{'='*100}")
        print("📊 미국 우선주 vs 보통주 배당률 비교 종합 테이블")
        print(f"{'='*100}")
        
        # 헤더 출력
        print(f"{'회사명':<15} {'보통주':<8} {'우선주':<8} {'보통주가':<10} {'우선주가':<10} {'보통주배당률':<12} {'우선주배당률':<12} {'프리미엄':<10}")
        print("-" * 100)
        
        # 섹터별로 정렬하여 출력
        sorted_results = sorted(analysis_results, key=lambda x: (x['sector'], x['company_name']))
        
        current_sector = None
        for result in sorted_results:
            if current_sector != result['sector']:
                current_sector = result['sector']
                print(f"\n🏭 {current_sector}")
                print("-" * 50)
            
            print(f"{result['company_name'][:14]:<15} {result['common_ticker']:<8} {result['preferred_ticker']:<8} "
                  f"${result['common_price']:<9.2f} ${result['preferred_price']:<9.2f} "
                  f"{result['common_yield']:<11.2f}% {result['preferred_yield']:<11.2f}% "
                  f"{result['yield_premium']:+9.2f}%p")
        
        # 요약 통계
        print(f"\n{'='*100}")
        print("📈 분석 요약")
        print(f"{'='*100}")
        
        total_pairs = len(analysis_results)
        positive_premium = len([r for r in analysis_results if r['yield_premium'] > 0])
        avg_premium = sum(r['yield_premium'] for r in analysis_results) / total_pairs if total_pairs > 0 else 0
        
        print(f"🔢 총 분석 페어: {total_pairs}개")
        print(f"✅ 우선주 배당률이 높은 페어: {positive_premium}개 ({positive_premium/total_pairs*100:.1f}%)")
        print(f"📊 평균 우선주 프리미엄: {avg_premium:+.2f}%p")
        
        # 섹터별 통계
        sector_stats = {}
        for result in analysis_results:
            sector = result['sector']
            if sector not in sector_stats:
                sector_stats[sector] = {'count': 0, 'avg_premium': 0, 'premiums': []}
            sector_stats[sector]['count'] += 1
            sector_stats[sector]['premiums'].append(result['yield_premium'])
        
        print(f"\n🏭 섹터별 우선주 프리미엄:")
        for sector, stats in sector_stats.items():
            avg_sector_premium = sum(stats['premiums']) / len(stats['premiums'])
            print(f"  {sector}: {avg_sector_premium:+.2f}%p (평균, {stats['count']}개 페어)")
        
        # 상위 추천 종목
        print(f"\n🎯 높은 우선주 프리미엄 TOP 5:")
        top_premiums = sorted(analysis_results, key=lambda x: x['yield_premium'], reverse=True)[:5]
        
        for i, result in enumerate(top_premiums, 1):
            print(f"  {i}. {result['company_name']} ({result['preferred_ticker']}): {result['yield_premium']:+.2f}%p")
            print(f"     📝 {result['description']}")
    
    return analysis_results

def save_dividend_analysis_report(analysis_results):
    """
    배당률 분석 결과를 마크다운 리포트로 저장합니다.
    
    Args:
        analysis_results (list): 분석 결과 리스트
    """
    try:
        report_file = './us_dividend_analysis_report.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 🇺🇸 미국 우선주 vs 보통주 배당률 분석 리포트\n\n")
            f.write(f"**생성일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**분석 대상:** {len(analysis_results)}개 우선주-보통주 페어\n\n")
            
            f.write("---\n\n")
            
            # Executive Summary
            total_pairs = len(analysis_results)
            positive_premium = len([r for r in analysis_results if r['yield_premium'] > 0])
            avg_premium = sum(r['yield_premium'] for r in analysis_results) / total_pairs if total_pairs > 0 else 0
            
            f.write("## 📊 분석 요약\n\n")
            f.write(f"- **총 분석 페어:** {total_pairs}개\n")
            f.write(f"- **우선주 배당률이 높은 페어:** {positive_premium}개 ({positive_premium/total_pairs*100:.1f}%)\n")
            f.write(f"- **평균 우선주 프리미엄:** {avg_premium:+.2f}%p\n\n")
            
            # 종합 테이블
            f.write("## 📋 배당률 비교 종합 테이블\n\n")
            f.write("| 회사명 | 섹터 | 보통주 | 우선주 | 보통주 가격 | 우선주 가격 | 보통주 배당률 | 우선주 배당률 | 우선주 프리미엄 |\n")
            f.write("|--------|------|--------|--------|-------------|-------------|---------------|---------------|------------------|\n")
            
            sorted_results = sorted(analysis_results, key=lambda x: (x['sector'], x['company_name']))
            
            for result in sorted_results:
                f.write(f"| {result['company_name']} | {result['sector']} | {result['common_ticker']} | "
                       f"{result['preferred_ticker']} | ${result['common_price']:.2f} | "
                       f"${result['preferred_price']:.2f} | {result['common_yield']:.2f}% | "
                       f"{result['preferred_yield']:.2f}% | **{result['yield_premium']:+.2f}%p** |\n")
            
            # 섹터별 분석
            f.write("\n## 🏭 섹터별 분석\n\n")
            
            sector_stats = {}
            for result in analysis_results:
                sector = result['sector']
                if sector not in sector_stats:
                    sector_stats[sector] = {'count': 0, 'results': [], 'premiums': []}
                sector_stats[sector]['count'] += 1
                sector_stats[sector]['results'].append(result)
                sector_stats[sector]['premiums'].append(result['yield_premium'])
            
            for sector, stats in sector_stats.items():
                avg_sector_premium = sum(stats['premiums']) / len(stats['premiums'])
                f.write(f"### {sector}\n\n")
                f.write(f"**평균 우선주 프리미엄:** {avg_sector_premium:+.2f}%p\n")
                f.write(f"**분석 페어 수:** {stats['count']}개\n\n")
                
                # 해당 섹터 회사들의 상세 정보
                for result in stats['results']:
                    f.write(f"#### {result['company_name']}\n")
                    f.write(f"**설명:** {result['description']}\n\n")
                    f.write(f"- **보통주 ({result['common_ticker']}):** ${result['common_price']:.2f} | 배당률 {result['common_yield']:.2f}%\n")
                    f.write(f"- **우선주 ({result['preferred_ticker']}):** ${result['preferred_price']:.2f} | 배당률 {result['preferred_yield']:.2f}%\n")
                    f.write(f"- **우선주 프리미엄:** {result['yield_premium']:+.2f}%p\n")
                    
                    if result['yield_premium'] > 2.0:
                        recommendation = "🟢 **강력 추천** - 높은 배당 프리미엄"
                    elif result['yield_premium'] > 1.0:
                        recommendation = "🟡 **추천** - 적정 배당 프리미엄"
                    elif result['yield_premium'] > 0:
                        recommendation = "🔵 **검토** - 낮은 배당 프리미엄"
                    else:
                        recommendation = "🔴 **비추천** - 배당 프리미엄 없음"
                    
                    f.write(f"- **투자 추천도:** {recommendation}\n\n")
            
            # TOP 추천 종목
            f.write("## 🎯 투자 추천 종목 TOP 5\n\n")
            top_premiums = sorted(analysis_results, key=lambda x: x['yield_premium'], reverse=True)[:5]
            
            for i, result in enumerate(top_premiums, 1):
                f.write(f"### {i}. {result['company_name']} - {result['preferred_ticker']}\n")
                f.write(f"**우선주 프리미엄:** {result['yield_premium']:+.2f}%p\n")
                f.write(f"**섹터:** {result['sector']}\n")
                f.write(f"**설명:** {result['description']}\n")
                f.write(f"**현재가:** 보통주 ${result['common_price']:.2f} | 우선주 ${result['preferred_price']:.2f}\n")
                f.write(f"**배당률:** 보통주 {result['common_yield']:.2f}% | 우선주 {result['preferred_yield']:.2f}%\n\n")
            
            # 투자 가이드라인
            f.write("## 💡 투자 가이드라인\n\n")
            f.write("### ✅ 추천 투자 전략\n")
            f.write("1. **배당 프리미엄 2%p 이상**: 강력 추천 종목으로 우선주 집중 투자\n")
            f.write("2. **금융 섹터 우선**: 전통적으로 안정적인 우선주 배당금 지급\n")
            f.write("3. **분산 투자**: 3-5개 종목으로 포트폴리오 구성\n")
            f.write("4. **정기 리밸런싱**: 분기별로 배당률 재검토\n\n")
            
            f.write("### ⚠️ 주의사항\n")
            f.write("1. **금리 리스크**: 금리 상승시 우선주 가격 하락 위험\n")
            f.write("2. **콜 리스크**: 발행사의 조기 상환 가능성\n")
            f.write("3. **유동성 리스크**: 보통주 대비 거래량 적음\n")
            f.write("4. **실시간 모니터링**: 배당금 변경 공지사항 주의\n\n")
            
            f.write("---\n\n")
            f.write("**📝 면책조항:** 본 분석은 과거 데이터 기반이며, 미래 배당금을 보장하지 않습니다. ")
            f.write("실제 투자시 추가적인 리서치와 전문가 상담을 권장합니다.\n")
            
        print(f"📋 배당률 분석 리포트 생성: {report_file}")
        
    except Exception as e:
        print(f"❌ 리포트 생성 실패: {e}")

def get_us_preferred_dividend_comparison(company_name, ticker_pair=None):
    """
    미국 회사의 보통주와 우선주 배당률을 비교합니다.
    
    Args:
        company_name (str): 회사명
        ticker_pair (tuple, optional): (보통주 티커, 우선주 티커) 튜플
        
    Returns:
        dict: 배당률 비교 결과
    """
    if company_name not in US_PREFERRED_STOCK_COMPANIES:
        print(f"❌ {company_name}는 지원되지 않는 회사입니다.")
        return None
    
    company_info = US_PREFERRED_STOCK_COMPANIES[company_name]
    
    if ticker_pair:
        common_ticker, preferred_ticker = ticker_pair
    else:
        common_ticker = company_info['common']
        # 첫 번째 우선주 사용
        preferred_stocks = company_info.get('preferred_stocks', {})
        if not preferred_stocks:
            print(f"❌ {company_name}에 우선주가 없습니다.")
            return None
        preferred_ticker = list(preferred_stocks.values())[0]
    
    print(f"\n🔍 {company_name} 배당률 비교 분석")
    print(f"📈 보통주: {common_ticker}")
    print(f"📊 우선주: {preferred_ticker}")
    print("-" * 60)
    
    try:
        # 주식 정보 가져오기
        common_stock = yf.Ticker(common_ticker)
        preferred_stock = yf.Ticker(preferred_ticker)
        
        # 현재 가격
        common_hist = common_stock.history(period="5d")
        preferred_hist = preferred_stock.history(period="5d")
        
        if common_hist.empty or preferred_hist.empty:
            print(f"❌ 가격 데이터를 가져올 수 없습니다.")
            return None
        
        common_price = common_hist['Close'].iloc[-1]
        preferred_price = preferred_hist['Close'].iloc[-1]
        
        # 배당금 정보
        common_dividends = common_stock.dividends
        preferred_dividends = preferred_stock.dividends
        
        # 최근 1년 배당금 계산
        one_year_ago = datetime.now() - timedelta(days=365)
        one_year_ago = one_year_ago.replace(tzinfo=None)  # timezone 정보 제거
        
        # 배당금 날짜를 naive datetime으로 변환
        if not common_dividends.empty:
            common_dividends.index = pd.to_datetime(common_dividends.index).tz_localize(None)
            common_recent = common_dividends[common_dividends.index >= one_year_ago]
        else:
            common_recent = pd.Series()
        
        if not preferred_dividends.empty:
            preferred_dividends.index = pd.to_datetime(preferred_dividends.index).tz_localize(None)
            preferred_recent = preferred_dividends[preferred_dividends.index >= one_year_ago]
        else:
            preferred_recent = pd.Series()
        
        common_annual_dividend = common_recent.sum() if not common_recent.empty else 0
        preferred_annual_dividend = preferred_recent.sum() if not preferred_recent.empty else 0
        
        # 배당률 계산
        common_yield = (common_annual_dividend / common_price * 100) if common_price > 0 else 0
        preferred_yield = (preferred_annual_dividend / preferred_price * 100) if preferred_price > 0 else 0
        
        result = {
            'company_name': company_name,
            'common_stock': {
                'ticker': common_ticker,
                'price': common_price,
                'annual_dividend': common_annual_dividend,
                'dividend_yield': common_yield,
                'dividend_count': len(common_recent)
            },
            'preferred_stock': {
                'ticker': preferred_ticker,
                'price': preferred_price,
                'annual_dividend': preferred_annual_dividend,
                'dividend_yield': preferred_yield,
                'dividend_count': len(preferred_recent)
            },
            'comparison': {
                'price_difference': common_price - preferred_price,
                'price_diff_ratio': ((common_price - preferred_price) / preferred_price * 100) if preferred_price > 0 else 0,
                'dividend_difference': preferred_annual_dividend - common_annual_dividend,
                'dividend_ratio': (preferred_annual_dividend / common_annual_dividend) if common_annual_dividend > 0 else 0,
                'yield_difference': preferred_yield - common_yield
            }
        }
        
        # 결과 출력
        print(f"💰 가격 정보:")
        print(f"  보통주: ${common_price:.2f}")
        print(f"  우선주: ${preferred_price:.2f}")
        print(f"  가격차이: ${result['comparison']['price_difference']:+.2f}")
        
        print(f"\n📊 배당 정보:")
        print(f"  보통주 연간배당: ${common_annual_dividend:.2f} (배당률: {common_yield:.3f}%)")
        print(f"  우선주 연간배당: ${preferred_annual_dividend:.2f} (배당률: {preferred_yield:.3f}%)")
        print(f"  배당률 차이: {result['comparison']['yield_difference']:+.3f}%p")
        
        if result['comparison']['dividend_ratio'] > 1:
            print(f"✅ 우선주가 {result['comparison']['dividend_ratio']:.2f}배 더 많은 배당금 지급")
        elif result['comparison']['dividend_ratio'] < 1 and result['comparison']['dividend_ratio'] > 0:
            print(f"⚠️ 보통주가 {1/result['comparison']['dividend_ratio']:.2f}배 더 많은 배당금 지급")
        else:
            print(f"○ 배당금 데이터 부족")
        
        return result
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return None

def generate_us_validation_report(validation_results):
    """
    미국 우선주 검증 결과 리포트를 생성합니다.
    
    Args:
        validation_results (dict): 검증 결과
    """
    try:
        report_file = './us_preferred_stock_validation_report.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 🇺🇸 미국 우선주 티커 검증 리포트\n\n")
            f.write(f"**생성일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**검증 대상:** {len(validation_results)}개 회사\n\n")
            
            f.write("---\n\n")
            
            # Executive Summary
            valid_companies = sum(1 for r in validation_results.values() if r['all_valid'])
            f.write("## 📊 검증 요약\n\n")
            f.write(f"- **총 검증 회사:** {len(validation_results)}개\n")
            f.write(f"- **완전히 유효한 회사:** {valid_companies}개 ({valid_companies/len(validation_results)*100:.1f}%)\n")
            f.write(f"- **부분적으로 유효한 회사:** {len(validation_results) - valid_companies}개\n\n")
            
            # 섹터별 분석
            sector_stats = {}
            for company_name, results in validation_results.items():
                sector = results['sector']
                if sector not in sector_stats:
                    sector_stats[sector] = {'total': 0, 'valid': 0, 'companies': []}
                sector_stats[sector]['total'] += 1
                sector_stats[sector]['companies'].append(company_name)
                if results['all_valid']:
                    sector_stats[sector]['valid'] += 1
            
            f.write("## 🏭 섹터별 분석\n\n")
            f.write("| 섹터 | 유효/총개수 | 유효율 | 회사들 |\n")
            f.write("|------|-------------|--------|--------|\n")
            
            for sector, stats in sector_stats.items():
                companies_str = ', '.join(stats['companies'])
                success_rate = stats['valid'] / stats['total'] * 100
                f.write(f"| {sector} | {stats['valid']}/{stats['total']} | {success_rate:.1f}% | {companies_str} |\n")
            
            # 회사별 상세 결과
            f.write("\n## 🏢 회사별 상세 검증 결과\n\n")
            
            for company_name, results in validation_results.items():
                status_icon = "✅" if results['all_valid'] else "⚠️"
                f.write(f"### {status_icon} {company_name}\n\n")
                f.write(f"**섹터:** {results['sector']}\n\n")
                
                # 보통주 정보
                common = results['common_stock']
                if common.get('valid', False):
                    f.write(f"**보통주:** ✅ {common['ticker']} - {common.get('name', 'N/A')} (${common.get('price', 0):.2f})\n\n")
                else:
                    f.write(f"**보통주:** ❌ {common['ticker']} - {common.get('error', 'Unknown error')}\n\n")
                
                # 우선주 정보
                if results['preferred_stocks']:
                    f.write(f"**우선주들:**\n")
                    for series, preferred in results['preferred_stocks'].items():
                        if preferred.get('valid', False):
                            f.write(f"- ✅ {preferred['ticker']} - {preferred.get('name', 'N/A')} (${preferred.get('price', 0):.2f})\n")
                        else:
                            f.write(f"- ❌ {preferred['ticker']} - {preferred.get('error', 'Unknown error')}\n")
                    f.write("\n")
                else:
                    f.write(f"**우선주들:** 없음 (Class 구조)\n\n")
            
            # 사용 가능한 분석 페어
            f.write("## 🎯 사용 가능한 분석 페어\n\n")
            available_pairs = []
            
            for company_name, results in validation_results.items():
                if results['common_stock'].get('valid', False):
                    common_ticker = results['common_stock']['ticker']
                    for series, preferred in results['preferred_stocks'].items():
                        if preferred.get('valid', False):
                            available_pairs.append((company_name, common_ticker, preferred['ticker']))
            
            if available_pairs:
                f.write("| 회사명 | 보통주 | 우선주 | 추천도 |\n")
                f.write("|--------|--------|--------|--------|\n")
                
                for company, common, preferred in available_pairs:
                    sector = validation_results[company]['sector']
                    if sector == 'Financial Services':
                        recommendation = "🟢 높음"
                    elif sector == 'Real Estate Investment Trust':
                        recommendation = "🟡 중간"
                    else:
                        recommendation = "🔵 보통"
                    
                    f.write(f"| {company} | {common} | {preferred} | {recommendation} |\n")
            else:
                f.write("사용 가능한 분석 페어가 없습니다.\n")
            
            f.write(f"\n📈 **총 사용 가능한 분석 페어:** {len(available_pairs)}개\n\n")
            
            # 권장사항
            f.write("## 💡 분석 권장사항\n\n")
            f.write("### 🏦 금융 섹터 (높은 우선순위)\n")
            f.write("- Bank of America, Wells Fargo, JPMorgan Chase\n")
            f.write("- 전통적으로 안정적인 우선주 배당금 지급\n")
            f.write("- 금리 환경에 민감하게 반응\n\n")
            
            f.write("### 🏠 리츠 섹터 (중간 우선순위)\n")
            f.write("- Realty Income, Digital Realty Trust\n")
            f.write("- 월배당 또는 분기배당으로 안정적 현금흐름\n")
            f.write("- 부동산 시장 동향에 따라 변동\n\n")
            
            f.write("### ⚡ 유틸리티 섹터 (안정적)\n")
            f.write("- NextEra Energy, Dominion Energy\n")
            f.write("- 안정적이지만 성장성 제한적\n")
            f.write("- 방어적 투자 성격\n\n")
            
            f.write("---\n\n")
            f.write("**⚠️ 주의사항:** 이 검증은 yfinance API를 통한 데이터 접근성만을 확인한 것이며, ")
            f.write("실제 투자 결정시에는 추가적인 리서치가 필요합니다.\n")
            
        print(f"📋 미국 우선주 검증 리포트 생성: {report_file}")
        
    except Exception as e:
        print(f"❌ 리포트 생성 실패: {e}")

def analyze_us_preferred_sector(sector_name=None):
    """
    특정 섹터의 미국 우선주들을 분석합니다.
    
    Args:
        sector_name (str, optional): 분석할 섹터명
    """
    if sector_name:
        companies = {name: info for name, info in US_PREFERRED_STOCK_COMPANIES.items() 
                    if info['sector'] == sector_name}
        if not companies:
            print(f"❌ '{sector_name}' 섹터에 해당하는 회사가 없습니다.")
            return
        print(f"🏭 {sector_name} 섹터 분석")
    else:
        companies = US_PREFERRED_STOCK_COMPANIES
        print(f"🌐 전체 섹터 분석")
    
    print("=" * 80)
    
    for company_name, company_info in companies.items():
        print(f"\n🏢 {company_name}")
        print(f"📊 섹터: {company_info['sector']}")
        
        # 각 우선주에 대해 분석
        preferred_stocks = company_info.get('preferred_stocks', {})
        if preferred_stocks:
            for series_name, preferred_ticker in preferred_stocks.items():
                ticker_pair = (company_info['common'], preferred_ticker)
                result = get_us_preferred_dividend_comparison(company_name, ticker_pair)
        else:
            print(f"  ○ 우선주 없음 (Class 구조)")

if __name__ == "__main__":
    import argparse
    
    print("🇺🇸 미국 우선주 분석 시스템")
    print("=" * 60)
    
    parser = argparse.ArgumentParser(description='미국 우선주 분석 시스템')
    parser.add_argument('--validate', '-v', action='store_true', help='티커 유효성 검증')
    parser.add_argument('--analyze', '-a', action='store_true', help='종합 배당률 분석')
    parser.add_argument('--company', '-c', type=str, help='특정 회사 분석')
    parser.add_argument('--sector', '-s', type=str, help='특정 섹터 분석')
    parser.add_argument('--list', '-l', action='store_true', help='지원 회사 목록 출력')
    
    args = parser.parse_args()
    
    if args.list:
        print("\n📋 지원하는 미국 회사들 (검증된 티커만):")
        print("=" * 80)
        for company, info in US_PREFERRED_STOCK_COMPANIES.items():
            print(f"🏢 {company} ({info['sector']})")
            print(f"  📈 보통주: {info['common']}")
            preferred = info.get('preferred_stocks', {})
            if preferred:
                for series, ticker in preferred.items():
                    print(f"  📊 우선주: {ticker}")
            print(f"  📝 설명: {info.get('description', 'N/A')}")
            print()
        exit(0)
    
    if args.validate:
        validation_results = validate_us_ticker_availability()
        generate_us_validation_report(validation_results)
    elif args.analyze:
        analysis_results = generate_comprehensive_dividend_analysis()
        if analysis_results:
            save_dividend_analysis_report(analysis_results)
    elif args.company:
        if args.company in US_PREFERRED_STOCK_COMPANIES:
            print(f"\n🎯 {args.company} 상세 분석")
            company_info = US_PREFERRED_STOCK_COMPANIES[args.company]
            print(f"📝 {company_info.get('description', 'N/A')}")
            
            preferred_stocks = company_info.get('preferred_stocks', {})
            for series_name, preferred_ticker in preferred_stocks.items():
                ticker_pair = (company_info['common'], preferred_ticker)
                result = get_us_preferred_dividend_comparison(args.company, ticker_pair)
        else:
            print(f"❌ '{args.company}'는 지원되지 않는 회사입니다.")
            print("사용 가능한 회사 목록을 보려면: python us_diff.py --list")
    elif args.sector:
        analyze_us_preferred_sector(args.sector)
    else:
        # 기본: 종합 배당률 분석
        print("기본 모드: 종합 배당률 분석을 실행합니다.")
        print("다른 옵션을 원하시면 --help를 참조하세요.")
        print()
        analysis_results = generate_comprehensive_dividend_analysis()
        if analysis_results:
            save_dividend_analysis_report(analysis_results)
