import streamlit as st
import pandas as pd
import numpy as np

def render_trade_summary(trades_df):
    """取引統計サマリーを表示"""
    if trades_df.empty:
        st.warning("取引データがありません")
        return
    
    # 基本統計計算
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['profit_loss'] > 0])
    losing_trades = len(trades_df[trades_df['profit_loss'] < 0])
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    total_profit_loss = trades_df['profit_loss'].sum()
    avg_profit_loss = trades_df['profit_loss'].mean()
    
    max_profit = trades_df['profit_loss'].max()
    max_loss = trades_df['profit_loss'].min()
    
    # 利益因子計算
    total_profit = trades_df[trades_df['profit_loss'] > 0]['profit_loss'].sum()
    total_loss = abs(trades_df[trades_df['profit_loss'] < 0]['profit_loss'].sum())
    profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
    
    # 勝ち負け取引の平均
    avg_winning_profit = trades_df[trades_df['profit_loss'] > 0]['profit_loss'].mean() if winning_trades > 0 else 0
    avg_losing_loss = trades_df[trades_df['profit_loss'] < 0]['profit_loss'].mean() if losing_trades > 0 else 0
    
    # 連勝連敗計算
    consecutive_wins, consecutive_losses = calculate_consecutive_trades(trades_df)
    
    # 平均保有期間
    avg_duration = trades_df['duration_days'].mean() if 'duration_days' in trades_df.columns else 0
    max_duration = trades_df['duration_days'].max() if 'duration_days' in trades_df.columns else 0
    min_duration = trades_df['duration_days'].min() if 'duration_days' in trades_df.columns else 0
    
    # 決済理由別統計
    exit_reason_stats = trades_df['exit_reason'].value_counts()
    
    # トレンド別統計
    trend_stats = trades_df['entry_trend'].value_counts() if 'entry_trend' in trades_df.columns else pd.Series()
    
    # 表示
    st.markdown("## 📊 取引統計サマリー")
    
    # 最重要情報（2行で表示）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("取引回数", f"{total_trades:,}回")
    
    with col2:
        st.metric("勝率", f"{win_rate:.1f}%")
    
    with col3:
        profit_color = "green" if total_profit_loss > 0 else "red"
        st.metric("最終利益", f"{total_profit_loss:,.0f}円")
    
    with col4:
        st.metric("平均損益", f"{avg_profit_loss:,.0f}円")
    
    # リスク・詳細統計（2行で表示）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("最大利益", f"{max_profit:,.0f}円")
    
    with col2:
        st.metric("最大損失", f"{max_loss:,.0f}円")
    
    with col3:
        st.metric("利益因子", f"{profit_factor:.2f}")
    
    with col4:
        st.metric("平均保有期間", f"{avg_duration:.1f}日")
    
    # 勝敗詳細（2行で表示）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("勝ち取引平均", f"{avg_winning_profit:,.0f}円")
    
    with col2:
        st.metric("負け取引平均", f"{avg_losing_loss:,.0f}円")
    
    with col3:
        st.metric("最大連勝", f"{consecutive_wins}回")
    
    with col4:
        st.metric("最大連敗", f"{consecutive_losses}回")
    


def calculate_consecutive_trades(trades_df):
    """連勝連敗を計算"""
    if trades_df.empty:
        return 0, 0
    
    # 損益の符号を取得
    profits = trades_df['profit_loss'].values
    signs = np.sign(profits)
    
    max_consecutive_wins = 0
    max_consecutive_losses = 0
    current_wins = 0
    current_losses = 0
    
    for sign in signs:
        if sign > 0:  # 勝ち
            current_wins += 1
            current_losses = 0
            max_consecutive_wins = max(max_consecutive_wins, current_wins)
        elif sign < 0:  # 負け
            current_losses += 1
            current_wins = 0
            max_consecutive_losses = max(max_consecutive_losses, current_losses)
    
    return max_consecutive_wins, max_consecutive_losses 