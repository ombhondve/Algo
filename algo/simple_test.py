"""
Simple test runner for trading model
"""

from comprehensive_tests import TradingModelTester

if __name__ == "__main__":
    tester = TradingModelTester()

    # Run just the data quality test
    print("Testing data quality...")
    tester.test_data_quality()

    print("\nTest completed.")