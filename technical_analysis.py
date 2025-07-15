import pandas as pd
import numpy as np

def calculate_moving_averages(df, periods=[25, 75, 200]):
    """移動平均線を計算"""
    df = df.copy()
    
    for period in periods:
        df[f'MA{period}'] = df['Close'].rolling(window=period).mean()
    
    return df

def analyze_trend_signals(df):
    """トレンドシグナルを分析"""
    df = df.copy()
    
    # 移動平均線の位置関係
    df['MA25_above_MA75'] = df['MA25'] > df['MA75']
    df['MA25_above_MA200'] = df['MA25'] > df['MA200']
    df['MA75_above_MA200'] = df['MA75'] > df['MA200']
    
    # クロスオーバー検出
    df['Golden_Cross_25_75'] = (df['MA25_above_MA75'] != df['MA25_above_MA75'].shift(1)) & df['MA25_above_MA75']
    df['Dead_Cross_25_75'] = (df['MA25_above_MA75'] != df['MA25_above_MA75'].shift(1)) & ~df['MA25_above_MA75']
    
    return df

def get_trend_status(df):
    """現在のトレンド状態を取得"""
    if df.empty:
        return "データなし", "gray"
    
    current_price = df['Close'].iloc[-1]
    ma25 = df['MA25'].iloc[-1]
    ma75 = df['MA75'].iloc[-1]
    ma200 = df['MA200'].iloc[-1]
    
    # トレンド判定
    if current_price > ma25 > ma75 > ma200:
        return "強気トレンド", "green"
    elif current_price < ma25 < ma75 < ma200:
        return "弱気トレンド", "red"
    else:
        return "横ばい/調整", "orange"

def get_moving_average_status(df):
    """移動平均線の位置関係を取得"""
    if df.empty:
        return {}
    
    ma25 = df['MA25'].iloc[-1]
    ma75 = df['MA75'].iloc[-1]
    ma200 = df['MA200'].iloc[-1]
    
    return {
        'ma25_above_ma75': ma25 > ma75,
        'ma75_above_ma200': ma75 > ma200,
        'ma25': ma25,
        'ma75': ma75,
        'ma200': ma200
    }

def get_cross_signals(df, start_date=None, end_date=None):
    """クロスシグナルを取得"""
    if start_date and end_date:
        # date型をdatetime型に変換
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        mask = (df['DateTime'] >= start_datetime) & (df['DateTime'] <= end_datetime)
        filtered_df = df[mask].copy()
    else:
        filtered_df = df.copy()
    
    golden_crosses = filtered_df[filtered_df['Golden_Cross_25_75']]
    dead_crosses = filtered_df[filtered_df['Dead_Cross_25_75']]
    
    return golden_crosses, dead_crosses 

def calculate_rsi(df, period=14):
    """RSIを計算してdf['RSI']に追加"""
    df = df.copy()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df 