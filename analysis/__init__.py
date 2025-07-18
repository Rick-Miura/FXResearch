from analysis.base_analyzer import BaseAnalyzer
from analysis.rsi_analyzer import RSIAnalyzer
from analysis.atr_analyzer import ATRAnalyzer
from analysis.price_deviation_analyzer import PriceDeviationAnalyzer
from analysis.ma_slope_analyzer import MASlopeAnalyzer
from analysis.volatility_analyzer import VolatilityAnalyzer
from analysis.trend_strength_analyzer import TrendStrengthAnalyzer
from analysis.win_rate_analyzer import WinRateAnalyzer
from analysis.rsi_divergence_analyzer import RSIDivergenceAnalyzer
from analysis.overall_analysis import render_overall_analysis

# アナライザーインスタンス
_rsi_analyzer = RSIAnalyzer()
_atr_analyzer = ATRAnalyzer()
_price_deviation_analyzer = PriceDeviationAnalyzer()
_ma_slope_analyzer = MASlopeAnalyzer()
_volatility_analyzer = VolatilityAnalyzer()
_trend_strength_analyzer = TrendStrengthAnalyzer()
_win_rate_analyzer = WinRateAnalyzer()
_rsi_divergence_analyzer = RSIDivergenceAnalyzer()

def render_rsi_analysis(trades_df):
    """RSI分析を表示"""
    return _rsi_analyzer.render_rsi_analysis(trades_df)

def render_atr_analysis(trades_df):
    """ATR分析を表示"""
    return _atr_analyzer.render_atr_analysis(trades_df)

def render_price_deviation_analysis(trades_df):
    """価格乖離率分析を表示"""
    return _price_deviation_analyzer.render_price_deviation_analysis(trades_df)

def render_ma_slope_analysis(trades_df):
    """MA傾き分析を表示"""
    return _ma_slope_analyzer.render_ma_slope_analysis(trades_df)

def render_volatility_analysis(trades_df):
    """ボラティリティ分析を表示"""
    return _volatility_analyzer.render_volatility_analysis(trades_df)

def render_trend_strength_analysis(trades_df):
    """トレンド強度分析を表示"""
    return _trend_strength_analyzer.render_trend_strength_analysis(trades_df)

def render_win_rate_analysis(trades_df):
    """勝率分析を表示"""
    return _win_rate_analyzer.render_win_rate_analysis(trades_df)

def render_rsi_divergence_analysis(trades_df):
    """RSIダイバージェンス分析を表示"""
    return _rsi_divergence_analyzer.render_rsi_divergence_analysis(trades_df)

def render_overall_analysis(trades_df):
    """全体分析を表示"""
    from analysis.overall_analysis import render_overall_analysis as overall_analysis_func
    return overall_analysis_func(trades_df) 