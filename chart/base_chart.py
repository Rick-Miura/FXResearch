import plotly.graph_objects as go
import pandas as pd

class BaseChart:
    """チャート作成の基本クラス"""
    
    def __init__(self):
        self.default_colors = {
            'increasing': '#26A69A',
            'decreasing': '#EF5350',
            'ma25': 'blue',
            'ma75': 'orange', 
            'ma200': 'red',
            'entry': 'green',
            'exit': 'red'
        }
    
    def filter_data_by_date(self, df, start_date=None, end_date=None):
        """日付範囲でデータをフィルタ"""
        if start_date and end_date:
            start_datetime = pd.to_datetime(start_date)
            end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            mask = (df['DateTime'] >= start_datetime) & (df['DateTime'] <= end_datetime)
            chart_df = df[mask].copy()
        else:
            chart_df = df.copy()
        
        # インデックスをリセットして単位として使用
        return chart_df.reset_index(drop=True)
    
    def create_base_layout(self, title, height=600):
        """基本レイアウト設定"""
        return dict(
            title=title,
            xaxis_title='単位',
            yaxis_title='価格',
            height=height,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            dragmode=False,
            modebar=dict(remove=['zoom', 'pan', 'select', 'lasso2d', 'reset', 'autoscale', 'hovercompare', 'hoverclosest'])
        )
    
    def add_candlestick(self, fig, chart_df):
        """ローソク足を追加"""
        fig.add_trace(go.Candlestick(
            x=chart_df.index,
            open=chart_df['Open'],
            high=chart_df['High'],
            low=chart_df['Low'],
            close=chart_df['Close'],
            name='USDJPY',
            increasing_line_color=self.default_colors['increasing'],
            decreasing_line_color=self.default_colors['decreasing']
        ))
    
    def add_moving_averages(self, fig, chart_df):
        """移動平均線を追加"""
        # MA25
        fig.add_trace(go.Scatter(
            x=chart_df.index,
            y=chart_df['MA25'],
            mode='lines',
            name='MA25',
            line=dict(color=self.default_colors['ma25'], width=2)
        ))
        
        # MA75
        fig.add_trace(go.Scatter(
            x=chart_df.index,
            y=chart_df['MA75'],
            mode='lines',
            name='MA75',
            line=dict(color=self.default_colors['ma75'], width=2)
        ))
        
        # MA200
        fig.add_trace(go.Scatter(
            x=chart_df.index,
            y=chart_df['MA200'],
            mode='lines',
            name='MA200',
            line=dict(color=self.default_colors['ma200'], width=3)
        )) 