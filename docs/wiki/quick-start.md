# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Navigate to Analysis Directory
```powershell
# IMPORTANT: Always work in dividend-in-korea directory
cd d:\code\stock_samsung\dividend-in-korea
```

### Step 2: Install Dependencies (First Time Only)
```powershell
# Install using uv package manager
.\run.ps1 install
```

### Step 3: Run Quick Analysis
```powershell
# Execute Korean dividend analysis
.\run.ps1 quick
```

**Expected Output:**
```
✅ Korean font set: Malgun Gothic
🎯 한국 우수 배당주 간단 분석
==================================================

🏆 5년 이상 연속배당 한국 기업 TOP 19:
====================================================================================================
 순위     회사명     섹터 연속배당년수     현재주가   배당률   연간배당금    시가총액 투자등급    점수
  1   현대자동차    자동차    11년 220,500원 5.90% 13,000원  54.2조원   A+ 100.0
  2    KT&G     담배    11년 137,100원 4.08%  5,600원  14.8조원   A+  94.5
  3  LG유플러스     통신    11년  14,440원 4.50%    650원   6.4조원   A+  92.0
  ...
```

## 📊 Understanding the Results

### Investment Grades Explained
- **A+ (90-100점)**: 최우수 배당주 - 강력 매수 추천
- **A (80-89점)**: 우수 배당주 - 매수 추천
- **B+ (70-79점)**: 양호 배당주 - 보유 추천
- **B (60-69점)**: 보통 배당주 - 중립
- **C+ (50-59점)**: 주의 배당주 - 주의
- **C (<50점)**: 투자 부적합 - 매도

### Key Metrics
- **연속배당년수**: 몇 년간 연속으로 배당을 지급했는지
- **배당률**: 현재 주가 대비 연간 배당금 비율 
- **시가총액**: 회사의 전체 가치 (조원, 천억원 단위)
- **투자점수**: 종합적인 투자 매력도 (100점 만점)

## 🎯 Common Use Cases

### Case 1: Find High-Yield Dividend Stocks
```powershell
# Run quick analysis and look for high 배당률
.\run.ps1 quick

# Focus on companies with 5%+ dividend yield
# Look for A+ or A grade investments
```

### Case 2: Conservative Long-term Investment
```powershell
# Look for companies with 10+ consecutive years
# Focus on large market cap (조원 단위)
# Prefer A+ grade with stable sectors (통신, 담배, 유틸리티)
```

### Case 3: Growth + Dividend Strategy
```powershell
# Look for companies with positive dividend growth
# Focus on technology and consumer sectors
# Balance between dividend yield and growth potential
```

## 🔧 Available Commands

### Essential Commands
```powershell
.\run.ps1 quick      # Quick analysis (recommended for daily use)
.\run.ps1 run        # Full analysis with charts
.\run.ps1 test       # System validation
.\run.ps1 check      # System health check
```

### Maintenance Commands
```powershell
.\run.ps1 install    # Install/update dependencies
.\run.ps1 clean      # Clean generated files
.\run.ps1 unittest   # Run comprehensive tests
.\run.ps1 help       # Show all available commands
```

## 📈 Output Files Generated

After running analysis, you'll find:

- **Console Output**: Immediate results in Korean
- **korean_dividend_analysis_results.json**: Detailed data for further analysis
- **korean_dividend_analysis.png**: Charts and visualizations (if run with `.\run.ps1 run`)

## 🛠️ Troubleshooting Quick Start

### Issue 1: "uv command not found"
```powershell
# Install uv first
curl -LsSf https://astral.sh/uv/install.ps1 | powershell
# Restart PowerShell and try again
```

### Issue 2: Korean text shows as boxes
```powershell
# System check should resolve this
.\run.ps1 check

# If still issues, verify Windows has Korean language support
```

### Issue 3: Network/API errors
```powershell
# Check internet connectivity
# Yahoo Finance API might be temporarily unavailable
# Try again in a few minutes
```

### Issue 4: Permission errors
```powershell
# Run PowerShell as Administrator if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📚 Next Steps

### Explore Advanced Features
```powershell
# Run full analysis with visualizations
.\run.ps1 run

# Examine detailed results
cat korean_dividend_analysis_results.json

# View generated charts
# Charts saved as korean_dividend_analysis.png
```

### Customize Analysis
- Edit company list in `korean_dividend_analyzer.py`
- Modify analysis parameters (minimum years, scoring weights)
- Add new Korean companies to the database

### Integration with Investment Tools
- Export results to Excel using pandas
- Use JSON data for custom analysis
- Integrate with portfolio management systems

## 🎯 Best Practices

### Daily Usage
1. **Morning Check**: Run `.\run.ps1 quick` for updated analysis
2. **Review Top 5**: Focus on A+ and A grade companies
3. **Sector Rotation**: Monitor sector performance changes
4. **Price Alerts**: Track companies approaching better valuations

### Investment Workflow
1. **Screen**: Use quick analysis to identify candidates
2. **Research**: Deep dive into top-rated companies
3. **Validate**: Cross-reference with other investment tools
4. **Monitor**: Regular re-analysis for portfolio maintenance

### Risk Management
- Diversify across sectors (avoid concentration in one 섹터)
- Consider market cap distribution (mix of large/mid-cap)
- Monitor consecutive dividend year trends
- Regular rebalancing based on grade changes

This quick start gets you productive with Korean dividend analysis immediately!