import streamlit as st
from core.data_manager import DataManager
from core.analysis_processor import AnalysisProcessor
from core.ui_manager import UIManager

class FXAnalysisApp:
    """FX分析アプリケーションのメインコントローラー"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.analysis_processor = AnalysisProcessor()
        self.ui_manager = UIManager()
        
        self.ui_manager.setup_page_config()
        self.ui_manager.setup_css()
    
    def run(self):
        """メインアプリケーション実行"""
        st.markdown('<h1 class="main-header">📈 FX移動平均線戦略分析</h1>', unsafe_allow_html=True)
        
        # 戦略情報を折りたたみ可能で表示
        self.ui_manager.render_strategy_info()
        
        # データ読み込みと処理（セッション状態に保存）
        df, trades_df, performance_stats = self.analysis_processor.load_and_process_data(self.data_manager)
        
        if df is None or df.empty:
            st.error("データが見つかりません")
            return
        
        # メインコンテンツを表示
        self.ui_manager.render_main_content(df, trades_df, performance_stats) 