import pandas as pd
import numpy as np
import streamlit as st

def load_fx_data(file_path):
    """FXデータを読み込み、市場クローズ中のデータを除外して詰める"""
    try:
        # データ読み込み
        df = pd.read_csv(file_path)
        
        # カラム名を確認して適切に設定
        if len(df.columns) >= 6:
            df.columns = ['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']
            # Volumeカラムを除外
            df = df[['DateTime', 'Open', 'High', 'Low', 'Close']]
        else:
            # カラム数が少ない場合は適応
            df.columns = ['DateTime', 'Open', 'High', 'Low', 'Close']
        
        # DateTimeをdatetime型に変換（日付形式に対応）
        def parse_datetime(date_str):
            try:
                # "01.01.2024 00:00:00.000 GMT+0900" 形式に対応
                if 'GMT' in str(date_str):
                    # GMT部分を除去してからパース
                    date_part = str(date_str).split(' GMT')[0]
                    return pd.to_datetime(date_part, format='%d.%m.%Y %H:%M:%S.%f')
                else:
                    return pd.to_datetime(date_str)
            except:
                # フォールバック
                return pd.to_datetime(date_str, errors='coerce')
        
        df['DateTime'] = df['DateTime'].apply(parse_datetime)
        df = df.sort_values('DateTime').reset_index(drop=True)
        
        # 市場クローズ中のデータを除外（open=close=high=lowの場合）
        df = remove_market_closed_data(df)
        
        # インデックスをリセット
        df = df.reset_index(drop=True)
        
        return df
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return None

def remove_market_closed_data(df):
    """市場クローズ中のデータ（open=close=high=low）を除外して詰める"""
    df = df.copy()
    
    # 市場クローズ中のデータを判定（open=close=high=low）
    market_closed = (
        (df['Open'] == df['Close']) & 
        (df['Close'] == df['High']) & 
        (df['High'] == df['Low'])
    )
    
    # 市場クローズ中のデータを除外
    df_filtered = df[~market_closed].copy()
    
    # 除外したデータ数を表示
    removed_count = len(df) - len(df_filtered)
    if removed_count > 0:
        st.info(f"市場クローズ中のデータ {removed_count}件 を除外しました")
    
    return df_filtered

def get_data_range(df):
    """データの範囲を取得（市場クローズ中データ除外後）"""
    if df is None or df.empty:
        return None, None
    
    min_date = df['DateTime'].min()
    max_date = df['DateTime'].max()
    
    return min_date, max_date 