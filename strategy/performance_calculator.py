import pandas as pd
import numpy as np

class PerformanceCalculator:
    """戦略パフォーマンス計算クラス"""
    
    def __init__(self):
        self.initial_capital = 10000
        self.leverage = 25
        self.position_size = self.initial_capital * self.leverage
    
    def calculate_strategy_performance(self, df):
        """戦略のパフォーマンスを計算"""
        df = df.copy()
        trades = []
        in_position = False
        entry_price = 0
        entry_date = None
        entry_trend = None
        
        for idx, row in df.iterrows():
            # エントリー
            if row['entry_signal'] and not in_position:
                trade_info = self._handle_entry(row)
                if trade_info:
                    in_position = True
                    entry_price = trade_info['entry_price']
                    entry_date = trade_info['entry_date']
                    entry_trend = trade_info['entry_trend']
            
            # 決済
            elif in_position:
                exit_info = self._handle_exit(row, entry_trend)
                if exit_info:
                    trade = self._create_trade_record(
                        entry_date, entry_price, entry_trend,
                        exit_info['exit_date'], exit_info['exit_price'],
                        exit_info['exit_reason'], row
                    )
                    trades.append(trade)
                    in_position = False
        
        return pd.DataFrame(trades)
    
    def _handle_entry(self, row):
        """エントリー処理"""
        entry_price = row['Close'] if pd.notnull(row['Close']) else None
        if entry_price is None:
            return None
        
        entry_trend = None
        if row['bullish_perfect_order']:
            entry_trend = 'bullish'
        elif row['bearish_perfect_order']:
            entry_trend = 'bearish'
        
        return {
            'entry_price': entry_price,
            'entry_date': row['DateTime'],
            'entry_trend': entry_trend
        }
    
    def _handle_exit(self, row, entry_trend):
        """決済処理"""
        exit_reason = None
        
        # トレンドごとの決済
        if entry_trend == 'bullish' and row['exit_signal_bullish']:
            exit_reason = 'デッドクロス'
        elif entry_trend == 'bearish' and row['exit_signal_bearish']:
            exit_reason = 'ゴールデンクロス'
        # 200MAストップロス
        elif entry_trend == 'bullish' and row['Close'] < row['MA200']:
            exit_reason = '200MAストップロス'
        elif entry_trend == 'bearish' and row['Close'] > row['MA200']:
            exit_reason = '200MAストップロス'
        
        if exit_reason:
            return {
                'exit_price': row['Close'],
                'exit_date': row['DateTime'],
                'exit_reason': exit_reason
            }
        
        return None
    
    def _create_trade_record(self, entry_date, entry_price, entry_trend, 
                           exit_date, exit_price, exit_reason, row):
        """取引記録を作成"""
        # 損益計算
        price_change = exit_price - entry_price
        price_change_pct = ((exit_price - entry_price) / entry_price) * 100
        
        if entry_trend == 'bullish':
            actual_profit_loss = price_change * (self.position_size / entry_price)
            actual_profit_loss_pct = price_change_pct * self.leverage
        else:
            actual_profit_loss = -price_change * (self.position_size / entry_price)
            actual_profit_loss_pct = -price_change_pct * self.leverage
        
        return {
            'entry_date': entry_date,
            'exit_date': exit_date,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'profit_loss': actual_profit_loss,
            'profit_loss_pct': actual_profit_loss_pct,
            'exit_reason': exit_reason,
            'duration_days': (exit_date - entry_date).days,
            'position_size': self.position_size,
            'leverage': self.leverage,
            'entry_rsi': row['RSI'] if 'RSI' in row else None,
            'exit_rsi': row['RSI'] if 'RSI' in row else None,
            'entry_atr': row['ATR'] if 'ATR' in row else None,
            'entry_ma25_deviation': self._calculate_ma_deviation(entry_price, row['MA25']),
            'entry_ma75_deviation': self._calculate_ma_deviation(entry_price, row['MA75']),
            'entry_trend': entry_trend
        }
    
    def _calculate_ma_deviation(self, price, ma_value):
        """MA乖離率を計算"""
        if pd.notnull(price) and pd.notnull(ma_value) and ma_value != 0:
            return ((price - ma_value) / ma_value) * 100
        return None
    
    def calculate_atr(self, df, period=14):
        """ATR（Average True Range）を計算"""
        df = df.copy()
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift(1))
        low_close = np.abs(df['Low'] - df['Close'].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=period, min_periods=1).mean()
        return df 