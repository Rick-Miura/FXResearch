import pandas as pd

class StatisticsCalculator:
    """統計計算クラス"""
    
    def __init__(self):
        self.initial_capital = 10000
        self.leverage = 25
    
    def get_strategy_statistics(self, trades_df):
        """戦略統計を取得"""
        if trades_df.empty:
            return {}
        
        stats = {
            'total_trades': len(trades_df),
            'winning_trades': len(trades_df[trades_df['profit_loss'] > 0]),
            'losing_trades': len(trades_df[trades_df['profit_loss'] < 0]),
            'win_rate': self._calculate_win_rate(trades_df),
            'total_profit_loss': trades_df['profit_loss'].sum(),
            'total_profit_loss_pct': trades_df['profit_loss_pct'].sum(),
            'avg_profit_loss': trades_df['profit_loss'].mean(),
            'avg_profit_loss_pct': trades_df['profit_loss_pct'].mean(),
            'max_profit': trades_df['profit_loss'].max(),
            'max_loss': trades_df['profit_loss'].min(),
            'avg_duration': trades_df['duration_days'].mean(),
            'exit_reasons': trades_df['exit_reason'].value_counts().to_dict(),
            'initial_capital': self.initial_capital,
            'leverage': self.leverage,
            'position_size': self.initial_capital * self.leverage,
            'total_return_pct': self._calculate_total_return(trades_df)
        }
        
        return stats
    
    def _calculate_win_rate(self, trades_df):
        """勝率を計算"""
        if len(trades_df) == 0:
            return 0
        return len(trades_df[trades_df['profit_loss'] > 0]) / len(trades_df) * 100
    
    def _calculate_total_return(self, trades_df):
        """総リターン率を計算"""
        total_profit_loss = trades_df['profit_loss'].sum()
        return (total_profit_loss / self.initial_capital) * 100 