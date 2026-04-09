"""
Partial test runner for trading model
"""

from comprehensive_tests import TradingModelTester

if __name__ == "__main__":
    tester = TradingModelTester()

    print("Running partial comprehensive tests...")

    # Run first 3 tests
    tester.test_data_quality()
    tester.test_strategy_performance()
    tester.test_risk_management()

    print("\nPartial tests completed.")