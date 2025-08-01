# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
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

# 우선주를 가진 한국 주요 회사들의 리스트 (실제 작동하는 4개 회사만)
PREFERRED_STOCK_COMPANIES = {
    '삼성전자': {
        'common': '005930.KS',      # 삼성전자
        'preferred': '005935.KS',   # 삼성전자(우)
        'name': '삼성전자',
        'sector': '전자/반도체',
        'dividend_data': [
            {"Ex-dividend Date": "6월 26, 2025", "Dividend": 361.00},
            {"Ex-dividend Date": "3월 27, 2025", "Dividend": 365.00},
            {"Ex-dividend Date": "12월 26, 2024", "Dividend": 364.00},
            {"Ex-dividend Date": "9월 26, 2024", "Dividend": 361.00},
            {"Ex-dividend Date": "6월 26, 2024", "Dividend": 361.00},
            {"Ex-dividend Date": "3월 27, 2024", "Dividend": 361.00},
            {"Ex-dividend Date": "12월 26, 2023", "Dividend": 362.00},
            {"Ex-dividend Date": "9월 25, 2023", "Dividend": 361.00},
            {"Ex-dividend Date": "6월 28, 2023", "Dividend": 361.00},
            {"Ex-dividend Date": "3월 29, 2023", "Dividend": 361.00},
            {"Ex-dividend Date": "12월 27, 2022", "Dividend": 362.00},
            {"Ex-dividend Date": "9월 28, 2022", "Dividend": 361.00},
            {"Ex-dividend Date": "6월 28, 2022", "Dividend": 361.00},
            {"Ex-dividend Date": "3월 29, 2022", "Dividend": 361.00},
            {"Ex-dividend Date": "12월 28, 2021", "Dividend": 362.00},
            {"Ex-dividend Date": "9월 28, 2021", "Dividend": 361.00},
            {"Ex-dividend Date": "6월 28, 2021", "Dividend": 361.00},
            {"Ex-dividend Date": "3월 29, 2021", "Dividend": 361.00},
            {"Ex-dividend Date": "12월 28, 2020", "Dividend": 1933.00},
            {"Ex-dividend Date": "9월 27, 2020", "Dividend": 354.00}
        ]
    },
    'LG화학': {
        'common': '051910.KS',      # LG화학
        'preferred': '051915.KS',   # LG화학(우)
        'name': 'LG화학',
        'sector': '화학',
        'dividend_data': None  # yfinance에서 자동 수집
    },
    'LG전자': {
        'common': '066570.KS',      # LG전자
        'preferred': '066575.KS',   # LG전자(우)
        'name': 'LG전자',
        'sector': '전자',
        'dividend_data': None
    },
    '현대자동차': {
        'common': '005380.KS',      # 현대자동차
        'preferred': '005385.KS',   # 현대자동차(우)
        'name': '현대자동차',
        'sector': '자동차',
        'dividend_data': None
    }
}

# 상장폐지되거나 거래 중단된 회사들 (참고용)
DELISTED_OR_SUSPENDED_COMPANIES = {
    # 'SK하이닉스': {
    #     'common': '000660.KS',      # SK하이닉스
    #     'preferred': '000665.KS',   # SK하이닉스(우) - 상장폐지 또는 거래 중단
    #     'name': 'SK하이닉스',
    #     'sector': '반도체',
    #     'status': 'delisted_or_suspended',
    #     'dividend_data': None
    # },
    # '포스코홀딩스': {
    #     'common': '005490.KS',      # 포스코홀딩스
    #     'preferred': '005495.KS',   # 포스코홀딩스(우) - 검증 필요
    #     'name': '포스코홀딩스',
    #     'sector': '철강',
    #     'status': 'requires_verification',
    #     'dividend_data': None
    # },
    # '카카오': {
    #     'common': '035720.KS',      # 카카오
    #     'preferred': '035725.KS',   # 카카오(우) - 2023년 상장폐지 확인됨
    #     'name': '카카오',
    #     'sector': 'IT서비스',
    #     'status': 'delisted_confirmed',
    #     'dividend_data': None
    # }
}

# 추가 검증이 필요한 회사들 (현재 주석 처리)
# 향후 데이터 검증 후 위 목록에 추가 가능
ADDITIONAL_COMPANIES_FOR_FUTURE_VERIFICATION = {
    # '기아': {
    #     'common': '000270.KS',      # 기아
    #     'preferred': '000275.KS',   # 기아(우)
    #     'name': '기아',
    #     'sector': '자동차',
    #     'dividend_data': None
    # },
    # 'NAVER': {
    #     'common': '035420.KS',      # NAVER
    #     'preferred': '035425.KS',   # NAVER(우)
    #     'name': 'NAVER',
    #     'sector': 'IT서비스',
    #     'dividend_data': None
    # },
    # 'SK이노베이션': {
    #     'common': '096770.KS',      # SK이노베이션
    #     'preferred': '096775.KS',   # SK이노베이션(우)
    #     'name': 'SK이노베이션',
    #     'sector': '에너지/화학',
    #     'dividend_data': None
    # },
    # 'LG생활건강': {
    #     'common': '051900.KS',      # LG생활건강
    #     'preferred': '051905.KS',   # LG생활건강(우)
    #     'name': 'LG생활건강',
    #     'sector': '생활용품',
    #     'dividend_data': None
    # },
    # '한화솔루션': {
    #     'common': '009830.KS',      # 한화솔루션
    #     'preferred': '009835.KS',   # 한화솔루션(우)
    #     'name': '한화솔루션',
    #     'sector': '태양광/화학',
    #     'dividend_data': None
    # },
    # 'CJ제일제당': {
    #     'common': '097950.KS',      # CJ제일제당
    #     'preferred': '097955.KS',   # CJ제일제당(우)
    #     'name': 'CJ제일제당',
    #     'sector': '식품',
    #     'dividend_data': None
    # },
    # '아모레퍼시픽': {
    #     'common': '090430.KS',      # 아모레퍼시픽
    #     'preferred': '090435.KS',   # 아모레퍼시픽(우)
    #     'name': '아모레퍼시픽',
    #     'sector': '화장품',
    #     'dividend_data': None
    # },
    # '롯데케미칼': {
    #     'common': '011170.KS',      # 롯데케미칼
    #     'preferred': '011175.KS',   # 롯데케미칼(우)
    #     'name': '롯데케미칼',
    #     'sector': '화학',
    #     'dividend_data': None
    # },
    # '카카오': {
    #     'common': '035720.KS',      # 카카오
    #     'preferred': '035725.KS',   # 카카오(우) - 2023년 상장폐지로 인해 분석 불가
    #     'name': '카카오',
    #     'sector': 'IT서비스',
    #     'dividend_data': None,
    #     'status': 'delisted_preferred'  # 우선주 상장폐지
    # }
}

def get_available_companies():
    """
    분석 가능한 우선주 보유 회사들의 목록을 반환합니다.
    
    Returns:
        dict: 회사명을 키로 하는 회사 정보 딕셔너리
    """
    return PREFERRED_STOCK_COMPANIES

def get_yfinance_dividend_data(ticker, start_date=None, end_date=None):
    """
    yfinance에서 특정 티커의 배당금 데이터를 가져옵니다.
    
    Args:
        ticker (str): 주식 티커 심볼
        start_date (str, optional): 시작 날짜 (YYYY-MM-DD)
        end_date (str, optional): 종료 날짜 (YYYY-MM-DD)
        
    Returns:
        pd.Series: 배당금 시계열 데이터
    """
    try:
        stock = yf.Ticker(ticker)
        
        if start_date and end_date:
            dividends = stock.dividends[start_date:end_date]
        else:
            # 기본적으로 최근 10년 데이터 가져오기
            ten_years_ago = (datetime.now() - timedelta(days=10*365)).strftime('%Y-%m-%d')
            dividends = stock.dividends[ten_years_ago:]
        
        if not dividends.empty:
            print(f"✓ {ticker} yfinance 배당금 데이터: {len(dividends)}개 항목")
            return dividends
        else:
            print(f"○ {ticker} 배당금 데이터 없음")
            return pd.Series(dtype=float)
            
    except Exception as e:
        print(f"❌ {ticker} 배당금 데이터 수집 실패: {e}")
        return pd.Series(dtype=float)

def merge_dividend_data(external_data, yfinance_data):
    """
    외부 배당금 데이터와 yfinance 데이터를 병합합니다.
    외부 데이터를 우선하되, yfinance에서 새로운 데이터가 있으면 추가합니다.
    
    Args:
        external_data (pd.Series): 외부 배당금 데이터
        yfinance_data (pd.Series): yfinance 배당금 데이터
        
    Returns:
        pd.Series: 병합된 배당금 데이터
    """
    if external_data.empty and yfinance_data.empty:
        return pd.Series(dtype=float)
    
    if external_data.empty:
        # yfinance 데이터의 타임존 정보 제거
        if not yfinance_data.empty and hasattr(yfinance_data.index, 'tz') and yfinance_data.index.tz is not None:
            yfinance_data.index = yfinance_data.index.tz_localize(None)
        return yfinance_data
    
    if yfinance_data.empty:
        return external_data
    
    # 타임존 정보 통일 (모두 naive datetime으로 변환)
    if hasattr(external_data.index, 'tz') and external_data.index.tz is not None:
        external_data.index = external_data.index.tz_localize(None)
    
    if hasattr(yfinance_data.index, 'tz') and yfinance_data.index.tz is not None:
        yfinance_data.index = yfinance_data.index.tz_localize(None)
    
    # 두 데이터를 병합 (외부 데이터 우선, 새로운 yfinance 데이터 추가)
    combined = external_data.copy()
    
    # yfinance 데이터에서 외부 데이터에 없는 날짜의 배당금 추가
    new_dates = yfinance_data.index[~yfinance_data.index.isin(external_data.index)]
    if len(new_dates) > 0:
        for date in new_dates:
            combined[date] = yfinance_data[date]
        print(f"✓ yfinance에서 {len(new_dates)}개 새로운 배당금 데이터 추가")
    
    return combined.sort_index()

def get_company_dividend_data(company_name, start_date=None, end_date=None, stock_type='preferred'):
    """
    특정 회사의 배당금 데이터를 반환합니다.
    외부 데이터와 yfinance 데이터를 자동으로 병합합니다.
    
    Args:
        company_name (str): 회사명
        start_date (str, optional): 시작 날짜 (YYYY-MM-DD)
        end_date (str, optional): 종료 날짜 (YYYY-MM-DD)
        stock_type (str): 'preferred' 또는 'common' (기본값: 'preferred')
        
    Returns:
        pd.Series: 배당금 시계열 데이터
    """
    if company_name not in PREFERRED_STOCK_COMPANIES:
        return pd.Series(dtype=float)
    
    company_info = PREFERRED_STOCK_COMPANIES[company_name]
    
    if stock_type == 'preferred':
        ticker = company_info['preferred']
        dividend_data = company_info['dividend_data']
        print(f"📊 {company_name} 우선주 배당금 데이터 수집 중...")
    else:  # common
        ticker = company_info['common']
        dividend_data = None  # 보통주는 외부 데이터 없이 yfinance만 사용
        print(f"📈 {company_name} 보통주 배당금 데이터 수집 중...")
    
    # 외부 배당금 데이터 처리 (우선주만)
    external_dividends = pd.Series(dtype=float)
    if stock_type == 'preferred' and dividend_data is not None:
        try:
            external_dividends = pd.Series({
                pd.to_datetime(item["Ex-dividend Date"], format='%m월 %d, %Y'): item["Dividend"]
                for item in dividend_data
            }).sort_index()
            print(f"✓ {company_name} {stock_type} 외부 배당금 데이터: {len(external_dividends)}개 항목")
        except Exception as e:
            print(f"❌ {company_name} {stock_type} 외부 배당금 데이터 파싱 실패: {e}")
    
    # yfinance에서 배당금 데이터 가져오기
    yfinance_dividends = get_yfinance_dividend_data(ticker, start_date, end_date)
    
    # 두 데이터 병합
    merged_dividends = merge_dividend_data(external_dividends, yfinance_dividends)
    
    if not merged_dividends.empty:
        print(f"✅ {company_name} {stock_type} 최종 배당금 데이터: {len(merged_dividends)}개 항목")
        return merged_dividends
    else:
        print(f"○ {company_name} {stock_type} 배당금 데이터 없음")
        return pd.Series(dtype=float)

def compare_dividend_yields(company_name, analysis_date=None):
    """
    특정 회사의 보통주와 우선주 배당률을 비교합니다.
    
    Args:
        company_name (str): 회사명
        analysis_date (str, optional): 분석 기준일 (YYYY-MM-DD, 기본값: 오늘)
        
    Returns:
        dict: 배당률 비교 결과
    """
    if company_name not in PREFERRED_STOCK_COMPANIES:
        return None
    
    if analysis_date is None:
        analysis_date = datetime.now().strftime('%Y-%m-%d')
    
    company_info = PREFERRED_STOCK_COMPANIES[company_name]
    common_ticker = company_info['common']
    preferred_ticker = company_info['preferred']
    
    print(f"\n🔍 {company_name} 배당률 비교 분석 ({analysis_date})")
    print("=" * 60)
    
    try:
        # 현재 주가 정보 가져오기
        common_stock = yf.Ticker(common_ticker)
        preferred_stock = yf.Ticker(preferred_ticker)
        
        # 최근 가격 정보
        common_info = common_stock.info
        preferred_info = preferred_stock.info
        
        common_price = common_info.get('regularMarketPrice', 0)
        preferred_price = preferred_info.get('regularMarketPrice', 0)
        
        if common_price == 0 or preferred_price == 0:
            # 가격 정보가 없으면 최근 거래일 데이터 사용
            common_hist = common_stock.history(period='5d')
            preferred_hist = preferred_stock.history(period='5d')
            
            if not common_hist.empty:
                common_price = common_hist['Close'].iloc[-1]
            if not preferred_hist.empty:
                preferred_price = preferred_hist['Close'].iloc[-1]
        
        print(f"📈 {company_name} 보통주 ({common_ticker}): {common_price:,.0f}원")
        print(f"📊 {company_name} 우선주 ({preferred_ticker}): {preferred_price:,.0f}원")
        
        # 배당금 데이터 수집 (최근 2년)
        start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        common_dividends = get_company_dividend_data(company_name, start_date, end_date, 'common')
        preferred_dividends = get_company_dividend_data(company_name, start_date, end_date, 'preferred')
        
        # 최근 1년 배당금 계산
        one_year_ago = datetime.now() - timedelta(days=365)
        
        common_recent_dividends = common_dividends[common_dividends.index >= one_year_ago] if not common_dividends.empty else pd.Series(dtype=float)
        preferred_recent_dividends = preferred_dividends[preferred_dividends.index >= one_year_ago] if not preferred_dividends.empty else pd.Series(dtype=float)
        
        # 연간 배당금 계산
        common_annual_dividend = common_recent_dividends.sum() if not common_recent_dividends.empty else 0
        preferred_annual_dividend = preferred_recent_dividends.sum() if not preferred_recent_dividends.empty else 0
        
        # 배당률 계산
        common_yield = (common_annual_dividend / common_price * 100) if common_price > 0 else 0
        preferred_yield = (preferred_annual_dividend / preferred_price * 100) if preferred_price > 0 else 0
        
        # 배당금 비율 계산
        dividend_ratio = (preferred_annual_dividend / common_annual_dividend) if common_annual_dividend > 0 else 0
        
        result = {
            'company_name': company_name,
            'analysis_date': analysis_date,
            'common_stock': {
                'ticker': common_ticker,
                'price': common_price,
                'annual_dividend': common_annual_dividend,
                'dividend_yield': common_yield,
                'dividend_count': len(common_recent_dividends)
            },
            'preferred_stock': {
                'ticker': preferred_ticker,
                'price': preferred_price,
                'annual_dividend': preferred_annual_dividend,
                'dividend_yield': preferred_yield,
                'dividend_count': len(preferred_recent_dividends)
            },
            'comparison': {
                'price_difference': common_price - preferred_price,
                'price_diff_ratio': ((common_price - preferred_price) / preferred_price * 100) if preferred_price > 0 else 0,
                'dividend_difference': preferred_annual_dividend - common_annual_dividend,
                'dividend_ratio_preferred_to_common': dividend_ratio,
                'yield_difference': preferred_yield - common_yield
            }
        }
        
        # 결과 출력
        print(f"\n📊 배당금 및 배당률 비교:")
        print(f"├─ 보통주 연간배당금: {common_annual_dividend:,.0f}원 (배당률: {common_yield:.3f}%)")
        print(f"├─ 우선주 연간배당금: {preferred_annual_dividend:,.0f}원 (배당률: {preferred_yield:.3f}%)")
        print(f"├─ 배당금 차이: {result['comparison']['dividend_difference']:+,.0f}원")
        print(f"├─ 우선주/보통주 배당금 비율: {dividend_ratio:.2f}배")
        print(f"└─ 배당률 차이: {result['comparison']['yield_difference']:+.3f}%p")
        
        if dividend_ratio > 1:
            print(f"✅ 우선주가 보통주보다 {dividend_ratio:.2f}배 많은 배당금 지급")
        elif dividend_ratio < 1 and dividend_ratio > 0:
            print(f"⚠️ 우선주가 보통주보다 {1/dividend_ratio:.2f}배 적은 배당금 지급")
        elif common_annual_dividend == 0 and preferred_annual_dividend > 0:
            print(f"✅ 우선주만 배당금 지급 (보통주는 무배당)")
        elif preferred_annual_dividend == 0 and common_annual_dividend > 0:
            print(f"⚠️ 보통주만 배당금 지급 (우선주는 무배당)")
        else:
            print(f"○ 두 주식 모두 무배당 또는 데이터 없음")
        
        return result
        
    except Exception as e:
        print(f"❌ {company_name} 배당률 비교 분석 실패: {e}")
        return None

def print_available_companies():
    """
    분석 가능한 회사들의 목록을 출력합니다.
    """
    print("📊 분석 가능한 우선주 보유 회사들:")
    print("=" * 60)
    
    companies_by_sector = {}
    for name, info in PREFERRED_STOCK_COMPANIES.items():
        sector = info['sector']
        if sector not in companies_by_sector:
            companies_by_sector[sector] = []
        companies_by_sector[sector].append((name, info))
    
    for sector, companies in companies_by_sector.items():
        print(f"\n🏭 {sector}:")
        for name, info in companies:
            common_ticker = info['common']
            preferred_ticker = info['preferred']
            has_dividend_data = "✓" if info['dividend_data'] is not None else "○"
            print(f"  {has_dividend_data} {name}: {common_ticker} / {preferred_ticker}")
    
    print(f"\n📈 총 {len(PREFERRED_STOCK_COMPANIES)}개 회사 분석 가능")
    print("✓: 배당금 데이터 보유, ○: yfinance 자동 수집")

def load_existing_data(json_file_path):
    """
    기존 JSON 파일에서 데이터를 로드합니다.
    
    Args:
        json_file_path (str): 기존 JSON 파일 경로
        
    Returns:
        tuple: (DataFrame, 마지막 날짜) 또는 (None, None)
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            return None, None
            
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index = pd.to_datetime(df.index, format='%y-%m-%d')
        df = df.sort_index()
        
        last_date = df.index[-1]
        print(f"✓ 기존 데이터 로드 완료: {df.index[0].strftime('%Y-%m-%d')} ~ {last_date.strftime('%Y-%m-%d')} ({len(df)}일)")
        
        return df, last_date
        
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"기존 데이터 파일을 찾을 수 없거나 로드할 수 없습니다: {e}")
        return None, None

def get_stock_data_with_diff_and_dividends(ticker1, ticker2, start_date, end_date, external_dividends=None, existing_df=None):
    """
    두 주식의 일별 종가 차이, 비율, 배당금 및 배당 수익률을 계산하여 DataFrame으로 반환합니다.
    외부 배당금 데이터를 사용하여 배당금 정보를 통합할 수 있습니다.
    또한, Price_Diff_Ratio의 해당 날짜까지의 25% 및 75% 사분위수 값을 계산하여 추가합니다.
    
    기존 데이터가 있는 경우 증분 업데이트를 수행합니다.

    Args:
        ticker1 (str): 첫 번째 주식의 티커 심볼 (예: '005930.KS' for 삼성전자)
        ticker2 (str): 두 번째 주식의 티커 심볼 (예: '005935.KS' for 삼성전자(우))
        start_date (str): 데이터 시작 날짜 (YYYY-MM-DD 형식)
        end_date (str): 데이터 종료 날짜 (YYYY-MM-DD 형식)
        external_dividends (pd.Series, optional): 외부에서 제공된 배당금 데이터 (인덱스는 날짜, 값은 배당금).
                                                  기본값은 None.
        existing_df (pd.DataFrame, optional): 기존 데이터프레임 (증분 업데이트용)

    Returns:
        pandas.DataFrame: 날짜, 종가 차이, 비율, 배당금, 배당 수익률, Price_Diff_Ratio 사분위수를 포함하는 DataFrame
    """
    try:
        # 기존 데이터가 있는 경우 증분 업데이트 처리
        if existing_df is not None and not existing_df.empty:
            print("🔄 증분 업데이트 모드: 기존 데이터 활용")
            
            # 기존 데이터의 마지막 날짜 이후부터 새 데이터 다운로드
            last_date = existing_df.index[-1]
            next_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # 새 데이터가 필요한지 확인
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
            if last_date.date() >= end_date_dt.date():
                print(f"✓ 기존 데이터가 최신입니다. 마지막 날짜: {last_date.strftime('%Y-%m-%d')}")
                return existing_df
            
            print(f"📅 새 데이터 다운로드: {next_date} ~ {end_date}")
            
            # 새 데이터만 다운로드
            new_data1 = yf.download(ticker1, start=next_date, end=end_date)
            new_data2 = yf.download(ticker2, start=next_date, end=end_date)
            
            if new_data1.empty and new_data2.empty:
                print("✓ 다운로드할 새 데이터가 없습니다.")
                return existing_df
                
        else:
            print("🆕 전체 데이터 다운로드 모드")
            # 전체 데이터 다운로드
            new_data1 = yf.download(ticker1, start=start_date, end=end_date)
            new_data2 = yf.download(ticker2, start=start_date, end=end_date)
        
        # 주식 데이터 다운로드
        data1 = yf.download(ticker1, start=start_date, end=end_date)
        data2 = yf.download(ticker2, start=start_date, end=end_date)

        # 증분 업데이트의 경우 새 데이터만 처리
        if existing_df is not None and not existing_df.empty:
            # 새 데이터 처리
            data1 = new_data1
            data2 = new_data2
        
        if data1.empty or data2.empty:
            if existing_df is not None and not existing_df.empty:
                print("새 데이터가 없으므로 기존 데이터를 반환합니다.")
                return existing_df
            else:
                print("Debug: One or both dataframes are empty after download.")
                return pd.DataFrame()

        # 종가(Close) 및 시가(Open) 데이터 추출 및 컬럼 이름 단순화
        close_prices1 = data1['Close']
        close_prices2 = data2['Close']
        open_prices1 = data1['Open']
        open_prices2 = data2['Open']

        # MultiIndex인 경우, 첫 번째 레벨의 'Close' 또는 'Open'을 선택
        if isinstance(close_prices1.columns, pd.MultiIndex):
            close_prices1 = close_prices1.xs('Close', level=0, axis=1)
            open_prices1 = open_prices1.xs('Open', level=0, axis=1)
        if isinstance(close_prices2.columns, pd.MultiIndex):
            close_prices2 = close_prices2.xs('Close', level=0, axis=1)
            open_prices2 = open_prices2.xs('Open', level=0, axis=1)

        # Series로 변환 (만약 DataFrame으로 남아있다면)
        if isinstance(close_prices1, pd.DataFrame):
            close_prices1 = close_prices1.iloc[:, 0]
            open_prices1 = open_prices1.iloc[:, 0]
        if isinstance(close_prices2, pd.DataFrame):
            close_prices2 = close_prices2.iloc[:, 0]
            open_prices2 = open_prices2.iloc[:, 0]

        # 배당금 데이터 처리
        if external_dividends is not None:
            # 외부 배당금 데이터를 사용
            if existing_df is not None and not existing_df.empty:
                # 새 데이터 기간에 해당하는 배당금만 필터링
                dividends_to_use = external_dividends[external_dividends.index.isin(data2.index)]
            else:
                dividends_to_use = external_dividends
        else:
            # yfinance에서 배당금 컬럼이 있다면 사용, 없으면 0으로 채움
            if 'Dividends' in data2.columns:
                dividends_to_use = data2['Dividends']
                if isinstance(dividends_to_use.columns, pd.MultiIndex):
                    dividends_to_use = dividends_to_use.xs('Dividends', level=0, axis=1)
                if isinstance(dividends_to_use, pd.DataFrame):
                    dividends_to_use = dividends_to_use.iloc[:, 0]
            else:
                dividends_to_use = pd.Series(0, index=data2.index, name='Dividends')
        
        # 모든 데이터를 날짜 기준으로 합치기
        new_combined_df = pd.concat([
            close_prices1.rename('Stock1_Close'),
            close_prices2.rename('Stock2_Close'),
            open_prices1.rename('Stock1_Open'),
            open_prices2.rename('Stock2_Open'),
            dividends_to_use.rename('Dividend_Amount_Raw') # 원본 배당금
        ], axis=1)

        new_combined_df = new_combined_df.dropna(subset=['Stock1_Close', 'Stock2_Close', 'Stock1_Open', 'Stock2_Open']) # 종가 및 시가 데이터가 있는 날짜만 사용
        
        new_combined_df['Dividend_Amount_Raw'] = new_combined_df['Dividend_Amount_Raw'].fillna(0)
        new_combined_df['Dividend_Amount'] = new_combined_df['Dividend_Amount_Raw'].replace(0, pd.NA).ffill().fillna(0)

        if new_combined_df.empty:
            if existing_df is not None and not existing_df.empty:
                print("새 데이터가 비어있으므로 기존 데이터를 반환합니다.")
                return existing_df
            else:
                print("Debug: new_combined_df is empty after dropna.")
                return pd.DataFrame()

        # 기존 데이터와 병합
        if existing_df is not None and not existing_df.empty:
            # 기존 데이터와 새 데이터 결합
            combined_df = pd.concat([existing_df, new_combined_df])
            combined_df = combined_df[~combined_df.index.duplicated(keep='last')]  # 중복 제거 (최신 데이터 유지)
            combined_df = combined_df.sort_index()
            print(f"✓ 데이터 병합 완료: 기존 {len(existing_df)}일 + 새로운 {len(new_combined_df)}일 = 총 {len(combined_df)}일")
        else:
            combined_df = new_combined_df

        # 가격 차이 계산 (새로 추가된 부분만 또는 전체)
        if existing_df is not None and not existing_df.empty:
            # 새로 추가된 행에 대해서만 계산
            new_rows_mask = ~combined_df.index.isin(existing_df.index)
            if new_rows_mask.any():
                combined_df.loc[new_rows_mask, 'Price_Difference'] = (
                    combined_df.loc[new_rows_mask, 'Stock1_Close'] - 
                    combined_df.loc[new_rows_mask, 'Stock2_Close']
                )
                combined_df.loc[new_rows_mask, 'Price_Diff_Ratio'] = combined_df.loc[new_rows_mask].apply(
                    lambda row: (row['Price_Difference'] * 100 / row['Stock2_Close']) if row['Stock2_Close'] != 0 else 0,
                    axis=1
                )
                combined_df.loc[new_rows_mask, 'Dividend_Yield_on_Preferred'] = combined_df.loc[new_rows_mask].apply(
                    lambda row: (row['Dividend_Amount'] * 100 / row['Stock2_Close']) if row['Stock2_Close'] != 0 else 0,
                    axis=1
                )
        else:
            # 전체 계산
            combined_df['Price_Difference'] = combined_df['Stock1_Close'] - combined_df['Stock2_Close']
            combined_df['Price_Diff_Ratio'] = combined_df.apply(
                lambda row: (row['Price_Difference'] * 100 / row['Stock2_Close']) if row['Stock2_Close'] != 0 else 0,
                axis=1
            )
            combined_df['Dividend_Yield_on_Preferred'] = combined_df.apply(
                lambda row: (row['Dividend_Amount'] * 100 / row['Stock2_Close']) if row['Stock2_Close'] != 0 else 0,
                axis=1
            )

        # 해당 날짜 이전 2년, 3년, 5년 데이터를 기준으로 한 Price_Diff_Ratio 25% 및 75% 사분위수 계산
        # 2년 = 약 730일, 3년 = 약 1095일, 5년 = 약 1825일 (365일 * 년수 + 윤년 고려)
        window_configs = {
            '2year': 730,
            '3year': 1095,
            '5year': 1825
        }
        
        def calculate_rolling_quantile_optimized(series, window_size, quantile, existing_df=None):
            """슬라이딩 윈도우로 분위수 계산 (최적화된 버전)"""
            if existing_df is not None and not existing_df.empty:
                # 증분 업데이트: 기존 계산된 값들을 활용
                existing_col_25 = f'Price_Diff_Ratio_25th_Percentile_{list(window_configs.keys())[0] if quantile == 0.25 else ""}'
                existing_col_75 = f'Price_Diff_Ratio_75th_Percentile_{list(window_configs.keys())[0] if quantile == 0.75 else ""}'
                
                # 새로 계산해야 할 인덱스 찾기
                new_indices = series.index[~series.index.isin(existing_df.index)]
                
                if len(new_indices) == 0:
                    # 새 데이터가 없으면 기존 값 반환
                    return existing_df[existing_col_25 if quantile == 0.25 else existing_col_75].tolist()
                
                # 기존 결과를 리스트로 변환
                result = existing_df[existing_col_25 if quantile == 0.25 else existing_col_75].tolist()
                
                # 새 데이터에 대해서만 계산
                series_array = series.values
                start_idx = len(existing_df)
                
                for i in range(start_idx, len(series)):
                    if i < window_size:
                        window_data = series_array[:i+1]
                    else:
                        window_data = series_array[i-window_size+1:i+1]
                    
                    if len(window_data) > 0:
                        result.append(pd.Series(window_data).quantile(quantile))
                    else:
                        result.append(0)
                
                return result
            else:
                # 전체 계산
                result = []
                series_array = series.values
                for i in range(len(series)):
                    if i < window_size:
                        window_data = series_array[:i+1]
                    else:
                        window_data = series_array[i-window_size+1:i+1]
                    
                    if len(window_data) > 0:
                        result.append(pd.Series(window_data).quantile(quantile))
                    else:
                        result.append(0)
                return result
        
        # 2년, 3년, 5년 각각에 대해 분위수 계산
        for window_name, window_days in window_configs.items():
            if existing_df is not None and not existing_df.empty:
                print(f"🔄 {window_name} 슬라이딩 윈도우 분위수 증분 계산 중...")
            else:
                print(f"🆕 {window_name} 슬라이딩 윈도우로 25% 및 75% 분위수 계산 중...")
                
            combined_df[f'Price_Diff_Ratio_25th_Percentile_{window_name}'] = calculate_rolling_quantile_optimized(
                combined_df['Price_Diff_Ratio'], window_days, 0.25, existing_df
            )
            combined_df[f'Price_Diff_Ratio_75th_Percentile_{window_name}'] = calculate_rolling_quantile_optimized(
                combined_df['Price_Diff_Ratio'], window_days, 0.75, existing_df
            )
        
        # 기존 컬럼명 유지를 위해 2년 데이터를 기본으로 설정
        combined_df['Price_Diff_Ratio_25th_Percentile'] = combined_df['Price_Diff_Ratio_25th_Percentile_2year']
        combined_df['Price_Diff_Ratio_75th_Percentile'] = combined_df['Price_Diff_Ratio_75th_Percentile_2year']


        # 필요한 컬럼만 선택
        result_df = combined_df[[
            'Price_Difference',
            'Price_Diff_Ratio',
            'Dividend_Amount',
            'Dividend_Yield_on_Preferred',
            'Stock1_Close',
            'Stock2_Close',
            'Stock1_Open',
            'Stock2_Open',
            'Price_Diff_Ratio_25th_Percentile',
            'Price_Diff_Ratio_75th_Percentile',
            'Price_Diff_Ratio_25th_Percentile_2year',
            'Price_Diff_Ratio_75th_Percentile_2year',
            'Price_Diff_Ratio_25th_Percentile_3year',
            'Price_Diff_Ratio_75th_Percentile_3year',
            'Price_Diff_Ratio_25th_Percentile_5year',
            'Price_Diff_Ratio_75th_Percentile_5year',
            'Dividend_Amount_Raw' # 추가
        ]]
        result_df.index.name = 'Date'
        return result_df

    except Exception as e:
        print(f"데이터를 가져오거나 처리하는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

def generate_stock_data_for_periods(company_name='삼성전자'):
    """
    다양한 기간(3년, 5년, 10년, 20년, 30년)에 대한 주식 데이터를 생성합니다.
    기존 데이터가 있는 경우 증분 업데이트를 수행합니다.
    
    Args:
        company_name (str): 분석할 회사명 (기본값: '삼성전자')
    """
    # 회사 정보 확인
    if company_name not in PREFERRED_STOCK_COMPANIES:
        print(f"❌ '{company_name}'는 지원되지 않는 회사입니다.")
        print_available_companies()
        return {}
    
    company_info = PREFERRED_STOCK_COMPANIES[company_name]
    common_ticker = company_info['common']
    preferred_ticker = company_info['preferred']
    
    print(f"🏢 분석 대상: {company_name}")
    print(f"📈 보통주: {common_ticker}")
    print(f"📊 우선주: {preferred_ticker}")
    print(f"🏭 업종: {company_info['sector']}")
    
    # 다양한 기간 설정 (3년, 5년, 10년, 20년, 30년)
    today = datetime.now()
    periods = {
        '3년': 3*365,
        '5년': 5*365,
        '10년': 10*365,
        '20년': 20*365,
        '30년': 30*365
    }
    
    # 전체 기간에 대한 배당금 데이터 준비 (가장 긴 기간인 30년 기준)
    max_days = max(periods.values())
    dividend_start_date = (today - timedelta(days=max_days)).strftime('%Y-%m-%d')
    dividend_end_date = today.strftime('%Y-%m-%d')
    
    external_dividends_series = get_company_dividend_data(company_name, dividend_start_date, dividend_end_date)
    if not external_dividends_series.empty:
        print(f"✅ 배당금 데이터 수집 완료: {len(external_dividends_series)}개 항목")
        # 수집된 배당금 데이터를 JSON 파일로 자동 저장
        save_updated_dividend_data(company_name, external_dividends_series)
    else:
        print("○ 배당금 데이터 없음 - 기본값 0으로 처리")
    
    results = {}
    
    for period_name, days in periods.items():
        print(f"\n{'='*80}")
        print(f"=== {company_name} {period_name} 데이터 처리 중 ===")
        print(f"{'='*80}")
        
        start_date = (today - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        # 회사별 파일명 설정
        safe_company_name = company_name.replace('/', '_').replace('\\', '_')
        output_json_path = f'./{safe_company_name}_stock_analysis_{period_name}.json'
        
        print(f"📅 대상 기간: {start_date} ~ {end_date}")
        
        # 기존 데이터 로드 시도
        existing_df, last_date = load_existing_data(output_json_path)
        
        if existing_df is not None:
            print(f"📊 기존 데이터 활용: {len(existing_df)}일의 데이터")
        else:
            print("🆕 새로운 데이터 생성")
        
        price_data_df = get_stock_data_with_diff_and_dividends(
            common_ticker, 
            preferred_ticker, 
            start_date, 
            end_date, 
            external_dividends=external_dividends_series if not external_dividends_series.empty else None,
            existing_df=existing_df
        )
        
        if not price_data_df.empty:
            # 날짜 형식을 YY-mm-dd로 변경
            price_data_df.index = price_data_df.index.strftime('%y-%m-%d')
            
            # 결과를 JSON 파일로 저장
            price_data_df.to_json(output_json_path, orient='index', indent=4)
            
            if existing_df is not None:
                new_days = len(price_data_df) - len(existing_df) if len(price_data_df) > len(existing_df) else 0
                print(f"💾 업데이트 완료: {output_json_path} ({new_days}일 추가, 총 {len(price_data_df)}일)")
            else:
                print(f"💾 저장 완료: {output_json_path} (총 {len(price_data_df)}일)")
            
            results[period_name] = {
                'data': price_data_df,
                'file_path': output_json_path,
                'start_date': start_date,
                'end_date': end_date,
                'is_updated': existing_df is not None,
                'company': company_name,
                'common_ticker': common_ticker,
                'preferred_ticker': preferred_ticker
            }
        else:
            print(f"❌ {company_name} {period_name} 주식 분석 데이터를 생성할 수 없습니다.")
    
    print(f"\n{'='*80}")
    print(f"=== {company_name} 데이터 처리 요약 ===")
    print(f"{'='*80}")
    
    updated_count = sum(1 for r in results.values() if r.get('is_updated', False))
    new_count = len(results) - updated_count
    
    print(f"📊 처리 완료: 총 {len(results)}개 기간")
    print(f"🔄 업데이트: {updated_count}개 기간")
    print(f"🆕 신규 생성: {new_count}개 기간")
    
    return results

def compare_all_companies_dividend_yields():
    """
    모든 회사의 보통주와 우선주 배당률을 비교하고 종합 리포트를 생성합니다.
    
    Returns:
        dict: 모든 회사의 배당률 비교 결과
    """
    print("🔍 전체 회사 배당률 비교 분석 시작")
    print("=" * 80)
    
    all_results = {}
    
    for company_name in PREFERRED_STOCK_COMPANIES.keys():
        try:
            result = compare_dividend_yields(company_name)
            if result:
                all_results[company_name] = result
        except Exception as e:
            print(f"❌ {company_name} 분석 실패: {e}")
    
    if not all_results:
        print("❌ 분석 가능한 회사가 없습니다.")
        return {}
    
    # 종합 리포트 생성
    print(f"\n{'='*80}")
    print("📊 전체 회사 배당률 비교 종합 리포트")
    print(f"{'='*80}")
    
    # 배당률 순위 (우선주 기준)
    sorted_by_preferred_yield = sorted(
        all_results.items(), 
        key=lambda x: x[1]['preferred_stock']['dividend_yield'], 
        reverse=True
    )
    
    print(f"\n🏆 우선주 배당률 순위:")
    for i, (company, data) in enumerate(sorted_by_preferred_yield, 1):
        preferred_yield = data['preferred_stock']['dividend_yield']
        common_yield = data['common_stock']['dividend_yield']
        dividend_ratio = data['comparison']['dividend_ratio_preferred_to_common']
        
        print(f"  {i:2d}. {company:8s}: {preferred_yield:6.3f}% (보통주: {common_yield:6.3f}%, 비율: {dividend_ratio:5.2f}배)")
    
    # 배당금 비율 순위 (우선주/보통주)
    sorted_by_dividend_ratio = sorted(
        all_results.items(), 
        key=lambda x: x[1]['comparison']['dividend_ratio_preferred_to_common'], 
        reverse=True
    )
    
    print(f"\n💰 우선주/보통주 배당금 비율 순위:")
    for i, (company, data) in enumerate(sorted_by_dividend_ratio, 1):
        dividend_ratio = data['comparison']['dividend_ratio_preferred_to_common']
        preferred_dividend = data['preferred_stock']['annual_dividend']
        common_dividend = data['common_stock']['annual_dividend']
        
        print(f"  {i:2d}. {company:8s}: {dividend_ratio:5.2f}배 (우선주: {preferred_dividend:,.0f}원, 보통주: {common_dividend:,.0f}원)")
    
    # 마크다운 리포트 생성
    generate_dividend_comparison_report(all_results)
    
    return all_results

def generate_dividend_comparison_report(all_results):
    """
    배당률 비교 결과를 마크다운 리포트로 생성합니다.
    
    Args:
        all_results (dict): 모든 회사의 배당률 비교 결과
    """
    try:
        report_file = './dividend_yield_comparison_report.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 📊 우선주 vs 보통주 배당률 비교 리포트\n\n")
            f.write(f"**생성일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**분석 대상:** {len(all_results)}개 회사\n")
            f.write(f"**분석 기준:** 최근 1년 배당금 기준\n\n")
            
            f.write("---\n\n")
            
            # Executive Summary
            f.write("## 🎯 Executive Summary\n\n")
            
            # 평균 배당률 계산
            avg_preferred_yield = sum(data['preferred_stock']['dividend_yield'] for data in all_results.values()) / len(all_results)
            avg_common_yield = sum(data['common_stock']['dividend_yield'] for data in all_results.values()) / len(all_results)
            avg_dividend_ratio = sum(data['comparison']['dividend_ratio_preferred_to_common'] for data in all_results.values()) / len(all_results)
            
            f.write(f"- **평균 우선주 배당률:** {avg_preferred_yield:.3f}%\n")
            f.write(f"- **평균 보통주 배당률:** {avg_common_yield:.3f}%\n")
            f.write(f"- **평균 배당금 비율 (우선주/보통주):** {avg_dividend_ratio:.2f}배\n\n")
            
            # 상세 분석 표
            f.write("## 📈 회사별 상세 분석\n\n")
            f.write("| 회사명 | 보통주 배당률 | 우선주 배당률 | 배당률 차이 | 배당금 비율 | 우선주 우위성 |\n")
            f.write("|--------|---------------|---------------|-------------|-------------|---------------|\n")
            
            for company_name, data in all_results.items():
                common_yield = data['common_stock']['dividend_yield']
                preferred_yield = data['preferred_stock']['dividend_yield']
                yield_diff = data['comparison']['yield_difference']
                dividend_ratio = data['comparison']['dividend_ratio_preferred_to_common']
                
                # 우선주 우위성 판단
                if dividend_ratio > 1.5:
                    advantage = "🟢 매우 유리"
                elif dividend_ratio > 1.0:
                    advantage = "🟡 유리"
                elif dividend_ratio > 0.8:
                    advantage = "🟠 비슷"
                else:
                    advantage = "🔴 불리"
                
                f.write(f"| {company_name} | {common_yield:.3f}% | {preferred_yield:.3f}% | {yield_diff:+.3f}%p | {dividend_ratio:.2f}배 | {advantage} |\n")
            
            # 순위 섹션
            f.write("\n## 🏆 순위 분석\n\n")
            
            # 우선주 배당률 순위
            sorted_by_preferred = sorted(all_results.items(), key=lambda x: x[1]['preferred_stock']['dividend_yield'], reverse=True)
            f.write("### 📊 우선주 배당률 순위\n\n")
            for i, (company, data) in enumerate(sorted_by_preferred, 1):
                yield_val = data['preferred_stock']['dividend_yield']
                f.write(f"{i}. **{company}**: {yield_val:.3f}%\n")
            
            # 배당금 비율 순위
            sorted_by_ratio = sorted(all_results.items(), key=lambda x: x[1]['comparison']['dividend_ratio_preferred_to_common'], reverse=True)
            f.write("\n### 💰 배당금 비율 순위 (우선주/보통주)\n\n")
            for i, (company, data) in enumerate(sorted_by_ratio, 1):
                ratio = data['comparison']['dividend_ratio_preferred_to_common']
                f.write(f"{i}. **{company}**: {ratio:.2f}배\n")
            
            # 인사이트 섹션
            f.write("\n## 💡 주요 인사이트\n\n")
            
            # 최고/최저 찾기
            highest_preferred_yield = max(all_results.items(), key=lambda x: x[1]['preferred_stock']['dividend_yield'])
            highest_ratio = max(all_results.items(), key=lambda x: x[1]['comparison']['dividend_ratio_preferred_to_common'])
            lowest_ratio = min(all_results.items(), key=lambda x: x[1]['comparison']['dividend_ratio_preferred_to_common'])
            
            f.write(f"**1. 배당률 리더:**\n")
            f.write(f"- **{highest_preferred_yield[0]}**가 가장 높은 우선주 배당률 ({highest_preferred_yield[1]['preferred_stock']['dividend_yield']:.3f}%)을 기록\n\n")
            
            f.write(f"**2. 배당금 비율 분석:**\n")
            f.write(f"- **{highest_ratio[0]}**가 가장 높은 배당금 비율 ({highest_ratio[1]['comparison']['dividend_ratio_preferred_to_common']:.2f}배)\n")
            f.write(f"- **{lowest_ratio[0]}**가 가장 낮은 배당금 비율 ({lowest_ratio[1]['comparison']['dividend_ratio_preferred_to_common']:.2f}배)\n\n")
            
            f.write(f"**3. 투자 시사점:**\n")
            
            # 배당금 비율이 1보다 큰 회사들
            high_ratio_companies = [name for name, data in all_results.items() if data['comparison']['dividend_ratio_preferred_to_common'] > 1]
            
            if high_ratio_companies:
                f.write(f"- **우선주 배당 우위 기업:** {', '.join(high_ratio_companies)}\n")
                f.write(f"- 이들 기업의 우선주는 보통주 대비 배당금 혜택이 있음\n")
            
            # 배당률이 높은 회사들
            high_yield_companies = [name for name, data in all_results.items() if data['preferred_stock']['dividend_yield'] > avg_preferred_yield]
            
            if high_yield_companies:
                f.write(f"- **고배당 기업:** {', '.join(high_yield_companies)}\n")
                f.write(f"- 평균 이상의 배당률을 제공하는 기업들\n")
            
            f.write("\n---\n\n")
            f.write("**📝 분석 방법론:**\n")
            f.write("- 최근 1년간의 배당금을 기준으로 연간 배당률 계산\n")
            f.write("- 배당률 = (연간 배당금 / 현재 주가) × 100\n")
            f.write("- 배당금 비율 = 우선주 연간 배당금 / 보통주 연간 배당금\n\n")
            f.write("**⚠️ 주의사항:**\n")
            f.write("- 과거 배당 실적 기준이며 미래 배당을 보장하지 않음\n")
            f.write("- 투자 결정 시 배당 외 기업 가치도 함께 고려 필요\n")
            
        print(f"📋 배당률 비교 리포트 생성: {report_file}")
        
    except Exception as e:
        print(f"❌ 배당률 비교 리포트 생성 실패: {e}")

def save_updated_dividend_data(company_name, dividend_series):
    """
    업데이트된 배당금 데이터를 JSON 파일로 저장합니다.
    
    Args:
        company_name (str): 회사명
        dividend_series (pd.Series): 배당금 데이터
    """
    if dividend_series.empty:
        return
    
    try:
        safe_company_name = company_name.replace('/', '_').replace('\\', '_')
        dividend_file_path = f'./{safe_company_name}_dividend_data.json'
        
        # 배당금 데이터를 JSON 형태로 변환
        dividend_dict = {
            date.strftime('%Y-%m-%d'): float(amount) 
            for date, amount in dividend_series.items()
        }
        
        with open(dividend_file_path, 'w', encoding='utf-8') as f:
            json.dump(dividend_dict, f, indent=4, ensure_ascii=False)
        
        print(f"💾 {company_name} 배당금 데이터 저장: {dividend_file_path}")
        
    except Exception as e:
        print(f"❌ {company_name} 배당금 데이터 저장 실패: {e}")

def generate_dividend_summary_report(all_results):
    """
    모든 회사의 배당금 데이터 요약 리포트를 생성합니다.
    
    Args:
        all_results (dict): 전체 회사 분석 결과
    """
    try:
        summary_file = './dividend_summary_report.md'
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# 📊 우선주 배당금 데이터 요약 리포트\n\n")
            f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 📈 회사별 배당금 데이터 현황\n\n")
            f.write("| 회사명 | 업종 | 우선주 티커 | 배당금 데이터 | 최근 배당금 | 배당 횟수 |\n")
            f.write("|--------|------|-------------|---------------|-------------|----------|\n")
            
            for company_name in PREFERRED_STOCK_COMPANIES.keys():
                company_info = PREFERRED_STOCK_COMPANIES[company_name]
                sector = company_info['sector']
                preferred_ticker = company_info['preferred']
                
                # 배당금 데이터 수집
                dividend_data = get_company_dividend_data(company_name)
                
                if not dividend_data.empty:
                    latest_dividend = dividend_data.iloc[-1]
                    dividend_count = len(dividend_data)
                    latest_date = dividend_data.index[-1].strftime('%Y-%m-%d')
                    status = f"✅ 최신: {latest_date}"
                    
                    # 개별 회사 배당금 데이터 저장
                    save_updated_dividend_data(company_name, dividend_data)
                else:
                    latest_dividend = "N/A"
                    dividend_count = 0
                    status = "❌ 데이터 없음"
                
                f.write(f"| {company_name} | {sector} | {preferred_ticker} | {status} | {latest_dividend} | {dividend_count} |\n")
            
            f.write(f"\n## 📋 분석 대상 기업 수: {len(PREFERRED_STOCK_COMPANIES)}개\n\n")
            f.write("---\n")
            f.write("*이 리포트는 yfinance API를 통해 자동 생성되었습니다.*\n")
        
        print(f"📋 배당금 요약 리포트 생성: {summary_file}")
        
    except Exception as e:
        print(f"❌ 배당금 요약 리포트 생성 실패: {e}")

def generate_data_for_all_companies():
    """
    모든 우선주 보유 회사들에 대해 데이터를 생성합니다.
    배당금 데이터도 함께 수집하고 저장합니다.
    """
    print("🚀 모든 회사 데이터 생성 시작")
    print("="*80)
    
    all_results = {}
    
    for company_name in PREFERRED_STOCK_COMPANIES.keys():
        try:
            print(f"\n🏢 {company_name} 처리 시작...")
            results = generate_stock_data_for_periods(company_name)
            all_results[company_name] = results
            print(f"✅ {company_name} 처리 완료")
        except Exception as e:
            print(f"❌ {company_name} 처리 중 오류: {e}")
            all_results[company_name] = {}
    
    print(f"\n{'='*80}")
    print("=== 전체 처리 결과 요약 ===")
    print(f"{'='*80}")
    
    for company_name, results in all_results.items():
        if results:
            print(f"✅ {company_name}: {len(results)}개 기간 처리 완료")
        else:
            print(f"❌ {company_name}: 처리 실패")
    
    print(f"\n📊 총 {len([r for r in all_results.values() if r])}개 회사 성공적으로 처리됨")
    
    # 배당금 요약 리포트 생성
    print(f"\n📋 배당금 데이터 요약 리포트 생성 중...")
    generate_dividend_summary_report(all_results)
    
    return all_results

if __name__ == "__main__":
    import argparse
    
    print("📊 우선주 가격차이 분석 시스템")
    print("=" * 60)
    
    # 사용 가능한 회사들 출력
    print_available_companies()
    
    # argparse 설정
    parser = argparse.ArgumentParser(
        description='우선주 가격차이 분석 시스템',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
사용 예시:
  python stock_diff.py                    # 모든 회사 분석 (기본값)
  python stock_diff.py --company 삼성전자   # 특정 회사만 분석
  python stock_diff.py --company LG화학    # 특정 회사만 분석
  python stock_diff.py --list             # 지원하는 회사 목록만 출력

지원하는 회사들: {', '.join(PREFERRED_STOCK_COMPANIES.keys())}
        """)
    
    parser.add_argument(
        '--company', '-c',
        type=str,
        help='분석할 특정 회사명 (예: 삼성전자, LG화학)'
    )
    
    parser.add_argument(
        '--dividend-compare', '-d',
        action='store_true',
        help='보통주와 우선주 배당률 비교 분석 수행'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='지원하는 회사 목록 출력 후 종료'
    )
    
    args = parser.parse_args()
    
    # --list 옵션 처리
    if args.list:
        print("\n📋 지원하는 회사 목록:")
        print_available_companies()
        exit(0)
    
    # --dividend-compare 옵션 처리
    if args.dividend_compare:
        if args.company:
            # 특정 회사의 배당률 비교
            print(f"\n🎯 {args.company} 배당률 비교 분석...")
            result = compare_dividend_yields(args.company)
            if result:
                print(f"\n✅ {args.company} 배당률 비교 완료!")
            else:
                print(f"❌ {args.company} 배당률 비교 실패!")
        else:
            # 모든 회사의 배당률 비교
            print(f"\n🌐 전체 회사 배당률 비교 분석...")
            results = compare_all_companies_dividend_yields()
            if results:
                print(f"\n✅ 전체 회사 배당률 비교 완료! ({len(results)}개 회사)")
            else:
                print(f"❌ 배당률 비교 분석 실패!")
        exit(0)
    
    # 회사별 분석 처리
    if args.company:
        # 특정 회사 분석
        company_name = args.company
        if company_name in PREFERRED_STOCK_COMPANIES:
            print(f"\n🎯 {company_name} 분석 시작...")
            results = generate_stock_data_for_periods(company_name)
            
            # 삼성전자인 경우 기존 호환성 유지
            if company_name == '삼성전자' and '20년' in results:
                price_data_df = results['20년']['data']
                
                # 기존 파일명으로도 저장
                output_json_path = r'./samsung_stock_analysis.json'
                price_data_df.to_json(output_json_path, orient='index', indent=4)
                print(f"\n기본 주식 분석 데이터가 {output_json_path}에도 저장되었습니다.")

                # Price_Diff_Ratio 히스토그램 및 박스 플롯 저장
                plt.figure(figsize=(12, 6))

                plt.subplot(1, 2, 1)
                sns.histplot(price_data_df['Price_Diff_Ratio'], kde=True)
                plt.title('Price_Diff_Ratio 히스토그램 (삼성전자 20년)')
                plt.xlabel('Price_Diff_Ratio (%)')
                plt.ylabel('빈도')

                plt.subplot(1, 2, 2)
                sns.boxplot(y=price_data_df['Price_Diff_Ratio'])
                plt.title('Price_Diff_Ratio 박스 플롯 (삼성전자 20년)')
                plt.ylabel('Price_Diff_Ratio (%)')

                plt.tight_layout()
                plot_output_path = r'./price_diff_ratio_distribution.png'
                plt.savefig(plot_output_path)
                plt.close()
                print(f"Price_Diff_Ratio 분포 그래프가 {plot_output_path}에 저장되었습니다.")
        else:
            print(f"\n❌ '{company_name}'는 지원되지 않는 회사입니다.")
            print("\n📋 지원하는 회사 목록:")
            print_available_companies()
            exit(1)
    else:
        # 기본값: 모든 회사 분석
        print(f"\n🚀 모든 회사 분석 시작...")
        all_results = generate_data_for_all_companies()
    
    print(f"\n✅ 분석 완료!")
    print(f"📁 생성된 파일들을 확인하세요.")

