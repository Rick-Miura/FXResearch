from strategy.perfect_order_detector import PerfectOrderDetector
from strategy.signal_analyzer import SignalAnalyzer
from strategy.performance_calculator import PerformanceCalculator
from strategy.statistics_calculator import StatisticsCalculator

class StrategyFactory:
    """戦略分析のファクトリークラス"""
    
    def __init__(self):
        self.perfect_order_detector = PerfectOrderDetector()
        self.signal_analyzer = SignalAnalyzer()
        self.performance_calculator = PerformanceCalculator()
        self.statistics_calculator = StatisticsCalculator()
    
    def get_perfect_order_detector(self):
        """パーフェクトオーダー検出を取得"""
        return self.perfect_order_detector
    
    def get_signal_analyzer(self):
        """シグナル分析を取得"""
        return self.signal_analyzer
    
    def get_performance_calculator(self):
        """パフォーマンス計算を取得"""
        return self.performance_calculator
    
    def get_statistics_calculator(self):
        """統計計算を取得"""
        return self.statistics_calculator 