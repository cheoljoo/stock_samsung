# -*- coding: utf-8 -*-
"""
Unit tests for Korean Dividend Analyzer
Tests the core functionality of Korean dividend analysis system
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from korean_dividend_analyzer import KoreanDividendAnalyzer, KOREAN_DIVIDEND_COMPANIES, setup_korean_font


class TestKoreanDividendAnalyzer(unittest.TestCase):
    """Test cases for KoreanDividendAnalyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = KoreanDividendAnalyzer()
        self.sample_company = '삼성전자'
        
        # Sample dividend data for testing
        dates = pd.date_range('2020-01-01', '2024-12-31', freq='6M')
        self.sample_dividends = pd.Series([1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900], 
                                         index=dates)
        
    def test_initialization(self):
        """Test KoreanDividendAnalyzer initialization"""
        self.assertIsInstance(self.analyzer.companies, dict)
        self.assertIsInstance(self.analyzer.analysis_results, dict)
        self.assertGreater(len(self.analyzer.companies), 0)
        
    def test_korean_companies_data_structure(self):
        """Test Korean companies data structure integrity"""
        for company_name, company_info in KOREAN_DIVIDEND_COMPANIES.items():
            self.assertIsInstance(company_name, str)
            self.assertIsInstance(company_info, dict)
            self.assertIn('common', company_info)
            self.assertIn('name', company_info)
            self.assertIn('sector', company_info)
            
            # Check ticker format
            common_ticker = company_info['common']
            self.assertTrue(common_ticker.endswith('.KS'))
            self.assertRegex(common_ticker, r'^\d{6}\.KS$')
            
    def test_check_consecutive_dividend_years(self):
        """Test consecutive dividend years calculation"""
        # Test with sample dividend data
        consecutive_years, is_qualified = self.analyzer.check_consecutive_dividend_years(self.sample_dividends, min_years=3)
        
        self.assertIsInstance(consecutive_years, int)
        self.assertIsInstance(is_qualified, bool)
        self.assertGreaterEqual(consecutive_years, 0)
        
    def test_check_consecutive_dividend_years_empty(self):
        """Test consecutive dividend years with empty data"""
        empty_dividends = pd.Series(dtype=float)
        consecutive_years, is_qualified = self.analyzer.check_consecutive_dividend_years(empty_dividends)
        
        self.assertEqual(consecutive_years, 0)
        self.assertFalse(is_qualified)
        
    def test_format_market_cap(self):
        """Test market cap formatting"""
        # Test trillion KRW
        result = self.analyzer.format_market_cap(1500000000000)
        self.assertIn('조원', result)
        
        # Test hundred billion KRW  
        result = self.analyzer.format_market_cap(500000000000)
        self.assertIn('천억원', result)
        
        # Test ten billion KRW
        result = self.analyzer.format_market_cap(50000000000)
        self.assertIn('백억원', result)
        
        # Test billion KRW
        result = self.analyzer.format_market_cap(5000000000)
        self.assertIn('억원', result)
        
        # Test zero
        result = self.analyzer.format_market_cap(0)
        self.assertEqual(result, '0억원')
        
    def test_get_investment_grade(self):
        """Test investment grade calculation"""
        # Test A+ grade
        grade = self.analyzer.get_investment_grade(90)
        self.assertEqual(grade, 'A+')
        
        # Test A grade
        grade = self.analyzer.get_investment_grade(80)
        self.assertEqual(grade, 'A')
        
        # Test B+ grade
        grade = self.analyzer.get_investment_grade(70)
        self.assertEqual(grade, 'B+')
        
        # Test B grade
        grade = self.analyzer.get_investment_grade(60)
        self.assertEqual(grade, 'B')
        
        # Test C+ grade
        grade = self.analyzer.get_investment_grade(50)
        self.assertEqual(grade, 'C+')
        
        # Test C grade
        grade = self.analyzer.get_investment_grade(30)
        self.assertEqual(grade, 'C')
        
    @patch('korean_dividend_analyzer.yf.Ticker')
    def test_get_dividend_history_success(self, mock_ticker):
        """Test successful dividend history retrieval"""
        # Mock yfinance response
        mock_stock = Mock()
        mock_stock.dividends = self.sample_dividends
        mock_ticker.return_value = mock_stock
        
        result = self.analyzer.get_dividend_history('005930.KS')
        
        self.assertIsInstance(result, pd.Series)
        mock_ticker.assert_called_once_with('005930.KS')
        
    @patch('korean_dividend_analyzer.yf.Ticker')
    def test_get_dividend_history_failure(self, mock_ticker):
        """Test dividend history retrieval failure"""
        # Mock yfinance failure
        mock_ticker.side_effect = Exception("Network error")
        
        result = self.analyzer.get_dividend_history('INVALID.KS')
        
        self.assertIsInstance(result, pd.Series)
        self.assertTrue(result.empty)
        
    @patch('korean_dividend_analyzer.yf.Ticker')
    def test_get_stock_info_success(self, mock_ticker):
        """Test successful stock info retrieval"""
        # Mock yfinance response
        mock_stock = Mock()
        mock_stock.info = {
            'marketCap': 500000000000000,
            'sharesOutstanding': 5969782550,
            'sector': 'Technology',
            'industry': 'Consumer Electronics'
        }
        mock_stock.history.return_value = pd.DataFrame({
            'Close': [70000, 71000, 72000, 73000, 74000]
        })
        mock_ticker.return_value = mock_stock
        
        result = self.analyzer.get_stock_info('005930.KS')
        
        self.assertIsNotNone(result)
        self.assertIn('price', result)
        self.assertIn('market_cap', result)
        self.assertIn('sector', result)
        
    @patch('korean_dividend_analyzer.yf.Ticker')
    def test_get_stock_info_failure(self, mock_ticker):
        """Test stock info retrieval failure"""
        # Mock yfinance failure
        mock_ticker.side_effect = Exception("Network error")
        
        result = self.analyzer.get_stock_info('INVALID.KS')
        
        self.assertIsNone(result)
        
    @patch.object(KoreanDividendAnalyzer, 'get_dividend_history')
    @patch.object(KoreanDividendAnalyzer, 'get_stock_info')
    def test_calculate_dividend_metrics(self, mock_get_stock_info, mock_get_dividend_history):
        """Test dividend metrics calculation"""
        # Mock data
        mock_get_dividend_history.return_value = self.sample_dividends
        mock_get_stock_info.return_value = {'price': 70000}
        
        result = self.analyzer.calculate_dividend_metrics('005930.KS', {'price': 70000})
        
        self.assertIsInstance(result, dict)
        self.assertIn('consecutive_years', result)
        self.assertIn('is_qualified', result)
        self.assertIn('annual_dividend', result)
        self.assertIn('dividend_yield', result)
        
    def test_analyze_single_company_invalid(self):
        """Test analyzing invalid company"""
        result = self.analyzer.analyze_single_company('INVALID_COMPANY')
        self.assertIsNone(result)
        
    @patch.object(KoreanDividendAnalyzer, 'get_stock_info')
    @patch.object(KoreanDividendAnalyzer, 'calculate_dividend_metrics')
    def test_analyze_single_company_valid(self, mock_calculate_metrics, mock_get_stock_info):
        """Test analyzing valid company"""
        # Mock returns
        mock_get_stock_info.return_value = {
            'price': 70000,
            'market_cap': 500000000000000,
            'shares_outstanding': 5969782550,
            'sector': 'Technology',
            'industry': 'Consumer Electronics'
        }
        
        mock_calculate_metrics.return_value = {
            'consecutive_years': 8,
            'is_qualified': True,
            'annual_dividend': 1500,
            'dividend_yield': 2.14,
            'dividend_growth_rate': 5.5,
            'total_dividends': 15000
        }
        
        result = self.analyzer.analyze_single_company(self.sample_company)
        
        self.assertIsNotNone(result)
        self.assertIn('company_name', result)
        self.assertIn('common_stock', result)
        self.assertEqual(result['company_name'], self.sample_company)
        
    def test_korean_font_setup(self):
        """Test Korean font setup function"""
        # This test verifies that the function runs without error
        # Actual font availability depends on the system
        try:
            result = setup_korean_font()
            self.assertIsInstance(result, bool)
        except Exception as e:
            self.fail(f"Korean font setup failed: {e}")


class TestKoreanDividendAnalyzerIntegration(unittest.TestCase):
    """Integration tests for Korean Dividend Analyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = KoreanDividendAnalyzer()
        
    def test_samsung_electronics_data_structure(self):
        """Test that Samsung Electronics has the expected data structure"""
        samsung_info = KOREAN_DIVIDEND_COMPANIES.get('삼성전자')
        self.assertIsNotNone(samsung_info)
        self.assertEqual(samsung_info['common'], '005930.KS')
        self.assertEqual(samsung_info['preferred'], '005935.KS')
        self.assertEqual(samsung_info['sector'], '전자/반도체')
        
    def test_all_companies_have_required_fields(self):
        """Test that all companies have required fields"""
        required_fields = ['common', 'name', 'sector']
        
        for company_name, company_info in KOREAN_DIVIDEND_COMPANIES.items():
            for field in required_fields:
                self.assertIn(field, company_info, 
                             f"Company {company_name} missing field: {field}")
                
    def test_ticker_format_validation(self):
        """Test that all ticker symbols follow Korean stock exchange format"""
        for company_name, company_info in KOREAN_DIVIDEND_COMPANIES.items():
            common_ticker = company_info['common']
            
            # Should be 6 digits + .KS
            self.assertRegex(common_ticker, r'^\d{6}\.KS$', 
                            f"Invalid ticker format for {company_name}: {common_ticker}")
            
            # If preferred stock exists, check its format too
            if 'preferred' in company_info:
                preferred_ticker = company_info['preferred']
                self.assertRegex(preferred_ticker, r'^\d{6}\.KS$',
                                f"Invalid preferred ticker format for {company_name}: {preferred_ticker}")


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(loader.loadTestsFromTestCase(TestKoreanDividendAnalyzer))
    suite.addTest(loader.loadTestsFromTestCase(TestKoreanDividendAnalyzerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
            
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
            
    if result.wasSuccessful():
        print("✅ All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed!")
        exit(1)