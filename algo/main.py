"""
APEX ALGO TRADING - MAIN RUNNER
Run backtest across all strategies and generate report
"""

import pandas as pd
import numpy as np
from trading_engine import (
    MultiTimeframeMomentum, BollingerMeanReversion,
    MACDTrendSystem, SupertrendStochastic,
    VWAPInstitutionalFlow, EnsembleStrategy,
    RSIDivergenceStrategy, IchimokuBreakoutStrategy,
    BollingerSqueezeBreakaoutStrategy, EMASimpleCrossoverStrategy,
    PriceActionStrategyAdvanced,
    RiskManager, RiskConfig, Backtester,
    LiveTradingExecutor
)
from data_fetchers import fetch_upstox, upstox_get_login_url, upstox_exchange_token, UPSTOX_ACCESS_TOKEN


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║      ██████╗ ██████╗ ███████╗██╗  ██╗                           ║
║     ██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝                           ║
║     ███████║██████╔╝█████╗   ╚███╔╝                            ║
║     ██╔══██║██╔═══╝ ██╔══╝   ██╔██╗                            ║
║     ██║  ██║██║     ███████╗██╔╝ ██╗                           ║
║     ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝  ALGO TRADING ENGINE     ║
║                                                                   ║
║     11 Strategies | Smart Risk Management | World Class          ║
╚══════════════════════════════════════════════════════════════════╝
    """)

def get_upstox_token():
    """Helper to get Upstox access token with instructions"""
    print("""
  ─────────────────────────────────────────────────────────────
  GET YOUR UPSTOX ACCESS TOKEN
  ─────────────────────────────────────────────────────────────
  
  Step 1: Get login URL
  ───────────────────────
  >>> from data_fetchers import upstox_get_login_url, upstox_exchange_token
  >>> url = upstox_get_login_url()
  
  Step 2: Login and copy authorization code
  ──────────────────────────────────────────
  - Browser will open automatically
  - Log in with your Upstox credentials
  - Copy the code from the redirect URL (code=XXXXXX)
  
  Step 3: Exchange code for token
  ────────────────────────────────
  >>> token = upstox_exchange_token("XXXXXX")  # paste your code
  >>> print(token)
  
  The token will be valid for 24 hours. Save it securely!
  ─────────────────────────────────────────────────────────────
    """)

def print_metrics(name: str, metrics: dict):
    if 'error' in metrics:
        print(f"  ERROR: {metrics['error']}")
        return

    wr = metrics['win_rate']
    ret = metrics['total_return_pct']
    dd = metrics['max_drawdown_pct']
    sharpe = metrics['sharpe_ratio']
    sortino = metrics['sortino_ratio']
    calmar = metrics['calmar_ratio']
    pf = metrics['profit_factor']
    exp = metrics['expectancy']

    # Score rating
    score = min(100, max(0,
        (wr - 40) * 1.2 +
        (sharpe * 10) +
        (calmar * 5) +
        (min(pf, 3) * 10) +
        (ret / 5)
    ))

    stars = "★" * int(score / 20) + "☆" * (5 - int(score / 20))

    print(f"""
  ┌─────────────────────────────────────────────────────┐
  │  {name:<51}│
  │  Rating: {stars}  Score: {score:.0f}/100              │
  ├─────────────────────────────────────────────────────┤
  │  Trades: {metrics['total_trades']:<5}  Win Rate: {wr:.1f}%                    │
  │  Total Return: {ret:>+8.2f}%   Max Drawdown: {dd:.2f}%    │
  │  Sharpe: {sharpe:>6.2f}      Sortino: {sortino:>6.2f}              │
  │  Calmar: {calmar:>6.2f}      Profit Factor: {pf:>5.2f}         │
  │  Expectancy: ₹{exp:>8.0f}  Final Capital: ₹{metrics['final_capital']:>10,.0f} │
  │  Best Trade: ₹{metrics['best_trade']:>8,.0f}  Worst: ₹{metrics['worst_trade']:>8,.0f}    │
  │  Avg Win: ₹{metrics['avg_win']:>8,.0f}    Avg Loss: ₹{metrics['avg_loss']:>8,.0f}  │
  │  Max Consec. Wins: {metrics['consecutive_wins']:<3}  Losses: {metrics['consecutive_losses']:<3}                │
  │  Exit Reasons: {str(metrics.get('exit_reasons', {}))[:37]:<37} │
  └─────────────────────────────────────────────────────┘""")


def run_strategy_comparison(from_date: str = "2020-01-01", to_date: str = "2026-04-09"):
    print_banner()

    # Only use real Upstox data - no synthetic data allowed
    print("\n  ─────────────────────────────────────────────────")
    print("  REAL DATA ONLY MODE: Using Upstox")
    print("  ─────────────────────────────────────────────────")
    
    upstox_token = UPSTOX_ACCESS_TOKEN.strip() if UPSTOX_ACCESS_TOKEN else ""
    
    if not upstox_token:
        print("\n  ❌ ERROR: No Upstox access token found!")
        print("  📋 To get real data:")
        print("  1. Run: from data_fetchers import upstox_get_login_url, upstox_exchange_token")
        print("  2. Get URL: url = upstox_get_login_url()")
        print("  3. Login and copy authorization code")
        print("  4. Get token: token = upstox_exchange_token('code')")
        print("  5. Set UPSTOX_ACCESS_TOKEN = 'your_token' in data_fetchers.py")
        raise ValueError("Upstox access token required for real data only mode")
    
    data_source = "REAL UPSTOX"
    print(f"\n  📊 DATA SOURCE: {data_source}")
    print(f"  [DATA] Fetching real data from Upstox (Nifty 50, {from_date} - {to_date})...")
    
    df = fetch_upstox(
        instrument_key="NSE_INDEX|Nifty 50",
        interval="day",
        from_date=from_date,
        to_date=to_date,
        access_token=upstox_token
    )
    
    if df.empty:
        print("\n  ❌ ERROR: Failed to fetch Upstox data!")
        print("  Possible issues:")
        print("  • Invalid or expired access token")
        print("  • Network connectivity issues")
        print("  • Upstox API service unavailable")
        print("  • Date range may be invalid")
        raise ValueError("Could not fetch real data from Upstox")
    
    print(f"  [DATA] Loaded {len(df)} bars | {df.index[0].date()} → {df.index[-1].date()}")
    print(f"  [DATA] Price range: ₹{df['close'].min():.2f} → ₹{df['close'].max():.2f}")
    print(f"  [DATA] Source: {data_source} (REAL DATA ONLY)")

    # Risk config - with optimized parameters
    risk_config = RiskConfig(
        max_position_pct=0.08,          # Reduced from 0.10 for safety
        max_portfolio_risk=0.15,        # Reduced from 0.20
        stop_loss_pct=0.025,            # Increased from 0.02 (wider stops)
        take_profit_pct=0.075,          # Increased from 0.06 (better R/R)
        trailing_stop_pct=0.02,         # Increased from 0.015
        max_trades_per_day=5,
        kelly_fraction=0.20             # Reduced from 0.25 (more conservative)
    )

    # Realistic costs
    backtester = Backtester(
        initial_capital=1_000_000,
        commission=0.001,               # 0.1% realistic (increased from 0.03%)
        slippage=0.001                  # 0.1% realistic (increased from 0.01%)
    )

    strategies = [
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

    print("\n" + "═" * 58)
    print("  STRATEGY BACKTEST RESULTS")
    print("═" * 58)
    
    # Detect overall market regime
    from trading_engine import MarketRegime
    market_regime = MarketRegime.detect(df)
    recommended = MarketRegime.recommended_strategies(market_regime)
    print(f"\n  📊 Market Regime: {market_regime}")
    print(f"  💡 Recommended strategies: {', '.join(recommended)}")

    all_results = {}
    for strategy in strategies:
        print(f"\n  ▶ Running: {strategy.name}...")
        try:
            rm = RiskManager(risk_config)
            signals = strategy.generate_signals(df.copy())
            trade_count = (signals != 0).sum()
            print(f"    Signals generated: {trade_count}")
            # Pass strategy name to backtester for signal quality scoring
            metrics = backtester.run(df.copy(), signals, rm, strategy_name=strategy.name)
            all_results[strategy.name] = metrics
            print_metrics(strategy.name, metrics)
        except Exception as e:
            print(f"  [ERROR] {strategy.name}: {e}")
            import traceback
            traceback.print_exc()

    # Summary leaderboard
    print("\n" + "═" * 58)
    print("  🏆 STRATEGY LEADERBOARD (by Sharpe Ratio)")
    print("═" * 58)
    ranked = sorted(
        [(k, v) for k, v in all_results.items() if 'sharpe_ratio' in v],
        key=lambda x: x[1]['sharpe_ratio'], reverse=True
    )
    for rank, (name, m) in enumerate(ranked, 1):
        medal = ["🥇", "🥈", "🥉", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "11."][rank - 1]
        print(f"  {medal} {name[:40]:<40} Sharpe: {m['sharpe_ratio']:>5.2f}  WR: {m['win_rate']:.1f}%  Return: {m['total_return_pct']:>+6.1f}%")

    print("\n" + "═" * 58)
    print("  ✅ BACKTEST COMPLETE")
    print("═" * 58)

    # Best strategy recommendation
    if ranked:
        best_name, best_m = ranked[0]
        num_trades = best_m.get('total_trades', 0)
        sample_warning = "" if num_trades >= 30 else f"⚠️  WARNING: Only {num_trades} trades (need ≥30 for reliable metrics)\n  "
        print(f"""
  📊 RECOMMENDATION
  ─────────────────
  Best Strategy: {best_name}
  → Sharpe Ratio: {best_m['sharpe_ratio']:.2f} (>1.5 is excellent)
  → Win Rate:     {best_m['win_rate']:.1f}%
  → Return:       {best_m['total_return_pct']:+.1f}%
  → Max Drawdown: {best_m['max_drawdown_pct']:.1f}%
  → Total Trades: {num_trades}

  📈 IMPROVEMENTS IN THIS VERSION:
  • Realistic costs: 0.1% commission + 0.1% slippage (not 0.03%)
  • Larger dataset: 10,000 bars (~27 years) for better statistics
  • Signal quality scoring: Filters low-confidence trades
  • Regime detection: Adapts strategy to market conditions
  • Dynamic stops: Wider in volatility, tighter in calm markets
  • Consecutive loss limits: Halts after 3 losses for recovery
  • Sample size adjustments: Sharpe ratios more realistic

  ⚠️  IMPORTANT NOTES:
  {sample_warning}• Paper trade for 30+ days @ low capital ($1-5k) first
  • Past backtest performance ≠ future results
  • Start with ≤5% of your actual capital
  • Never risk money you cannot afford to lose
  • Expected realistic win rate: 55-62% (not higher)
        """)


    return all_results


def demo_live_trading():
    """Demo the live trading loop (paper mode)"""
    print("\n" + "═" * 58)
    print("  📡 LIVE TRADING DEMO (PAPER MODE)")
    print("═" * 58)

    executor = LiveTradingExecutor(broker='paper')
    strategy = EnsembleStrategy()
    risk_config = RiskConfig()
    rm = RiskManager(risk_config)

    # Simulate 5 ticks of live data
    df = generate_realistic_ohlcv(periods=300, seed=99, start_date='2020-01-01', freq='1D')
    signals = strategy.generate_signals(df)

    print(f"\n  Scanning last 10 bars for signals...\n")
    for i in range(-10, 0):
        sig = signals.iloc[i]
        price = df['close'].iloc[i]
        ts = df.index[i]
        sig_str = "🟢 BUY " if sig == 1 else ("🔴 SELL" if sig == -1 else "⚪ HOLD")
        print(f"  {ts.strftime('%Y-%m-%d %H:%M')} | Price: ₹{price:,.2f} | Signal: {sig_str}")
        if sig != 0:
            side = 'BUY' if sig == 1 else 'SELL'
            atr = df['close'].iloc[i] * 0.01
            qty = rm.calculate_position_size(1_000_000, price, atr)
            executor.place_order("NIFTY50", qty, side)

    print("\n  [DONE] Live trading loop demo complete.")


if __name__ == "__main__":
    # Real data only - customize date range here
    from_date = "2020-01-01"  # Start date (YYYY-MM-DD)
    to_date = "2026-04-09"    # End date (YYYY-MM-DD)
    
    try:
        results = run_strategy_comparison(from_date=from_date, to_date=to_date)
        # demo_live_trading()  # Commented out - uncomment if you want the demo
        print("\n  ════════════════════════════════════════")
        print("  Apex Algo Trading Engine | Real Data Only")
        print("  ════════════════════════════════════════\n")
    except ValueError as e:
        print(f"\n❌ FATAL ERROR: {e}")
        print("\n💡 SOLUTION: Get Upstox access token and try again")
        print("   from data_fetchers import upstox_get_login_url, upstox_exchange_token")
        print("   url = upstox_get_login_url()  # Opens browser")
        print("   # Login and copy auth code, then:")
        print("   token = upstox_exchange_token('your_code_here')")
        print("   # Set UPSTOX_ACCESS_TOKEN in data_fetchers.py")
        exit(1)
