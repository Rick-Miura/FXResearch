import plotly.graph_objects as go
from chart.base_chart import BaseChart

class MovingAverageChart(BaseChart):
    """移動平均線チャート作成クラス"""
    
    def create_chart(self, df, start_date=None, end_date=None):
        """移動平均線比較チャートを作成"""
        chart_df = self.filter_data_by_date(df, start_date, end_date)
        
        fig = go.Figure()
        
        # 移動平均線を追加
        self.add_moving_averages(fig, chart_df)
        
        # レイアウト設定
        layout = self.create_base_layout('移動平均線比較', height=400)
        fig.update_layout(layout)
        
        return fig 