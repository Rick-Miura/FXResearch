from component.sidebar_manager import SidebarManager
from component.stats_renderer import StatsRenderer
from component.signal_analyzer import SignalAnalyzer

class UIFactory:
    """UIコンポーネント作成のファクトリークラス"""
    
    def __init__(self):
        self.sidebar_manager = SidebarManager()
        self.stats_renderer = StatsRenderer()
        self.signal_analyzer = SignalAnalyzer()
    
    def get_sidebar_manager(self):
        """サイドバー管理を取得"""
        return self.sidebar_manager
    
    def get_stats_renderer(self):
        """統計表示を取得"""
        return self.stats_renderer
    
    def get_signal_analyzer(self):
        """シグナル分析を取得"""
        return self.signal_analyzer 