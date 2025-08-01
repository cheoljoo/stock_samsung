# Makefile for running Python scripts with uv

.PHONY: all run-stock-diff run-analyze-ratio run-backtest-strategy run-get-ltd-dividend clean

# Default target: runs the main data generation script
all: run-stock-diff run-analyze-ratio run-get-ltd-dividend run-backtest-strategy

# Run stock_diff.py to generate analysis data and plots
run-stock-diff:
	@echo "Running stock_diff.py to generate data..."
	uv run python stock_diff.py

# Run analyze_ratio.py
run-analyze-ratio:
	@echo "Running analyze_ratio.py..."
	uv run python analyze_ratio.py

# Run backtest_strategy.py
run-backtest-strategy:
	@echo "Running backtest_strategy.py..."
	uv run python backtest_strategy.py

# Run get_samsung_ltd_dividend.py
run-get-ltd-dividend:
	@echo "Running get_samsung_ltd_dividend.py..."
	uv run python get_samsung_ltd_dividend.py

# Clean up generated files
clean:
	@echo "Cleaning up generated files..."
	rm -f samsung_stock_analysis.json price_diff_ratio_distribution.png portfolio_comparison.png samsung_ltd_dividends.json
