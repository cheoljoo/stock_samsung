# Installation and Setup Guide

## 🚀 Quick Start Installation

### Prerequisites
- **Python 3.12+**: Modern Python version required
- **uv**: Fast Python package installer and resolver
- **Git**: Version control system
- **Windows 10/11**: For optimal Korean font support

### Step 1: Install uv Package Manager
```powershell
# Windows installation
curl -LsSf https://astral.sh/uv/install.ps1 | powershell

# Verify installation
uv --version
```

### Step 2: Clone and Setup Project
```powershell
# Clone repository
git clone <repository-url>
cd stock_samsung

# Navigate to dividend analysis directory (REQUIRED)
cd dividend-in-korea

# Install dependencies
.\run.ps1 install
```

### Step 3: System Verification
```powershell
# Check system setup
.\run.ps1 check

# Test Korean font configuration
.\run.ps1 test

# Run unit tests
.\run.ps1 unittest
```

## 🛠️ Detailed Installation

### Environment Setup

#### Windows Setup (Recommended)
```powershell
# 1. Verify Korean font (Malgun Gothic)
Get-WmiObject -Class Win32_SystemEncoding | Select-Object LocaleID
# Should show Korean locale support

# 2. Install uv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression

# 3. Clone and setup
git clone <repository-url> stock_samsung
cd stock_samsung\dividend-in-korea
uv sync
```

#### Linux/WSL Setup
```bash
# 1. Install Korean fonts
sudo apt-get update
sudo apt-get install fonts-nanum fonts-nanum-coding fonts-nanum-extra

# 2. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# 3. Setup project
git clone <repository-url> stock_samsung
cd stock_samsung/dividend-in-korea
uv sync
```

#### macOS Setup
```bash
# 1. Optional: Install Nanum fonts
brew install --cask font-nanum-gothic

# 2. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Setup project
git clone <repository-url> stock_samsung
cd stock_samsung/dividend-in-korea
uv sync
```

## 📋 Dependencies and Requirements

### Core Dependencies
```toml
# From pyproject.toml
[project]
requires-python = ">=3.12"
dependencies = [
    "matplotlib>=3.10.3",    # Korean text visualization
    "seaborn>=0.13.2",       # Statistical plots
    "yfinance>=0.2.65",      # Stock data API
    "pandas>=2.0.0",         # Data manipulation
    "numpy>=1.24.0",         # Numerical computing
]
```

### Development Dependencies
```powershell
# Additional tools for development
uv add --dev pytest pytest-cov black flake8
```

### System Requirements
- **Memory**: 4GB+ RAM recommended
- **Storage**: 1GB+ free space
- **Network**: Internet connection for stock data
- **Fonts**: Korean font support (automatic detection)

## 🔧 Configuration Options

### Font Configuration
```python
# Automatic font detection (default)
setup_korean_font()  # Auto-detects best Korean font

# Manual font override
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['font.family'] = 'AppleGothic'    # macOS  
plt.rcParams['font.family'] = 'NanumGothic'    # Linux
```

### Data Source Configuration
```python
# Default: Yahoo Finance (no configuration needed)
# Korean stock tickers format: XXXXXX.KS
# Example: 005930.KS (Samsung Electronics)
```

### Analysis Parameters
```python
# Minimum consecutive dividend years (default: 5)
analyzer.analyze_all_companies(min_consecutive_years=5)

# Analysis timeframe (default: 10 years)
analyzer.get_dividend_history(ticker, years=10)
```

## 🧪 Verification and Testing

### System Verification Commands
```powershell
# Full system check
.\run.ps1 check
# Output: ✅ uv found, ✅ System check passed

# Korean font test  
.\run.ps1 test
# Output: ✅ Korean font setup successful

# Unit test suite
.\run.ps1 unittest
# Output: 17/17 tests passed
```

### Manual Verification
```python
# Test Korean font in Python
python -c "from korean_dividend_analyzer import setup_korean_font; setup_korean_font()"
# Expected: ✅ Korean font set: Malgun Gothic

# Test data connection
python -c "import yfinance as yf; print(yf.Ticker('005930.KS').info['longName'])"  
# Expected: Samsung Electronics Co., Ltd.
```

## 🚨 Troubleshooting

### Common Issues

#### Issue 1: uv command not found
```powershell
# Solution: Add uv to PATH
$env:PATH += ";$HOME\.cargo\bin"
# Or restart terminal after installation
```

#### Issue 2: Korean text displays as boxes
```powershell
# Check font installation
python -c "import matplotlib.font_manager as fm; print([f.name for f in fm.fontManager.ttflist if 'gothic' in f.name.lower()])"

# Force font cache rebuild  
python -c "import matplotlib.font_manager as fm; fm._rebuild()"
```

#### Issue 3: Network/API errors
```powershell
# Test network connectivity
curl -s "https://query1.finance.yahoo.com/v8/finance/chart/005930.KS"

# Check firewall/proxy settings
```

#### Issue 4: Permission errors
```powershell
# Windows: Run as Administrator if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Linux: Check file permissions
chmod +x run.sh
```

### Performance Optimization
```powershell
# Clear cache for faster startup
.\run.ps1 clean

# Use quick analysis for faster results
.\run.ps1 quick

# Optimize for specific companies only
# Edit KOREAN_DIVIDEND_COMPANIES in korean_dividend_analyzer.py
```

## 📚 Next Steps

After successful installation:

1. **Quick Analysis**: Run `.\run.ps1 quick` for immediate results
2. **Full Analysis**: Run `.\run.ps1 run` for comprehensive analysis  
3. **Explore Results**: Check generated PNG charts and JSON data
4. **Customize**: Modify company list or analysis parameters
5. **Integrate**: Use results in your investment workflow

## 🔄 Maintenance

### Regular Updates
```powershell
# Update dependencies
uv sync --upgrade

# Update stock data (automatic on each run)
.\run.ps1 run

# Clean temporary files
.\run.ps1 clean
```

### Version Control
```powershell
# Track configuration changes
git add .
git commit -m "Update analysis configuration"

# Keep documentation in sync
git add docs/wiki/
git commit -m "Update documentation"
```

This setup ensures optimal performance and Korean text support across all platforms.