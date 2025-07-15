import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from rsi_analysis import render_rsi_analysis
from atr_analysis import render_atr_analysis
from ma_deviation_analysis import render_ma_deviation_analysis
from ma75_position_analysis import render_ma75_position_analysis
from position_size_analysis import render_position_size_analysis
from position_size_ma75_analysis import render_position_size_ma75_analysis
from ma_change_analysis import render_ma_change_analysis

def define_perfect_order_conditions():
    """パーフェクトオーダーの条件を定義"""
    conditions = {
        "entry_conditions": {
            "bullish_perfect_order": "MA25 > MA75 > MA200 かつ 3つのMAの傾きがすべて同じ（強気パーフェクトオーダー)",
            "bearish_perfect_order": "MA25 < MA75 < MA200 かつ 3つのMAの傾きがすべて同じ（弱気パーフェクトオーダー)",
            "price_breakout_bullish": "強気トレンドで価格がMA25を上向きにブレイク",
            "price_breakout_bearish": "弱気トレンドで価格がMA25を下向きにブレイク",
            "rsi_condition": "RSIが30～70の範囲内（過買い・過売りを避ける）",
            "ma25_above_ma75": "MA25がMA75を上回っている", 
            "ma75_above_ma200": "MA75がMA200を上回っている",
            "ma25_below_ma75": "MA25がMA75を下回っている",
            "ma75_below_ma200": "MA75がMA200を下回っている",
            "slope_consistency": "3つのMAの傾きの正負がすべて同じ"
        },
        "exit_conditions": {
            "bullish_exit": "強気トレンド: MA25がMA75を下向きにクロス（デッドクロス）",
            "bearish_exit": "弱気トレンド: MA25がMA75を上向きにクロス（ゴールデンクロス）",
            "trend_reversal": "パーフェクトオーダーが崩れた時"
        },
        "risk_management": {
            "stop_loss": "200MAを下回った時（強気）または上回った時（弱気）",
            "position_sizing": "リスク管理のためのポジションサイズ調整"
        }
    }
    return conditions

def detect_perfect_order(df):
    """パーフェクトオーダーを検出"""
    df = df.copy()
    
    # MAの傾きを計算（前の値との差分）
    df['MA25_slope'] = df['MA25'] - df['MA25'].shift(1)
    df['MA75_slope'] = df['MA75'] - df['MA75'].shift(1)
    df['MA200_slope'] = df['MA200'] - df['MA200'].shift(1)
    
    # 傾きの正負を判定
    df['MA25_slope_positive'] = df['MA25_slope'] > 0
    df['MA75_slope_positive'] = df['MA75_slope'] > 0
    df['MA200_slope_positive'] = df['MA200_slope'] > 0
    
    # 強気パーフェクトオーダー条件
    df['bullish_perfect_order'] = (
        (df['MA25'] > df['MA75']) & 
        (df['MA75'] > df['MA200']) &
        (df['MA25_slope_positive'] == df['MA75_slope_positive']) &
        (df['MA75_slope_positive'] == df['MA200_slope_positive'])
    )
    
    # 弱気パーフェクトオーダー条件
    df['bearish_perfect_order'] = (
        (df['MA25'] < df['MA75']) & 
        (df['MA75'] < df['MA200']) &
        (df['MA25_slope_positive'] == df['MA75_slope_positive']) &
        (df['MA75_slope_positive'] == df['MA200_slope_positive'])
    )
    
    # パーフェクトオーダー（強気または弱気）
    df['perfect_order'] = df['bullish_perfect_order'] | df['bearish_perfect_order']
    
    # パーフェクトオーダーの開始と終了
    df['perfect_order_start'] = (df['perfect_order'] != df['perfect_order'].shift(1)) & df['perfect_order']
    df['perfect_order_end'] = (df['perfect_order'] != df['perfect_order'].shift(1)) & ~df['perfect_order']
    
    # 価格がMA25を外に抜けた時の検出（トレンドに応じて）
    # 強気トレンド（MA25 > MA75 > MA200）では価格がMA25を上向きにブレイク
    df['price_breakout_bullish'] = (
        (df['Close'] > df['MA25']) & 
        (df['Close'].shift(1) <= df['MA25'].shift(1)) &
        df['bullish_perfect_order']
    )
    
    # 弱気トレンド（MA25 < MA75 < MA200）では価格がMA25を下向きにブレイク
    df['price_breakout_bearish'] = (
        (df['Close'] < df['MA25']) & 
        (df['Close'].shift(1) >= df['MA25'].shift(1)) &
        df['bearish_perfect_order']
    )
    
    return df

def analyze_trading_signals(df, n_continued=1):
    """取引シグナルを分析（RSI条件追加・パーフェクトオーダーがn単位前から継続している場合のみエントリー）"""
    df = df.copy()
    
    # RSI条件（30～70の範囲内）
    df['rsi_in_range'] = (df['RSI'] >= 30) & (df['RSI'] <= 70)
    
    # パーフェクトオーダーがn単位前から継続しているか
    cond = df['perfect_order']
    for i in range(1, n_continued+1):
        cond = cond & df['perfect_order'].shift(i)
    df['perfect_order_continued'] = cond
    
    # エントリーシグナル（パーフェクトオーダーがn単位前から継続かつ価格がMA25を外に抜けた時かつRSI条件を満たす時）
    df['entry_signal'] = (
        (df['price_breakout_bullish'] | df['price_breakout_bearish']) & 
        df['rsi_in_range'] &
        df['perfect_order_continued']
    )
    
    # 決済シグナル（トレンドに応じて）
    # デッドクロスまたはゴールデンクロスで決済（パーフェクトオーダーが崩れても持ち続ける）
    df['exit_signal_bullish'] = df['Dead_Cross_25_75']
    df['exit_signal_bearish'] = df['Golden_Cross_25_75']
    df['exit_signal'] = df['exit_signal_bullish'] | df['exit_signal_bearish']
    
    return df

def calculate_atr(df, period=14):
    """ATR（Average True Range）を計算"""
    df = df.copy()
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift(1))
    low_close = np.abs(df['Low'] - df['Close'].shift(1))
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=period, min_periods=1).mean()
    return df

def calculate_strategy_performance(df, atr_multiple=2):
    """戦略のパフォーマンスを計算（75EMAストップロス対応）"""
    df = df.copy()
    trades = []
    in_position = False
    entry_price = 0
    entry_date = None
    entry_trend = None
    
    # 取引設定
    initial_capital = 10000  # 初期資金10000円
    leverage = 25  # 25倍レバレッジ
    position_size = initial_capital * leverage  # 取引サイズ
    
    for idx, row in df.iterrows():
        # エントリー
        if row['entry_signal'] and not in_position:
            entry_price = row['Close'] if pd.notnull(row['Close']) else None
            if entry_price is None:
                continue  # 価格がNoneならエントリーしない
            in_position = True
            entry_date = row['DateTime']
            entry_rsi = row['RSI'] if 'RSI' in row else None
            entry_atr = row['ATR'] if 'ATR' in row else None
            
            # MA乖離率計算
            entry_ma25_deviation = None
            entry_ma75_deviation = None
            if pd.notnull(entry_price) and 'MA25' in row and pd.notnull(row['MA25']) and 'MA75' in row and pd.notnull(row['MA75']):
                entry_ma25_deviation = ((entry_price - row['MA25']) / row['MA25']) * 100
                entry_ma75_deviation = ((entry_price - row['MA75']) / row['MA75']) * 100
            
            # トレンド判定
            if row['bullish_perfect_order']:
                entry_trend = 'bullish'
            elif row['bearish_perfect_order']:
                entry_trend = 'bearish'
            else:
                entry_trend = None
        
        # 決済
        elif in_position:
            exit_reason = None
            # トレンドごとの決済（パーフェクトオーダーが崩れても持ち続ける）
            if entry_trend == 'bullish' and row['exit_signal_bullish']:
                exit_reason = 'デッドクロス'
            elif entry_trend == 'bearish' and row['exit_signal_bearish']:
                exit_reason = 'ゴールデンクロス'
            # 200MAストップロス
            elif entry_trend == 'bullish' and row['Close'] < row['MA200']:
                exit_reason = '200MAストップロス'
            elif entry_trend == 'bearish' and row['Close'] > row['MA200']:
                exit_reason = '200MAストップロス'
            
            if exit_reason:
                exit_price = row['Close']
                exit_date = row['DateTime']
                exit_rsi = row['RSI'] if 'RSI' in row else None
                # 安全な損益計算
                if exit_price is not None and entry_price is not None and entry_price != 0:
                    # 価格変動による損益
                    price_change = exit_price - entry_price
                    price_change_pct = ((exit_price - entry_price) / entry_price) * 100
                    
                    # レバレッジを考慮した実際の損益計算
                    if entry_trend == 'bullish':
                        # 強気ポジション（買い）
                        actual_profit_loss = price_change * (position_size / entry_price)
                        actual_profit_loss_pct = price_change_pct * leverage
                    else:
                        # 弱気ポジション（売り）
                        actual_profit_loss = -price_change * (position_size / entry_price)
                        actual_profit_loss_pct = -price_change_pct * leverage
                else:
                    actual_profit_loss = 0
                    actual_profit_loss_pct = 0
                    price_change = 0
                    price_change_pct = 0
                
                trade = {
                    'entry_date': entry_date,
                    'exit_date': exit_date,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'price_change': price_change,
                    'price_change_pct': price_change_pct,
                    'profit_loss': actual_profit_loss,
                    'profit_loss_pct': actual_profit_loss_pct,
                    'exit_reason': exit_reason,
                    'duration_days': (exit_date - entry_date).days,
                    'position_size': position_size,
                    'leverage': leverage,
                    'entry_rsi': entry_rsi,
                    'exit_rsi': exit_rsi,
                    'entry_atr': entry_atr,
                    'entry_ma25_deviation': entry_ma25_deviation,
                    'entry_ma75_deviation': entry_ma75_deviation,
                    'entry_trend': entry_trend
                }
                trades.append(trade)
                in_position = False
    
    return pd.DataFrame(trades)

def get_strategy_statistics(trades_df):
    """戦略統計を取得"""
    if trades_df.empty:
        return {}
    
    # 初期資金とレバレッジ情報
    initial_capital = 10000
    leverage = 25
    
    stats = {
        'total_trades': len(trades_df),
        'winning_trades': len(trades_df[trades_df['profit_loss'] > 0]),
        'losing_trades': len(trades_df[trades_df['profit_loss'] < 0]),
        'win_rate': len(trades_df[trades_df['profit_loss'] > 0]) / len(trades_df) * 100,
        'total_profit_loss': trades_df['profit_loss'].sum(),
        'total_profit_loss_pct': trades_df['profit_loss_pct'].sum(),
        'avg_profit_loss': trades_df['profit_loss'].mean(),
        'avg_profit_loss_pct': trades_df['profit_loss_pct'].mean(),
        'max_profit': trades_df['profit_loss'].max(),
        'max_loss': trades_df['profit_loss'].min(),
        'avg_duration': trades_df['duration_days'].mean(),
        'exit_reasons': trades_df['exit_reason'].value_counts().to_dict(),
        'initial_capital': initial_capital,
        'leverage': leverage,
        'position_size': initial_capital * leverage,
        'total_return_pct': (trades_df['profit_loss'].sum() / initial_capital) * 100
    }
    
    return stats

def render_strategy_conditions():
    """戦略条件を表示"""
    # エントリー条件カード
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background-color: #d4edda; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745; color: #155724;">
            <h4 style="color: #155724;">📈 強気パーフェクトオーダー</h4>
            <ul style="color: #155724;">
            <li>MA25 > MA75 > MA200</li>
            <li>3つのMAの傾きがすべて同じ</li>
            <li>価格がMA25を上向きにブレイク</li>
            <li><strong>RSIが30～70の範囲内</strong></li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: #f8d7da; padding: 15px; border-radius: 10px; border-left: 5px solid #dc3545; color: #721c24;">
            <h4 style="color: #721c24;">📉 弱気パーフェクトオーダー</h4>
            <ul style="color: #721c24;">
            <li>MA25 < MA75 < MA200</li>
            <li>3つのMAの傾きがすべて同じ</li>
            <li>価格がMA25を下向きにブレイク</li>
            <li><strong>RSIが30～70の範囲内</strong></li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # 決済条件カード
    st.markdown("### 📊 決済条件")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background-color: #cce7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; color: #004085;">
            <h4 style="color: #004085;">🔴 強気トレンド決済</h4>
            <ul style="color: #004085;">
            <li>MA25がMA75を下向きにクロス（デッドクロス）</li>
            <li>※パーフェクトオーダーが崩れても持ち続ける</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: #cce7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; color: #004085;">
            <h4 style="color: #004085;">🟢 弱気トレンド決済</h4>
            <ul style="color: #004085;">
            <li>MA25がMA75を上向きにクロス（ゴールデンクロス）</li>
            <li>※パーフェクトオーダーが崩れても持ち続ける</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # RSI条件カード
    st.markdown("### 📊 RSI条件")
    st.markdown("""
    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745; color: #155724;">
    <h4 style="color: #155724;">🎯 RSIフィルター</h4>
    <ul style="color: #155724;">
    <li><strong>エントリー条件</strong>: RSIが30～70の範囲内</li>
    <li><strong>目的</strong>: 過買い（70以上）・過売り（30以下）を避ける</li>
    <li><strong>効果</strong>: より安全なエントリーポイントを選択</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # リスク管理カード
    st.markdown("### ⚠️ リスク管理")
    st.markdown("""
    <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; border-left: 5px solid #ffc107; color: #856404;">
    <h4 style="color: #856404;">🛡️ ストップロス</h4>
    <ul style="color: #856404;">
    <li><strong>強気トレンド</strong>: 200MAを下回った時</li>
    <li><strong>弱気トレンド</strong>: 200MAを上回った時</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 戦略概要
    st.markdown("### 💡 戦略概要")
    st.markdown("""
    <div style="background-color: #e2e3e5; padding: 15px; border-radius: 10px; border-left: 5px solid #6c757d; color: #383d41;">
    <ol style="color: #383d41;">
    <li><strong>エントリー</strong>: パーフェクトオーダーかつ価格がMA25を外に抜けた時かつRSIが30～70の範囲内</li>
    <li><strong>決済</strong>: デッドクロス（強気）またはゴールデンクロス（弱気）</li>
    <li><strong>ストップロス</strong>: 200MAベース</li>
    <li><strong>RSI条件</strong>: 過買い（70以上）・過売り（30以下）を避ける</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)

def render_performance_analysis(trades_df, stats, df):
    """パフォーマンス分析を表示"""
    
    if trades_df.empty:
        st.warning("分析期間中に取引シグナルはありませんでした。")
        return
    
    # 取引設定の表示
    st.info(f"💰 **取引設定**: 初期資金 {stats['initial_capital']:,}円 × {stats['leverage']}倍レバレッジ = {stats['position_size']:,}円の取引サイズ")
    
    # RSI条件の統計
    if not trades_df.empty and 'entry_rsi' in trades_df.columns:
        rsi_stats = trades_df['entry_rsi'].describe()
        st.info(f"📊 **RSI統計**: エントリー時のRSI平均 {rsi_stats['mean']:.1f} (範囲: {rsi_stats['min']:.1f} - {rsi_stats['max']:.1f})")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("総取引数", stats['total_trades'])
        st.metric("勝率", f"{stats['win_rate']:.1f}%")
    
    with col2:
        st.metric("総損益", f"{stats['total_profit_loss']:,.0f}円")
        st.metric("平均損益", f"{stats['avg_profit_loss']:,.0f}円")
    
    with col3:
        st.metric("最大利益", f"{stats['max_profit']:,.0f}円")
        st.metric("最大損失", f"{stats['max_loss']:,.0f}円")
    
    with col4:
        st.metric("平均保有期間", f"{stats['avg_duration']:.1f}日")
        st.metric("総リターン率", f"{stats['total_return_pct']:.2f}%")
    
    # 損益推移チャート
    st.subheader("📈 損益推移")
    profit_loss_chart = create_profit_loss_chart(trades_df)
    if profit_loss_chart:
        st.plotly_chart(profit_loss_chart, use_container_width=True, config={
            'displayModeBar': True,
            'modeBarButtonsToRemove': [
                'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
                'pan2d', 'select2d', 'lasso2d', 'toggleSpikelines', 'hoverCompareCartesian', 'hoverClosestCartesian'
            ]
        })
    
    # 取引詳細チャート
    st.subheader("📊 取引詳細チャート")
    
    if not trades_df.empty:
        # 表示用のデータフレームを作成（選択肢用）
        display_df = trades_df.copy()
        display_df['entry_date'] = display_df['entry_date'].dt.strftime('%Y-%m-%d %H:%M')
        display_df['exit_date'] = display_df['exit_date'].dt.strftime('%Y-%m-%d %H:%M')
        display_df['profit_loss'] = display_df['profit_loss'].round(0).astype(int)
        
        # 取引選択用のセレクトボックス
        trade_options = [f"取引{i+1}: {row['entry_date']} → {row['exit_date']} (損益: {row['profit_loss']:,}円)" 
                        for i, (idx, row) in enumerate(display_df.iterrows())]
        
        selected_trade_index = st.selectbox(
            "詳細を見たい取引を選択:",
            options=range(len(trades_df)),
            format_func=lambda x: trade_options[x]
        )
        
        if selected_trade_index is not None:
            selected_trade = trades_df.iloc[selected_trade_index]
            
            # 選択された取引の詳細チャートを表示
            from chart_creator import create_trade_detail_chart
            trade_chart = create_trade_detail_chart(df, selected_trade)
            st.plotly_chart(trade_chart, use_container_width=True, config={
                'displayModeBar': True,
                'modeBarButtonsToRemove': [
                    'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
                    'pan2d', 'select2d', 'lasso2d', 'toggleSpikelines', 'hoverCompareCartesian', 'hoverClosestCartesian'
                ]
            })

    # RSI分析
    # render_rsi_analysis(trades_df)
    
    # ATR分析
    # render_atr_analysis(trades_df)
    
    # MA乖離率分析
    # render_ma_deviation_analysis(trades_df)
    
    # MA75位置関係分析
    # render_ma75_position_analysis(trades_df, df)
    
    # 取引サイズ別分析
    # render_position_size_analysis(trades_df)
    
    # 取引サイズ別MA75位置関係分析
    render_position_size_ma75_analysis(trades_df, df)
    
    # MA変化量分析
    render_ma_change_analysis(trades_df, df)

def render_trade_summary(stats):
    """トレード結果のサマリー（成功確率と資金増加率）を簡単に表示"""
    st.subheader("✅ トレードサマリー")
    if not stats or stats.get('total_trades', 0) == 0:
        st.info("取引がありませんでした。")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("成功確率 (勝率)", f"{stats['win_rate']:.1f}%")
    with col2:
        st.metric("総リターン率", f"{stats['total_return_pct']:.2f}%")
    with col3:
        st.metric("総損益", f"{stats['total_profit_loss']:,.0f}円") 

def create_profit_loss_chart(trades_df):
    """損益推移チャートを作成"""
    import plotly.graph_objects as go
    
    if trades_df.empty:
        return None
    
    # 累積損益を計算
    trades_df = trades_df.copy()
    trades_df['cumulative_profit_loss'] = trades_df['profit_loss'].cumsum()
    
    fig = go.Figure()
    
    # 累積損益線
    fig.add_trace(go.Scatter(
        x=trades_df['exit_date'],
        y=trades_df['cumulative_profit_loss'],
        mode='lines+markers',
        name='累積損益',
        line=dict(color='blue', width=2),
        marker=dict(size=6)
    ))
    
    # ゼロライン
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title='損益推移チャート',
        xaxis_title='日時',
        yaxis_title='累積損益 (円)',
        height=400,
        showlegend=True,
        hovermode='x unified',
        # インタラクティブ機能を無効化
        dragmode=False,
        modebar=dict(remove=['zoom', 'pan', 'select', 'lasso2d', 'reset', 'autoscale', 'hovercompare', 'hoverclosest'])
    )
    
    return fig

 