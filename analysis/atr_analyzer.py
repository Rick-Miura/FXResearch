import streamlit as st
import numpy as np
import plotly.graph_objects as go
from analysis.base_analyzer import BaseAnalyzer

class ATRAnalyzer(BaseAnalyzer):
    """ATR分析クラス"""
    
    def render_atr_analysis(self, trades_df):
        """利益・損失グループでエントリーATRの分布や平均値を比較し、t検定も行う"""
        st.subheader("📊 ATR分析（エントリー時・損益グループ比較）")
        if trades_df.empty or 'entry_atr' not in trades_df:
            st.info("ATRデータがありません")
            return

        # 利益・損失グループ分け
        profit_trades = trades_df[trades_df['profit_loss'] > 0]
        loss_trades = trades_df[trades_df['profit_loss'] <= 0]

        # エントリーATR
        entry_atr_profit = profit_trades['entry_atr'].dropna()
        entry_atr_loss = loss_trades['entry_atr'].dropna()

        # 統計計算
        stats = self._calculate_stats(entry_atr_profit, entry_atr_loss)

        # ヒストグラム表示
        self._render_histogram(entry_atr_profit, entry_atr_loss)

        # 統計値・t検定結果表示
        self._render_statistics(stats)

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



    def _render_histogram(self, profit_data, loss_data):
        """ヒストグラムを表示"""
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=profit_data, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
        ))
        fig.add_trace(go.Histogram(
            x=loss_data, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
        ))
        fig.update_layout(
            barmode='group',
            title='エントリー時ATR分布',
            xaxis_title='ATR',
            yaxis_title='件数',
            legend=dict(x=0.7, y=0.95)
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_statistics(self, stats):
        """統計値を表示"""
        import pandas as pd
        
        st.markdown("#### <b>平均・標準偏差</b>", unsafe_allow_html=True)
        stats_df = pd.DataFrame({
            'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
            'エントリーATR<br>平均±SD': [
                f"<b>{stats['profit_mean']:.4f} ± {stats['profit_std']:.4f}</b>", 
                f"<b>{stats['loss_mean']:.4f} ± {stats['loss_std']:.4f}</b>"
            ]
        })
        st.markdown(stats_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown("#### <b>t検定（平均値の有意差）</b>", unsafe_allow_html=True)
        st.markdown(self._pval_badge(stats['p_value'], 'エントリーATR'), unsafe_allow_html=True)

    def _pval_badge(self, p, label):
        """p値バッジを生成"""
        color = '#28a745' if p < 0.05 else '#6c757d'
        text = '有意差あり' if p < 0.05 else '有意差なし'
        return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>"
    
    def calculate_p_value(self, trades_df):
        """p値を計算"""
        return self.calculate_group_comparison_p_value(trades_df, 'entry_atr') 