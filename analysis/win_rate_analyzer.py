import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from analysis.base_analyzer import BaseAnalyzer

class WinRateAnalyzer(BaseAnalyzer):
    """勝率分析クラス"""
    
    def render_win_rate_analysis(self, trades_df):
        """エントリー条件別の勝率を分析"""
        st.subheader("📊 勝率分析（エントリー条件別）")
        if trades_df.empty:
            st.info("取引データがありません")
            return

        # エントリートレンド別勝率
        if 'entry_trend' in trades_df.columns:
            self._render_trend_win_rate(trades_df)
        
        # RSI範囲別勝率
        if 'entry_rsi' in trades_df.columns:
            self._render_rsi_win_rate(trades_df)

    def _render_trend_win_rate(self, trades_df):
        """トレンド別勝率を表示"""
        st.markdown("#### トレンド別勝率")
        
        trend_stats = trades_df.groupby('entry_trend').agg({
            'profit_loss': ['count', lambda x: (x > 0).sum()]
        }).round(2)
        
        trend_stats.columns = ['総取引数', '勝ち取引数']
        trend_stats['勝率'] = (trend_stats['勝ち取引数'] / trend_stats['総取引数'] * 100).round(1)
        trend_stats['平均損益'] = trades_df.groupby('entry_trend')['profit_loss'].mean().round(0)
        
        st.dataframe(trend_stats, use_container_width=True)

    def _render_rsi_win_rate(self, trades_df):
        """RSI範囲別勝率を表示"""
        st.markdown("#### RSI範囲別勝率")
        
        # エントリー条件に合わせてRSIが30-70の範囲内の取引のみを分析
        valid_trades = trades_df[(trades_df['entry_rsi'] >= 30) & (trades_df['entry_rsi'] <= 70)]
        
        if valid_trades.empty:
            st.info("RSI 30-70の範囲内の取引がありません")
            return
        
        # RSI範囲を作成（30-70の範囲内のみ）
        valid_trades['rsi_range'] = pd.cut(valid_trades['entry_rsi'], 
                                          bins=[30, 40, 50, 60, 70], 
                                          labels=['30-40', '40-50', '50-60', '60-70'])
        
        rsi_stats = valid_trades.groupby('rsi_range').agg({
            'profit_loss': ['count', lambda x: (x > 0).sum()]
        }).round(2)
        
        rsi_stats.columns = ['総取引数', '勝ち取引数']
        rsi_stats['勝率'] = (rsi_stats['勝ち取引数'] / rsi_stats['総取引数'] * 100).round(1)
        rsi_stats['平均損益'] = valid_trades.groupby('rsi_range')['profit_loss'].mean().round(0)
        
        st.dataframe(rsi_stats, use_container_width=True)
    
    def calculate_p_value(self, trades_df):
        """p値を計算（カイ二乗検定で勝率の有意差を検定）"""
        return self.calculate_chi2_p_value(trades_df, 'entry_trend') 