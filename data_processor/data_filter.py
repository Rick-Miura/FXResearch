import pandas as pd
import streamlit as st

class DataFilter:
    """データフィルタリングクラス"""
    
    def remove_market_closed_data(self, df):
        """市場クローズ中のデータ（open=close=high=low）を除外"""
        df = df.copy()
        market_closed = (
            (df['Open'] == df['Close']) & 
            (df['Close'] == df['High']) & 
            (df['High'] == df['Low'])
        )
        df_filtered = df[~market_closed].copy()
        removed_count = len(df) - len(df_filtered)
        if removed_count > 0:
            st.info(f"市場クローズ中データ {removed_count}件 を除外しました")
        return df_filtered.reset_index(drop=True)
    
    def get_data_range(self, df):
        """データの範囲を取得"""
        if df is None or df.empty:
            return None, None
        return df['DateTime'].min(), df['DateTime'].max() 