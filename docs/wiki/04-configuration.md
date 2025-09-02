# Configuration Guide

## ⚙️ System Configuration

### Environment Variables

The system uses minimal configuration with smart defaults. Most settings are auto-detected or configured through the codebase.

```python
# Key configuration constants in korean_dividend_analyzer.py
KOREAN_DIVIDEND_COMPANIES = {
    # Company database - easily extensible
    '삼성전자': {'common': '005930.KS', 'preferred': '005935.KS', 'sector': '전자/반도체'},
    # ... add more companies as needed
}

# Analysis parameters
DEFAULT_MIN_YEARS = 5          # Minimum consecutive dividend years
DEFAULT_ANALYSIS_PERIOD = 10   # Years of historical data to analyze
DEFAULT_SCORE_WEIGHTS = {
    'dividend_reliability': 0.4,   # 40%
    'financial_strength': 0.3,     # 30% 
    'growth_potential': 0.2,       # 20%
    'risk_assessment': 0.1         # 10%
}
```

### Font Configuration

#### Automatic Font Detection
```python
# System automatically detects optimal Korean font
def setup_korean_font():
    system_name = platform.system()
    
    if system_name == 'Windows':
        font_candidates = ['Malgun Gothic', 'NanumGothic', 'Gulim', 'Dotum']
    elif system_name == 'Darwin':  # macOS
        font_candidates = ['AppleGothic', 'AppleSDGothicNeo', 'NanumGothic']
    else:  # Linux
        font_candidates = ['NanumGothic', 'NanumBarunGothic', 'DejaVu Sans']
```

#### Manual Font Override
```python
# Force specific font (add to korean_dividend_analyzer.py)
import matplotlib.pyplot as plt

# Windows specific
plt.rcParams['font.family'] = 'Malgun Gothic'

# macOS specific  
plt.rcParams['font.family'] = 'AppleGothic'

# Linux specific
plt.rcParams['font.family'] = 'NanumGothic'

# Universal fallback
plt.rcParams['font.family'] = ['sans-serif']
```

## 🏢 Company Database Configuration

### Adding New Companies

To add companies to the analysis, modify the `KOREAN_DIVIDEND_COMPANIES` dictionary:

```python
# Add to korean_dividend_analyzer.py
KOREAN_DIVIDEND_COMPANIES = {
    # ... existing companies ...
    
    # New company template
    '새로운회사': {
        'common': 'XXXXXX.KS',           # 6-digit ticker + .KS
        'preferred': 'XXXXXX.KS',        # Optional preferred stock
        'name': '새로운회사',              # Korean name
        'sector': '업종명'                # Korean sector name
    },
    
    # Example: Adding Hanwha Systems
    '한화시스템': {
        'common': '272210.KS',
        'name': '한화시스템', 
        'sector': '방산/항공'
    }
}
```

### Sector Configuration

Standard sector classifications used in the system:

```python
STANDARD_SECTORS = {
    '전자/반도체': 'Electronics/Semiconductor',
    '자동차': 'Automotive', 
    '화학': 'Chemical',
    '통신': 'Telecommunications',
    '담배': 'Tobacco',
    '철강': 'Steel',
    '지주회사': 'Holding Company',
    '생활용품': 'Consumer Goods',
    '화장품': 'Cosmetics',
    'IT서비스': 'IT Services',
    '정유': 'Oil Refining',
    '가스': 'Gas Utility',
    '식품': 'Food & Beverage',
    '에너지/화학': 'Energy/Chemical',
    '전력': 'Electric Power'
}
```

## 📊 Analysis Parameter Configuration

### Scoring Weight Adjustment

Modify investment scoring criteria by adjusting weights:

```python
def calculate_investment_score(company_results):
    # Customizable weight configuration
    WEIGHTS = {
        'dividend_reliability': 0.4,    # Increase for dividend-focused strategy
        'financial_strength': 0.3,      # Increase for conservative approach
        'growth_potential': 0.2,        # Increase for growth-oriented strategy  
        'risk_assessment': 0.1          # Increase for risk-averse approach
    }
    
    # Example: Conservative dividend strategy
    CONSERVATIVE_WEIGHTS = {
        'dividend_reliability': 0.5,    # 50% - Higher emphasis on consistency
        'financial_strength': 0.35,     # 35% - Safety first
        'growth_potential': 0.1,        # 10% - Less focus on growth
        'risk_assessment': 0.05         # 5% - Minimal risk weighting
    }
```

### Analysis Timeframe Configuration

```python
# Modify analysis periods in functions
def analyze_all_companies(min_consecutive_years=5):    # Default: 5 years
    # Change to 7 for more conservative screening
    # Change to 3 for more inclusive screening
    
def get_dividend_history(ticker, years=10):           # Default: 10 years
    # Change to 15 for longer historical analysis
    # Change to 5 for recent performance focus
```

### Grade Threshold Configuration

```python
def get_investment_grade(score):
    # Default thresholds
    DEFAULT_THRESHOLDS = {
        'A+': 90, 'A': 80, 'B+': 70, 
        'B': 60, 'C+': 50, 'C': 0
    }
    
    # Stricter grading (fewer A+ grades)
    STRICT_THRESHOLDS = {
        'A+': 95, 'A': 85, 'B+': 75,
        'B': 65, 'C+': 55, 'C': 0  
    }
    
    # More lenient grading (more A+ grades)
    LENIENT_THRESHOLDS = {
        'A+': 85, 'A': 75, 'B+': 65,
        'B': 55, 'C+': 45, 'C': 0
    }
```

## 🔧 PowerShell Script Configuration

### Custom Commands

Add new commands to `run.ps1`:

```powershell
# Add to the switch statement in run.ps1
switch ($Command.ToLower()) {
    # ... existing commands ...
    
    "custom" { Run-CustomAnalysis }
    "export" { Export-Results }
    "backup" { Backup-Data }
}

# Add custom functions
function Run-CustomAnalysis {
    Write-Host "🎯 Running custom analysis..." -ForegroundColor Green
    uv run python custom_analysis.py
}

function Export-Results {
    Write-Host "📤 Exporting analysis results..." -ForegroundColor Green
    uv run python -c "
    from korean_dividend_analyzer import KoreanDividendAnalyzer
    analyzer = KoreanDividendAnalyzer()
    # Export logic here
    "
}
```

### Environment-Specific Configuration

```powershell
# Add environment detection to run.ps1
function Get-Environment {
    if ($env:COMPUTERNAME -eq "PRODUCTION-SERVER") {
        return "production"
    } elseif ($env:COMPUTERNAME -like "*DEV*") {
        return "development"  
    } else {
        return "local"
    }
}

function Run-EnvironmentSpecificAnalysis {
    $env = Get-Environment
    Write-Host "🌍 Running analysis for environment: $env" -ForegroundColor Yellow
    
    switch ($env) {
        "production" { 
            # Production settings: full analysis, all companies
            uv run python korean_dividend_analyzer.py --full --all-companies
        }
        "development" {
            # Development settings: quick analysis, subset of companies  
            uv run python quick_dividend_analysis.py --sample
        }
        "local" {
            # Local settings: standard analysis
            uv run python quick_dividend_analysis.py
        }
    }
}
```

## 📈 Output Configuration

### Chart Configuration

```python
# Modify chart settings in generate_visualizations()
def generate_visualizations(self):
    # Chart size configuration
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))  # Default size
    # Change to (20, 15) for larger charts
    # Change to (12, 9) for smaller charts
    
    # Color scheme configuration
    COLORS = {
        'primary': 'steelblue',      # Main chart color
        'secondary': 'lightcoral',   # Secondary elements
        'accent': 'gold',            # Highlights
        'background': 'white'        # Background color
    }
    
    # Korean color theme
    KOREAN_COLORS = {
        'primary': '#003d82',        # 태극기 파랑
        'secondary': '#cd2e3a',      # 태극기 빨강  
        'accent': '#ffd700',         # 금색
        'background': '#f8f9fa'      # 연한 회색
    }
```

### Export Format Configuration

```python
# Configure output file formats
def save_results(self, filename='korean_dividend_analysis_results.json'):
    # JSON export (default)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
    
    # Additional export formats
    def export_to_excel(self):
        df = self.create_comparison_table()
        df.to_excel('dividend_analysis.xlsx', index=False, engine='openpyxl')
    
    def export_to_csv(self):
        df = self.create_comparison_table()  
        df.to_csv('dividend_analysis.csv', index=False, encoding='utf-8-sig')
```

## 🔐 Security Configuration

### API Security

```python
# No API keys required for Yahoo Finance
# But you can add rate limiting for production use

import time
from functools import wraps

def rate_limit(calls_per_second=1):
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

# Apply to data collection functions
@rate_limit(calls_per_second=0.5)  # 2 second intervals
def get_stock_info(self, ticker):
    # ... existing implementation
```

### Data Privacy

```python
# No personal data collected
# All data is public market information
# Configuration for compliance logging

import logging

def setup_compliance_logging():
    logging.basicConfig(
        filename='compliance.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Log data access
    logging.info("Dividend analysis initiated")
    logging.info("Public market data accessed via Yahoo Finance API")
```

This configuration system provides flexibility while maintaining simplicity and Korean market focus.