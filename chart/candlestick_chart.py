import plotly.graph_objects as go
from chart.base_chart import BaseChart

class CandlestickChart(BaseChart):
    """ローソク足チャート作成クラス"""
    
    def create_chart(self, df, start_date=None, end_date=None):
        """ローソク足チャートを作成"""
        chart_df = self.filter_data_by_date(df, start_date, end_date)
        
        fig = go.Figure()
        
        # ローソク足を追加
        self.add_candlestick(fig, chart_df)
        
        # レイアウト設定
        layout = self.create_base_layout('USDJPY 15分足チャート')
        fig.update_layout(layout)
        
        return fig 