import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import ttest_ind
import pandas as pd


def categorize_position_size(position_size):
    """取引サイズを小・中・大の3グループに分類"""
    if position_size <= 100000:  # 10万円以下
        return '小'
    elif position_size <= 300000:  # 10-30万円
        return '中'
    else:  # 30万円超
        return '大'


def render_position_size_analysis(trades_df):
    """取引サイズごとのグループ分け分析"""
    st.subheader("💰 取引サイズ別分析")
    
    if trades_df.empty:
        st.info("取引データがありません")
        return
    
    # 取引サイズのカテゴリを追加
    trades_df = trades_df.copy()
    trades_df['position_size_category'] = trades_df['position_size'].apply(categorize_position_size)
    
    # 各グループの基本統計
    st.markdown("### 📊 取引サイズ別基本統計")
    
    size_stats = []
    for category in ['小', '中', '大']:
        group_trades = trades_df[trades_df['position_size_category'] == category]
        if len(group_trades) > 0:
            stats = {
                '取引サイズ': category,
                '取引数': len(group_trades),
                '勝率 (%)': (len(group_trades[group_trades['profit_loss'] > 0]) / len(group_trades)) * 100,
                '平均損益 (円)': group_trades['profit_loss'].mean(),
                '平均損益率 (%)': group_trades['profit_loss_pct'].mean(),
                '総損益 (円)': group_trades['profit_loss'].sum(),
                '最大利益 (円)': group_trades['profit_loss'].max(),
                '最大損失 (円)': group_trades['profit_loss'].min(),
                '平均保有期間 (日)': group_trades['duration_days'].mean()
            }
            size_stats.append(stats)
    
    if size_stats:
        stats_df = pd.DataFrame(size_stats)
        st.dataframe(stats_df.round(2), use_container_width=True)
    
    # 取引サイズ別の損益分布
    st.markdown("### 📈 取引サイズ別損益分布")
    
    fig_profit_loss = go.Figure()
    colors = {'小': 'blue', '中': 'orange', '大': 'red'}
    
    for category in ['小', '中', '大']:
        group_trades = trades_df[trades_df['position_size_category'] == category]
        if len(group_trades) > 0:
            fig_profit_loss.add_trace(go.Histogram(
                x=group_trades['profit_loss'],
                name=f'{category}サイズ',
                opacity=0.7,
                marker_color=colors[category],
                nbinsx=20
            ))
    
    fig_profit_loss.update_layout(
        barmode='overlay',
        title='取引サイズ別損益分布',
        xaxis_title='損益 (円)',
        yaxis_title='件数',
        legend=dict(x=0.7, y=0.95)
    )
    
    st.plotly_chart(fig_profit_loss, use_container_width=True)
    
    # 取引サイズ別の勝率比較
    st.markdown("### 🎯 取引サイズ別勝率比較")
    
    win_rates = []
    categories = []
    for category in ['小', '中', '大']:
        group_trades = trades_df[trades_df['position_size_category'] == category]
        if len(group_trades) > 0:
            win_rate = (len(group_trades[group_trades['profit_loss'] > 0]) / len(group_trades)) * 100
            win_rates.append(win_rate)
            categories.append(category)
    
    if win_rates:
        fig_win_rate = go.Figure()
        fig_win_rate.add_trace(go.Bar(
            x=categories,
            y=win_rates,
            marker_color=['blue', 'orange', 'red'],
            text=[f'{rate:.1f}%' for rate in win_rates],
            textposition='auto'
        ))
        
        fig_win_rate.update_layout(
            title='取引サイズ別勝率',
            xaxis_title='取引サイズ',
            yaxis_title='勝率 (%)',
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig_win_rate, use_container_width=True)
    
    # 取引サイズ別の平均損益比較
    st.markdown("### 💰 取引サイズ別平均損益比較")
    
    avg_profits = []
    categories = []
    for category in ['小', '中', '大']:
        group_trades = trades_df[trades_df['position_size_category'] == category]
        if len(group_trades) > 0:
            avg_profit = group_trades['profit_loss'].mean()
            avg_profits.append(avg_profit)
            categories.append(category)
    
    if avg_profits:
        fig_avg_profit = go.Figure()
        colors = ['green' if profit > 0 else 'red' for profit in avg_profits]
        fig_avg_profit.add_trace(go.Bar(
            x=categories,
            y=avg_profits,
            marker_color=colors,
            text=[f'{profit:,.0f}円' for profit in avg_profits],
            textposition='auto'
        ))
        
        fig_avg_profit.update_layout(
            title='取引サイズ別平均損益',
            xaxis_title='取引サイズ',
            yaxis_title='平均損益 (円)'
        )
        
        st.plotly_chart(fig_avg_profit, use_container_width=True)
    
    # 取引サイズ別の指標分析（RSI、ATR、MA乖離率など）
    st.markdown("### 📊 取引サイズ別指標分析")
    
    # 利用可能な指標を確認
    available_indicators = []
    if 'entry_rsi' in trades_df.columns:
        available_indicators.append('RSI')
    if 'entry_atr' in trades_df.columns:
        available_indicators.append('ATR')
    if 'entry_ma25_deviation' in trades_df.columns:
        available_indicators.append('MA25乖離率')
    if 'entry_ma75_deviation' in trades_df.columns:
        available_indicators.append('MA75乖離率')
    
    if available_indicators:
        selected_indicator = st.selectbox(
            "分析する指標を選択:",
            available_indicators
        )
        
        if selected_indicator == 'RSI':
            indicator_col = 'entry_rsi'
            indicator_name = 'RSI'
        elif selected_indicator == 'ATR':
            indicator_col = 'entry_atr'
            indicator_name = 'ATR'
        elif selected_indicator == 'MA25乖離率':
            indicator_col = 'entry_ma25_deviation'
            indicator_name = 'MA25乖離率 (%)'
        elif selected_indicator == 'MA75乖離率':
            indicator_col = 'entry_ma75_deviation'
            indicator_name = 'MA75乖離率 (%)'
        
        # 取引サイズ別の指標分布
        fig_indicator = go.Figure()
        colors = {'小': 'blue', '中': 'orange', '大': 'red'}
        
        for category in ['小', '中', '大']:
            group_trades = trades_df[trades_df['position_size_category'] == category]
            if len(group_trades) > 0:
                indicator_data = group_trades[indicator_col].dropna()
                if len(indicator_data) > 0:
                    fig_indicator.add_trace(go.Histogram(
                        x=indicator_data,
                        name=f'{category}サイズ',
                        opacity=0.7,
                        marker_color=colors[category],
                        nbinsx=15
                    ))
        
        fig_indicator.update_layout(
            barmode='overlay',
            title=f'取引サイズ別{indicator_name}分布',
            xaxis_title=indicator_name,
            yaxis_title='件数',
            legend=dict(x=0.7, y=0.95)
        )
        
        st.plotly_chart(fig_indicator, use_container_width=True)
        
        # 取引サイズ別の指標統計
        st.markdown(f"#### {indicator_name}の取引サイズ別統計")
        indicator_stats = []
        for category in ['小', '中', '大']:
            group_trades = trades_df[trades_df['position_size_category'] == category]
            if len(group_trades) > 0:
                indicator_data = group_trades[indicator_col].dropna()
                if len(indicator_data) > 0:
                    stats = {
                        '取引サイズ': category,
                        '平均': indicator_data.mean(),
                        '標準偏差': indicator_data.std(),
                        '最小値': indicator_data.min(),
                        '最大値': indicator_data.max(),
                        'データ数': len(indicator_data)
                    }
                    indicator_stats.append(stats)
        
        if indicator_stats:
            indicator_df = pd.DataFrame(indicator_stats)
            st.dataframe(indicator_df.round(3), use_container_width=True)
    
    # 取引サイズ別のトレンド分析
    if 'entry_trend' in trades_df.columns:
        st.markdown("### 📈 取引サイズ別トレンド分析")
        
        trend_stats = []
        for category in ['小', '中', '大']:
            group_trades = trades_df[trades_df['position_size_category'] == category]
            if len(group_trades) > 0:
                bullish_trades = group_trades[group_trades['entry_trend'] == 'bullish']
                bearish_trades = group_trades[group_trades['entry_trend'] == 'bearish']
                
                stats = {
                    '取引サイズ': category,
                    '強気取引数': len(bullish_trades),
                    '弱気取引数': len(bearish_trades),
                    '強気勝率 (%)': (len(bullish_trades[bullish_trades['profit_loss'] > 0]) / len(bullish_trades) * 100) if len(bullish_trades) > 0 else 0,
                    '弱気勝率 (%)': (len(bearish_trades[bearish_trades['profit_loss'] > 0]) / len(bearish_trades) * 100) if len(bearish_trades) > 0 else 0
                }
                trend_stats.append(stats)
        
        if trend_stats:
            trend_df = pd.DataFrame(trend_stats)
            st.dataframe(trend_df.round(2), use_container_width=True) 