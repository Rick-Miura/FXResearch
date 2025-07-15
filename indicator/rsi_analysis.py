import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import ttest_ind

def render_rsi_analysis(trades_df):
    """利益・損失グループでRSIの分布や平均値を比較し、t検定も行う"""
    st.subheader("📊 RSI分析（利益・損失グループ比較）")
    if trades_df.empty or 'entry_rsi' not in trades_df or 'exit_rsi' not in trades_df:
        st.info("RSIデータがありません")
        return

    # 利益・損失グループ分け
    profit_trades = trades_df[trades_df['profit_loss'] > 0]
    loss_trades = trades_df[trades_df['profit_loss'] <= 0]

    # エントリーRSI
    entry_rsi_profit = profit_trades['entry_rsi'].dropna()
    entry_rsi_loss = loss_trades['entry_rsi'].dropna()
    # 決済RSI
    exit_rsi_profit = profit_trades['exit_rsi'].dropna()
    exit_rsi_loss = loss_trades['exit_rsi'].dropna()

    # 平均・標準偏差
    def stats(arr):
        return np.mean(arr), np.std(arr)

    entry_rsi_profit_mean, entry_rsi_profit_std = stats(entry_rsi_profit)
    entry_rsi_loss_mean, entry_rsi_loss_std = stats(entry_rsi_loss)
    exit_rsi_profit_mean, exit_rsi_profit_std = stats(exit_rsi_profit)
    exit_rsi_loss_mean, exit_rsi_loss_std = stats(exit_rsi_loss)

    # t検定
    entry_ttest = ttest_ind(entry_rsi_profit, entry_rsi_loss, equal_var=False, nan_policy='omit')
    exit_ttest = ttest_ind(exit_rsi_profit, exit_rsi_loss, equal_var=False, nan_policy='omit')
    def get_pvalue(ttest_result):
        # scipy 1.6以降はTtestResult、古いバージョンはタプル
        if hasattr(ttest_result, 'pvalue'):
            return float(ttest_result.pvalue)
        elif isinstance(ttest_result, (tuple, list)) and len(ttest_result) > 1:
            return float(ttest_result[1])
        return float('nan')

    entry_p = get_pvalue(entry_ttest)
    exit_p = get_pvalue(exit_ttest)

    # ヒストグラム
    fig_entry = go.Figure()
    fig_entry.add_trace(go.Histogram(
        x=entry_rsi_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
    ))
    fig_entry.add_trace(go.Histogram(
        x=entry_rsi_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
    ))
    fig_entry.update_layout(
        barmode='group',
        title='エントリー時RSI分布',
        xaxis_title='RSI',
        yaxis_title='件数',
        legend=dict(x=0.7, y=0.95)
    )

    fig_exit = go.Figure()
    fig_exit.add_trace(go.Histogram(
        x=exit_rsi_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
    ))
    fig_exit.add_trace(go.Histogram(
        x=exit_rsi_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
    ))
    fig_exit.update_layout(
        barmode='group',
        title='決済時RSI分布',
        xaxis_title='RSI',
        yaxis_title='件数',
        legend=dict(x=0.7, y=0.95)
    )

    st.plotly_chart(fig_entry, use_container_width=True)
    st.plotly_chart(fig_exit, use_container_width=True)

    # 統計値・t検定結果
    st.markdown("#### <b>平均・標準偏差</b>", unsafe_allow_html=True)
    import pandas as pd
    stats_df = pd.DataFrame({
        'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
        'エントリーRSI<br>平均±SD': [f"<b>{entry_rsi_profit_mean:.2f} ± {entry_rsi_profit_std:.2f}</b>", f"<b>{entry_rsi_loss_mean:.2f} ± {entry_rsi_loss_std:.2f}</b>"],
        '決済RSI<br>平均±SD': [f"<b>{exit_rsi_profit_mean:.2f} ± {exit_rsi_profit_std:.2f}</b>", f"<b>{exit_rsi_loss_mean:.2f} ± {exit_rsi_loss_std:.2f}</b>"]
    })
    st.markdown(stats_df.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.markdown("#### <b>t検定（平均値の有意差）</b>", unsafe_allow_html=True)
    def pval_badge(p, label):
        color = '#28a745' if p < 0.05 else '#6c757d'
        text = '有意差あり' if p < 0.05 else '有意差なし'
        return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>"

    st.markdown(pval_badge(entry_p, 'エントリーRSI'), unsafe_allow_html=True)
    st.markdown(pval_badge(exit_p, '決済RSI'), unsafe_allow_html=True) 