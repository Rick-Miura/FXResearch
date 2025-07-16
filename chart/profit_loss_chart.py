import plotly.graph_objects as go
import pandas as pd
from chart.base_chart import BaseChart

class ProfitLossChart(BaseChart):
    """損益推移チャート作成クラス"""
    
    def create_chart(self, trades_df):
        """損益推移チャートを作成"""
        if trades_df.empty:
            return None
        
        # 累積損益を計算
        trades_df = trades_df.copy()
        trades_df['cumulative_profit_loss'] = trades_df['profit_loss'].cumsum()
        trades_df['cumulative_profit_loss_pct'] = trades_df['profit_loss_pct'].cumsum()
        
        fig = go.Figure()
        
        # 累積損益線を追加
        fig.add_trace(go.Scatter(
            x=trades_df.index,
            y=trades_df['cumulative_profit_loss'],
            mode='lines',
            name='累積損益',
            line=dict(color='blue', width=2)
        ))
        
        # ゼロラインを追加
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="red"
        )
        
        # レイアウト設定
        layout = self.create_base_layout('損益推移チャート', height=400)
        layout.update(
            xaxis_title='取引番号',
            yaxis_title='累積損益（円）',
            title='取引損益推移'
        )
        fig.update_layout(layout)
        
        return fig 