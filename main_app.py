import streamlit as st
import pandas as pd

# カスタムモジュールのインポート
from data_loader import load_fx_data, get_data_range
from technical_analysis import (
    calculate_moving_averages, 
    analyze_trend_signals,
    calculate_rsi
)
from chart_creator import create_candlestick_chart
from ui_components import (
    render_sidebar, 
    render_basic_stats
)
from strategy_analysis import (
    detect_perfect_order,
    analyze_trading_signals,
    calculate_strategy_performance,
    get_strategy_statistics,
    render_strategy_conditions,
    render_performance_analysis,
    render_trade_summary,
    calculate_atr
)

# ページ設定
st.set_page_config(
    page_title="FX移動平均線分析",
    page_icon="📈",
    layout="wide"
)

# タイトル
st.title("📈 FX移動平均線分析 (15分足)")
st.markdown("---")

def main():
    """メインアプリケーション"""
    # 年選択
    year = st.sidebar.selectbox("データ年を選択", ["2024年", "2023年", "2022年"])
    if year == "2024年":
        data_path = 'data/USDJPY_2024_15min.csv'
    elif year == "2023年":
        data_path = 'data/USDJPY_2023_15min.csv'
    else:
        data_path = 'data/USDJPY_2022_15min.csv'

    # n単位前継続の選択
    n_continued = st.sidebar.selectbox("パーフェクトオーダー継続判定の単位数 (n)", [1,2,3,4,5], index=0, help="エントリー条件としてパーフェクトオーダーがn単位前から継続している場合のみエントリーします。デフォルトは1単位前から継続。")

    # データ読み込み
    df = load_fx_data(data_path)
    
    if df is None:
        st.error("データを読み込めませんでした。")
        return
    
    # 移動平均線計算
    df = calculate_moving_averages(df)
    df = analyze_trend_signals(df)
    # RSI計算（14期間）
    df = calculate_rsi(df, period=14)

    # ATR計算
    df = calculate_atr(df)

    # 戦略分析
    df = detect_perfect_order(df)
    df = analyze_trading_signals(df, n_continued=n_continued)
    
    # データ範囲取得
    min_date, max_date = get_data_range(df)
    
    if min_date is None or max_date is None:
        st.error("データ範囲を取得できませんでした。")
        return
    
    # サイドバー
    start_date, end_date = render_sidebar(df, min_date, max_date)
    render_basic_stats(df, start_date, end_date)
    
    # メインコンテンツ
    st.subheader("📈 チャート分析")
    
    # チャート表示
    chart_fig = create_candlestick_chart(df, start_date, end_date)
    st.plotly_chart(chart_fig, use_container_width=True, config={
        'displayModeBar': True,
        'modeBarButtonsToRemove': [
            'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
            'pan2d', 'select2d', 'lasso2d', 'toggleSpikelines', 'hoverCompareCartesian', 'hoverClosestCartesian'
        ]
    })
    
    # 戦略分析セクション
    st.markdown("---")
    st.subheader("🎯 パーフェクトオーダー戦略分析")
    
    # 戦略条件の表示
    render_strategy_conditions()
    
    # パフォーマンス分析
    filtered_df = df[(df['DateTime'] >= pd.to_datetime(start_date)) & 
                     (df['DateTime'] <= pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))]
    
    trades_df = calculate_strategy_performance(filtered_df)
    stats = get_strategy_statistics(trades_df)

    # サマリー表示
    render_trade_summary(stats)
    
    render_performance_analysis(trades_df, stats, df)
    


if __name__ == "__main__":
    main() 