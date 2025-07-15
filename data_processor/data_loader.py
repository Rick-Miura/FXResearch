import pandas as pd
import streamlit as st

class DataLoader:
    """データ読み込みの基本クラス"""
    
    def load_data(self, file_path):
        """FXデータを読み込み"""
        try:
            df = pd.read_csv(file_path)
            df = self._set_column_names(df)
            df = self._parse_datetime(df)
            df = df.copy().sort_values('DateTime').reset_index(drop=True)
            return df
        except Exception as e:
            st.error(f"データ読み込みエラー: {e}")
            return None
    
    def _set_column_names(self, df):
        """カラム名を設定し、必要な列のみ抽出"""
        df = df.copy()
        if len(df.columns) >= 6:
            df.columns = ['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']
            return df[['DateTime', 'Open', 'High', 'Low', 'Close']]
        else:
            df.columns = ['DateTime', 'Open', 'High', 'Low', 'Close']
            return df
    
    def _parse_datetime(self, df):
        """DateTimeをdatetime型に変換"""
        def parse_datetime(date_str):
            try:
                if 'GMT' in str(date_str):
                    date_part = str(date_str).split(' GMT')[0]
                    return pd.to_datetime(date_part, format='%d.%m.%Y %H:%M:%S.%f')
                else:
                    return pd.to_datetime(date_str)
            except:
                return pd.to_datetime(date_str, errors='coerce')
        
        df['DateTime'] = df['DateTime'].apply(parse_datetime)
        return df 