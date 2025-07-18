import streamlit as st
import numpy as np
import plotly.graph_objects as go
from analysis.base_analyzer import BaseAnalyzer

class RSIAnalyzer(BaseAnalyzer):
    """RSI分析クラス"""
    
    def render_rsi_analysis(self, trades_df):
        """利益・損失グループでRSIの分布や平均値を比較し、t検定も行う"""
        st.subheader("📊 RSI分析（エントリー時）")
        if trades_df.empty or 'entry_rsi' not in trades_df:
            st.info("RSIデータがありません")
            return

        # 利益・損失グループ分け
        profit_trades = trades_df[trades_df['profit_loss'] > 0]
        loss_trades = trades_df[trades_df['profit_loss'] <= 0]

        # エントリーRSI
        entry_rsi_profit = profit_trades['entry_rsi'].dropna()
        entry_rsi_loss = loss_trades['entry_rsi'].dropna()

        # 統計計算
        entry_stats = self._calculate_stats(entry_rsi_profit, entry_rsi_loss)

        # ヒストグラム表示
        self._render_histograms(entry_rsi_profit, entry_rsi_loss)

        # 統計値・t検定結果表示
        self._render_statistics(entry_stats)

    def _calculate_stats(self, profit_data, loss_data):
        """統計値を計算"""
        def stats(arr):
            return np.mean(arr), np.std(arr)

        profit_mean, profit_std = stats(profit_data)
        loss_mean, loss_std = stats(loss_data)

        # t検定
        p_value = self.calculate_t_test_p_value(profit_data, loss_data)

        return {
            'profit_mean': profit_mean,
            'profit_std': profit_std,
            'loss_mean': loss_mean,
            'loss_std': loss_std,
            'p_value': p_value
        }



    def _render_histograms(self, entry_profit, entry_loss):
        """ヒストグラムを表示"""
        # エントリーRSIヒストグラム
        fig_entry = go.Figure()
        fig_entry.add_trace(go.Histogram(
            x=entry_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
        ))
        fig_entry.add_trace(go.Histogram(
            x=entry_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
        ))
        fig_entry.update_layout(
            barmode='group',
            title='エントリー時RSI分布',
            xaxis_title='RSI',
            yaxis_title='件数',
            legend=dict(x=0.7, y=0.95)
        )

        st.plotly_chart(fig_entry, use_container_width=True)

    def _render_statistics(self, entry_stats):
        """統計値を表示"""
        import pandas as pd
        
        st.markdown("#### <b>平均・標準偏差</b>", unsafe_allow_html=True)
        stats_df = pd.DataFrame({
            'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
            'エントリーRSI<br>平均±SD': [
                f"<b>{entry_stats['profit_mean']:.2f} ± {entry_stats['profit_std']:.2f}</b>", 
                f"<b>{entry_stats['loss_mean']:.2f} ± {entry_stats['loss_std']:.2f}</b>"
            ]
        })
        st.markdown(stats_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown("#### <b>t検定（平均値の有意差）</b>", unsafe_allow_html=True)
        st.markdown(self._pval_badge(entry_stats['p_value'], 'エントリーRSI'), unsafe_allow_html=True)

    def _pval_badge(self, p, label):
        """p値バッジを生成"""
        color = '#28a745' if p < 0.05 else '#6c757d'
        text = '有意差あり' if p < 0.05 else '有意差なし'
        return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>"
    
    def calculate_p_value(self, trades_df):
        """p値を計算"""
        return self.calculate_group_comparison_p_value(trades_df, 'entry_rsi') 