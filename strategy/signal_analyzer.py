import pandas as pd

class SignalAnalyzer:
    """取引シグナル分析クラス"""
    
    def analyze_trading_signals(self, df, n_continued=1):
        """取引シグナルを分析"""
        df = df.copy()
        
        # RSI条件を追加
        df = self._add_rsi_condition(df)
        
        # パーフェクトオーダー継続条件を追加
        df = self._add_perfect_order_continuation(df, n_continued)
        
        # エントリーシグナルを生成
        df = self._generate_entry_signals(df)
        
        # 決済シグナルを生成
        df = self._generate_exit_signals(df)
        
        return df
    
    def _add_rsi_condition(self, df):
        """RSI条件を追加"""
        df['rsi_in_range'] = (df['RSI'] >= 30) & (df['RSI'] <= 70)
        return df
    
    def _add_perfect_order_continuation(self, df, n_continued):
        """パーフェクトオーダー継続条件を追加"""
        cond = df['perfect_order']
        n_continued = int(n_continued)  # 浮動小数点数を整数に変換
        for i in range(1, n_continued+1):
            cond = cond & df['perfect_order'].shift(i)
        df['perfect_order_continued'] = cond
        return df
    
    def _generate_entry_signals(self, df):
        """エントリーシグナルを生成"""
        df['entry_signal'] = (
            (df['price_breakout_bullish'] | df['price_breakout_bearish']) & 
            df['rsi_in_range'] &
            df['perfect_order_continued']
        )
        return df
    
    def _generate_exit_signals(self, df):
        """決済シグナルを生成"""
        df['exit_signal_bullish'] = df['Dead_Cross_25_75']
        df['exit_signal_bearish'] = df['Golden_Cross_25_75']
        df['exit_signal'] = df['exit_signal_bullish'] | df['exit_signal_bearish']
        return df 