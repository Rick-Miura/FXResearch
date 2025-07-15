import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import ttest_ind
import pandas as pd


def calculate_ma75_position_ratio(trades_df, df):
    """エントリー前10データのCloseがMA75より上にある割合を計算"""
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


def categorize_position_size_by_profit_loss(trades_df):
    """損益の絶対値で小・中・大の3グループに分類"""
    trades_df = trades_df.copy()
    
    # 損益の絶対値を計算
    trades_df['profit_loss_abs'] = trades_df['profit_loss'].abs()
    
    # 損益の絶対値で3分割
    profit_loss_abs_sorted = trades_df['profit_loss_abs'].sort_values()
    n = len(profit_loss_abs_sorted)
    
    if n == 0:
        return trades_df
    
    # 3分割の境界値を計算
    small_threshold = profit_loss_abs_sorted.iloc[n // 3]
    large_threshold = profit_loss_abs_sorted.iloc[2 * n // 3]
    
    # 分類
    def categorize_by_profit_loss(row):
        abs_profit_loss = row['profit_loss_abs']
        if abs_profit_loss <= small_threshold:
            return '小'
        elif abs_profit_loss <= large_threshold:
            return '中'
        else:
            return '大'
    
    trades_df['position_size_category'] = trades_df.apply(categorize_by_profit_loss, axis=1)
    return trades_df


def render_position_size_ma75_analysis(trades_df, df):
    """取引サイズ別でMA75位置関係分析を行う"""
    # st.subheader("💰 取引サイズ別MA75位置関係分析")
    
    # MA75位置関係の割合を計算
    trades_df_with_ratio = calculate_ma75_position_ratio(trades_df, df)
    
    if trades_df_with_ratio.empty or 'ma75_position_ratio' not in trades_df_with_ratio:
        # st.info("MA75位置関係データがありません")
        return
    
    # 取引サイズのカテゴリを追加（損益の絶対値で分類）
    trades_df_with_ratio = categorize_position_size_by_profit_loss(trades_df_with_ratio)
    
    # 取引サイズ分布の確認
    # st.markdown("### 📊 損益別分類結果")
    # size_distribution = trades_df_with_ratio['position_size_category'].value_counts()
    # st.info(f"分類結果: 小サイズ {size_distribution.get('小', 0)}件, 中サイズ {size_distribution.get('中', 0)}件, 大サイズ {size_distribution.get('大', 0)}件")
    
    # 各カテゴリの損益範囲を表示
    # for category in ['小', '中', '大']:
    #     category_trades = trades_df_with_ratio[trades_df_with_ratio['position_size_category'] == category]
    #     if len(category_trades) > 0:
    #         min_profit_loss = category_trades['profit_loss'].min()
    #         max_profit_loss = category_trades['profit_loss'].max()
    #         st.info(f"{category}サイズ: 損益範囲 {min_profit_loss:,.0f}円 ～ {max_profit_loss:,.0f}円")
    
    # 取引サイズ別に分析
    # for category in ['小', '中', '大']:
    #     category_trades = trades_df_with_ratio[trades_df_with_ratio['position_size_category'] == category]
        
    #     if len(category_trades) == 0:
    #         st.info(f"{category}サイズの取引データがありません")
    #         continue
            
    #     st.markdown(f"### 📊 {category}サイズ取引のMA75位置関係分析")
    #     st.info(f"{category}サイズ取引数: {len(category_trades)}件")
        
    #     # 強気・弱気トレンド別に分析
    #     bullish_trades = category_trades[category_trades['entry_trend'] == 'bullish']
    #     bearish_trades = category_trades[category_trades['entry_trend'] == 'bearish']
        
    #     # 強気トレンドの分析
    #     if len(bullish_trades) > 0:
    #         st.markdown(f"#### 📈 {category}サイズ: 強気パーフェクトオーダー")
            
    #         # 利益・損失グループ分け（強気のみ）
    #         bullish_profit = bullish_trades[bullish_trades['profit_loss'] > 0]
    #         bullish_loss = bullish_trades[bullish_trades['profit_loss'] <= 0]
            
    #         if len(bullish_profit) > 0 and len(bullish_loss) > 0:
    #             # MA75位置関係の割合（強気）
    #             ma75_ratio_bullish_profit = bullish_profit['ma75_position_ratio'].dropna()
    #             ma75_ratio_bullish_loss = bullish_loss['ma75_position_ratio'].dropna()
                
    #             if len(ma75_ratio_bullish_profit) > 0 and len(ma75_ratio_bullish_loss) > 0:
    #                 # 平均・標準偏差
    #                 def stats(arr):
    #                     return np.mean(arr), np.std(arr)
                    
    #                 ma75_ratio_bullish_profit_mean, ma75_ratio_bullish_profit_std = stats(ma75_ratio_bullish_profit)
    #                 ma75_ratio_bullish_loss_mean, ma75_ratio_bullish_loss_std = stats(ma75_ratio_bullish_loss)
                    
    #                 # t検定
    #                 ma75_ratio_bullish_ttest = ttest_ind(ma75_ratio_bullish_profit, ma75_ratio_bullish_loss, equal_var=False, nan_policy='omit')
    #                 def get_pvalue(ttest_result):
    #                     if hasattr(ttest_result, 'pvalue'):
    #                         return float(ttest_result.pvalue)
    #                     elif isinstance(ttest_result, (tuple, list)) and len(ttest_result) > 1:
    #                         return float(ttest_result[1])
    #                     return float('nan')
                    
    #                 ma75_ratio_bullish_p = get_pvalue(ma75_ratio_bullish_ttest)
                    
    #                 # ヒストグラム（強気）
    #                 # fig_bullish = go.Figure()
    #                 # fig_bullish.add_trace(go.Histogram(
    #                 #     x=ma75_ratio_bullish_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
    #                 # ))
    #                 # fig_bullish.add_trace(go.Histogram(
    #                 #     x=ma75_ratio_bullish_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
    #                 # ))
    #                 # fig_bullish.update_layout(
    #                 #     barmode='group',
    #                 #     title=f'{category}サイズ強気: エントリー前10データのCloseがMA75より上にある割合分布',
    #                 #     xaxis_title='MA75より上にある割合 (%)',
    #                 #     yaxis_title='件数',
    #                 #     legend=dict(x=0.7, y=0.95)
    #                 # )
                    
    #                 # st.plotly_chart(fig_bullish, use_container_width=True)
                    
    #                 # 統計値・t検定結果（強気）
    #                 st.markdown(f"#### <b>{category}サイズ強気: 平均・標準偏差</b>", unsafe_allow_html=True)
    #                 stats_df_bullish = pd.DataFrame({
    #                     'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
    #                     '取引数': [len(ma75_ratio_bullish_profit), len(ma75_ratio_bullish_loss)],
    #                     'MA75より上にある割合<br>平均±SD (%)': [f"<b>{ma75_ratio_bullish_profit_mean:.1f} ± {ma75_ratio_bullish_profit_std:.1f}</b>", f"<b>{ma75_ratio_bullish_loss_mean:.1f} ± {ma75_ratio_bullish_loss_std:.1f}</b>"]
    #                 })
    #                 st.markdown(stats_df_bullish.to_html(escape=False, index=False), unsafe_allow_html=True)
                    
    #                 st.markdown(f"#### <b>{category}サイズ強気: t検定（平均値の有意差）</b>", unsafe_allow_html=True)
    #                 def pval_badge(p, label):
    #                     color = '#28a745' if p < 0.05 else '#6c757d'
    #                     text = '有意差あり' if p < 0.05 else '有意差なし'
    #                     return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>"
                    
    #                 st.markdown(pval_badge(ma75_ratio_bullish_p, f'{category}サイズ強気MA75位置関係割合'), unsafe_allow_html=True)
    #         else:
    #             st.info(f"{category}サイズ強気: 利益グループ({len(bullish_profit)}件) または 損失グループ({len(bullish_loss)}件)のデータが不足しています")
    #     else:
    #         st.info(f"{category}サイズ: 強気取引データがありません")
        
    #     # 弱気トレンドの分析
    #     if len(bearish_trades) > 0:
    #         st.markdown(f"#### 📉 {category}サイズ: 弱気パーフェクトオーダー")
            
    #         # 利益・損失グループ分け（弱気のみ）
    #         bearish_profit = bearish_trades[bearish_trades['profit_loss'] > 0]
    #         bearish_loss = bearish_trades[bearish_trades['profit_loss'] <= 0]
            
    #         if len(bearish_profit) > 0 and len(bearish_loss) > 0:
    #             # MA75位置関係の割合（弱気）
    #             ma75_ratio_bearish_profit = bearish_profit['ma75_position_ratio'].dropna()
    #             ma75_ratio_bearish_loss = bearish_loss['ma75_position_ratio'].dropna()
                
    #             if len(ma75_ratio_bearish_profit) > 0 and len(ma75_ratio_bearish_loss) > 0:
    #                 # 平均・標準偏差
    #                 def stats(arr):
    #                     return np.mean(arr), np.std(arr)
                    
    #                 ma75_ratio_bearish_profit_mean, ma75_ratio_bearish_profit_std = stats(ma75_ratio_bearish_profit)
    #                 ma75_ratio_bearish_loss_mean, ma75_ratio_bearish_loss_std = stats(ma75_ratio_bearish_loss)
                    
    #                 # t検定
    #                 ma75_ratio_bearish_ttest = ttest_ind(ma75_ratio_bearish_profit, ma75_ratio_bearish_loss, equal_var=False, nan_policy='omit')
    #                 def get_pvalue(ttest_result):
    #                     if hasattr(ttest_result, 'pvalue'):
    #                         return float(ttest_result.pvalue)
    #                     elif isinstance(ttest_result, (tuple, list)) and len(ttest_result) > 1:
    #                         return float(ttest_result[1])
    #                     return float('nan')
                    
    #                 ma75_ratio_bearish_p = get_pvalue(ma75_ratio_bearish_ttest)
                    
    #                 # ヒストグラム（弱気）
    #                 # fig_bearish = go.Figure()
    #                 # fig_bearish.add_trace(go.Histogram(
    #                 #     x=ma75_ratio_bearish_profit, name='利益グループ', opacity=0.8, marker_color='blue', marker_line_width=2, marker_line_color='black'
    #                 # ))
    #                 # fig_bearish.add_trace(go.Histogram(
    #                 #     x=ma75_ratio_bearish_loss, name='損失グループ', opacity=0.8, marker_color='red', marker_line_width=2, marker_line_color='black'
    #                 # ))
    #                 # fig_bearish.update_layout(
    #                 #     barmode='group',
    #                 #     title=f'{category}サイズ弱気: エントリー前10データのCloseがMA75より上にある割合分布',
    #                 #     xaxis_title='MA75より上にある割合 (%)',
    #                 #     yaxis_title='件数',
    #                 #     legend=dict(x=0.7, y=0.95)
    #                 # )
                    
    #                 # st.plotly_chart(fig_bearish, use_container_width=True)
                    
    #                 # 統計値・t検定結果（弱気）
    #                 st.markdown(f"#### <b>{category}サイズ弱気: 平均・標準偏差</b>", unsafe_allow_html=True)
    #                 stats_df_bearish = pd.DataFrame({
    #                     'グループ': ['<b style=\"color:blue\">利益グループ</b>', '<b style=\"color:red\">損失グループ</b>'],
    #                     '取引数': [len(ma75_ratio_bearish_profit), len(ma75_ratio_bearish_loss)],
    #                     'MA75より上にある割合<br>平均±SD (%)': [f"<b>{ma75_ratio_bearish_profit_mean:.1f} ± {ma75_ratio_bearish_profit_std:.1f}</b>", f"<b>{ma75_ratio_bearish_loss_mean:.1f} ± {ma75_ratio_bearish_loss_std:.1f}</b>"]
    #                 })
    #                 st.markdown(stats_df_bearish.to_html(escape=False, index=False), unsafe_allow_html=True)
                    
    #                 st.markdown(f"#### <b>{category}サイズ弱気: t検定（平均値の有意差）</b>", unsafe_allow_html=True)
    #                 def pval_badge(p, label):
    #                     color = '#28a745' if p < 0.05 else '#6c757d'
    #                     text = '有意差あり' if p < 0.05 else '有意差なし'
    #                     return f"{label}: <span style='background:{color};color:white;padding:2px 8px;border-radius:8px;font-weight:bold;'>p={p:.4f} {text}</span>"
                    
    #                 st.markdown(pval_badge(ma75_ratio_bearish_p, f'{category}サイズ弱気MA75位置関係割合'), unsafe_allow_html=True)
    #         else:
    #             st.info(f"{category}サイズ弱気: 利益グループ({len(bearish_profit)}件) または 損失グループ({len(bearish_loss)}件)のデータが不足しています")
    #     else:
    #         st.info(f"{category}サイズ: 弱気取引データがありません")
        
    #     st.markdown("---")
    
    # --- 強気・弱気ごとに直前10データのMA75上/下で勝率を可視化 ---
    # st.markdown("## 📊 強気・弱気×MA75上/下での勝率比較")
    # for trend_label, trend_name in [('bullish', '強気'), ('bearish', '弱気')]:
    #     trend_trades = trades_df_with_ratio[trades_df_with_ratio['entry_trend'] == trend_label]
    #     if len(trend_trades) == 0:
    #         st.info(f"{trend_name}パーフェクトオーダーの取引データがありません")
    #         continue
    #     # 直前10データのうちMA75より上にある割合でグループ分け
    #     above_50 = trend_trades[trend_trades['ma75_position_ratio'] >= 50]
    #     below_50 = trend_trades[trend_trades['ma75_position_ratio'] < 50]
    #     # 勝率計算
    #     def win_rate(df):
    #         return (len(df[df['profit_loss'] > 0]) / len(df) * 100) if len(df) > 0 else 0
    #     win_rate_above = win_rate(above_50)
    #     win_rate_below = win_rate(below_50)
    #     # 件数
    #     n_above = len(above_50)
    #     n_below = len(below_50)
    #     # 棒グラフ
    #     fig = go.Figure()
    #     fig.add_trace(go.Bar(
    #         x=[f'{trend_name}・上(50%以上)', f'{trend_name}・下(50%未満)'],
    #         y=[win_rate_above, win_rate_below],
    #         marker_color=['blue', 'red'],
    #         text=[f'{win_rate_above:.1f}% ({n_above}件)', f'{win_rate_below:.1f}% ({n_below}件)'],
    #         textposition='auto'
    #     ))
    #     fig.update_layout(
    #         title=f'{trend_name}パーフェクトオーダー: 直前10データのMA75上/下での勝率比較',
    #         yaxis_title='勝率(%)',
    #         xaxis_title='グループ',
    #         yaxis=dict(range=[0, 100])
    #     )
    #     st.plotly_chart(fig, use_container_width=True)
    #     st.markdown(f"- {trend_name}・上(50%以上): {n_above}件, 勝率 {win_rate_above:.1f}%")
    #     st.markdown(f"- {trend_name}・下(50%未満): {n_below}件, 勝率 {win_rate_below:.1f}%")

    # 解釈の説明
    # st.markdown("#### <b>分析の解釈</b>", unsafe_allow_html=True)
    # st.markdown("""
    # <div style="background-color: #e8f5e8; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745; color: #155724;">
    # <ul style="color: #155724;">
    # <li><strong>高い割合</strong>: エントリー前10データの多くがMA75より上にある → 上昇トレンドでのエントリー</li>
    # <li><strong>低い割合</strong>: エントリー前10データの多くがMA75より下にある → 下降トレンドでのエントリー</li>
    # <li><strong>50%付近</strong>: エントリー前10データがMA75をまたいでいる → 横ばい・調整局面でのエントリー</li>
    # <li><strong>取引サイズ別分析</strong>: 小・中・大サイズで異なる傾向があるかを検証</li>
    # </ul>
    # </div>
    # """, unsafe_allow_html=True) 