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
        
        # デバッグ情報を追加
        self._add_debug_info(df)
        
        return df
    
    def _add_rsi_condition(self, df):
        """RSI条件を追加"""
        df['rsi_in_range'] = (df['RSI'] >= 30) & (df['RSI'] <= 70)
        return df
    
    def _add_perfect_order_continuation(self, df, n_continued):
        """パーフェクトオーダー継続条件を追加"""
        cond = df['perfect_order']
        n_continued = int(n_continued)  # 浮動小数点数を整数に変換
        
        # 最低3期間の継続を要求
        min_continued = max(3, n_continued)
        for i in range(1, min_continued+1):
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
    
    def _add_debug_info(self, df):
        """デバッグ情報を追加"""
        # 各条件の満たされている回数をカウント
        price_breakout_count = (df['price_breakout_bullish'] | df['price_breakout_bearish']).sum()
        rsi_in_range_count = df['rsi_in_range'].sum()
        perfect_order_continued_count = df['perfect_order_continued'].sum()
        entry_signal_count = df['entry_signal'].sum()
        
        # パーフェクトオーダーの詳細
        bullish_perfect_order_count = df['bullish_perfect_order'].sum()
        bearish_perfect_order_count = df['bearish_perfect_order'].sum()
        perfect_order_count = df['perfect_order'].sum()
        
        # デバッグ情報をDataFrameに追加
        df['debug_price_breakout'] = df['price_breakout_bullish'] | df['price_breakout_bearish']
        df['debug_rsi_in_range'] = df['rsi_in_range']
        df['debug_perfect_order_continued'] = df['perfect_order_continued']
        
        # 統計情報を表示（開発時のみ）
        print(f"=== デバッグ情報 ===")
        print(f"パーフェクトオーダー（強気）: {bullish_perfect_order_count}回")
        print(f"パーフェクトオーダー（弱気）: {bearish_perfect_order_count}回")
        print(f"パーフェクトオーダー（合計）: {perfect_order_count}回")
        print(f"パーフェクトオーダー継続: {perfect_order_continued_count}回")
        print(f"価格ブレイクアウト: {price_breakout_count}回")
        print(f"RSI 30-70範囲内: {rsi_in_range_count}回")
        print(f"エントリーシグナル: {entry_signal_count}回")
        print(f"==================")
        
        return df 