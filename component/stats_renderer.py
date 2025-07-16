import streamlit as st
import pandas as pd

class StatsRenderer:
    """統計表示クラス"""
    
    def __init__(self):
        self.trend_colors = {
            '強気トレンド': 'green',
            '弱気トレンド': 'red',
            '横ばい/調整': 'orange'
        }
    
    def render_basic_stats(self, df, start_date, end_date):
        """基本統計をレンダリング（無効化）"""
        # 基本統計表示を削除
        pass
    
    def render_trend_analysis(self, df, start_date, end_date):
        """トレンド分析をレンダリング"""
        # date型をdatetime型に変換
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        filtered_df = df[(df['datetime'] >= start_datetime) & (df['datetime'] <= end_datetime)]
        
        if not filtered_df.empty:
            trend_info = self._analyze_trend(filtered_df)
            self._display_trend(trend_info)
    
    def _analyze_trend(self, filtered_df):
        """トレンド分析を実行"""
        current_price = filtered_df['Close'].iloc[-1]
        ma25 = filtered_df['MA25'].iloc[-1]
        ma75 = filtered_df['MA75'].iloc[-1]
        ma200 = filtered_df['MA200'].iloc[-1]
        
        # トレンド判定
        if current_price > ma25 > ma75 > ma200:
            trend = "強気トレンド"
        elif current_price < ma25 < ma75 < ma200:
            trend = "弱気トレンド"
        else:
            trend = "横ばい/調整"
        
        return {
            'trend': trend,
            'color': self.trend_colors[trend],
            'current_price': current_price,
            'ma25': ma25,
            'ma75': ma75,
            'ma200': ma200
        }
    
    def _display_trend(self, trend_info):
        """トレンド情報を表示"""
        st.markdown(
            f"**現在のトレンド:** <span style='color:{trend_info['color']}'>{trend_info['trend']}</span>", 
            unsafe_allow_html=True
        )
    
    def render_statistics_tables(self, df, start_date, end_date):
        """統計テーブルをレンダリング"""
        # この関数は空にする（価格統計を削除）
        pass 