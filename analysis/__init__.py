from analysis.rsi_analyzer import RSIAnalyzer
from analysis.atr_analyzer import ATRAnalyzer

# アナライザーインスタンス
_rsi_analyzer = RSIAnalyzer()
_atr_analyzer = ATRAnalyzer()

def render_rsi_analysis(trades_df):
    """RSI分析を表示"""
    return _rsi_analyzer.render_rsi_analysis(trades_df)

def render_atr_analysis(trades_df):
    """ATR分析を表示"""
    return _atr_analyzer.render_atr_analysis(trades_df) 