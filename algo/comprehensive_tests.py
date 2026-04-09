"""
APEX ALGO TRADING - COMPREHENSIVE TEST SUITE
Run all tests that the trading model should face
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from trading_engine import (
    MultiTimeframeMomentum, BollingerMeanReversion,
    MACDTrendSystem, SupertrendStochastic,
    VWAPInstitutionalFlow, EnsembleStrategy,
    RSIDivergenceStrategy, IchimokuBreakoutStrategy,
    BollingerSqueezeBreakaoutStrategy, EMASimpleCrossoverStrategy,
    PriceActionStrategyAdvanced,
    RiskManager, RiskConfig, Backtester,
    LiveTradingExecutor, MarketRegime
)
from data_fetchers import fetch_upstox, UPSTOX_ACCESS_TOKEN


class TradingModelTester:
    """Comprehensive test suite for the trading model"""

    def __init__(self):
        self.strategies = [
            MultiTimeframeMomentum(),
            BollingerMeanReversion(),
            MACDTrendSystem(),
            SupertrendStochastic(),
            VWAPInstitutionalFlow(),
            RSIDivergenceStrategy(),
            IchimokuBreakoutStrategy(),
            BollingerSqueezeBreakaoutStrategy(),
            EMASimpleCrossoverStrategy(),
            PriceActionStrategyAdvanced(),
            EnsembleStrategy(),
        ]

        self.test_results = {}

    def run_all_tests(self):
        """Run the complete test suite"""
        print("🚀 STARTING COMPREHENSIVE TRADING MODEL TEST SUITE")
        print("=" * 60)

        # 1. Data Quality Tests
        self.test_data_quality()

        # 2. Strategy Performance Tests
        self.test_strategy_performance()

        # 3. Risk Management Tests
        self.test_risk_management()

        # 4. Market Regime Tests
        self.test_market_regimes()

        # 5. Stress Tests
        self.test_stress_scenarios()

        # 6. Parameter Sensitivity Tests
        self.test_parameter_sensitivity()

        # 7. Statistical Robustness Tests
        self.test_statistical_robustness()

        # 8. Walk-Forward Analysis
        self.test_walk_forward_analysis()

        # 9. Out-of-Sample Tests
        self.test_out_of_sample()

        # 10. Final Report
        self.generate_test_report()

    def test_data_quality(self):
        """Test 1: Data Quality and Robustness"""
        print("\n📊 TEST 1: DATA QUALITY & ROBUSTNESS")
        print("-" * 40)

        # Test with real data only
        print("  ▶ Testing with Real Upstox Data...")
        real_data = self._get_real_data("2023-01-01", "2025-12-31")
        if not real_data.empty:
            print(f"    ✅ Real data loaded: {len(real_data)} bars")
        else:
            print("    ❌ No real data available - skipping data quality tests")
            self.test_results['data_quality'] = {'error': 'No real data available'}
            return

        # Test data preprocessing
        print("  ▶ Testing Data Preprocessing...")
        processed_data = self._preprocess_data(real_data.copy())
        print(f"    ✅ Data preprocessing complete: {len(processed_data)} bars")

        # Test missing data handling
        print("  ▶ Testing Missing Data Handling...")
        corrupted_data = real_data.copy()
        corrupted_data.loc[corrupted_data.sample(frac=0.05).index, 'close'] = np.nan  # Less corruption
        cleaned_data = self._handle_missing_data(corrupted_data)
        print(f"    ✅ Missing data handled: {len(cleaned_data)} bars")

        self.test_results['data_quality'] = {
            'real_data_bars': len(real_data),
            'processed_bars': len(processed_data),
            'cleaned_bars': len(cleaned_data)
        }

    def test_strategy_performance(self):
        """Test 2: Individual Strategy Performance"""
        print("\n📈 TEST 2: STRATEGY PERFORMANCE")
        print("-" * 40)

        # Use real data only
        data = self._get_real_data("2020-01-01", "2025-12-31")
        if data.empty:
            print("    ❌ No real data available - skipping strategy tests")
            self.test_results['strategy_performance'] = {'error': 'No real data available'}
            return
        risk_config = RiskConfig()
        backtester = Backtester(initial_capital=100000)

        strategy_results = {}

        for strategy in self.strategies:
            print(f"  ▶ Testing {strategy.name}...")

            try:
                signals = strategy.generate_signals(data.copy())
                rm = RiskManager(risk_config)
                metrics = backtester.run(data.copy(), signals, rm, strategy_name=strategy.name)

                strategy_results[strategy.name] = {
                    'total_return': metrics.get('total_return_pct', 0),
                    'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                    'win_rate': metrics.get('win_rate', 0),
                    'max_drawdown': metrics.get('max_drawdown_pct', 0),
                    'total_trades': metrics.get('total_trades', 0),
                    'profit_factor': metrics.get('profit_factor', 0)
                }

                print(f"    ✅ Sharpe: {metrics.get('sharpe_ratio', 0):.2f}, "
                      f"Return: {metrics.get('total_return_pct', 0):.2f}%, "
                      f"Trades: {metrics.get('total_trades', 0)}")

            except Exception as e:
                print(f"    ❌ Error: {e}")
                strategy_results[strategy.name] = {'error': str(e)}

        self.test_results['strategy_performance'] = strategy_results

    def test_risk_management(self):
        """Test 3: Risk Management Systems"""
        print("\n⚠️  TEST 3: RISK MANAGEMENT")
        print("-" * 40)

        # Use real data only
        data = self._get_real_data("2020-01-01", "2025-12-31")
        if data.empty:
            print("    ❌ No real data available - skipping risk management tests")
            self.test_results['risk_management'] = {'error': 'No real data available'}
            return

        strategy = EnsembleStrategy()

        # Test different risk configurations
        risk_configs = [
            {'name': 'Conservative', 'kelly_fraction': 0.1, 'max_position_pct': 0.05},
            {'name': 'Moderate', 'kelly_fraction': 0.25, 'max_position_pct': 0.10},
            {'name': 'Aggressive', 'kelly_fraction': 0.5, 'max_position_pct': 0.20}
        ]

        risk_results = {}

        for config in risk_configs:
            print(f"  ▶ Testing {config['name']} Risk Profile...")

            risk_cfg = RiskConfig(
                kelly_fraction=config['kelly_fraction'],
                max_position_pct=config['max_position_pct']
            )

            backtester = Backtester(initial_capital=100000)
            signals = strategy.generate_signals(data.copy())
            rm = RiskManager(risk_cfg)
            metrics = backtester.run(data.copy(), signals, rm)

            risk_results[config['name']] = {
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'max_drawdown': metrics.get('max_drawdown_pct', 0),
                'total_return': metrics.get('total_return_pct', 0),
                'portfolio_risk': config['kelly_fraction']
            }

            print(f"    ✅ Sharpe: {metrics.get('sharpe_ratio', 0):.2f}, "
                  f"Max DD: {metrics.get('max_drawdown_pct', 0):.2f}%")

        self.test_results['risk_management'] = risk_results

    def test_market_regimes(self):
        """Test 4: Performance Across Market Regimes"""
        print("\n🌊 TEST 4: MARKET REGIME ADAPTATION")
        print("-" * 40)

        # Use different periods of real data to represent different market conditions
        regime_periods = {
            'BULL_MARKET': {'start': '2023-01-01', 'end': '2023-12-31'},  # Post-COVID recovery
            'BEAR_MARKET': {'start': '2022-01-01', 'end': '2022-12-31'},  # COVID bear market
            'SIDEWAYS': {'start': '2021-01-01', 'end': '2021-12-31'},     # Consolidation
            'RECENT': {'start': '2024-01-01', 'end': '2025-12-31'}        # Current market
        }

        regime_results = {}

        for regime_name, period in regime_periods.items():
            print(f"  ▶ Testing in {regime_name} Market...")

            # Get real data for this period
            data = self._get_real_data(period['start'], period['end'])
            if data.empty:
                print(f"    ⚠️  No data available for {regime_name}")
                continue

            # Detect regime
            detected_regime = MarketRegime.detect(data)
            recommended_strategies = MarketRegime.recommended_strategies(detected_regime)

            # Test ensemble strategy
            strategy = EnsembleStrategy()
            signals = strategy.generate_signals(data.copy())
            backtester = Backtester(initial_capital=100000)
            rm = RiskManager(RiskConfig())
            metrics = backtester.run(data.copy(), signals, rm)

            regime_results[regime_name] = {
                'detected_regime': detected_regime,
                'recommended_strategies': recommended_strategies,
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'total_return': metrics.get('total_return_pct', 0),
                'win_rate': metrics.get('win_rate', 0),
                'data_points': len(data)
            }

            print(f"    ✅ Detected: {detected_regime}, Sharpe: {metrics.get('sharpe_ratio', 0):.2f}, Data: {len(data)} bars")

        self.test_results['market_regimes'] = regime_results

    def test_stress_scenarios(self):
        """Test 5: Stress Testing with Historical Crises"""
        print("\n💥 TEST 5: STRESS SCENARIOS")
        print("-" * 40)

        # Test with real historical crisis periods (available in our data)
        stress_periods = {
            'COVID_Crash': {'start': '2020-02-01', 'end': '2020-04-30'},  # COVID crash period
            'Post_COVID': {'start': '2020-05-01', 'end': '2020-12-31'},   # Recovery period
            '2022_Bear': {'start': '2022-01-01', 'end': '2022-06-30'},    # 2022 bear market
            '2022_Recovery': {'start': '2022-07-01', 'end': '2022-12-31'} # Recovery period
        }

        stress_results = {}

        for scenario_name, period in stress_periods.items():
            print(f"  ▶ Testing {scenario_name} Scenario...")

            # Get real historical data for crisis period
            data = self._get_real_data(period['start'], period['end'])
            if data.empty:
                print(f"    ⚠️  No data available for {scenario_name}")
                continue

            # Test strategy performance during this period
            strategy = EnsembleStrategy()
            signals = strategy.generate_signals(data.copy())
            backtester = Backtester(initial_capital=100000)
            rm = RiskManager(RiskConfig())
            metrics = backtester.run(data.copy(), signals, rm)

            stress_results[scenario_name] = {
                'max_drawdown': metrics.get('max_drawdown_pct', 0),
                'total_return': metrics.get('total_return_pct', 0),
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'survival_rate': 1 if metrics.get('final_capital', 0) > 50000 else 0,  # >50% capital preserved
                'data_points': len(data)
            }

            print(f"    ✅ Max DD: {metrics.get('max_drawdown_pct', 0):.1f}%, "
                  f"Return: {metrics.get('total_return_pct', 0):.1f}%, Data: {len(data)} bars")

        self.test_results['stress_scenarios'] = stress_results

    def test_parameter_sensitivity(self):
        """Test 6: Enhanced Parameter Sensitivity Analysis"""
        print("\n🔧 TEST 6: PARAMETER SENSITIVITY")
        print("-" * 40)

        # Use real data for parameter testing
        data = self._get_real_data("2023-01-01", "2025-12-31")
        if data.empty:
            print("    ❌ No real data available - skipping parameter sensitivity tests")
            self.test_results['parameter_sensitivity'] = {'error': 'No real data available'}
            return

        # Test multiple strategies with different parameter combinations
        strategies = [
            ('Bollinger Mean Reversion', BollingerMeanReversion()),
            ('Advanced Ensemble', EnsembleStrategy()),
            ('MACD Trend System', MACDTrendSystem())
        ]

        # Comprehensive parameter combinations
        param_sets = [
            {'name': 'Conservative', 'stop_loss': 0.015, 'take_profit': 0.045, 'kelly_fraction': 0.15, 'max_positions': 3},
            {'name': 'Moderate', 'stop_loss': 0.025, 'take_profit': 0.075, 'kelly_fraction': 0.25, 'max_positions': 5},
            {'name': 'Aggressive', 'stop_loss': 0.035, 'take_profit': 0.105, 'kelly_fraction': 0.35, 'max_positions': 8},
            {'name': 'High Frequency', 'stop_loss': 0.01, 'take_profit': 0.03, 'kelly_fraction': 0.1, 'max_positions': 10}
        ]

        sensitivity_results = {}

        for strategy_name, strategy in strategies:
            print(f"  ▶ Testing {strategy_name} with different parameters...")

            strategy_results = {}
            for param_set in param_sets:
                risk_config = RiskConfig(
                    stop_loss_pct=param_set['stop_loss'],
                    take_profit_pct=param_set['take_profit'],
                    kelly_fraction=param_set['kelly_fraction'],
                    max_trades_per_day=param_set['max_positions'] * 20  # Scale up for testing
                )

                try:
                    signals = strategy.generate_signals(data.copy())
                    backtester = Backtester(initial_capital=100000)
                    rm = RiskManager(risk_config)
                    metrics = backtester.run(data.copy(), signals, rm)

                    strategy_results[param_set['name']] = {
                        'parameters': param_set,
                        'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                        'total_return': metrics.get('total_return_pct', 0),
                        'max_drawdown': metrics.get('max_drawdown_pct', 0),
                        'win_rate': metrics.get('win_rate', 0),
                        'profit_factor': metrics.get('profit_factor', 1.0),
                        'total_trades': metrics.get('total_trades', 0)
                    }

                    print(f"    ✅ {param_set['name']}: Sharpe {metrics.get('sharpe_ratio', 0):.2f}, "
                          f"Return {metrics.get('total_return_pct', 0):.2f}%, "
                          f"Trades: {metrics.get('total_trades', 0)}")

                except Exception as e:
                    print(f"    ❌ {param_set['name']} failed: {e}")
                    strategy_results[param_set['name']] = {'error': str(e)}

            sensitivity_results[strategy_name] = strategy_results

        # Calculate optimal parameters for each strategy
        for strategy_name, results in sensitivity_results.items():
            if not results:
                continue

            # Find best parameter set based on risk-adjusted return
            best_params = None
            best_score = -float('inf')

            for param_name, metrics in results.items():
                if 'error' in metrics:
                    continue

                # Risk-adjusted score: Sharpe ratio with penalty for high drawdown
                sharpe = metrics['sharpe_ratio']
                drawdown_penalty = metrics['max_drawdown'] * 0.1  # Penalize high drawdown
                score = sharpe - drawdown_penalty

                if score > best_score:
                    best_score = score
                    best_params = param_name

            if best_params:
                sensitivity_results[strategy_name]['optimal_parameters'] = best_params
                print(f"    🎯 {strategy_name} Optimal: {best_params}")

        self.test_results['parameter_sensitivity'] = sensitivity_results

    def test_statistical_robustness(self):
        """Test 7: Enhanced Statistical Significance and Robustness"""
        print("\n📊 TEST 7: STATISTICAL ROBUSTNESS")
        print("-" * 40)

        # Use real data for robustness testing
        full_data = self._get_real_data("2020-01-01", "2025-12-31")
        if full_data.empty or len(full_data) < 500:
            print("    ❌ Insufficient real data - skipping statistical robustness tests")
            self.test_results['statistical_robustness'] = {'error': 'Insufficient real data'}
            return

        # Enhanced bootstrap analysis with multiple strategies
        bootstrap_results = []
        strategies = [
            BollingerMeanReversion(),
            EnsembleStrategy(),
            MACDTrendSystem(),
            RSIDivergenceStrategy()
        ]

        print("  ▶ Running Enhanced Bootstrap Analysis (50 runs across multiple strategies)...")

        for run in range(50):  # Increased from 30
            # Sample random subset of real data (60-90% of available data)
            sample_size = np.random.randint(int(len(full_data) * 0.6), int(len(full_data) * 0.9))
            sampled_data = full_data.sample(n=sample_size, replace=False).sort_index()

            run_results = {'run': run, 'sample_size': len(sampled_data)}

            for strategy in strategies:
                try:
                    signals = strategy.generate_signals(sampled_data.copy())
                    backtester = Backtester(initial_capital=100000)
                    rm = RiskManager(RiskConfig())
                    metrics = backtester.run(sampled_data.copy(), signals, rm)

                    strategy_key = strategy.name.replace(' ', '_').lower()
                    run_results[f'{strategy_key}_sharpe'] = metrics.get('sharpe_ratio', 0)
                    run_results[f'{strategy_key}_return'] = metrics.get('total_return_pct', 0)
                    run_results[f'{strategy_key}_max_dd'] = metrics.get('max_drawdown_pct', 0)
                    run_results[f'{strategy_key}_win_rate'] = metrics.get('win_rate', 0)
                    run_results[f'{strategy_key}_profit_factor'] = metrics.get('profit_factor', 1.0)

                except Exception as e:
                    print(f"    [WARN] Strategy {strategy.name} failed in run {run}: {e}")
                    strategy_key = strategy.name.replace(' ', '_').lower()
                    run_results[f'{strategy_key}_sharpe'] = 0
                    run_results[f'{strategy_key}_return'] = 0
                    run_results[f'{strategy_key}_max_dd'] = 0
                    run_results[f'{strategy_key}_win_rate'] = 0
                    run_results[f'{strategy_key}_profit_factor'] = 1.0

            bootstrap_results.append(run_results)

        # Calculate comprehensive statistics
        robustness_stats = {}

        for strategy in strategies:
            strategy_key = strategy.name.replace(' ', '_').lower()

            sharpe_ratios = [r[f'{strategy_key}_sharpe'] for r in bootstrap_results]
            returns = [r[f'{strategy_key}_return'] for r in bootstrap_results]
            win_rates = [r[f'{strategy_key}_win_rate'] for r in bootstrap_results]
            profit_factors = [r[f'{strategy_key}_profit_factor'] for r in bootstrap_results]

            robustness_stats[strategy_key] = {
                'sharpe_mean': np.mean(sharpe_ratios),
                'sharpe_std': np.std(sharpe_ratios),
                'sharpe_min': np.min(sharpe_ratios),
                'sharpe_max': np.max(sharpe_ratios),
                'return_mean': np.mean(returns),
                'return_std': np.std(returns),
                'positive_sharpe_pct': (np.array(sharpe_ratios) > 0).mean() * 100,
                'profitable_runs_pct': (np.array(returns) > 0).mean() * 100,
                'win_rate_mean': np.mean(win_rates),
                'profit_factor_mean': np.mean(profit_factors),
                'consistency_score': self._calculate_consistency_score(sharpe_ratios, returns)
            }

        # Overall robustness score (weighted average of key metrics)
        ensemble_stats = robustness_stats['advanced_ensemble_strategy']
        bollinger_stats = robustness_stats['bollinger_mean_reversion']

        overall_score = (
            ensemble_stats['positive_sharpe_pct'] * 0.3 +
            ensemble_stats['profitable_runs_pct'] * 0.3 +
            ensemble_stats['consistency_score'] * 0.2 +
            bollinger_stats['positive_sharpe_pct'] * 0.1 +
            bollinger_stats['profitable_runs_pct'] * 0.1
        )

        robustness_stats['overall_score'] = overall_score
        robustness_stats['bootstrap_runs'] = len(bootstrap_results)

        # Print results
        print(f"    ✅ Ensemble Strategy - Sharpe: {ensemble_stats['sharpe_mean']:.2f} ± {ensemble_stats['sharpe_std']:.2f}")
        print(f"    ✅ Ensemble Strategy - Positive Sharpe: {ensemble_stats['positive_sharpe_pct']:.1f}%")
        print(f"    ✅ Ensemble Strategy - Profitable Runs: {ensemble_stats['profitable_runs_pct']:.1f}%")
        print(f"    ✅ Bollinger Strategy - Sharpe: {bollinger_stats['sharpe_mean']:.2f} ± {bollinger_stats['sharpe_std']:.2f}")
        print(f"    ✅ Bollinger Strategy - Positive Sharpe: {bollinger_stats['positive_sharpe_pct']:.1f}%")
        print(f"    ✅ Overall Robustness Score: {overall_score:.1f}/100")

        self.test_results['statistical_robustness'] = robustness_stats

    def _calculate_consistency_score(self, sharpe_ratios, returns):
        """Calculate consistency score based on Sharpe ratio stability and profitability"""
        sharpe_std = np.std(sharpe_ratios)
        positive_sharpe_pct = (np.array(sharpe_ratios) > 0).mean() * 100
        profitable_pct = (np.array(returns) > 0).mean() * 100

        # Penalize high volatility in Sharpe ratios
        volatility_penalty = max(0, sharpe_std - 1.0) * 10

        # Reward consistency and profitability
        consistency_score = (
            positive_sharpe_pct * 0.4 +
            profitable_pct * 0.4 +
            (2.0 - min(2.0, sharpe_std)) * 10  # Reward low volatility
        ) - volatility_penalty

        return max(0, min(100, consistency_score))

        self.test_results['statistical_robustness'] = robustness_stats

    def test_walk_forward_analysis(self):
        """Test 8: Walk-Forward Analysis"""
        print("\n🚶 TEST 8: WALK-FORWARD ANALYSIS")
        print("-" * 40)

        # Use real data for walk-forward analysis
        data = self._get_real_data("2020-01-01", "2025-12-31")
        if data.empty or len(data) < 300:
            print("    ❌ Insufficient real data - skipping walk-forward analysis")
            self.test_results['walk_forward'] = {'error': 'Insufficient real data'}
            return

        strategy = EnsembleStrategy()

        walk_forward_results = []
        window_size = min(200, len(data) // 3)  # Adaptive window size
        step_size = max(30, window_size // 6)   # Adaptive step size

        print(f"  ▶ Running Walk-Forward Analysis (window: {window_size}, step: {step_size})...")

        for i in range(0, len(data) - window_size, step_size):
            train_end = i + window_size
            test_end = min(train_end + step_size, len(data))

            if test_end > len(data):
                break

            # Training period (not used in this simplified version)
            # Test period
            test_data = data.iloc[train_end:test_end]

            if len(test_data) < 10:  # Skip very small test windows
                continue

            # Generate signals on test data
            signals = strategy.generate_signals(test_data.copy())
            backtester = Backtester(initial_capital=100000)
            rm = RiskManager(RiskConfig())
            metrics = backtester.run(test_data.copy(), signals, rm)

            walk_forward_results.append({
                'window': f"{test_data.index[0].date()}-{test_data.index[-1].date()}",
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'total_return': metrics.get('total_return_pct', 0),
                'win_rate': metrics.get('win_rate', 0),
                'test_size': len(test_data)
            })

        if not walk_forward_results:
            print("    ❌ No valid walk-forward windows - insufficient data")
            self.test_results['walk_forward'] = {'error': 'No valid windows'}
            return

        # Calculate walk-forward statistics
        wf_sharpes = [r['sharpe_ratio'] for r in walk_forward_results]
        wf_stats = {
            'mean_sharpe': np.mean(wf_sharpes),
            'sharpe_consistency': (np.array(wf_sharpes) > 0).mean() * 100,
            'sharpe_volatility': np.std(wf_sharpes),
            'total_windows': len(walk_forward_results)
        }

        print(f"    ✅ Walk-Forward Sharpe: {wf_stats['mean_sharpe']:.2f}")
        print(f"    ✅ Consistency: {wf_stats['sharpe_consistency']:.1f}% positive")

        self.test_results['walk_forward'] = wf_stats

    def test_out_of_sample(self):
        """Test 9: Out-of-Sample Testing"""
        print("\n🎯 TEST 9: OUT-OF-SAMPLE TESTING")
        print("-" * 40)

        # Use real data and split chronologically
        full_data = self._get_real_data("2020-01-01", "2025-12-31")
        if full_data.empty or len(full_data) < 200:
            print("    ❌ Insufficient real data - skipping out-of-sample tests")
            self.test_results['out_of_sample'] = {'error': 'Insufficient real data'}
            return

        # Split chronologically: earlier data = in-sample, later data = out-of-sample
        split_point = int(len(full_data) * 0.7)
        in_sample = full_data.iloc[:split_point]
        out_sample = full_data.iloc[split_point:]

        strategy = EnsembleStrategy()

        print("  ▶ Testing In-Sample Performance...")
        signals_is = strategy.generate_signals(in_sample.copy())
        backtester = Backtester(initial_capital=100000)
        rm = RiskManager(RiskConfig())
        metrics_is = backtester.run(in_sample.copy(), signals_is, rm)

        print("  ▶ Testing Out-of-Sample Performance...")
        signals_oos = strategy.generate_signals(out_sample.copy())
        metrics_oos = backtester.run(out_sample.copy(), signals_oos, rm)

        oos_results = {
            'in_sample': {
                'sharpe_ratio': metrics_is.get('sharpe_ratio', 0),
                'total_return': metrics_is.get('total_return_pct', 0),
                'win_rate': metrics_is.get('win_rate', 0),
                'period': f"{in_sample.index[0].date()} to {in_sample.index[-1].date()}"
            },
            'out_of_sample': {
                'sharpe_ratio': metrics_oos.get('sharpe_ratio', 0),
                'total_return': metrics_oos.get('total_return_pct', 0),
                'win_rate': metrics_oos.get('win_rate', 0),
                'period': f"{out_sample.index[0].date()} to {out_sample.index[-1].date()}"
            },
            'oos_degradation': {
                'sharpe_degradation': metrics_oos.get('sharpe_ratio', 0) - metrics_is.get('sharpe_ratio', 0),
                'return_degradation': metrics_oos.get('total_return_pct', 0) - metrics_is.get('total_return_pct', 0)
            }
        }

        print(f"    ✅ In-Sample Sharpe: {metrics_is.get('sharpe_ratio', 0):.2f}")
        print(f"    ✅ Out-of-Sample Sharpe: {metrics_oos.get('sharpe_ratio', 0):.2f}")
        print(f"    ✅ Degradation: {oos_results['oos_degradation']['sharpe_degradation']:.2f}")

        self.test_results['out_of_sample'] = oos_results

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 60)

        # Overall Assessment
        print("\n🎯 OVERALL ASSESSMENT")
        print("-" * 30)

        # Calculate composite score
        scores = []

        # Strategy Performance Score (0-100)
        if 'strategy_performance' in self.test_results:
            strat_results = self.test_results['strategy_performance']
            valid_strategies = [s for s in strat_results.values() if 'error' not in s]
            if valid_strategies:
                avg_sharpe = np.mean([s['sharpe_ratio'] for s in valid_strategies])
                strat_score = min(100, max(0, (avg_sharpe + 2) * 25))  # Scale to 0-100
                scores.append(('Strategy Performance', strat_score))

        # Risk Management Score
        if 'risk_management' in self.test_results:
            risk_results = self.test_results['risk_management']
            conservative_dd = risk_results.get('Conservative', {}).get('max_drawdown', 100)
            risk_score = max(0, 100 - conservative_dd * 10)  # Lower DD = higher score
            scores.append(('Risk Management', risk_score))

        # Statistical Robustness Score
        if 'statistical_robustness' in self.test_results:
            robust_results = self.test_results['statistical_robustness']
            consistency_score = robust_results.get('positive_sharpe_pct', 0)
            scores.append(('Statistical Robustness', consistency_score))

        # Market Regime Adaptation Score
        if 'market_regimes' in self.test_results:
            regime_results = self.test_results['market_regimes']
            avg_regime_sharpe = np.mean([r['sharpe_ratio'] for r in regime_results.values()])
            regime_score = min(100, max(0, (avg_regime_sharpe + 1) * 50))
            scores.append(('Market Adaptation', regime_score))

        # Overall Score
        if scores:
            overall_score = np.mean([score for _, score in scores])
            print(f"🏆 OVERALL MODEL SCORE: {overall_score:.1f}/100")

            for test_name, score in scores:
                status = "✅ PASS" if score >= 60 else "⚠️  MARGINAL" if score >= 40 else "❌ FAIL"
                print(f"  {test_name}: {score:.1f}/100 - {status}")

        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 20)

        if 'strategy_performance' in self.test_results:
            strat_results = self.test_results['strategy_performance']
            best_strategy = max(strat_results.items(),
                              key=lambda x: x[1].get('sharpe_ratio', -999) if 'error' not in x[1] else -999)
            if best_strategy[1].get('sharpe_ratio', 0) > 0:
                print(f"✅ Best Strategy: {best_strategy[0]} (Sharpe: {best_strategy[1]['sharpe_ratio']:.2f})")
            else:
                print("⚠️  No strategy achieved positive Sharpe ratio")

        if 'statistical_robustness' in self.test_results:
            robust = self.test_results['statistical_robustness']
            if robust.get('positive_sharpe_pct', 0) < 70:
                print("⚠️  Low statistical significance - results may be due to chance")

        if 'out_of_sample' in self.test_results:
            oos = self.test_results['out_of_sample']
            degradation = oos['oos_degradation']['sharpe_degradation']
            if degradation < -0.5:
                print("⚠️  Significant out-of-sample degradation detected")

        print("\n🚀 DEPLOYMENT READINESS")
        print("-" * 25)
        if scores and np.mean([score for _, score in scores]) >= 60:
            print("✅ MODEL READY FOR PAPER TRADING")
            print("   • Start with $1,000-5,000 capital")
            print("   • Monitor for 30+ trades")
            print("   • Track live vs backtest performance")
        else:
            print("⚠️  MODEL NEEDS IMPROVEMENT")
            print("   • Address failing test categories")
            print("   • Consider strategy optimization")
            print("   • Increase sample sizes")

        print("\n" + "=" * 60)
        print("🏁 COMPREHENSIVE TESTING COMPLETE")
        print("=" * 60)

    # Helper methods
    def _get_real_data(self, from_date, to_date):
        """Get real market data"""
        if UPSTOX_ACCESS_TOKEN:
            try:
                return fetch_upstox(
                    instrument_key="NSE_INDEX|Nifty 50",
                    interval="day",
                    from_date=from_date,
                    to_date=to_date,
                    access_token=UPSTOX_ACCESS_TOKEN
                )
            except:
                pass
        return pd.DataFrame()

    def _preprocess_data(self, data):
        """Basic data preprocessing"""
        # Remove any NaN values
        data = data.dropna()

        # Ensure proper OHLCV columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if all(col in data.columns for col in required_cols):
            return data[required_cols]

        return data

    def _handle_missing_data(self, data):
        """Handle missing data points"""
        # Forward fill missing values
        data = data.ffill()

        # If still missing, use interpolation
        data = data.interpolate(method='linear')

        # Drop any remaining NaN
        return data.dropna()


def run_comprehensive_tests():
    """Main function to run all tests"""
    tester = TradingModelTester()
    tester.run_all_tests()
    return tester.test_results


if __name__ == "__main__":
    results = run_comprehensive_tests()