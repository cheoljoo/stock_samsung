# stock_samsung
보통주와 우선주의 비교 : 언제 어떤 것을 사야 유리한지?

# How to Run

## Prerequisites
### Install uv (Python package manager)
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: via pip
pip install uv
```

### Install Korean fonts (for chart visualization)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install fonts-nanum fonts-nanum-coding fonts-nanum-extra

# CentOS/RHEL/Fedora
sudo yum install google-noto-sans-cjk-fonts
# or
sudo dnf install google-noto-sans-cjk-fonts

# macOS
brew install font-nanum-gothic font-nanum-myeongjo

# Windows
# Download and install NanumGothic from: https://hangeul.naver.com/2017/nanum
```

## Running the Analysis

### Option 1: Direct Installation
- cd many_company_effective_years_with_window_size
- make
- if you want run in interactive mode ,
  - make interactive

### Option 2: Using Docker (Recommended)
```bash
# Build Docker image with your user permissions
./docker-run.sh build

# Run analysis in specific directory
./docker-run.sh run many_company_effective_years_with_window_size

# Run US preferred stock analysis
./docker-run.sh run many_company_effective_years_with_window_size
# Then inside container: uv run python us_diff.py --analyze

# Execute additional commands in running container
./docker-run.sh exec

# Stop container
./docker-run.sh stop

# Clean up Docker resources
./docker-run.sh clean
```

#### Docker Usage Examples:
```bash
# Korean stock analysis
./docker-run.sh run many_company_effective_years_with_window_size
# Inside container: make interactive

# US preferred stock analysis  
./docker-run.sh run many_company_effective_years_with_window_size
# Inside container: uv run python us_diff.py --analyze

# Run specific company analysis
./docker-run.sh run many_company_effective_years_with_window_size
# Inside container: uv run python stock_diff.py --company "삼성전자"
```

## 분석 결과 해석 가이드

### 📊 **생성되는 주요 파일들**
1. **분석 리포트**: `{회사명}_strategy_analysis_report_{기간}.md`
2. **매매 기록**: `trading_log_{기간}_{전략}_{윈도우}.csv`
3. **성과 그래프**: `strategy_comparison_{기간}.png`
4. **원시 데이터**: `{회사명}_stock_analysis.json`

### 🎯 **회사별 주요 확인 포인트**

#### **1. 수익률 분석**
- **최고 성과 전략**: 어떤 윈도우 크기에서 최고 수익률을 보이는지
- **Buy & Hold 대비**: 차익거래 전략이 단순 보유 대비 얼마나 우수한지
- **기간별 일관성**: 여러 기간에서 일관되게 좋은 성과를 보이는 전략

#### **2. 자산 구성 분석**
```markdown
| 구분 | 주식 가치 | 배당금 (현금) | 총 자산 | 배당금 비율 |
```
- **배당금 기여도**: 총 수익에서 배당금이 차지하는 비중
- **주식 가치 증가**: 순수한 주가 상승에 의한 수익
- **전략별 차이**: 기본전략 vs 반대전략의 자산 구성 차이

#### **3. 매매 빈도 분석**
- **거래 횟수**: 윈도우 크기별 매매 빈도
- **거래 비용 고려**: 실제 투자시 수수료 계산을 위한 참고
- **리밸런싱 부담**: 매매가 너무 잦으면 실행 부담 증가

#### **4. 윈도우 크기별 특성**
- **2년 윈도우**: 빠른 반응, 높은 변동성
- **3년 윈도우**: 균형잡힌 접근
- **5년 윈도우**: 안정적이지만 느린 반응

### 🏆 **투자 결정을 위한 체크리스트**

#### **✅ 추천 조건**
1. **수익률**: Buy & Hold 대비 20% 이상 높은 수익률
2. **일관성**: 여러 기간에서 안정적인 성과
3. **매매 빈도**: 연간 10회 이하의 적당한 거래 빈도
4. **배당 효과**: 배당금이 총 수익에 긍정적 기여

#### **⚠️ 주의 신호**
1. **과도한 매매**: 연간 20회 이상의 잦은 거래
2. **불안정성**: 기간별로 성과가 크게 다름
3. **저조한 성과**: Buy & Hold보다 낮은 수익률
4. **높은 변동성**: 수익률의 기간별 편차가 큰 경우

### 📈 **회사별 특성 분석**

#### **대형주 (삼성전자, LG전자 등)**
- 상대적으로 안정적인 패턴
- 배당금 수익 기여도가 높음
- 장기 윈도우(5년)가 효과적

#### **중형주 (LG화학, 현대자동차 등)**
- 변동성이 높아 차익거래 기회 많음
- 중기 윈도우(3년)가 균형점
- 업종별 특성을 고려한 분석 필요

#### **성장주 vs 배당주**
- **성장주**: 주가 차이에 의한 수익이 주요
- **배당주**: 배당금 수익이 안정적 기여

### 💡 **실전 투자 가이드**

1. **포트폴리오 구성**: 1-2개 우수 전략 선택
2. **자금 규모**: 최소 5천만원 이상 권장 (거래 비용 효율성)
3. **모니터링**: 일일 체크, 신호 발생시 즉시 실행
4. **리스크 관리**: 전체 자산의 20-30% 이내로 제한

# 개발 순서
- old directory : 20년치 backtest
- 250630 directory : 5년치 backtest
- 5years : 5년치 backtest 
- 20years : 20년치 backtest에 여러가지 그래프 추가
- 5years_copied_from_20years : 5년치인데 20years처럼 여러가지 그래프 추가
- reverse/5years_copied_from_20years : 기존 사분위 25%이하이면 삼성전자 구매 -> 삼성전자(우)로 구매로 반대 매수
- reverse/20years : 기존 사분위 25%이하이면 삼성전자 구매 -> 삼성전자(우)로 구매로 반대 매수
- 20years_with_window_size : 사분위를 구할때 위의 것들은 모든 구간에 대해서 계산을 했지만, 구하는 시간의 2,3 5년 Window size를 가지고 계산하도록 수정함.
- years_with_window_size : windows size는 2,3,5년이고,  backtest 기간도 3,5,10,20,30년으로 한다.
- effective_years_with_window_size : report_backup 에 기존 내용들 저장 / effective하게 한번 계산된 사분위나 주식 가격을 다시 처리하지 않음. 파일에 저장했다가 불러옴
- many_company_effective_years_with_window_size : 우선주가 있는 여러개의 회사들에 대해서 처리 , make interactive를 하면 선택해서 수행가능
  - uv run python us_diff.py