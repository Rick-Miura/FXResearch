import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_candlestick_chart(df, start_date=None, end_date=None):
    """ローソク足チャートを作成（x軸は単位）"""
    if start_date and end_date:
        # date型をdatetime型に変換
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        mask = (df['DateTime'] >= start_datetime) & (df['DateTime'] <= end_datetime)
        chart_df = df[mask].copy()
    else:
        chart_df = df.copy()
    
    # インデックスをリセットして単位として使用
    chart_df = chart_df.reset_index(drop=True)
    
    fig = go.Figure()
    
    # ローソク足（x軸はインデックス）
    fig.add_trace(go.Candlestick(
        x=chart_df.index,
        open=chart_df['Open'],
        high=chart_df['High'],
        low=chart_df['Low'],
        close=chart_df['Close'],
        name='USDJPY',
        increasing_line_color='#26A69A',
        decreasing_line_color='#EF5350'
    ))
    
    fig.update_layout(
        title='USDJPY 15分足チャート',
        xaxis_title='単位',
        yaxis_title='価格',
        height=600,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        # インタラクティブ機能を無効化
        dragmode=False,
        modebar=dict(remove=['zoom', 'pan', 'select', 'lasso2d', 'reset', 'autoscale', 'hovercompare', 'hoverclosest'])
    )
    
    return fig

def create_moving_average_comparison_chart(df, start_date=None, end_date=None):
    """移動平均線比較チャートを作成（x軸は単位）"""
    if start_date and end_date:
        # date型をdatetime型に変換
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        mask = (df['DateTime'] >= start_datetime) & (df['DateTime'] <= end_datetime)
        chart_df = df[mask].copy()
    else:
        chart_df = df.copy()
    
    # インデックスをリセットして単位として使用
    chart_df = chart_df.reset_index(drop=True)
    
    fig = go.Figure()
    
    # 移動平均線のみ（x軸はインデックス）
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['MA25'],
        mode='lines',
        name='MA25',
        line=dict(color='blue', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['MA75'],
        mode='lines',
        name='MA75',
        line=dict(color='orange', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['MA200'],
        mode='lines',
        name='MA200',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title='移動平均線比較',
        xaxis_title='単位',
        yaxis_title='価格',
        height=400,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        # インタラクティブ機能を無効化
        dragmode=False,
        modebar=dict(remove=['zoom', 'pan', 'select', 'lasso2d', 'reset', 'autoscale', 'hovercompare', 'hoverclosest'])
    )
    
    return fig 

def create_trade_detail_chart(df, trade, buffer_hours=4):
    """特定のトレード期間の詳細チャートを作成（x軸は単位）"""
    # トレード期間の前後4時間をバッファとして追加（より広い範囲で表示）
    start_time = trade['entry_date'] - pd.Timedelta(hours=buffer_hours)
    end_time = trade['exit_date'] + pd.Timedelta(hours=buffer_hours)
    
    # 期間のデータを抽出
    mask = (df['DateTime'] >= start_time) & (df['DateTime'] <= end_time)
    chart_df = df[mask].copy()
    
    # インデックスをリセットして単位として使用
    chart_df = chart_df.reset_index(drop=True)
    
    # エントリー・エグジットのインデックスを取得
    entry_idx = chart_df[chart_df['DateTime'] == trade['entry_date']].index
    exit_idx = chart_df[chart_df['DateTime'] == trade['exit_date']].index
    
    if len(entry_idx) == 0 or len(exit_idx) == 0:
        # 該当するインデックスが見つからない場合は近似値を使用
        entry_idx = [chart_df.index[0]]
        exit_idx = [chart_df.index[-1]]
    else:
        entry_idx = [entry_idx[0]]
        exit_idx = [exit_idx[0]]
    
    fig = go.Figure()
    
    # ローソク足（x軸はインデックス）
    fig.add_trace(go.Candlestick(
        x=chart_df.index,
        open=chart_df['Open'],
        high=chart_df['High'],
        low=chart_df['Low'],
        close=chart_df['Close'],
        name='USDJPY',
        increasing_line_color='#26A69A',
        decreasing_line_color='#EF5350'
    ))
    
    # 移動平均線（x軸はインデックス）
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['MA25'],
        mode='lines',
        name='MA25',
        line=dict(color='blue', width=1)
    ))
    
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['MA75'],
        mode='lines',
        name='MA75',
        line=dict(color='orange', width=1)
    ))
    
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['MA200'],
        mode='lines',
        name='MA200',
        line=dict(color='red', width=2)
    ))
    
    # エントリーポイントとエグジットポイントに垂直線を追加（x軸はインデックス）
    # エントリー線
    fig.add_shape(
        type="line",
        x0=entry_idx[0],
        x1=entry_idx[0],
        y0=chart_df['Low'].min(),
        y1=chart_df['High'].max(),
        line=dict(color="green", width=3, dash="dash"),
        name="エントリー"
    )
    
    # エグジット線
    fig.add_shape(
        type="line",
        x0=exit_idx[0],
        x1=exit_idx[0],
        y0=chart_df['Low'].min(),
        y1=chart_df['High'].max(),
        line=dict(color="red", width=3, dash="dash"),
        name="エグジット"
    )
    
    # エントリー注釈
    fig.add_annotation(
        x=entry_idx[0],
        y=chart_df['High'].max(),
        text=f"エントリー: {trade['entry_price']:.2f}",
        showarrow=True,
        arrowhead=2,
        arrowcolor="green",
        font=dict(color="green", size=12),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="green",
        borderwidth=1
    )
    
    # エグジット注釈
    fig.add_annotation(
        x=exit_idx[0],
        y=chart_df['Low'].min(),
        text=f"エグジット: {trade['exit_price']:.2f}",
        showarrow=True,
        arrowhead=2,
        arrowcolor="red",
        font=dict(color="red", size=12),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="red",
        borderwidth=1
    )
    
    # 損益情報をタイトルに追加
    profit_loss_text = f"損益: {trade['profit_loss']:,.0f}円 ({trade['profit_loss_pct']:.2f}%)"
    fig.update_layout(
        title=f'取引詳細: {trade["entry_date"].strftime("%Y-%m-%d %H:%M")} → {trade["exit_date"].strftime("%Y-%m-%d %H:%M")}<br>{profit_loss_text}',
        xaxis_title='単位',
        yaxis_title='価格',
        height=600,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        # インタラクティブ機能を無効化
        dragmode=False,
        modebar=dict(remove=['zoom', 'pan', 'select', 'lasso2d', 'reset', 'autoscale', 'hovercompare', 'hoverclosest'])
    )
    
    return fig 