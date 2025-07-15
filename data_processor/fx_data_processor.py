import pandas as pd
import streamlit as st
from data_processor.data_loader import DataLoader
from data_processor.data_filter import DataFilter

class FXDataProcessor:
    """FXデータ処理の統合クラス"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.data_filter = DataFilter()
    
    def load_fx_data(self, file_path):
        """FXデータを読み込み、市場クローズ中のデータを除外"""
        try:
            df = self.data_loader.load_data(file_path)
            if df is None:
                return None
            df = self.data_filter.remove_market_closed_data(df)
            return df
        except Exception as e:
            st.error(f"データ処理エラー: {e}")
            return None
    
    def get_data_range(self, df):
        """データの範囲を取得"""
        return self.data_filter.get_data_range(df) 