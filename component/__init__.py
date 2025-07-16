from component.ui_factory import UIFactory

# ファクトリーインスタンス
_ui_factory = UIFactory()

def render_sidebar(df, min_date, max_date):
    """サイドバーをレンダリング"""
    sidebar_manager = _ui_factory.get_sidebar_manager()
    return sidebar_manager.render_sidebar(df, min_date, max_date)

def render_basic_stats(df, start_date, end_date):
    """基本統計をレンダリング"""
    stats_renderer = _ui_factory.get_stats_renderer()
    return stats_renderer.render_basic_stats(df, start_date, end_date)

def render_trend_analysis(df, start_date, end_date):
    """トレンド分析をレンダリング"""
    stats_renderer = _ui_factory.get_stats_renderer()
    return stats_renderer.render_trend_analysis(df, start_date, end_date)

def render_statistics_tables(df, start_date, end_date):
    """統計テーブルをレンダリング"""
    stats_renderer = _ui_factory.get_stats_renderer()
    return stats_renderer.render_statistics_tables(df, start_date, end_date)

def render_signal_analysis(golden_crosses, dead_crosses):
    """シグナル分析をレンダリング"""
    signal_analyzer = _ui_factory.get_signal_analyzer()
    return signal_analyzer.render_signal_analysis(golden_crosses, dead_crosses)

def render_trade_summary(trades_df):
    """取引統計サマリーをレンダリング"""
    from component.trade_summary import render_trade_summary as render_summary
    return render_summary(trades_df) 