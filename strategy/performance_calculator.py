import pandas as pd
import numpy as np

class PerformanceCalculator:
    """戦略パフォーマンス計算クラス"""
    
    def __init__(self):
        self.initial_capital = 10000
        self.leverage = 25
        self.position_size = self.initial_capital * self.leverage
        self.profit_multiplier = 2.0  # デフォルト値
    
    def calculate_strategy_performance(self, df):
        """戦略のパフォーマンスを計算"""
        df = df.copy()
        trades = []
        in_position = False
        entry_price = 0
        entry_date = None
        entry_trend = None
        entry_ma200 = None  # エントリー時の200MAを保存
        entry_rsi = None  # エントリー時のRSIを保存
        entry_atr = None  # エントリー時のATRを保存
        entry_ma25 = None  # エントリー時のMA25を保存
        entry_ma75 = None  # エントリー時のMA75を保存
        
        for idx, row in df.iterrows():
            # エントリー
            if row['entry_signal'] and not in_position:
                trade_info = self._handle_entry(row)
                if trade_info:
                    in_position = True
                    entry_price = trade_info['entry_price']
                    entry_date = trade_info['entry_date']
                    entry_trend = trade_info['entry_trend']
                    entry_ma200 = row['MA200']  # エントリー時の200MAを保存
                    entry_rsi = row['RSI'] if 'RSI' in row else None  # エントリー時のRSIを保存
                    entry_atr = row['ATR'] if 'ATR' in row else None  # エントリー時のATRを保存
                    entry_ma25 = row['MA25'] if 'MA25' in row else None  # エントリー時のMA25を保存
                    entry_ma75 = row['MA75'] if 'MA75' in row else None  # エントリー時のMA75を保存
            
            # 決済
            elif in_position:
                exit_info = self._handle_exit(row, entry_trend, entry_price, entry_ma200)
                if exit_info:
                    trade = self._create_trade_record(
                        entry_date, entry_price, entry_trend,
                        exit_info['exit_date'], exit_info['exit_price'],
                        exit_info['exit_reason'], row,
                        entry_rsi, entry_atr, entry_ma25, entry_ma75
                    )
                    trades.append(trade)
                    in_position = False
                    entry_ma200 = None  # リセット
                    entry_rsi = None  # リセット
                    entry_atr = None  # リセット
                    entry_ma25 = None  # リセット
                    entry_ma75 = None  # リセット
        
        trades_df = pd.DataFrame(trades)
        
        # デバッグ情報を表示
        if not trades_df.empty:
            rsi_out_of_range = trades_df[(trades_df['entry_rsi'] < 30) | (trades_df['entry_rsi'] > 70)]
            if not rsi_out_of_range.empty:
                print(f"⚠️ 警告: RSI 30-70範囲外の取引が{len(rsi_out_of_range)}件あります")
                print(f"RSI範囲外の取引: {rsi_out_of_range['entry_rsi'].tolist()}")
            else:
                print(f"✅ RSI 30-70範囲内の取引のみ: {len(trades_df)}件")
        
        return trades_df
    
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
            'entry_date': row['datetime'],
            'entry_trend': entry_trend
        }
    
    def _handle_exit(self, row, entry_trend, entry_price, entry_ma200):
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
                'exit_date': row['datetime'],
                'exit_reason': exit_reason
            }
        
        return None
    
    def _create_trade_record(self, entry_date, entry_price, entry_trend, 
                           exit_date, exit_price, exit_reason, row,
                           entry_rsi=None, entry_atr=None, entry_ma25=None, entry_ma75=None):
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
            'entry_rsi': entry_rsi,  # エントリー時のRSI
            'exit_rsi': row['RSI'] if 'RSI' in row else None,  # 決済時のRSI
            'entry_atr': entry_atr,  # エントリー時のATR
            'entry_ma25_deviation': self._calculate_ma_deviation(entry_price, entry_ma25),
            'entry_ma75_deviation': self._calculate_ma_deviation(entry_price, entry_ma75),
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