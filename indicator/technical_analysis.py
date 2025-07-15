import pandas as pd
import numpy as np

def calculate_moving_averages(df, periods=[25, 75, 200]):
    """移動平均線を計算"""
    df = df.copy()
    
    for period in periods:
        df[f'MA{period}'] = df['Close'].rolling(window=period).mean()
    
    return df

def calculate_rsi(df, period=14):
    """RSIを計算"""
    df = df.copy()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def calculate_atr(df, period=14):
    """ATR（Average True Range）を計算"""
    df = df.copy()
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift(1))
    low_close = np.abs(df['Low'] - df['Close'].shift(1))
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=period, min_periods=1).mean()
    return df

def calculate_cross_signals(df):
    """クロスシグナルを計算"""
    df = df.copy()
    
    # 移動平均線の位置関係
    df['MA25_above_MA75'] = df['MA25'] > df['MA75']
    
    # クロスオーバー検出
    df['Golden_Cross_25_75'] = (df['MA25_above_MA75'] != df['MA25_above_MA75'].shift(1)) & df['MA25_above_MA75']
    df['Dead_Cross_25_75'] = (df['MA25_above_MA75'] != df['MA25_above_MA75'].shift(1)) & ~df['MA25_above_MA75']
    
    return df 