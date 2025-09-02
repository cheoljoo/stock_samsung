# Korean Dividend Analysis Makefile
# Use 'uv' for Python package management and execution

.PHONY: help install run quick clean analyze test check deps

# Default target
help:
	@echo "🏆 Korean Dividend Analysis - Available Commands:"
	@echo ""
	@echo "  make install    - Install dependencies using uv"
	@echo "  make run        - Run full dividend analysis (korean_dividend_analyzer.py)"
	@echo "  make quick      - Run quick dividend analysis (quick_dividend_analysis.py)"
	@echo "  make analyze    - Alias for 'make run'"
	@echo "  make test       - Test the analysis with a sample company"
	@echo "  make check      - Check dependencies and system setup"
	@echo "  make clean      - Clean generated files"
	@echo "  make deps       - Show dependency information"
	@echo ""
	@echo "💡 Examples:"
	@echo "  make install && make run    - Full setup and analysis"
	@echo "  make quick                  - Quick analysis only"

# Install dependencies
install:
	@echo "📦 Installing dependencies using uv..."
	uv sync
	@echo "✅ Dependencies installed successfully!"

# Run full dividend analysis
run: check
	@echo "🚀 Running Korean Dividend Analysis..."
	@echo "📊 This will analyze all Korean companies for 5+ consecutive dividend years"
	uv run python korean_dividend_analyzer.py

# Run quick analysis
quick: check
	@echo "⚡ Running Quick Dividend Analysis..."
	@echo "🎯 Focused analysis with summary table"
	uv run python quick_dividend_analysis.py

# Alias for run
analyze: run

# Test with sample analysis
test: check
	@echo "🧪 Testing dividend analysis system..."
	@echo "Testing Korean dividend analyzer import..."
	uv run python -c "from korean_dividend_analyzer import KoreanDividendAnalyzer; print('✅ Import successful')"
	@echo "Testing yfinance connection..."
	uv run python -c "import yfinance as yf; stock = yf.Ticker('005930.KS'); print('✅ Yahoo Finance connection successful')"
	@echo "Testing sample company analysis..."
	uv run python -c "from korean_dividend_analyzer import KoreanDividendAnalyzer; analyzer = KoreanDividendAnalyzer(); result = analyzer.analyze_single_company('삼성전자'); print(f'✅ Sample analysis successful: {bool(result)}')"

# Check system dependencies and setup
check:
	@echo "🔍 Checking system setup..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv not found. Please install uv first: https://docs.astral.sh/uv/"; exit 1; }
	@echo "✅ uv found"
	@uv --version
	@echo "✅ System check passed"

# Show dependency information
deps:
	@echo "📋 Current dependencies:"
	@echo "Required packages:"
	@echo "  - yfinance (Yahoo Finance data)"
	@echo "  - pandas (Data manipulation)"
	@echo "  - numpy (Numerical computing)"
	@echo "  - matplotlib (Plotting)"
	@echo "  - seaborn (Statistical visualization)"
	@echo ""
	@echo "📦 Installed packages:"
	uv tree 2>/dev/null || echo "Run 'make install' first to see installed packages"

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	@rm -f *.png *.json *.csv *.log 2>/dev/null || true
	@rm -rf __pycache__ .pytest_cache .coverage 2>/dev/null || true
	@rm -f korean_dividend_analysis.png 2>/dev/null || true
	@rm -f korean_dividend_analysis_results.json 2>/dev/null || true
	@echo "✅ Cleanup completed"

# Interactive help for first-time users
setup-guide:
	@echo "🎯 First Time Setup Guide:"
	@echo ""
	@echo "1️⃣  Install uv (if not already installed):"
	@echo "   Windows: curl -LsSf https://astral.sh/uv/install.ps1 | powershell"
	@echo "   Linux/Mac: curl -LsSf https://astral.sh/uv/install.sh | sh"
	@echo ""
	@echo "2️⃣  Install project dependencies:"
	@echo "   make install"
	@echo ""
	@echo "3️⃣  Run analysis:"
	@echo "   make quick     (for quick summary)"
	@echo "   make run       (for full analysis with charts)"
	@echo ""
	@echo "📊 Output files will include:"
	@echo "   - korean_dividend_analysis.png (charts)"
	@echo "   - korean_dividend_analysis_results.json (data)"

# Show analysis options
options:
	@echo "🎛️ Analysis Options:"
	@echo ""
	@echo "📈 Full Analysis (make run):"
	@echo "   - Analyzes all Korean companies"
	@echo "   - Generates detailed comparison table"
	@echo "   - Creates visualization charts"
	@echo "   - Saves results to JSON"
	@echo "   - Shows investment recommendations"
	@echo ""
	@echo "⚡ Quick Analysis (make quick):"
	@echo "   - Focused on top dividend companies"
	@echo "   - Summary table only"
	@echo "   - Faster execution"
	@echo "   - Investment grade rankings"
	@echo ""
	@echo "🧪 Test Mode (make test):"
	@echo "   - Validates system setup"
	@echo "   - Tests sample company analysis"
	@echo "   - Verifies data connections"