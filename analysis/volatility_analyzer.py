import streamlit as st
import numpy as np
import plotly.graph_objects as go
from analysis.base_analyzer import BaseAnalyzer

class VolatilityAnalyzer(BaseAnalyzer):
    """ボラティリティ分析クラス"""
    
    def render_volatility_analysis(self, trades_df):
        """エントリー時の価格変動を分析"""
        st.subheader("📊 ボラティリティ分析（エントリー時）")
        if trades_df.empty or 'entry_atr' not in trades_df.columns:
            st.info("ボラティリティデータがありません")
            return

        # 利益・損失グループ分け
        profit_trades = trades_df[trades_df['profit_loss'] > 0]
        loss_trades = trades_df[trades_df['profit_loss'] <= 0]

        # ATRデータ
        atr_profit = profit_trades['entry_atr'].dropna()
        atr_loss = loss_trades['entry_atr'].dropna()

        # 統計計算
        atr_stats = self._calculate_stats(atr_profit, atr_loss)

        # ヒストグラム表示
        self._render_histograms(atr_profit, atr_loss)

        # 統計値・t検定結果表示
        self._render_statistics(atr_stats)

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



    def _render_histograms(self, atr_profit, atr_loss):
        """ヒストグラムを表示"""
        # ATRヒストグラム
        fig_atr = go.Figure()
        fig_atr.add_trace(go.Histogram(
            x=atr_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
        ))
        fig_atr.add_trace(go.Histogram(
            x=atr_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
        ))
        fig_atr.update_layout(
            barmode='group',
            title='エントリー時ATR分布',
            xaxis_title='ATR',
            yaxis_title='件数',
            legend=dict(x=0.7, y=0.95)
        )

        st.plotly_chart(fig_atr, use_container_width=True)

    def _render_statistics(self, atr_stats):
        """統計値を表示"""
        import pandas as pd
        
        st.markdown("#### <b>平均・標準偏差</b>", unsafe_allow_html=True)
        stats_df = pd.DataFrame({
            'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
            'ATR<br>平均±SD': [
                f"<b>{atr_stats['profit_mean']:.4f} ± {atr_stats['profit_std']:.4f}</b>", 
                f"<b>{atr_stats['loss_mean']:.4f} ± {atr_stats['loss_std']:.4f}</b>"
            ]
        })
        st.markdown(stats_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown("#### <b>t検定（平均値の有意差）</b>", unsafe_allow_html=True)
        st.markdown(self._pval_badge(atr_stats['p_value'], 'ATR'), unsafe_allow_html=True)

    def _pval_badge(self, p, label):
        """p値バッジを生成"""
        color = '#28a745' if p < 0.05 else '#6c757d'
        text = '有意差あり' if p < 0.05 else '有意差なし'
        return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>"
    
    def calculate_p_value(self, trades_df):
        """p値を計算"""
        return self.calculate_group_comparison_p_value(trades_df, 'entry_atr') 