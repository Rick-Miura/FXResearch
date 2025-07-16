from chart.chart_factory import ChartFactory

# ファクトリーインスタンス
_chart_factory = ChartFactory()

def create_candlestick_chart(df, start_date=None, end_date=None):
    """ローソク足チャートを作成（x軸は単位）"""
    return _chart_factory.create_candlestick_chart(df, start_date, end_date)

def create_moving_average_comparison_chart(df, start_date=None, end_date=None):
    """移動平均線比較チャートを作成（x軸は単位）"""
    return _chart_factory.create_moving_average_chart(df, start_date, end_date)

def create_trade_detail_chart(df, trade, buffer_hours=4):
    """特定のトレード期間の詳細チャートを作成（x軸は単位）"""
    return _chart_factory.create_trade_detail_chart(df, trade, buffer_hours)

def create_profit_loss_chart(trades_df):
    """損益推移チャートを作成"""
    return _chart_factory.create_profit_loss_chart(trades_df) 