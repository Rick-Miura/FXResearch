import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import ttest_ind


def render_ma_deviation_analysis(trades_df):
    """利益・損失グループでエントリー時のMA乖離率の分布や平均値を比較し、t検定も行う"""
    st.subheader("📊 MA乖離率分析（エントリー時・損益グループ比較）")
    if trades_df.empty or 'entry_ma25_deviation' not in trades_df or 'entry_ma75_deviation' not in trades_df:
        st.info("MA乖離率データがありません")
        return

    # 利益・損失グループ分け
    profit_trades = trades_df[trades_df['profit_loss'] > 0]
    loss_trades = trades_df[trades_df['profit_loss'] <= 0]

    # エントリーMA乖離率
    entry_ma25_dev_profit = profit_trades['entry_ma25_deviation'].dropna()
    entry_ma25_dev_loss = loss_trades['entry_ma25_deviation'].dropna()
    entry_ma75_dev_profit = profit_trades['entry_ma75_deviation'].dropna()
    entry_ma75_dev_loss = loss_trades['entry_ma75_deviation'].dropna()

    # 平均・標準偏差
    def stats(arr):
        return np.mean(arr), np.std(arr)

    entry_ma25_dev_profit_mean, entry_ma25_dev_profit_std = stats(entry_ma25_dev_profit)
    entry_ma25_dev_loss_mean, entry_ma25_dev_loss_std = stats(entry_ma25_dev_loss)
    entry_ma75_dev_profit_mean, entry_ma75_dev_profit_std = stats(entry_ma75_dev_profit)
    entry_ma75_dev_loss_mean, entry_ma75_dev_loss_std = stats(entry_ma75_dev_loss)

    # t検定
    entry_ma25_ttest = ttest_ind(entry_ma25_dev_profit, entry_ma25_dev_loss, equal_var=False, nan_policy='omit')
    entry_ma75_ttest = ttest_ind(entry_ma75_dev_profit, entry_ma75_dev_loss, equal_var=False, nan_policy='omit')
    def get_pvalue(ttest_result):
        if hasattr(ttest_result, 'pvalue'):
            return float(ttest_result.pvalue)
        elif isinstance(ttest_result, (tuple, list)) and len(ttest_result) > 1:
            return float(ttest_result[1])
        return float('nan')

    entry_ma25_p = get_pvalue(entry_ma25_ttest)
    entry_ma75_p = get_pvalue(entry_ma75_ttest)

    # ヒストグラム（MA25乖離率）
    fig_ma25 = go.Figure()
    fig_ma25.add_trace(go.Histogram(
        x=entry_ma25_dev_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
    ))
    fig_ma25.add_trace(go.Histogram(
        x=entry_ma25_dev_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
    ))
    fig_ma25.update_layout(
        barmode='group',
        title='エントリー時MA25乖離率分布',
        xaxis_title='MA25乖離率 (%)',
        yaxis_title='件数',
        legend=dict(x=0.7, y=0.95)
    )

    # ヒストグラム（MA75乖離率）
    fig_ma75 = go.Figure()
    fig_ma75.add_trace(go.Histogram(
        x=entry_ma75_dev_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
    ))
    fig_ma75.add_trace(go.Histogram(
        x=entry_ma75_dev_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
    ))
    fig_ma75.update_layout(
        barmode='group',
        title='エントリー時MA75乖離率分布',
        xaxis_title='MA75乖離率 (%)',
        yaxis_title='件数',
        legend=dict(x=0.7, y=0.95)
    )

    st.plotly_chart(fig_ma25, use_container_width=True)
    st.plotly_chart(fig_ma75, use_container_width=True)

    # 統計値・t検定結果
    st.markdown("#### <b>平均・標準偏差</b>", unsafe_allow_html=True)
    import pandas as pd
    stats_df = pd.DataFrame({
        'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
        'MA25乖離率<br>平均±SD (%)': [f"<b>{entry_ma25_dev_profit_mean:.2f} ± {entry_ma25_dev_profit_std:.2f}</b>", f"<b>{entry_ma25_dev_loss_mean:.2f} ± {entry_ma25_dev_loss_std:.2f}</b>"],
        'MA75乖離率<br>平均±SD (%)': [f"<b>{entry_ma75_dev_profit_mean:.2f} ± {entry_ma75_dev_profit_std:.2f}</b>", f"<b>{entry_ma75_dev_loss_mean:.2f} ± {entry_ma75_dev_loss_std:.2f}</b>"]
    })
    st.markdown(stats_df.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.markdown("#### <b>t検定（平均値の有意差）</b>", unsafe_allow_html=True)
    def pval_badge(p, label):
        color = '#28a745' if p < 0.05 else '#6c757d'
        text = '有意差あり' if p < 0.05 else '有意差なし'
        return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>"

    st.markdown(pval_badge(entry_ma25_p, 'MA25乖離率'), unsafe_allow_html=True)
    st.markdown(pval_badge(entry_ma75_p, 'MA75乖離率'), unsafe_allow_html=True) 