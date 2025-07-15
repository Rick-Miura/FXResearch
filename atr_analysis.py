import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import ttest_ind


def render_atr_analysis(trades_df):
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

    # 平均・標準偏差
    def stats(arr):
        return np.mean(arr), np.std(arr)

    entry_atr_profit_mean, entry_atr_profit_std = stats(entry_atr_profit)
    entry_atr_loss_mean, entry_atr_loss_std = stats(entry_atr_loss)

    # t検定
    entry_ttest = ttest_ind(entry_atr_profit, entry_atr_loss, equal_var=False, nan_policy='omit')
    def get_pvalue(ttest_result):
        if hasattr(ttest_result, 'pvalue'):
            return float(ttest_result.pvalue)
        elif isinstance(ttest_result, (tuple, list)) and len(ttest_result) > 1:
            return float(ttest_result[1])
        return float('nan')

    entry_p = get_pvalue(entry_ttest)

    # ヒストグラム
    fig_entry = go.Figure()
    fig_entry.add_trace(go.Histogram(
        x=entry_atr_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
    ))
    fig_entry.add_trace(go.Histogram(
        x=entry_atr_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
    ))
    fig_entry.update_layout(
        barmode='group',
        title='エントリー時ATR分布',
        xaxis_title='ATR',
        yaxis_title='件数',
        legend=dict(x=0.7, y=0.95)
    )

    st.plotly_chart(fig_entry, use_container_width=True)

    # 統計値・t検定結果
    st.markdown("#### <b>平均・標準偏差</b>", unsafe_allow_html=True)
    import pandas as pd
    stats_df = pd.DataFrame({
        'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
        'エントリーATR<br>平均±SD': [f"<b>{entry_atr_profit_mean:.4f} ± {entry_atr_profit_std:.4f}</b>", f"<b>{entry_atr_loss_mean:.4f} ± {entry_atr_loss_std:.4f}</b>"]
    })
    st.markdown(stats_df.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.markdown("#### <b>t検定（平均値の有意差）</b>", unsafe_allow_html=True)
    def pval_badge(p, label):
        color = '#28a745' if p < 0.05 else '#6c757d'
        text = '有意差あり' if p < 0.05 else '有意差なし'
        return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>"

    st.markdown(pval_badge(entry_p, 'エントリーATR'), unsafe_allow_html=True) 