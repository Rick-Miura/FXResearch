import streamlit as st
import pandas as pd

def render_sidebar(df, min_date, max_date):
    """サイドバーをレンダリング"""
    st.sidebar.header("📊 分析設定")
    
    # 日付範囲選択
    st.sidebar.subheader("📅 日付範囲")
    start_date = st.sidebar.date_input(
        "開始日",
        value=min_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    end_date = st.sidebar.date_input(
        "終了日",
        value=max_date.date(),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    return start_date, end_date

def render_basic_stats(df, start_date, end_date):
    """基本統計をレンダリング"""
    st.sidebar.subheader("📈 基本統計")
    # date型をdatetime型に変換
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    filtered_df = df[(df['DateTime'] >= start_datetime) & (df['DateTime'] <= end_datetime)]
    
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

def render_trend_analysis(df, start_date, end_date):
    """トレンド分析をレンダリング"""
    # date型をdatetime型に変換
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    filtered_df = df[(df['DateTime'] >= start_datetime) & (df['DateTime'] <= end_datetime)]
    
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

def render_statistics_tables(df, start_date, end_date):
    """統計テーブルをレンダリング"""
    # この関数は空にする（価格統計を削除）
    pass

def render_signal_analysis(golden_crosses, dead_crosses):
    """シグナル分析をレンダリング（ゴールデンクロス・デッドクロスの列挙を削除）"""
    st.subheader("🎯 シグナル分析")
    st.info("この戦略ではゴールデンクロス・デッドクロスの列挙は省略しています。") 