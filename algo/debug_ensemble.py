"""
Debug Ensemble Strategy
"""

from comprehensive_tests import TradingModelTester
from trading_engine import EnsembleStrategy

if __name__ == "__main__":
    # Get real data
    tester = TradingModelTester()
    data = tester._get_real_data("2023-01-01", "2025-12-31")

    if not data.empty:
        print(f"Data loaded: {len(data)} bars")

        # Test individual strategies
        ensemble = EnsembleStrategy()
        print(f"Ensemble has {len(ensemble.strategies)} strategies")

        for strategy in ensemble.strategies:
            signals = strategy.generate_signals(data.copy())
            signal_count = (signals != 0).sum()
            print(f"{strategy.name}: {signal_count} signals")

        # Test ensemble
        ensemble_signals = ensemble.generate_signals(data.copy())
        ensemble_count = (ensemble_signals != 0).sum()
        print(f"Ensemble: {ensemble_count} signals")
    else:
        print("No data available")