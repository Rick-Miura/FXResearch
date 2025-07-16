import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# カスタムモジュールのインポート
from data_processor import load_fx_data, get_data_range
from chart import create_trade_detail_chart, create_profit_loss_chart
from component import render_sidebar, render_basic_stats, render_trade_summary
from strategy import detect_perfect_order, analyze_trading_signals, calculate_strategy_performance, get_strategy_statistics
from indicator.technical_analysis import calculate_moving_averages, calculate_rsi, calculate_atr, calculate_cross_signals
from analysis import (
    render_rsi_analysis, render_atr_analysis,
    render_price_deviation_analysis, render_ma_slope_analysis,
    render_volatility_analysis, render_trend_strength_analysis,
    render_win_rate_analysis, render_rsi_divergence_analysis
)

class FXAnalysisApp:
    """FX分析アプリケーションのメインコントローラー"""
    
    def __init__(self):
        self.setup_page_config()
        self.setup_css()
    
    def setup_page_config(self):
        """ページ設定"""
        st.set_page_config(
            page_title="FX移動平均線戦略分析",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def setup_css(self):
        """CSS設定"""
        st.markdown("""
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1f77b4;
                text-align: center;
                margin-bottom: 2rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin: 0.5rem 0;
            }
            .profit { color: #28a745; font-weight: bold; }
            .loss { color: #dc3545; font-weight: bold; }
            .neutral { color: #6c757d; font-weight: bold; }
            .strategy-info {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 1rem;
                margin: 1rem 0;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def render_strategy_info(self):
        """戦略情報を表示"""
        # 折りたたみ可能なセクション
        if st.button("📋 パーフェクトオーダー戦略詳細を表示", key="strategy_toggle"):
            st.session_state.show_strategy = not st.session_state.get('show_strategy', False)
        
        if st.session_state.get('show_strategy', False):
            st.markdown("### 📈 強気パーフェクトオーダー")
            st.markdown("- MA25 > MA75 > MA200")
            st.markdown("- 3つのMAの傾きがすべて同じ")
            st.markdown("- 価格がMA25を上向きにブレイク")
            st.markdown("- RSIが30～70の範囲内")
            
            st.markdown("### 📉 弱気パーフェクトオーダー")
            st.markdown("- MA25 < MA75 < MA200")
            st.markdown("- 3つのMAの傾きがすべて同じ")
            st.markdown("- 価格がMA25を下向きにブレイク")
            st.markdown("- RSIが30～70の範囲内")
            
            st.markdown("### 📊 決済条件")
            st.markdown("**🔴 強気トレンド決済**")
            st.markdown("MA25がMA75を下向きにクロス（デッドクロス）")
            st.markdown("※パーフェクトオーダーが崩れても持ち続ける")
            
            st.markdown("**🟢 弱気トレンド決済**")
            st.markdown("MA25がMA75を上向きにクロス（ゴールデンクロス）")
            st.markdown("※パーフェクトオーダーが崩れても持ち続ける")
            
            st.markdown("### 📊 RSI条件")
            st.markdown("**🎯 RSIフィルター**")
            st.markdown("エントリー条件: RSIが30～70の範囲内")
            st.markdown("目的: 過買い（70以上）・過売り（30以下）を避ける")
            st.markdown("効果: より安全なエントリーポイントを選択")
            
            st.markdown("### ⚠️ リスク管理")
            st.markdown("**🛡️ ストップロス**")
            st.markdown("強気トレンド: 200MAを下回った時")
            st.markdown("弱気トレンド: 200MAを上回った時")
            

            
            st.markdown("### 💡 戦略概要")
            st.markdown("**エントリー:** パーフェクトオーダーかつ価格がMA25を外に抜けた時かつRSIが30～70の範囲内")
            st.markdown("**決済:** デッドクロス（強気）またはゴールデンクロス（弱気）")
            st.markdown("**ストップロス:** 200MAベース")
            st.markdown("**RSI条件:** 過買い（70以上）・過売り（30以下）を避ける")
    
    def run(self):
        """メインアプリケーション実行"""
        st.markdown('<h1 class="main-header">📈 FX移動平均線戦略分析</h1>', unsafe_allow_html=True)
        
        # 戦略情報を折りたたみ可能で表示
        self.render_strategy_info()
        
        # データ読み込み
        result = self.load_data()
        if result[0] is None:
            return
        df, n_continued = result
        
        if df is None or df.empty:
            st.error("データが見つかりません")
            return
        
        # テクニカル指標計算
        df = self.calculate_technical_indicators(df)
        
        # 戦略分析
        trades_df, performance_stats = self.analyze_strategy(df, n_continued)
        
        # 取引統計サマリーを最初に表示
        if not trades_df.empty:
            render_trade_summary(trades_df)
        
        # メインコンテンツ
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 取引リスト選択UI追加
            selected_trade_idx = None
            if not trades_df.empty:
                trade_options = []
                for i, trade in trades_df.iterrows():
                    label = f"取引{i}: (損益: {int(trade['profit_loss']):,}円)"
                    trade_options.append(label)
                selected_trade_label = st.selectbox("詳細を見たい取引を選択:", trade_options)
                selected_trade_idx = trade_options.index(selected_trade_label)
            
            # 選択された取引の詳細チャートのみ表示
            if selected_trade_idx is not None:
                self.render_trade_chart(df, trades_df, selected_trade_idx)
        
        with col2:
            # 統計表示
            self.render_statistics(df, trades_df, performance_stats)
        
        # 詳細分析
        self.render_detailed_analysis(trades_df)
    
    def load_data(self):
        """データを読み込み"""
        # サイドバーから年選択
        years = ["2022", "2023", "2024"]
        selected_year = st.sidebar.selectbox("年を選択", years, index=2)
        
        # パーフェクトオーダー連続回数設定
        st.sidebar.markdown("### 📊 パーフェクトオーダー設定")
        n_continued = st.sidebar.slider(
            "パーフェクトオーダー連続回数",
            min_value=1,
            max_value=5,
            value=1,
            step=1,
            help="パーフェクトオーダーが何回連続した場合にエントリーするか"
        )
        

        
        # データファイルパス
        file_path = f"data/USDJPY_{selected_year}_15min.csv"
        
        try:
            df = load_fx_data(file_path)
            return df, n_continued
        except Exception as e:
            st.error(f"データ読み込みエラー: {e}")
            return None, None
    
    def calculate_technical_indicators(self, df):
        """テクニカル指標を計算"""
        df = calculate_moving_averages(df)
        df = calculate_rsi(df)
        df = calculate_atr(df)
        df = calculate_cross_signals(df)
        return df
    
    def analyze_strategy(self, df, n_continued=1):
        """戦略分析を実行"""
        # パーフェクトオーダー検出
        df = detect_perfect_order(df)
        
        # 取引シグナル分析
        df = analyze_trading_signals(df, n_continued=n_continued)
        
        # パフォーマンス計算
        trades_df = calculate_strategy_performance(df)
        
        # 統計計算
        performance_stats = get_strategy_statistics(trades_df)
        
        return trades_df, performance_stats
    
    def render_trade_chart(self, df, trades_df, selected_trade_idx):
        """選択された取引の詳細チャートを表示"""
        if selected_trade_idx is not None and not trades_df.empty:
            # 選択された取引の詳細チャートを表示
            trade = trades_df.iloc[selected_trade_idx]
            trade_fig = create_trade_detail_chart(df, trade)
            st.plotly_chart(trade_fig, use_container_width=True)
            
            # 損益推移チャートを表示
            profit_loss_fig = create_profit_loss_chart(trades_df)
            if profit_loss_fig:
                st.plotly_chart(profit_loss_fig, use_container_width=True)
    
    def render_statistics(self, df, trades_df, performance_stats):
        """統計情報を表示"""
        # 基本統計のみ表示
        min_date, max_date = get_data_range(df)
        render_basic_stats(df, min_date, max_date)
    

    
    def render_detailed_analysis(self, trades_df):
        """詳細分析を表示"""
        if trades_df is None or trades_df.empty:
            return
        
        # 分析タイプ選択
        analysis_type = st.selectbox(
            "詳細分析を選択",
            ["価格乖離率分析", "MA傾き分析", "ボラティリティ分析", "トレンド強度分析", "勝率分析", "RSIダイバージェンス分析", "RSI分析", "ATR分析"],
            index=0
        )
        
        if analysis_type == "価格乖離率分析":
            render_price_deviation_analysis(trades_df)
        elif analysis_type == "MA傾き分析":
            render_ma_slope_analysis(trades_df)
        elif analysis_type == "ボラティリティ分析":
            render_volatility_analysis(trades_df)
        elif analysis_type == "トレンド強度分析":
            render_trend_strength_analysis(trades_df)
        elif analysis_type == "勝率分析":
            render_win_rate_analysis(trades_df)
        elif analysis_type == "RSIダイバージェンス分析":
            render_rsi_divergence_analysis(trades_df)
        elif analysis_type == "RSI分析":
            render_rsi_analysis(trades_df)
        elif analysis_type == "ATR分析":
            render_atr_analysis(trades_df) 