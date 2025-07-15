import streamlit as st

class SignalAnalyzer:
    """シグナル分析クラス"""
    
    def __init__(self):
        self.header_text = "🎯 シグナル分析"
        self.info_text = "この戦略ではゴールデンクロス・デッドクロスの列挙は省略しています。"
    
    def render_signal_analysis(self, golden_crosses, dead_crosses):
        """シグナル分析をレンダリング（ゴールデンクロス・デッドクロスの列挙を削除）"""
        st.subheader(self.header_text)
        st.info(self.info_text) 