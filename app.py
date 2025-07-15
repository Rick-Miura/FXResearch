import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ページ設定
st.set_page_config(
    page_title="FX移動平均線分析",
    page_icon="📈",
    layout="wide"
)

# タイトル
st.title("📈 FX移動平均線分析 (15分足)")
st.markdown("---")

# load_data関数の引数をファイルパス指定に変更
@st.cache_data
def load_data(file_path):
    """データを読み込む（Open, High, Low, Closeのみ、市場クローズ中データ除外、インデックス振り直し）"""
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(file_path)
        
        # カラム名を確認して適切に設定
        if len(df.columns) >= 6:
            df.columns = ['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']
        else:
            df.columns = ['DateTime', 'Open', 'High', 'Low', 'Close']
        # Open, High, Low, Close のみ使用
        df = df[['DateTime', 'Open', 'High', 'Low', 'Close']]
        
        # DateTimeを柔軟にパース
        def parse_datetime(date_str):
            try:
                if 'GMT' in str(date_str):
                    date_part = str(date_str).split(' GMT')[0]
                    return pd.to_datetime(date_part, format='%d.%m.%Y %H:%M:%S.%f')
                else:
                    return pd.to_datetime(date_str)
            except:
                return pd.to_datetime(date_str, errors='coerce')
        df['DateTime'] = df['DateTime'].apply(parse_datetime)
        df = df.sort_values('DateTime').reset_index(drop=True)
        
        # 市場クローズ中のデータを除外（open=close=high=low）
        market_closed = (
            (df['Open'] == df['Close']) &
            (df['Close'] == df['High']) &
            (df['High'] == df['Low'])
        )
        df = df[~market_closed].copy()
        
        # インデックスを振りなおす
        df = df.reset_index(drop=True)
        
        return df
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        return None

def calculate_moving_averages(df):
    """移動平均線を計算"""
    df = df.copy()
    
    # 移動平均線を計算
    df['MA25'] = df['Close'].rolling(window=25).mean()
    df['MA75'] = df['Close'].rolling(window=75).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    return df

def analyze_signals(df):
    """シグナル分析"""
    df = df.copy()
    
    # ゴールデンクロス・デッドクロス検出
    df['MA25_above_MA75'] = df['MA25'] > df['MA75']
    df['MA25_above_MA200'] = df['MA25'] > df['MA200']
    df['MA75_above_MA200'] = df['MA75'] > df['MA200']
    
    # クロスオーバー検出
    df['Golden_Cross_25_75'] = (df['MA25_above_MA75'] != df['MA25_above_MA75'].shift(1)) & df['MA25_above_MA75']
    df['Dead_Cross_25_75'] = (df['MA25_above_MA75'] != df['MA25_above_MA75'].shift(1)) & ~df['MA25_above_MA75']
    
    return df

def create_candlestick_chart(df, start_idx=None, end_idx=None):
    """ローソク足チャートを作成（x軸はインデックス）"""
    if start_idx is not None and end_idx is not None:
        chart_df = df.iloc[start_idx:end_idx+1].copy()
    else:
        chart_df = df.copy()
    fig = go.Figure()
    # ローソク足（x軸はインデックス）
    fig.add_trace(go.Candlestick(
        x=chart_df.index,
        open=chart_df['Open'],
        high=chart_df['High'],
        low=chart_df['Low'],
        close=chart_df['Close'],
        name='USDJPY',
        increasing_line_color='#26A69A',
        decreasing_line_color='#EF5350'
    ))
    # 移動平均線
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['MA25'],
        mode='lines',
        name='MA25',
        line=dict(color='blue', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['MA75'],
        mode='lines',
        name='MA75',
        line=dict(color='orange', width=1)
    ))
    fig.add_trace(go.Scatter(
        x=chart_df.index,
        y=chart_df['MA200'],
        mode='lines',
        name='MA200',
        line=dict(color='red', width=2)
    ))
    fig.update_layout(
        title='USDJPY 15分足チャート (インデックスベース)',
        xaxis_title='単位',
        yaxis_title='価格',
        height=600,
        showlegend=True
    )
    return fig

def main():
    # サイドバーでデータファイル選択
    st.sidebar.header("📁 データ選択")
    data_file = st.sidebar.selectbox(
        "使用するデータファイルを選択",
        [
            "USDJPY_2024_15min.csv",
            "USDJPY_2023_15min.csv",
            "USDJPY_2022_15min.csv"
        ],
        index=0
    )
    data_path = f"data/{data_file}"

    # データ読み込み
    df = load_data(data_path)
    
    if df is None:
        st.error("データを読み込めませんでした。")
        return
    
    # 移動平均線計算
    df = calculate_moving_averages(df)
    df = analyze_signals(df)
    
    # サイドバー
    st.sidebar.header("�� 分析設定")
    
    # インデックス範囲選択
    min_idx = 0
    max_idx = len(df) - 1
    st.sidebar.subheader("🔢 単位範囲（インデックス）")
    start_idx = st.sidebar.number_input("開始インデックス", min_value=min_idx, max_value=max_idx, value=min_idx)
    end_idx = st.sidebar.number_input("終了インデックス", min_value=min_idx, max_value=max_idx, value=max_idx)
    
    # 分析期間の表示
    st.sidebar.subheader("📈 基本統計")
    filtered_df = df.iloc[start_idx:end_idx+1]
    
    if not filtered_df.empty:
        st.sidebar.metric("期間中の最高値", f"{filtered_df['High'].max():.2f}")
        st.sidebar.metric("期間中の最安値", f"{filtered_df['Low'].min():.2f}")
        st.sidebar.metric("現在値", f"{filtered_df['Close'].iloc[-1]:.2f}")
        
        # 移動平均線の現在値
        current_ma25 = filtered_df['MA25'].iloc[-1]
        current_ma75 = filtered_df['MA75'].iloc[-1]
        current_ma200 = filtered_df['MA200'].iloc[-1]
        
        st.sidebar.subheader("📊 移動平均線")
        st.sidebar.metric("MA25", f"{current_ma25:.2f}")
        st.sidebar.metric("MA75", f"{current_ma75:.2f}")
        st.sidebar.metric("MA200", f"{current_ma200:.2f}")
    
    # メインコンテンツ
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 チャート分析")
        # チャート表示
        chart_fig = create_candlestick_chart(df, start_idx, end_idx)
        st.plotly_chart(chart_fig, use_container_width=True, config={
            'displayModeBar': True,
            'modeBarButtonsToRemove': [
                'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
                'pan2d', 'select2d', 'lasso2d', 'toggleSpikelines', 'hoverCompareCartesian', 'hoverClosestCartesian'
            ]
        })
    
    with col2:
        st.subheader("📊 分析結果")
        if not filtered_df.empty:
            # トレンド分析
            current_price = filtered_df['Close'].iloc[-1]
            ma25 = filtered_df['MA25'].iloc[-1]
            ma75 = filtered_df['MA75'].iloc[-1]
            ma200 = filtered_df['MA200'].iloc[-1]
            # トレンド判定
            if current_price > ma25 > ma75 > ma200:
                trend = "強気トレンド"
                trend_color = "green"
            elif current_price < ma25 < ma75 < ma200:
                trend = "弱気トレンド"
                trend_color = "red"
            else:
                trend = "横ばい/調整"
                trend_color = "orange"
            st.markdown(f"**現在のトレンド:** <span style='color:{trend_color}'>{trend}</span>", unsafe_allow_html=True)
            # 移動平均線の位置関係
            st.markdown("**移動平均線の位置関係:**")
            if ma25 > ma75:
                st.markdown("✅ MA25 > MA75 (短期上昇)")
            else:
                st.markdown("❌ MA25 < MA75 (短期下降)")
            if ma75 > ma200:
                st.markdown("✅ MA75 > MA200 (中期上昇)")
            else:
                st.markdown("❌ MA75 < MA200 (中期下降)")
    # 詳細分析セクション
    st.markdown("---")
    st.subheader("🔍 詳細分析")
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("📊 価格統計")
        if not filtered_df.empty:
            stats_df = filtered_df[['Open', 'High', 'Low', 'Close']].describe()
            st.dataframe(stats_df, use_container_width=True)
    with col4:
        st.subheader("📈 移動平均線統計")
        if not filtered_df.empty:
            ma_stats = filtered_df[['MA25', 'MA75', 'MA200']].describe()
            st.dataframe(ma_stats, use_container_width=True)
    # シグナル分析
    st.subheader("🎯 シグナル分析")
    if not filtered_df.empty:
        golden_crosses = filtered_df[filtered_df['Golden_Cross_25_75']]
        dead_crosses = filtered_df[filtered_df['Dead_Cross_25_75']]
        col5, col6 = st.columns(2)
        with col5:
            st.markdown("**🟢 ゴールデンクロス (MA25 > MA75)**")
            if not golden_crosses.empty:
                for idx, row in golden_crosses.iterrows():
                    st.markdown(f"- {idx}: {row['Close']:.2f}")
            else:
                st.markdown("期間中にゴールデンクロスはありません")
        with col6:
            st.markdown("**🔴 デッドクロス (MA25 < MA75)**")
            if not dead_crosses.empty:
                for idx, row in dead_crosses.iterrows():
                    st.markdown(f"- {idx}: {row['Close']:.2f}")
            else:
                st.markdown("期間中にデッドクロスはありません")

if __name__ == "__main__":
    main() 