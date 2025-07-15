import pandas as pd

class PerfectOrderDetector:
    """パーフェクトオーダー検出クラス"""
    
    def detect_perfect_order(self, df):
        """パーフェクトオーダーを検出"""
        df = df.copy()
        
        # MAの傾きを計算
        df = self._calculate_ma_slopes(df)
        
        # 強気・弱気パーフェクトオーダーを検出
        df = self._detect_bullish_perfect_order(df)
        df = self._detect_bearish_perfect_order(df)
        
        # パーフェクトオーダーの開始・終了を検出
        df = self._detect_perfect_order_changes(df)
        
        # 価格ブレイクアウトを検出
        df = self._detect_price_breakouts(df)
        
        return df
    
    def _calculate_ma_slopes(self, df):
        """MAの傾きを計算"""
        df['MA25_slope'] = df['MA25'] - df['MA25'].shift(1)
        df['MA75_slope'] = df['MA75'] - df['MA75'].shift(1)
        df['MA200_slope'] = df['MA200'] - df['MA200'].shift(1)
        
        df['MA25_slope_positive'] = df['MA25_slope'] > 0
        df['MA75_slope_positive'] = df['MA75_slope'] > 0
        df['MA200_slope_positive'] = df['MA200_slope'] > 0
        
        return df
    
    def _detect_bullish_perfect_order(self, df):
        """強気パーフェクトオーダーを検出"""
        df['bullish_perfect_order'] = (
            (df['MA25'] > df['MA75']) & 
            (df['MA75'] > df['MA200']) &
            (df['MA25_slope_positive'] == df['MA75_slope_positive']) &
            (df['MA75_slope_positive'] == df['MA200_slope_positive'])
        )
        return df
    
    def _detect_bearish_perfect_order(self, df):
        """弱気パーフェクトオーダーを検出"""
        df['bearish_perfect_order'] = (
            (df['MA25'] < df['MA75']) & 
            (df['MA75'] < df['MA200']) &
            (df['MA25_slope_positive'] == df['MA75_slope_positive']) &
            (df['MA75_slope_positive'] == df['MA200_slope_positive'])
        )
        return df
    
    def _detect_perfect_order_changes(self, df):
        """パーフェクトオーダーの開始・終了を検出"""
        df['perfect_order'] = df['bullish_perfect_order'] | df['bearish_perfect_order']
        df['perfect_order_start'] = (df['perfect_order'] != df['perfect_order'].shift(1)) & df['perfect_order']
        df['perfect_order_end'] = (df['perfect_order'] != df['perfect_order'].shift(1)) & ~df['perfect_order']
        return df
    
    def _detect_price_breakouts(self, df):
        """価格ブレイクアウトを検出"""
        # 強気トレンドでの価格ブレイクアウト
        df['price_breakout_bullish'] = (
            (df['Close'] > df['MA25']) & 
            (df['Close'].shift(1) <= df['MA25'].shift(1)) &
            df['bullish_perfect_order']
        )
        
        # 弱気トレンドでの価格ブレイクアウト
        df['price_breakout_bearish'] = (
            (df['Close'] < df['MA25']) & 
            (df['Close'].shift(1) >= df['MA25'].shift(1)) &
            df['bearish_perfect_order']
        )
        
        return df 