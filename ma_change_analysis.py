import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import ttest_ind
import pandas as pd


def calculate_ma_change_rate(trades_df, df):
    """エントリー時のMA25、MA75、MA200の5単位前からの変化量（％）を計算"""
    trades_df = trades_df.copy()
    
    # 各MAの変化量を格納するリスト
    ma25_change_rates = []
    ma75_change_rates = []
    ma200_change_rates = []
    
    for idx, trade in trades_df.iterrows():
        entry_date = trade['entry_date']
        
        # エントリー日のインデックスを取得
        entry_idx = df[df['DateTime'] == entry_date].index
        if len(entry_idx) == 0:
            ma25_change_rates.append(None)
            ma75_change_rates.append(None)
            ma200_change_rates.append(None)
            continue
            
        entry_idx = entry_idx[0]
        
        # 5単位前のインデックス
        prev_idx = max(0, entry_idx - 5)
        
        # エントリー時と5単位前のMA値を取得
        entry_ma25 = df.iloc[entry_idx]['MA25']
        entry_ma75 = df.iloc[entry_idx]['MA75']
        entry_ma200 = df.iloc[entry_idx]['MA200']
        
        prev_ma25 = df.iloc[prev_idx]['MA25']
        prev_ma75 = df.iloc[prev_idx]['MA75']
        prev_ma200 = df.iloc[prev_idx]['MA200']
        
        # 変化量（％）を計算
        def calc_change_rate(current, previous):
            if pd.notnull(current) and pd.notnull(previous) and previous != 0:
                return ((current - previous) / previous) * 100
            else:
                return None
        
        ma25_change_rate = calc_change_rate(entry_ma25, prev_ma25)
        ma75_change_rate = calc_change_rate(entry_ma75, prev_ma75)
        ma200_change_rate = calc_change_rate(entry_ma200, prev_ma200)
        
        ma25_change_rates.append(ma25_change_rate)
        ma75_change_rates.append(ma75_change_rate)
        ma200_change_rates.append(ma200_change_rate)
    
    trades_df['ma25_change_rate'] = ma25_change_rates
    trades_df['ma75_change_rate'] = ma75_change_rates
    trades_df['ma200_change_rate'] = ma200_change_rates
    
    return trades_df


def render_ma_change_analysis(trades_df, df):
    """MAの5単位前からの変化量（％）と損益の関連性を分析"""
    st.subheader("📈 MA変化量分析（5単位前からの変化率）")
    
    # MA変化量を計算
    trades_df_with_change = calculate_ma_change_rate(trades_df, df)
    
    if trades_df_with_change.empty:
        st.info("MA変化量データがありません")
        return
    
    # 利益・損失グループ分け
    profit_trades = trades_df_with_change[trades_df_with_change['profit_loss'] > 0]
    loss_trades = trades_df_with_change[trades_df_with_change['profit_loss'] <= 0]
    
    if len(profit_trades) == 0 or len(loss_trades) == 0:
        st.info("利益グループまたは損失グループのデータが不足しています")
        return
    
    # 各MAの変化量を分析
    ma_columns = ['ma25_change_rate', 'ma75_change_rate', 'ma200_change_rate']
    ma_names = ['MA25', 'MA75', 'MA200']
    
    for ma_col, ma_name in zip(ma_columns, ma_names):
        st.markdown(f"### 📊 {ma_name}変化量分析")
        
        # 利益・損失グループの変化量を取得
        profit_changes = profit_trades[ma_col].dropna()
        loss_changes = loss_trades[ma_col].dropna()
        
        if len(profit_changes) == 0 or len(loss_changes) == 0:
            st.info(f"{ma_name}の変化量データが不足しています")
            continue
        
        # 統計値計算
        profit_mean = np.mean(profit_changes)
        profit_std = np.std(profit_changes)
        loss_mean = np.mean(loss_changes)
        loss_std = np.std(loss_changes)
        
        # t検定
        ttest_result = ttest_ind(profit_changes, loss_changes, equal_var=False, nan_policy='omit')
        p_value = ttest_result.pvalue if hasattr(ttest_result, 'pvalue') else float('nan')
        
        # ヒストグラム
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=profit_changes, name='利益グループ', opacity=0.8, 
            marker_color='blue', marker_line_width=2, marker_line_color='black'
        ))
        fig.add_trace(go.Histogram(
            x=loss_changes, name='損失グループ', opacity=0.8, 
            marker_color='red', marker_line_width=2, marker_line_color='black'
        ))
        fig.update_layout(
            barmode='group',
            title=f'{ma_name}: エントリー時5単位前からの変化量分布',
            xaxis_title='変化量 (%)',
            yaxis_title='件数',
            legend=dict(x=0.7, y=0.95)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 統計値・t検定結果
        st.markdown(f"#### <b>{ma_name}: 平均・標準偏差</b>", unsafe_allow_html=True)
        stats_df = pd.DataFrame({
            'グループ': ['<b style="color:blue">利益グループ</b>', '<b style="color:red">損失グループ</b>'],
            '取引数': [len(profit_changes), len(loss_changes)],
            f'{ma_name}変化量<br>平均±SD (%)': [
                f"<b>{profit_mean:.3f} ± {profit_std:.3f}</b>", 
                f"<b>{loss_mean:.3f} ± {loss_std:.3f}</b>"
            ]
        })
        st.markdown(stats_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        st.markdown(f"#### <b>{ma_name}: t検定（平均値の有意差）</b>", unsafe_allow_html=True)
        def pval_badge(p, label):
            color = '#28a745' if p < 0.05 else '#6c757d'
            text = '有意差あり' if p < 0.05 else '有意差なし'
            return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>"
        
        st.markdown(pval_badge(p_value, f'{ma_name}変化量'), unsafe_allow_html=True)
        
        st.markdown("---")
    
    # 強気・弱気トレンド別分析
    st.markdown("### 📊 トレンド別MA変化量分析")
    
    for trend_label, trend_name in [('bullish', '強気'), ('bearish', '弱気')]:
        trend_trades = trades_df_with_change[trades_df_with_change['entry_trend'] == trend_label]
        
        if len(trend_trades) == 0:
            st.info(f"{trend_name}パーフェクトオーダーの取引データがありません")
            continue
        
        st.markdown(f"#### 📈 {trend_name}パーフェクトオーダー")
        
        # 利益・損失グループ分け（トレンド別）
        trend_profit = trend_trades[trend_trades['profit_loss'] > 0]
        trend_loss = trend_trades[trend_trades['profit_loss'] <= 0]
        
        if len(trend_profit) == 0 or len(trend_loss) == 0:
            st.info(f"{trend_name}: 利益グループ({len(trend_profit)}件) または 損失グループ({len(trend_loss)}件)のデータが不足しています")
            continue
        
        # 各MAの変化量を分析（トレンド別）
        for ma_col, ma_name in zip(ma_columns, ma_names):
            profit_changes = trend_profit[ma_col].dropna()
            loss_changes = trend_loss[ma_col].dropna()
            
            if len(profit_changes) == 0 or len(loss_changes) == 0:
                continue
            
            # 統計値計算
            profit_mean = np.mean(profit_changes)
            profit_std = np.std(profit_changes)
            loss_mean = np.mean(loss_changes)
            loss_std = np.std(loss_changes)
            
            # t検定
            ttest_result = ttest_ind(profit_changes, loss_changes, equal_var=False, nan_policy='omit')
            p_value = ttest_result.pvalue if hasattr(ttest_result, 'pvalue') else float('nan')
            
            # 統計値・t検定結果（トレンド別）
            st.markdown(f"**{ma_name}**: 利益 {profit_mean:.3f}±{profit_std:.3f}% vs 損失 {loss_mean:.3f}±{loss_std:.3f}% (p={p_value:.4f})")
        
        st.markdown("---")
    
    # 解釈の説明
    st.markdown("#### <b>分析の解釈</b>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745; color: #155724;">
    <ul style="color: #155724;">
    <li><strong>正の変化量</strong>: MAが上昇トレンド → 上昇勢いでのエントリー</li>
    <li><strong>負の変化量</strong>: MAが下降トレンド → 下降勢いでのエントリー</li>
    <li><strong>大きな変化量</strong>: 急激なMAの変化 → 強いトレンドでのエントリー</li>
    <li><strong>小さな変化量</strong>: 緩やかなMAの変化 → 弱いトレンドでのエントリー</li>
    <li><strong>トレンド別分析</strong>: 強気・弱気で異なる傾向があるかを検証</li>
    </ul>
    </div>
    """, unsafe_allow_html=True) 