"""
Remaining test runner for trading model
"""

from comprehensive_tests import TradingModelTester

if __name__ == "__main__":
    tester = TradingModelTester()

    print("Running remaining comprehensive tests...")

    # Run remaining tests
    tester.test_market_regimes()
    tester.test_stress_scenarios()
    tester.test_parameter_sensitivity()
    tester.test_statistical_robustness()
    tester.test_walk_forward_analysis()
    tester.test_out_of_sample()

    # Generate final report
    tester.generate_test_report()

    print("\nRemaining tests completed.")