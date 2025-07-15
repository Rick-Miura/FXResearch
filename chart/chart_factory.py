from chart.candlestick_chart import CandlestickChart
from chart.ma_chart import MovingAverageChart
from chart.trade_chart import TradeDetailChart

class ChartFactory:
    """チャート作成のファクトリークラス"""
    
    def __init__(self):
        self.candlestick_chart = CandlestickChart()
        self.ma_chart = MovingAverageChart()
        self.trade_chart = TradeDetailChart()
    
    def create_candlestick_chart(self, df, start_date=None, end_date=None):
        """ローソク足チャートを作成"""
        return self.candlestick_chart.create_chart(df, start_date, end_date)
    
    def create_moving_average_chart(self, df, start_date=None, end_date=None):
        """移動平均線チャートを作成"""
        return self.ma_chart.create_chart(df, start_date, end_date)
    
    def create_trade_detail_chart(self, df, trade, buffer_hours=4):
        """取引詳細チャートを作成"""
        return self.trade_chart.create_chart(df, trade, buffer_hours) 