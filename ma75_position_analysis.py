import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import ttest_ind
import pandas as pd


def calculate_ma75_position_ratio(trades_df, df):
    """エントリー前10データのCloseがMA75より上にある割合を計算（トレンド別）"""
    trades_df = trades_df.copy()
    ma75_position_ratios = []
    
    for idx, trade in trades_df.iterrows():
        entry_date = trade['entry_date']
        
        # エントリー前10データを取得
        entry_idx = df[df['DateTime'] == entry_date].index
        if len(entry_idx) == 0:
            ma75_position_ratios.append(None)
            continue
            
        entry_idx = entry_idx[0]
        start_idx = max(0, entry_idx - 10)
        
        # エントリー前10データ（エントリー日は含まない）
        recent_data = df.iloc[start_idx:entry_idx]
        
        if len(recent_data) == 0:
            ma75_position_ratios.append(None)
            continue
        
        # CloseがMA75より上にあるデータ数をカウント
        above_ma75_count = 0
        total_count = 0
        
        for _, row in recent_data.iterrows():
            if pd.notnull(row['Close']) and pd.notnull(row['MA75']):
                total_count += 1
                if row['Close'] > row['MA75']:
                    above_ma75_count += 1
        
        # 割合を計算（0-100%）
        if total_count > 0:
            ratio = (above_ma75_count / total_count) * 100
        else:
            ratio = None
            
        ma75_position_ratios.append(ratio)
    
    trades_df['ma75_position_ratio'] = ma75_position_ratios
    return trades_df


def render_ma75_position_analysis(trades_df, df):
    """利益・損失グループでエントリー前10データのMA75位置関係の分布や平均値を比較し、t検定も行う（トレンド別）"""
    st.subheader("📊 MA75位置関係分析（エントリー前10データ・損益グループ比較）")
    
    # MA75位置関係の割合を計算
    trades_df_with_ratio = calculate_ma75_position_ratio(trades_df, df)
    
    if trades_df_with_ratio.empty or 'ma75_position_ratio' not in trades_df_with_ratio:
        st.info("MA75位置関係データがありません")
        return

    # 強気・弱気トレンド別に分析
    bullish_trades = trades_df_with_ratio[trades_df_with_ratio['entry_trend'] == 'bullish']
    bearish_trades = trades_df_with_ratio[trades_df_with_ratio['entry_trend'] == 'bearish']
    
    # 強気トレンドの分析
    if len(bullish_trades) > 0:
        st.markdown("### 📈 強気パーフェクトオーダー分析")
        
        # 利益・損失グループ分け（強気のみ）
        bullish_profit = bullish_trades[bullish_trades['profit_loss'] > 0]
        bullish_loss = bullish_trades[bullish_trades['profit_loss'] <= 0]
        
        if len(bullish_profit) > 0 and len(bullish_loss) > 0:
            # MA75位置関係の割合（強気）
            ma75_ratio_bullish_profit = bullish_profit['ma75_position_ratio'].dropna()
            ma75_ratio_bullish_loss = bullish_loss['ma75_position_ratio'].dropna()
            
            if len(ma75_ratio_bullish_profit) > 0 and len(ma75_ratio_bullish_loss) > 0:
                # 平均・標準偏差
                def stats(arr):
                    return np.mean(arr), np.std(arr)
                
                ma75_ratio_bullish_profit_mean, ma75_ratio_bullish_profit_std = stats(ma75_ratio_bullish_profit)
                ma75_ratio_bullish_loss_mean, ma75_ratio_bullish_loss_std = stats(ma75_ratio_bullish_loss)
                
                # t検定
                ma75_ratio_bullish_ttest = ttest_ind(ma75_ratio_bullish_profit, ma75_ratio_bullish_loss, equal_var=False, nan_policy='omit')
                def get_pvalue(ttest_result):
                    if hasattr(ttest_result, 'pvalue'):
                        return float(ttest_result.pvalue)
                    elif isinstance(ttest_result, (tuple, list)) and len(ttest_result) > 1:
                        return float(ttest_result[1])
                    return float('nan')
                
                ma75_ratio_bullish_p = get_pvalue(ma75_ratio_bullish_ttest)
                
                # ヒストグラム（強気）
                fig_bullish = go.Figure()
                fig_bullish.add_trace(go.Histogram(
                    x=ma75_ratio_bullish_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
                ))
                fig_bullish.add_trace(go.Histogram(
                    x=ma75_ratio_bullish_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
                ))
                fig_bullish.update_layout(
                    barmode='group',
                    title='強気パーフェクトオーダー: エントリー前10データのCloseがMA75より上にある割合分布',
                    xaxis_title='MA75より上にある割合 (%)',
                    yaxis_title='件数',
                    legend=dict(x=0.7, y=0.95)
                )
                
                st.plotly_chart(fig_bullish, use_container_width=True)
                
                # 統計値・t検定結果（強気）
                st.markdown("#### <b>強気パーフェクトオーダー: 平均・標準偏差</b>", unsafe_allow_html=True)
                import pandas as pd
                stats_df_bullish = pd.DataFrame({
                    'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
                    'MA75より上にある割合<br>平均±SD (%)': [f"<b>{ma75_ratio_bullish_profit_mean:.1f} ± {ma75_ratio_bullish_profit_std:.1f}</b>", f"<b>{ma75_ratio_bullish_loss_mean:.1f} ± {ma75_ratio_bullish_loss_std:.1f}</b>"]
                })
                st.markdown(stats_df_bullish.to_html(escape=False, index=False), unsafe_allow_html=True)
                
                st.markdown("#### <b>強気パーフェクトオーダー: t検定（平均値の有意差）</b>", unsafe_allow_html=True)
                def pval_badge(p, label):
                    color = '#28a745' if p < 0.05 else '#6c757d'
                    text = '有意差あり' if p < 0.05 else '有意差なし'
                    return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>"
                
                st.markdown(pval_badge(ma75_ratio_bullish_p, '強気MA75位置関係割合'), unsafe_allow_html=True)
    
    # 弱気トレンドの分析
    if len(bearish_trades) > 0:
        st.markdown("### 📉 弱気パーフェクトオーダー分析")
        
        # 利益・損失グループ分け（弱気のみ）
        bearish_profit = bearish_trades[bearish_trades['profit_loss'] > 0]
        bearish_loss = bearish_trades[bearish_trades['profit_loss'] <= 0]
        
        if len(bearish_profit) > 0 and len(bearish_loss) > 0:
            # MA75位置関係の割合（弱気）
            ma75_ratio_bearish_profit = bearish_profit['ma75_position_ratio'].dropna()
            ma75_ratio_bearish_loss = bearish_loss['ma75_position_ratio'].dropna()
            
            if len(ma75_ratio_bearish_profit) > 0 and len(ma75_ratio_bearish_loss) > 0:
                # 平均・標準偏差
                def stats(arr):
                    return np.mean(arr), np.std(arr)
                
                ma75_ratio_bearish_profit_mean, ma75_ratio_bearish_profit_std = stats(ma75_ratio_bearish_profit)
                ma75_ratio_bearish_loss_mean, ma75_ratio_bearish_loss_std = stats(ma75_ratio_bearish_loss)
                
                # t検定
                ma75_ratio_bearish_ttest = ttest_ind(ma75_ratio_bearish_profit, ma75_ratio_bearish_loss, equal_var=False, nan_policy='omit')
                def get_pvalue(ttest_result):
                    if hasattr(ttest_result, 'pvalue'):
                        return float(ttest_result.pvalue)
                    elif isinstance(ttest_result, (tuple, list)) and len(ttest_result) > 1:
                        return float(ttest_result[1])
                    return float('nan')
                
                ma75_ratio_bearish_p = get_pvalue(ma75_ratio_bearish_ttest)
                
                # ヒストグラム（弱気）
                fig_bearish = go.Figure()
                fig_bearish.add_trace(go.Histogram(
                    x=ma75_ratio_bearish_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
                ))
                fig_bearish.add_trace(go.Histogram(
                    x=ma75_ratio_bearish_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
                ))
                fig_bearish.update_layout(
                    barmode='group',
                    title='弱気パーフェクトオーダー: エントリー前10データのCloseがMA75より上にある割合分布',
                    xaxis_title='MA75より上にある割合 (%)',
                    yaxis_title='件数',
                    legend=dict(x=0.7, y=0.95)
                )
                
                st.plotly_chart(fig_bearish, use_container_width=True)
                
                # 統計値・t検定結果（弱気）
                st.markdown("#### <b>弱気パーフェクトオーダー: 平均・標準偏差</b>", unsafe_allow_html=True)
                stats_df_bearish = pd.DataFrame({
                    'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
                    'MA75より上にある割合<br>平均±SD (%)': [f"<b>{ma75_ratio_bearish_profit_mean:.1f} ± {ma75_ratio_bearish_profit_std:.1f}</b>", f"<b>{ma75_ratio_bearish_loss_mean:.1f} ± {ma75_ratio_bearish_loss_std:.1f}</b>"]
                })
                st.markdown(stats_df_bearish.to_html(escape=False, index=False), unsafe_allow_html=True)
                
                st.markdown("#### <b>弱気パーフェクトオーダー: t検定（平均値の有意差）</b>", unsafe_allow_html=True)
                def pval_badge(p, label):
                    color = '#28a745' if p < 0.05 else '#6c757d'
                    text = '有意差あり' if p < 0.05 else '有意差なし'
                    return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>"
                
                st.markdown(pval_badge(ma75_ratio_bearish_p, '弱気MA75位置関係割合'), unsafe_allow_html=True)
    
    # 解釈の説明
    st.markdown("#### <b>分析の解釈</b>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745; color: #155724;">
    <ul style="color: #155724;">
    <li><strong>強気パーフェクトオーダー</strong>: エントリー前10データの多くがMA75より上にある（高い割合）方が良い</li>
    <li><strong>弱気パーフェクトオーダー</strong>: エントリー前10データの多くがMA75より下にある（低い割合）方が良い</li>
    <li><strong>50%付近</strong>: エントリー前10データがMA75をまたいでいる → 横ばい・調整局面でのエントリー</li>
    </ul>
    </div>
    """, unsafe_allow_html=True) 