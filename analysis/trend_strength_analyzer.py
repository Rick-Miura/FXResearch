import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import ttest_ind

class TrendStrengthAnalyzer:
    """トレンド強度分析クラス"""
    
    def render_trend_strength_analysis(self, trades_df):
        """エントリー時のトレンド強度を分析"""
        st.subheader("📊 トレンド強度分析（エントリー時）")
        if trades_df.empty:
            st.info("トレンド強度データがありません")
            return

        # 利益・損失グループ分け
        profit_trades = trades_df[trades_df['profit_loss'] > 0]
        loss_trades = trades_df[trades_df['profit_loss'] <= 0]

        # トレンド強度データ（仮のデータ、実際はtrades_dfに含まれる必要）
        # ここでは例として、エントリー時のRSIをトレンド強度の代わりに使用
        if 'entry_rsi' in trades_df.columns:
            trend_strength_profit = profit_trades['entry_rsi'].dropna()
            trend_strength_loss = loss_trades['entry_rsi'].dropna()
        else:
            st.info("トレンド強度データが利用できません")
            return

        # 統計計算
        trend_stats = self._calculate_stats(trend_strength_profit, trend_strength_loss)

        # ヒストグラム表示
        self._render_histograms(trend_strength_profit, trend_strength_loss)

        # 統計値・t検定結果表示
        self._render_statistics(trend_stats)

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

    def _render_histograms(self, trend_profit, trend_loss):
        """ヒストグラムを表示"""
        # トレンド強度ヒストグラム
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Histogram(
            x=trend_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
        ))
        fig_trend.add_trace(go.Histogram(
            x=trend_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
        ))
        fig_trend.update_layout(
            barmode='group',
            title='エントリー時トレンド強度分布',
            xaxis_title='トレンド強度',
            yaxis_title='件数',
            legend=dict(x=0.7, y=0.95)
        )

        st.plotly_chart(fig_trend, use_container_width=True)

    def _render_statistics(self, trend_stats):
        """統計値を表示"""
        import pandas as pd
        
        st.markdown("#### <b>平均・標準偏差</b>", unsafe_allow_html=True)
        stats_df = pd.DataFrame({
            'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
            'トレンド強度<br>平均±SD': [
                f"<b>{trend_stats['profit_mean']:.2f} ± {trend_stats['profit_std']:.2f}</b>", 
                f"<b>{trend_stats['loss_mean']:.2f} ± {trend_stats['loss_std']:.2f}</b>"
            ]
        })
        st.markdown(stats_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown("#### <b>t検定（平均値の有意差）</b>", unsafe_allow_html=True)
        st.markdown(self._pval_badge(trend_stats['p_value'], 'トレンド強度'), unsafe_allow_html=True)

    def _pval_badge(self, p, label):
        """p値バッジを生成"""
        color = '#28a745' if p < 0.05 else '#6c757d'
        text = '有意差あり' if p < 0.05 else '有意差なし'
        return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>" 