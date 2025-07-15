import plotly.graph_objects as go
import pandas as pd
from chart.base_chart import BaseChart

class TradeDetailChart(BaseChart):
    """取引詳細チャート作成クラス"""
    
    def create_chart(self, df, trade, buffer_hours=4):
        """特定のトレード期間の詳細チャートを作成"""
        # トレード期間の前後4時間をバッファとして追加
        start_time = trade['entry_date'] - pd.Timedelta(hours=buffer_hours)
        end_time = trade['exit_date'] + pd.Timedelta(hours=buffer_hours)
        
        # 期間のデータを抽出
        mask = (df['DateTime'] >= start_time) & (df['DateTime'] <= end_time)
        chart_df = df[mask].copy()
        
        # インデックスをリセットして単位として使用
        chart_df = chart_df.reset_index(drop=True)
        
        # エントリー・エグジットのインデックスを取得
        entry_idx, exit_idx = self._get_trade_indices(chart_df, trade)
        
        fig = go.Figure()
        
        # ローソク足を追加
        self.add_candlestick(fig, chart_df)
        
        # 移動平均線を追加（細い線）
        self._add_thin_moving_averages(fig, chart_df)
        
        # エントリー・エグジット線を追加
        self._add_trade_lines(fig, chart_df, entry_idx, exit_idx)
        
        # 注釈を追加
        self._add_trade_annotations(fig, chart_df, trade, entry_idx, exit_idx)
        
        # レイアウト設定
        title = self._create_trade_title(trade)
        layout = self.create_base_layout(title)
        fig.update_layout(layout)
        
        return fig
    
    def _get_trade_indices(self, chart_df, trade):
        """取引のインデックスを取得"""
        entry_idx = chart_df[chart_df['DateTime'] == trade['entry_date']].index
        exit_idx = chart_df[chart_df['DateTime'] == trade['exit_date']].index
        
        if len(entry_idx) == 0 or len(exit_idx) == 0:
            # 該当するインデックスが見つからない場合は近似値を使用
            entry_idx = [chart_df.index[0]]
            exit_idx = [chart_df.index[-1]]
        else:
            entry_idx = [entry_idx[0]]
            exit_idx = [exit_idx[0]]
        
        return entry_idx, exit_idx
    
    def _add_thin_moving_averages(self, fig, chart_df):
        """細い移動平均線を追加"""
        # MA25
        fig.add_trace(go.Scatter(
            x=chart_df.index,
            y=chart_df['MA25'],
            mode='lines',
            name='MA25',
            line=dict(color=self.default_colors['ma25'], width=1)
        ))
        
        # MA75
        fig.add_trace(go.Scatter(
            x=chart_df.index,
            y=chart_df['MA75'],
            mode='lines',
            name='MA75',
            line=dict(color=self.default_colors['ma75'], width=1)
        ))
        
        # MA200
        fig.add_trace(go.Scatter(
            x=chart_df.index,
            y=chart_df['MA200'],
            mode='lines',
            name='MA200',
            line=dict(color=self.default_colors['ma200'], width=2)
        ))
    
    def _add_trade_lines(self, fig, chart_df, entry_idx, exit_idx):
        """取引線を追加"""
        # エントリー線
        fig.add_shape(
            type="line",
            x0=entry_idx[0],
            x1=entry_idx[0],
            y0=chart_df['Low'].min(),
            y1=chart_df['High'].max(),
            line=dict(color=self.default_colors['entry'], width=3, dash="dash"),
            name="エントリー"
        )
        
        # エグジット線
        fig.add_shape(
            type="line",
            x0=exit_idx[0],
            x1=exit_idx[0],
            y0=chart_df['Low'].min(),
            y1=chart_df['High'].max(),
            line=dict(color=self.default_colors['exit'], width=3, dash="dash"),
            name="エグジット"
        )
    
    def _add_trade_annotations(self, fig, chart_df, trade, entry_idx, exit_idx):
        """取引注釈を追加"""
        # エントリー注釈
        fig.add_annotation(
            x=entry_idx[0],
            y=chart_df['High'].max(),
            text=f"エントリー: {trade['entry_price']:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor=self.default_colors['entry'],
            font=dict(color=self.default_colors['entry'], size=12),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor=self.default_colors['entry'],
            borderwidth=1
        )
        
        # エグジット注釈
        fig.add_annotation(
            x=exit_idx[0],
            y=chart_df['Low'].min(),
            text=f"エグジット: {trade['exit_price']:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor=self.default_colors['exit'],
            font=dict(color=self.default_colors['exit'], size=12),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor=self.default_colors['exit'],
            borderwidth=1
        )
    
    def _create_trade_title(self, trade):
        """取引タイトルを作成"""
        profit_loss_text = f"損益: {trade['profit_loss']:,.0f}円 ({trade['profit_loss_pct']:.2f}%)"
        return f'取引詳細: {trade["entry_date"].strftime("%Y-%m-%d %H:%M")} → {trade["exit_date"].strftime("%Y-%m-%d %H:%M")}<br>{profit_loss_text}' 