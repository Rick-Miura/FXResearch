import streamlit as st
import pandas as pd
from strategy import detect_perfect_order, analyze_trading_signals, calculate_strategy_performance, get_strategy_statistics
from indicator.technical_analysis import calculate_moving_averages, calculate_rsi, calculate_atr, calculate_cross_signals

class AnalysisProcessor:
    """分析処理クラス"""
    
    def __init__(self):
        pass
    
    def load_and_process_data(self, data_manager):
        """データ読み込みと処理を一括で実行（セッション状態に保存）"""
        # セッション状態のキーを生成
        selected_year = st.session_state.get('selected_year', '全期間')
        n_continued = st.session_state.get('n_continued', 1)
        
        # セッション状態のキー
        data_key = f"processed_data_{selected_year}_{n_continued}"
        trades_key = f"trades_data_{selected_year}_{n_continued}"
        stats_key = f"performance_stats_{selected_year}_{n_continued}"
        
        # セッション状態にデータがある場合はそれを返す
        if (data_key in st.session_state and 
            trades_key in st.session_state and 
            stats_key in st.session_state):
            st.sidebar.info("⚡ キャッシュされたデータを使用中...")
            return (st.session_state[data_key], 
                   st.session_state[trades_key], 
                   st.session_state[stats_key])
        
        # データがない場合は新しく処理
        st.sidebar.info("🔄 データを処理中...")
        
        # データ読み込み
        result = data_manager.load_data()
        if result[0] is None:
            return None, None, None
        df, n_continued = result
        
        if df is None or df.empty:
            return None, None, None
        
        # テクニカル指標計算
        df = self.calculate_technical_indicators(df)
        
        # 戦略分析
        trades_df, performance_stats = self.analyze_strategy(df, n_continued)
        
        # セッション状態に保存
        st.session_state[data_key] = df
        st.session_state[trades_key] = trades_df
        st.session_state[stats_key] = performance_stats
        
        st.sidebar.success("✅ データ処理完了")
        
        return df, trades_df, performance_stats
    
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