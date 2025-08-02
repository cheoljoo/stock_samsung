# Makefile for running Python scripts with uv

.PHONY: all interactive run-stock-diff run-analyze-ratio run-analyze-all run-backtest-strategy run-get-ltd-dividend run-comprehensive-report run-dividend-compare clean help

# Default target: run all companies analysis
all: run-full-pipeline-all

# Interactive company selection and analysis
interactive:
	@echo "🏢 지원되는 회사 목록:"
	@echo ""
	@uv run python -c "from stock_diff import PREFERRED_STOCK_COMPANIES; companies = list(PREFERRED_STOCK_COMPANIES.keys()); [print(f'  {i:2d}. {company}') for i, company in enumerate(companies, 1)]; print('')"
	@echo "📝 사용법:"
	@echo "  - 회사 번호 입력: 해당 회사만 분석"
	@echo "  - 회사 이름 입력: 해당 회사만 분석"
	@echo "  - Enter (빈 입력): 모든 회사 분석"
	@echo ""
	@read -p "🎯 분석할 회사를 선택하세요 (번호/이름/Enter): " choice; \
	if [ -z "$$choice" ]; then \
		echo "🌐 모든 회사에 대한 전체 분석을 시작합니다..."; \
		$(MAKE) run-full-pipeline-all; \
	elif echo "$$choice" | grep -qE '^[0-9]+$$'; then \
		company=$$(uv run python -c "from stock_diff import PREFERRED_STOCK_COMPANIES; companies = list(PREFERRED_STOCK_COMPANIES.keys()); idx = int('$$choice') - 1; print(companies[idx] if 0 <= idx < len(companies) else '')"); \
		if [ -n "$$company" ]; then \
			echo "🎯 $$company에 대한 분석을 시작합니다..."; \
			$(MAKE) run-full-pipeline-company COMPANY="$$company"; \
		else \
			echo "❌ 잘못된 번호입니다."; \
		fi; \
	else \
		echo "🎯 $$choice에 대한 분석을 시작합니다..."; \
		$(MAKE) run-full-pipeline-company COMPANY="$$choice"; \
	fi

# Full pipeline for specific company
run-full-pipeline-company:
	@echo "🚀 $(COMPANY) - 데이터 생성 중..."
	@$(MAKE) run-stock-diff-company COMPANY="$(COMPANY)"
	@echo ""
	@echo "📊 $(COMPANY) - 상세 분석 중..."
	@$(MAKE) run-analyze-ratio-company COMPANY="$(COMPANY)"
	@echo ""
	@echo "💰 $(COMPANY) - 배당률 비교 분석 중..."
	@$(MAKE) run-dividend-compare-company COMPANY="$(COMPANY)"
	@echo ""
	@echo "🎮 $(COMPANY) - 백테스팅 중..."
	@$(MAKE) run-backtest-strategy-company COMPANY="$(COMPANY)"
	@echo ""
	@echo "✅ $(COMPANY) 분석 완료!"

# Full pipeline for all companies
run-full-pipeline-all:
	@echo "🚀 모든 회사 - 데이터 생성 중..."
	@$(MAKE) run-stock-diff
	@echo ""
	@echo "📊 모든 회사 - 상세 분석 중..."
	@$(MAKE) run-analyze-ratio
	@echo ""
	@echo "🌐 모든 회사 - 종합 비교 분석 중..."
	@$(MAKE) run-analyze-all
	@echo ""
	@echo "� 배당률 비교 분석 중..."
	@$(MAKE) run-dividend-compare
	@echo ""
	@echo "�📋 종합 비교 리포트 생성 중..."
	@$(MAKE) run-comprehensive-report
	@echo ""
	@echo "🎮 백테스팅 중..."
	@$(MAKE) run-backtest-strategy
	@echo ""
	@echo "✅ 모든 회사 분석 완료!"

# === 주식 데이터 생성 ===

# Run stock_diff.py to generate analysis data (기본: 모든 회사)
run-stock-diff:
	@echo "🚀 Running stock_diff.py to generate data for all companies..."
	uv run python stock_diff.py

# Run stock_diff.py for specific company (usage: make run-stock-diff-company COMPANY=삼성전자)
run-stock-diff-company:
	@echo "🎯 Running stock_diff.py for $(COMPANY)..."
	uv run python stock_diff.py --company "$(COMPANY)"

# Show supported companies
list-companies:
	@echo "📋 Showing supported companies..."
	uv run python stock_diff.py --list

# === 개별 회사 심화 분석 ===

# Run analyze_ratio.py for detailed analysis (기본: 모든 회사)
run-analyze-ratio:
	@echo "📊 Running detailed analysis with analyze_ratio.py..."
	uv run python analyze_ratio.py

# Run analyze_ratio.py for specific company (usage: make run-analyze-ratio-company COMPANY=LG화학)
run-analyze-ratio-company:
	@echo "🎯 Running detailed analysis for $(COMPANY)..."
	uv run python analyze_ratio.py --company "$(COMPANY)"

# Run analyze_ratio.py for single period (usage: make run-analyze-single-period PERIOD=20년)
run-analyze-single-period:
	@echo "📊 Running single period analysis..."
	uv run python analyze_ratio.py --period "$(PERIOD)"

# Run analyze_ratio.py for specific company and period (usage: make run-analyze-company-period COMPANY=삼성전자 PERIOD=10년)
run-analyze-company-period:
	@echo "🎯 Running analysis for $(COMPANY) ($(PERIOD))..."
	uv run python analyze_ratio.py --company "$(COMPANY)" --period "$(PERIOD)"

# Generate timeseries plots (usage: make run-timeseries COMPANY=현대자동차)
run-timeseries:
	@echo "📈 Generating timeseries plots for $(COMPANY)..."
	uv run python analyze_ratio.py --company "$(COMPANY)" --timeseries

# === 다중 회사 비교 분석 ===

# Run analyze_all_companies.py for comprehensive comparison
run-analyze-all:
	@echo "🌐 Running comprehensive company comparison..."
	uv run python analyze_all_companies.py

# Run analyze_all_companies.py for specific company stats (usage: make run-single-stats COMPANY=삼성전자)
run-single-stats:
	@echo "🔍 Running individual stats for $(COMPANY)..."
	uv run python analyze_all_companies.py --company "$(COMPANY)"

# Generate comprehensive comparison report
run-comprehensive-report:
	@echo "📋 Generating comprehensive company comparison report..."
	uv run python comprehensive_company_comparison_report.py

# Compare dividend yields between common and preferred stocks
run-dividend-compare:
	@echo "💰 Comparing dividend yields for all companies..."
	uv run python stock_diff.py --dividend-compare

# Compare dividend yields for specific company (usage: make run-dividend-compare-company COMPANY=삼성전자)
run-dividend-compare-company:
	@echo "💰 Comparing dividend yields for $(COMPANY)..."
	uv run python stock_diff.py --company "$(COMPANY)" --dividend-compare

# === 백테스팅 ===

# Run backtest_strategy.py
run-backtest-strategy:
	@echo "🎮 Running backtest_strategy_with_report.py..."
	uv run python backtest_strategy_with_report.py

# Run backtest_strategy.py for specific company (usage: make run-backtest-strategy-company COMPANY=삼성전자)
run-backtest-strategy-company:
	@echo "🎮 Running backtest_strategy_with_report.py for $(COMPANY)..."
	uv run python backtest_strategy_with_report.py --company "$(COMPANY)"

# === 기타 도구 ===

# Run get_samsung_ltd_dividend.py (legacy)
run-get-ltd-dividend:
	@echo "💰 Running get_samsung_ltd_dividend.py..."
	uv run python get_samsung_ltd_dividend.py

# === 정리 작업 ===

# Clean up generated files
clean:
	@echo "🧹 Cleaning up generated files..."
	rm -f *_stock_analysis_*.json
	rm -f *_dividend_data.json
	rm -f *.png
	rm -f *.md
	rm -f samsung_stock_analysis.json
	rm -f samsung_ltd_dividends.json

# Clean only chart files
clean-charts:
	@echo "🧹 Cleaning up chart files..."
	rm -f *.png

# Clean only data files
clean-data:
	@echo "🧹 Cleaning up data files..."
	rm -f *_stock_analysis_*.json
	rm -f *_dividend_data.json
	rm -f *.md

# === 도움말 ===

help:
	@echo "📖 사용 가능한 명령어:"
	@echo ""
	@echo "🎯 기본 사용법:"
	@echo "  make                                    - 모든 회사 자동 분석 (전체 파이프라인)"
	@echo "  make interactive                        - 대화형 회사 선택 및 분석"
	@echo ""
	@echo "🚀 데이터 생성:"
	@echo "  make run-stock-diff                     - 모든 회사 데이터 생성"
	@echo "  make run-stock-diff-company COMPANY=회사명  - 특정 회사 데이터 생성"
	@echo "  make list-companies                     - 지원 회사 목록"
	@echo ""
	@echo "📊 개별 심화 분석 (analyze_ratio.py):"
	@echo "  make run-analyze-ratio                  - 모든 회사 전체 기간 종합 분석"
	@echo "  make run-analyze-ratio-company COMPANY=회사명  - 특정 회사 전체 기간 종합 분석"
	@echo "  make run-analyze-single-period PERIOD=기간    - 모든 회사 특정 기간 분석"
	@echo "  make run-analyze-company-period COMPANY=회사명 PERIOD=기간  - 특정 회사 특정 기간 분석"
	@echo "  make run-timeseries COMPANY=회사명       - 시계열 그래프 생성"
	@echo ""
	@echo "🌐 다중 회사 비교 (analyze_all_companies.py):"
	@echo "  make run-analyze-all                    - 모든 회사 종합 비교"
	@echo "  make run-single-stats COMPANY=회사명     - 특정 회사 통계만"
	@echo "  make run-comprehensive-report           - 종합 비교 리포트 생성"
	@echo ""
	@echo "💰 배당률 비교 분석:"
	@echo "  make run-dividend-compare               - 모든 회사 배당률 비교"
	@echo "  make run-dividend-compare-company COMPANY=회사명  - 특정 회사 배당률 비교"
	@echo ""
	@echo "🎮 백테스팅:"
	@echo "  make run-backtest-strategy              - 백테스팅 실행"
	@echo "  make run-backtest-strategy-company COMPANY=회사명  - 특정 회사 백테스팅"
	@echo ""
	@echo "🚀 전체 파이프라인:"
	@echo "  make run-full-pipeline-company COMPANY=회사명  - 특정 회사 전체 분석"
	@echo "  make run-full-pipeline-all              - 모든 회사 전체 분석"
	@echo ""
	@echo "🧹 정리:"
	@echo "  make clean                              - 모든 생성 파일 삭제"
	@echo "  make clean-charts                       - 차트 파일만 삭제"
	@echo "  make clean-data                         - 데이터 파일만 삭제"
	@echo ""
	@echo "예시:"
	@echo "  make                                    # 모든 회사 자동 분석"
	@echo "  make interactive                        # 대화형 선택"
	@echo "  make run-stock-diff-company COMPANY=삼성전자"
	@echo "  make run-analyze-ratio-company COMPANY=LG화학"
	@echo "  make run-analyze-company-period COMPANY=현대자동차 PERIOD=10년"
	@echo "  make run-dividend-compare-company COMPANY=현대자동차"
	@echo "  make run-comprehensive-report           # 종합 리포트 생성"
