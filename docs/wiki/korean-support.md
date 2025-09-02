# Korean Text Support Configuration

## 🎨 Font Configuration System

The system includes comprehensive Korean text support with automatic font detection and fallback mechanisms.

### Supported Fonts by Platform

| Platform | Primary Font | Fallback Options | Status |
|----------|-------------|------------------|--------|
| **Windows** | Malgun Gothic | NanumGothic, Gulim, Dotum | ✅ Tested |
| **macOS** | AppleGothic | AppleSDGothicNeo, NanumGothic | ✅ Supported |
| **Linux** | NanumGothic | NanumBarunGothic, DejaVu Sans | ✅ Supported |

### Font Setup Function

```python
def setup_korean_font():
    """Enhanced Korean font setup with fallback options"""
    system_name = platform.system()
    
    if system_name == 'Windows':
        font_candidates = ['Malgun Gothic', 'NanumGothic', 'Gulim', 'Dotum']
    elif system_name == 'Darwin':  
        font_candidates = ['AppleGothic', 'AppleSDGothicNeo', 'NanumGothic']
    else:  # Linux and others
        font_candidates = ['NanumGothic', 'NanumBarunGothic', 'DejaVu Sans']
    
    # Automatic font detection and setup
    selected_font = detect_available_font(font_candidates)
    plt.rcParams['font.family'] = selected_font
    plt.rcParams['axes.unicode_minus'] = False
```

## 📊 Korean Text Elements

### Business Terminology
- **회사명 (Company Names)**: 삼성전자, LG화학, 현대자동차
- **섹터명 (Sectors)**: 전자/반도체, 화학, 자동차, 통신
- **투자등급 (Investment Grades)**: A+, A, B+, B, C+, C
- **화폐단위 (Currency)**: 조원, 천억원, 백억원, 억원

### Output Text Formatting
```python
# Market cap formatting in Korean
def format_market_cap(market_cap):
    if market_cap >= 1_000_000_000_000:
        return f"{market_cap/1_000_000_000_000:.1f}조원"
    elif market_cap >= 100_000_000_000:
        return f"{market_cap/100_000_000_000:.1f}천억원"
    # ... additional formatting
```

## 🛠️ Installation Requirements

### Windows Setup
```powershell
# Malgun Gothic is pre-installed on Windows 10/11
# No additional installation required
.\run.ps1 check  # Verifies font availability
```

### Linux Setup  
```bash
# Install Nanum fonts
sudo apt-get install fonts-nanum fonts-nanum-coding fonts-nanum-extra

# Verify installation
fc-list | grep -i nanum
```

### macOS Setup
```bash
# Apple Gothic is pre-installed
# Optional: Install Nanum fonts via Homebrew
brew install --cask font-nanum-gothic
```

## 🧪 Testing Korean Text Support

### Unit Test Coverage
- **Font Detection**: Automatic system font identification
- **Text Rendering**: Korean character display validation  
- **Chart Labels**: Graph axis and legend Korean text
- **Report Generation**: Korean text in tables and summaries

### Manual Verification
```python
# Test Korean font setup
from korean_dividend_analyzer import setup_korean_font
setup_korean_font()  # Should output: "✅ Korean font set: Malgun Gothic"

# Test Korean text in analysis
analyzer = KoreanDividendAnalyzer()
result = analyzer.analyze_single_company('삼성전자')
print(result['company_name'])  # Should display: 삼성전자
```

## 📋 Common Issues and Solutions

### Issue 1: Font Display as Boxes (□□□)
**Cause**: Korean font not properly configured
**Solution**: 
```python
# Check font availability
import matplotlib.font_manager as fm
fonts = [f.name for f in fm.fontManager.ttflist]
korean_fonts = [f for f in fonts if 'gothic' in f.lower() or 'nanum' in f.lower()]
print(korean_fonts)
```

### Issue 2: Mixed Korean/English Alignment
**Cause**: Font fallback to different fonts
**Solution**:
```python
# Force consistent font usage
plt.rcParams['font.family'] = ['Malgun Gothic']
plt.rcParams['font.sans-serif'] = ['Malgun Gothic']
```

### Issue 3: Chart Export with Corrupted Korean Text
**Cause**: Font embedding issues in PNG/PDF export
**Solution**:
```python
# Ensure font embedding in exports
plt.savefig('chart.png', dpi=300, bbox_inches='tight', 
           facecolor='white', edgecolor='none')
```

## 🎯 Best Practices

### Code Standards
- Always call `setup_korean_font()` before matplotlib operations
- Use consistent Korean terminology across the application
- Test Korean text display on different platforms
- Include Korean text in unit tests

### User Experience
- Provide Korean language error messages
- Use familiar Korean business terminology  
- Maintain consistent font styling across all outputs
- Include Korean language help documentation

This configuration ensures reliable Korean text support across all platforms and use cases.