import streamlit as st
import pandas as pd

class SidebarManager:
    """サイドバー管理クラス"""
    
    def __init__(self):
        self.header_text = "📊 分析設定"
        self.date_header = "📅 日付範囲"
    
    def render_sidebar(self, df, min_date, max_date):
        """サイドバーをレンダリング"""
        st.sidebar.header(self.header_text)
        
        # 日付範囲選択
        start_date, end_date = self._render_date_range(min_date, max_date)
        
        return start_date, end_date
    
    def _render_date_range(self, min_date, max_date):
        """日付範囲選択をレンダリング"""
        st.sidebar.subheader(self.date_header)
        
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