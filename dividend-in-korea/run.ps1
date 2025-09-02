# Korean Dividend Analysis - PowerShell Runner Script
# Use this script on Windows instead of Makefile

param(
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "🏆 Korean Dividend Analysis - Available Commands:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  .\run.ps1 install    - Install dependencies using uv" -ForegroundColor Cyan
    Write-Host "  .\run.ps1 run        - Run full dividend analysis (korean_dividend_analyzer.py)" -ForegroundColor Cyan
    Write-Host "  .\run.ps1 quick      - Run quick dividend analysis (quick_dividend_analysis.py)" -ForegroundColor Cyan
    Write-Host "  .\run.ps1 analyze    - Alias for 'run'" -ForegroundColor Cyan
    Write-Host "  .\run.ps1 test       - Test the analysis with a sample company" -ForegroundColor Cyan
    Write-Host "  .\run.ps1 unittest   - Run unit tests for the analyzer" -ForegroundColor Cyan
    Write-Host "  .\run.ps1 check      - Check dependencies and system setup" -ForegroundColor Cyan
    Write-Host "  .\run.ps1 clean      - Clean generated files" -ForegroundColor Cyan
    Write-Host "  .\run.ps1 deps       - Show dependency information" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "💡 Examples:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 install; .\run.ps1 run    - Full setup and analysis" -ForegroundColor White
    Write-Host "  .\run.ps1 quick                     - Quick analysis only" -ForegroundColor White
}

function Install-Dependencies {
    Write-Host "📦 Installing dependencies using uv..." -ForegroundColor Green
    try {
        uv sync
        Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to install dependencies. Make sure uv is installed and try again."
        exit 1
    }
}

function Run-FullAnalysis {
    Check-System
    Write-Host "🚀 Running Korean Dividend Analysis..." -ForegroundColor Green
    Write-Host "📊 This will analyze all Korean companies for 5+ consecutive dividend years" -ForegroundColor Yellow
    uv run python korean_dividend_analyzer.py
}

function Run-QuickAnalysis {
    Check-System
    Write-Host "⚡ Running Quick Dividend Analysis..." -ForegroundColor Green
    Write-Host "🎯 Focused analysis with summary table" -ForegroundColor Yellow
    uv run python quick_dividend_analysis.py
}

function Test-Analysis {
    Check-System
    Write-Host "🧪 Testing dividend analysis system..." -ForegroundColor Green
    
    try {
        Write-Host "Testing Korean font setup..." -ForegroundColor Yellow
        uv run python -c "from korean_dividend_analyzer import setup_korean_font; print('✅ Korean font setup successful')"
        
        Write-Host "Testing Korean dividend analyzer import..." -ForegroundColor Yellow
        uv run python -c "from korean_dividend_analyzer import KoreanDividendAnalyzer; print('✅ Import successful')"
        
        Write-Host "Testing yfinance connection..." -ForegroundColor Yellow
        uv run python -c "import yfinance as yf; stock = yf.Ticker('005930.KS'); print('✅ Yahoo Finance connection successful')"
        
        Write-Host "Testing sample company analysis..." -ForegroundColor Yellow
        uv run python -c "from korean_dividend_analyzer import KoreanDividendAnalyzer; analyzer = KoreanDividendAnalyzer(); result = analyzer.analyze_single_company('삼성전자'); print(f'✅ Sample analysis successful: {bool(result)}')"
        
        Write-Host "✅ All tests passed!" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Tests failed. Please check your setup."
        Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

function Run-UnitTests {
    Check-System
    Write-Host "🧪 Running unit tests for Korean Dividend Analyzer..." -ForegroundColor Green
    Write-Host "📋 Testing core functionality and Korean text support" -ForegroundColor Yellow
    
    try {
        uv run python test_korean_dividend_analyzer.py
        Write-Host "✅ Unit tests completed successfully!" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Unit tests failed. Please check the test output above."
        Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

function Check-System {
    Write-Host "🔍 Checking system setup..." -ForegroundColor Green
    
    # Check if uv is installed
    try {
        $uvVersion = uv --version
        Write-Host "✅ uv found: $uvVersion" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ uv not found. Please install uv first: https://docs.astral.sh/uv/"
        Write-Host "Windows installation: curl -LsSf https://astral.sh/uv/install.ps1 | powershell" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✅ System check passed" -ForegroundColor Green
}

function Show-Dependencies {
    Write-Host "📋 Current dependencies:" -ForegroundColor Green
    Write-Host "Required packages:" -ForegroundColor Yellow
    Write-Host "  - yfinance (Yahoo Finance data)" -ForegroundColor White
    Write-Host "  - pandas (Data manipulation)" -ForegroundColor White
    Write-Host "  - numpy (Numerical computing)" -ForegroundColor White
    Write-Host "  - matplotlib (Plotting)" -ForegroundColor White
    Write-Host "  - seaborn (Statistical visualization)" -ForegroundColor White
    Write-Host ""
    Write-Host "📦 Installed packages:" -ForegroundColor Yellow
    
    try {
        uv tree
    }
    catch {
        Write-Host "Run '.\run.ps1 install' first to see installed packages" -ForegroundColor Red
    }
}

function Clean-Files {
    Write-Host "🧹 Cleaning generated files..." -ForegroundColor Green
    
    $filesToClean = @(
        "*.png", "*.json", "*.csv", "*.log",
        "__pycache__", ".pytest_cache", ".coverage",
        "korean_dividend_analysis.png",
        "korean_dividend_analysis_results.json"
    )
    
    foreach ($pattern in $filesToClean) {
        try {
            Remove-Item $pattern -Recurse -Force -ErrorAction SilentlyContinue
        }
        catch {
            # Ignore errors for files that don't exist
        }
    }
    
    Write-Host "✅ Cleanup completed" -ForegroundColor Green
}

function Show-SetupGuide {
    Write-Host "🎯 First Time Setup Guide:" -ForegroundColor Green
    Write-Host ""
    Write-Host "1️⃣  Install uv (if not already installed):" -ForegroundColor Yellow
    Write-Host "   Windows: curl -LsSf https://astral.sh/uv/install.ps1 | powershell" -ForegroundColor White
    Write-Host ""
    Write-Host "2️⃣  Install project dependencies:" -ForegroundColor Yellow
    Write-Host "   .\run.ps1 install" -ForegroundColor White
    Write-Host ""
    Write-Host "3️⃣  Run analysis:" -ForegroundColor Yellow
    Write-Host "   .\run.ps1 quick     (for quick summary)" -ForegroundColor White
    Write-Host "   .\run.ps1 run       (for full analysis with charts)" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Output files will include:" -ForegroundColor Yellow
    Write-Host "   - korean_dividend_analysis.png (charts)" -ForegroundColor White
    Write-Host "   - korean_dividend_analysis_results.json (data)" -ForegroundColor White
}

function Show-Options {
    Write-Host "🎛️ Analysis Options:" -ForegroundColor Green
    Write-Host ""
    Write-Host "📈 Full Analysis (.\run.ps1 run):" -ForegroundColor Yellow
    Write-Host "   - Analyzes all Korean companies" -ForegroundColor White
    Write-Host "   - Generates detailed comparison table" -ForegroundColor White
    Write-Host "   - Creates visualization charts" -ForegroundColor White
    Write-Host "   - Saves results to JSON" -ForegroundColor White
    Write-Host "   - Shows investment recommendations" -ForegroundColor White
    Write-Host ""
    Write-Host "⚡ Quick Analysis (.\run.ps1 quick):" -ForegroundColor Yellow
    Write-Host "   - Focused on top dividend companies" -ForegroundColor White
    Write-Host "   - Summary table only" -ForegroundColor White
    Write-Host "   - Faster execution" -ForegroundColor White
    Write-Host "   - Investment grade rankings" -ForegroundColor White
    Write-Host ""
    Write-Host "🧪 Test Mode (.\run.ps1 test):" -ForegroundColor Yellow
    Write-Host "   - Validates system setup" -ForegroundColor White
    Write-Host "   - Tests sample company analysis" -ForegroundColor White
    Write-Host "   - Verifies data connections" -ForegroundColor White
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Dependencies }
    "run" { Run-FullAnalysis }
    "quick" { Run-QuickAnalysis }
    "analyze" { Run-FullAnalysis }
    "test" { Test-Analysis }
    "unittest" { Run-UnitTests }
    "check" { Check-System }
    "deps" { Show-Dependencies }
    "clean" { Clean-Files }
    "setup-guide" { Show-SetupGuide }
    "options" { Show-Options }
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use '.\run.ps1 help' to see available commands" -ForegroundColor Yellow
    }
}