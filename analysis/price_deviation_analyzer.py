import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import ttest_ind

class PriceDeviationAnalyzer:
    """価格乖離率分析クラス"""
    
    def render_price_deviation_analysis(self, trades_df):
        """エントリー時の価格とMAの乖離率を分析"""
        st.subheader("📊 価格乖離率分析（エントリー時）")
        if trades_df.empty or 'entry_ma25_deviation' not in trades_df.columns:
            st.info("価格乖離率データがありません")
            return

        # 利益・損失グループ分け
        profit_trades = trades_df[trades_df['profit_loss'] > 0]
        loss_trades = trades_df[trades_df['profit_loss'] <= 0]

        # MA25乖離率
        ma25_profit = profit_trades['entry_ma25_deviation'].dropna()
        ma25_loss = loss_trades['entry_ma25_deviation'].dropna()
        
        # MA75乖離率
        ma75_profit = profit_trades['entry_ma75_deviation'].dropna()
        ma75_loss = loss_trades['entry_ma75_deviation'].dropna()

        # 統計計算
        ma25_stats = self._calculate_stats(ma25_profit, ma25_loss)
        ma75_stats = self._calculate_stats(ma75_profit, ma75_loss)

        # ヒストグラム表示
        self._render_histograms(ma25_profit, ma25_loss, ma75_profit, ma75_loss)

        # 統計値・t検定結果表示
        self._render_statistics(ma25_stats, ma75_stats)

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

    def _render_histograms(self, ma25_profit, ma25_loss, ma75_profit, ma75_loss):
        """ヒストグラムを表示"""
        # MA25乖離率ヒストグラム
        fig_ma25 = go.Figure()
        fig_ma25.add_trace(go.Histogram(
            x=ma25_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
        ))
        fig_ma25.add_trace(go.Histogram(
            x=ma25_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
        ))
        fig_ma25.update_layout(
            barmode='group',
            title='エントリー時MA25乖離率分布',
            xaxis_title='乖離率（%）',
            yaxis_title='件数',
            legend=dict(x=0.7, y=0.95)
        )

        # MA75乖離率ヒストグラム
        fig_ma75 = go.Figure()
        fig_ma75.add_trace(go.Histogram(
            x=ma75_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
        ))
        fig_ma75.add_trace(go.Histogram(
            x=ma75_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
        ))
        fig_ma75.update_layout(
            barmode='group',
            title='エントリー時MA75乖離率分布',
            xaxis_title='乖離率（%）',
            yaxis_title='件数',
            legend=dict(x=0.7, y=0.95)
        )

        st.plotly_chart(fig_ma25, use_container_width=True)
        st.plotly_chart(fig_ma75, use_container_width=True)

    def _render_statistics(self, ma25_stats, ma75_stats):
        """統計値を表示"""
        import pandas as pd
        
        st.markdown("#### <b>平均・標準偏差</b>", unsafe_allow_html=True)
        stats_df = pd.DataFrame({
            'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
            'MA25乖離率<br>平均±SD（%）': [
                f"<b>{ma25_stats['profit_mean']:.2f} ± {ma25_stats['profit_std']:.2f}</b>", 
                f"<b>{ma25_stats['loss_mean']:.2f} ± {ma25_stats['loss_std']:.2f}</b>"
            ],
            'MA75乖離率<br>平均±SD（%）': [
                f"<b>{ma75_stats['profit_mean']:.2f} ± {ma75_stats['profit_std']:.2f}</b>", 
                f"<b>{ma75_stats['loss_mean']:.2f} ± {ma75_stats['loss_std']:.2f}</b>"
            ]
        })
        st.markdown(stats_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown("#### <b>t検定（平均値の有意差）</b>", unsafe_allow_html=True)
        st.markdown(self._pval_badge(ma25_stats['p_value'], 'MA25乖離率'), unsafe_allow_html=True)
        st.markdown(self._pval_badge(ma75_stats['p_value'], 'MA75乖離率'), unsafe_allow_html=True)

    def _pval_badge(self, p, label):
        """p値バッジを生成"""
        color = '#28a745' if p < 0.05 else '#6c757d'
        text = '有意差あり' if p < 0.05 else '有意差なし'
        return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>" 