import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import ttest_ind

class RSIDivergenceAnalyzer:
    """RSIダイバージェンス分析クラス"""
    
    def render_rsi_divergence_analysis(self, trades_df):
        """価格とRSIの乖離を分析"""
        st.subheader("📊 RSIダイバージェンス分析（エントリー時）")
        if trades_df.empty or 'entry_rsi' not in trades_df.columns:
            st.info("RSIダイバージェンスデータがありません")
            return

        # 利益・損失グループ分け
        profit_trades = trades_df[trades_df['profit_loss'] > 0]
        loss_trades = trades_df[trades_df['profit_loss'] <= 0]

        # RSIダイバージェンスデータ（仮のデータ、実際はtrades_dfに含まれる必要）
        # ここでは例として、エントリー時のRSIをダイバージェンスの代わりに使用
        if 'entry_rsi' in trades_df.columns:
            divergence_profit = profit_trades['entry_rsi'].dropna()
            divergence_loss = loss_trades['entry_rsi'].dropna()
        else:
            st.info("RSIダイバージェンスデータが利用できません")
            return

        # 統計計算
        divergence_stats = self._calculate_stats(divergence_profit, divergence_loss)

        # ヒストグラム表示
        self._render_histograms(divergence_profit, divergence_loss)

        # 統計値・t検定結果表示
        self._render_statistics(divergence_stats)

    def _calculate_stats(self, profit_data, loss_data):
        """統計値を計算"""
        def stats(arr):
            return np.mean(arr), np.std(arr)

        profit_mean, profit_std = stats(profit_data)
        loss_mean, loss_std = stats(loss_data)

        # t検定
        ttest = ttest_ind(profit_data, loss_data, equal_var=False, nan_policy='omit')
        p_value = self._get_pvalue(ttest)

        return {
            'profit_mean': profit_mean,
            'profit_std': profit_std,
            'loss_mean': loss_mean,
            'loss_std': loss_std,
            'p_value': p_value
        }

    def _get_pvalue(self, ttest_result):
        """p値を取得"""
        if hasattr(ttest_result, 'pvalue'):
            return float(ttest_result.pvalue)
        elif isinstance(ttest_result, (tuple, list)) and len(ttest_result) > 1:
            return float(ttest_result[1])
        return float('nan')

    def _render_histograms(self, divergence_profit, divergence_loss):
        """ヒストグラムを表示"""
        # RSIダイバージェンスヒストグラム
        fig_divergence = go.Figure()
        fig_divergence.add_trace(go.Histogram(
            x=divergence_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
        ))
        fig_divergence.add_trace(go.Histogram(
            x=divergence_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
        ))
        fig_divergence.update_layout(
            barmode='group',
            title='エントリー時RSIダイバージェンス分布',
            xaxis_title='RSI値',
            yaxis_title='件数',
            legend=dict(x=0.7, y=0.95)
        )

        st.plotly_chart(fig_divergence, use_container_width=True)

    def _render_statistics(self, divergence_stats):
        """統計値を表示"""
        import pandas as pd
        
        st.markdown("#### <b>平均・標準偏差</b>", unsafe_allow_html=True)
        stats_df = pd.DataFrame({
            'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
            'RSIダイバージェンス<br>平均±SD': [
                f"<b>{divergence_stats['profit_mean']:.2f} ± {divergence_stats['profit_std']:.2f}</b>", 
                f"<b>{divergence_stats['loss_mean']:.2f} ± {divergence_stats['loss_std']:.2f}</b>"
            ]
        })
        st.markdown(stats_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown("#### <b>t検定（平均値の有意差）</b>", unsafe_allow_html=True)
        st.markdown(self._pval_badge(divergence_stats['p_value'], 'RSIダイバージェンス'), unsafe_allow_html=True)

    def _pval_badge(self, p, label):
        """p値バッジを生成"""
        color = '#28a745' if p < 0.05 else '#6c757d'
        text = '有意差あり' if p < 0.05 else '有意差なし'
        return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>" 