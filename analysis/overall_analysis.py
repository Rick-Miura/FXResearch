import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from analysis.rsi_analyzer import RSIAnalyzer
from analysis.atr_analyzer import ATRAnalyzer
from analysis.price_deviation_analyzer import PriceDeviationAnalyzer
from analysis.ma_slope_analyzer import MASlopeAnalyzer
from analysis.volatility_analyzer import VolatilityAnalyzer
from analysis.trend_strength_analyzer import TrendStrengthAnalyzer
from analysis.win_rate_analyzer import WinRateAnalyzer
from analysis.rsi_divergence_analyzer import RSIDivergenceAnalyzer

def render_overall_analysis(trades_df):
    """全体分析を表示"""
    st.markdown("## 📊 全体分析")
    st.markdown("各分析のp値を低い順に並べて表示します。p値が低いほど統計的に有意な結果を示します。")
    
    if trades_df is None or trades_df.empty:
        st.warning("取引データがありません")
        return
    
    # 各分析のp値を計算
    analysis_results = {}
    
    # RSI分析
    try:
        rsi_analyzer = RSIAnalyzer()
        rsi_p_value = rsi_analyzer.calculate_p_value(trades_df)
        analysis_results["RSI分析"] = rsi_p_value
    except Exception as e:
        st.error(f"RSI分析でエラーが発生しました: {e}")
        analysis_results["RSI分析"] = 1.0
    
    # ATR分析
    try:
        atr_analyzer = ATRAnalyzer()
        atr_p_value = atr_analyzer.calculate_p_value(trades_df)
        analysis_results["ATR分析"] = atr_p_value
    except Exception as e:
        st.error(f"ATR分析でエラーが発生しました: {e}")
        analysis_results["ATR分析"] = 1.0
    
    # 価格乖離率分析
    try:
        price_dev_analyzer = PriceDeviationAnalyzer()
        price_dev_p_value = price_dev_analyzer.calculate_p_value(trades_df)
        analysis_results["価格乖離率分析"] = price_dev_p_value
    except Exception as e:
        st.error(f"価格乖離率分析でエラーが発生しました: {e}")
        analysis_results["価格乖離率分析"] = 1.0
    
    # MA傾き分析
    try:
        ma_slope_analyzer = MASlopeAnalyzer()
        ma_slope_p_value = ma_slope_analyzer.calculate_p_value(trades_df)
        analysis_results["MA傾き分析"] = ma_slope_p_value
    except Exception as e:
        st.error(f"MA傾き分析でエラーが発生しました: {e}")
        analysis_results["MA傾き分析"] = 1.0
    
    # ボラティリティ分析
    try:
        volatility_analyzer = VolatilityAnalyzer()
        volatility_p_value = volatility_analyzer.calculate_p_value(trades_df)
        analysis_results["ボラティリティ分析"] = volatility_p_value
    except Exception as e:
        st.error(f"ボラティリティ分析でエラーが発生しました: {e}")
        analysis_results["ボラティリティ分析"] = 1.0
    
    # トレンド強度分析
    try:
        trend_strength_analyzer = TrendStrengthAnalyzer()
        trend_strength_p_value = trend_strength_analyzer.calculate_p_value(trades_df)
        analysis_results["トレンド強度分析"] = trend_strength_p_value
    except Exception as e:
        st.error(f"トレンド強度分析でエラーが発生しました: {e}")
        analysis_results["トレンド強度分析"] = 1.0
    
    # 勝率分析
    try:
        win_rate_analyzer = WinRateAnalyzer()
        win_rate_p_value = win_rate_analyzer.calculate_p_value(trades_df)
        analysis_results["勝率分析"] = win_rate_p_value
    except Exception as e:
        st.error(f"勝率分析でエラーが発生しました: {e}")
        analysis_results["勝率分析"] = 1.0
    
    # RSIダイバージェンス分析
    try:
        rsi_divergence_analyzer = RSIDivergenceAnalyzer()
        rsi_divergence_p_value = rsi_divergence_analyzer.calculate_p_value(trades_df)
        analysis_results["RSIダイバージェンス分析"] = rsi_divergence_p_value
    except Exception as e:
        st.error(f"RSIダイバージェンス分析でエラーが発生しました: {e}")
        analysis_results["RSIダイバージェンス分析"] = 1.0
    
    # p値でソート
    sorted_results = sorted(analysis_results.items(), key=lambda x: x[1])
    
    # 結果を表示
    st.markdown("### 📈 分析結果（p値順）")
    
    # テーブル形式で表示
    results_data = []
    for i, (analysis_name, p_value) in enumerate(sorted_results, 1):
        significance = ""
        if p_value < 0.01:
            significance = "🔴 非常に有意"
        elif p_value < 0.05:
            significance = "🟡 有意"
        elif p_value < 0.1:
            significance = "🟢 やや有意"
        else:
            significance = "⚪ 有意でない"
        
        results_data.append({
            "順位": i,
            "分析名": analysis_name,
            "p値": f"{p_value:.4f}",
            "有意性": significance
        })
    
    results_df = pd.DataFrame(results_data)
    st.dataframe(results_df, use_container_width=True)
    
    # 統計的説明
    st.markdown("### 📊 統計的説明")
    st.markdown("- **p値 < 0.01**: 非常に統計的に有意（1%水準）")
    st.markdown("- **p値 < 0.05**: 統計的に有意（5%水準）")
    st.markdown("- **p値 < 0.1**: やや統計的に有意（10%水準）")
    st.markdown("- **p値 ≥ 0.1**: 統計的に有意でない")
    
    # 有意な分析の詳細表示
    significant_analyses = [name for name, p_value in sorted_results if p_value < 0.1]
    if significant_analyses:
        st.markdown(f"### 🎯 有意な分析（{len(significant_analyses)}件）")
        for analysis_name in significant_analyses:
            st.markdown(f"- **{analysis_name}**: 統計的に有意な結果を示しています")
    else:
        st.markdown("### ⚠️ 注意")
        st.markdown("統計的に有意な分析が見つかりませんでした。")
    
    # 推奨事項
    st.markdown("### 💡 推奨事項")
    if sorted_results[0][1] < 0.05:
        st.markdown(f"**{sorted_results[0][0]}**が最も統計的に有意な結果を示しています。")
        st.markdown("この分析結果を重視して戦略の改善を検討してください。")
    else:
        st.markdown("統計的に有意な分析が少ないため、より多くのデータでの検証が必要です。")
        st.markdown("または、分析手法の見直しを検討してください。") 