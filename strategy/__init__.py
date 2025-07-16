from strategy.strategy_factory import StrategyFactory

# ファクトリーインスタンス
_strategy_factory = StrategyFactory()

def detect_perfect_order(df):
    """パーフェクトオーダーを検出"""
    detector = _strategy_factory.get_perfect_order_detector()
    return detector.detect_perfect_order(df)

def analyze_trading_signals(df, n_continued=1):
    """取引シグナルを分析"""
    analyzer = _strategy_factory.get_signal_analyzer()
    return analyzer.analyze_trading_signals(df, n_continued)

def calculate_strategy_performance(df, atr_multiple=2):
    """戦略のパフォーマンスを計算"""
    calculator = _strategy_factory.get_performance_calculator()
    return calculator.calculate_strategy_performance(df)

def get_strategy_statistics(trades_df):
    """戦略統計を取得"""
    calculator = _strategy_factory.get_statistics_calculator()
    return calculator.get_strategy_statistics(trades_df)

def calculate_atr(df, period=14):
    """ATR（Average True Range）を計算"""
    calculator = _strategy_factory.get_performance_calculator()
    return calculator.calculate_atr(df, period) 