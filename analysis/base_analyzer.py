import numpy as np
from scipy.stats import ttest_ind, chi2_contingency
import pandas as pd

class BaseAnalyzer:
    """分析クラスの基底クラス - 共通のp値計算メソッドを提供"""
    
    def _get_pvalue(self, ttest_result):
        """t検定のp値を取得"""
        if hasattr(ttest_result, 'pvalue'):
            return float(ttest_result.pvalue)
        elif isinstance(ttest_result, (tuple, list)) and len(ttest_result) > 1:
            return float(ttest_result[1])
        return float('nan')
    
    def calculate_t_test_p_value(self, profit_data, loss_data):
        """t検定によるp値を計算"""
        if len(profit_data) == 0 or len(loss_data) == 0:
            return 1.0
        
        try:
            ttest = ttest_ind(profit_data, loss_data, equal_var=False, nan_policy='omit')
            return self._get_pvalue(ttest)
        except:
            return 1.0
    
    def calculate_chi2_p_value(self, trades_df, group_column, target_column=None):
        """カイ二乗検定によるp値を計算"""
        if trades_df.empty or group_column not in trades_df.columns:
            return 1.0
        
        if target_column is None:
            # デフォルトは利益・損失の判定
            target_column = (trades_df['profit_loss'] > 0)
        elif target_column in trades_df.columns:
            target_column = trades_df[target_column]
        else:
            return 1.0
        
        try:
            # クロス集計表を作成
            contingency_table = pd.crosstab(trades_df[group_column], target_column)
            
            if contingency_table.shape[0] > 1 and contingency_table.shape[1] > 1:
                chi2, p_value, dof, expected = chi2_contingency(contingency_table)
                return p_value
        except:
            pass
        
        return 1.0
    
    def calculate_group_comparison_p_value(self, trades_df, data_column, group_by_profit_loss=True):
        """利益・損失グループ比較によるp値を計算"""
        if trades_df.empty or data_column not in trades_df.columns:
            return 1.0
        
        # 利益・損失グループ分け
        if group_by_profit_loss:
            profit_trades = trades_df[trades_df['profit_loss'] > 0]
            loss_trades = trades_df[trades_df['profit_loss'] <= 0]
        else:
            # 他のグループ分け方法がある場合はここで実装
            return 1.0
        
        # データを取得
        profit_data = profit_trades[data_column].dropna()
        loss_data = loss_trades[data_column].dropna()
        
        return self.calculate_t_test_p_value(profit_data, loss_data)
    
    def calculate_multiple_comparison_p_value(self, trades_df, data_columns, group_by_profit_loss=True):
        """複数のデータ列の平均p値を計算"""
        if trades_df.empty:
            return 1.0
        
        p_values = []
        
        for column in data_columns:
            if column in trades_df.columns:
                p_value = self.calculate_group_comparison_p_value(trades_df, column, group_by_profit_loss)
                p_values.append(p_value)
        
        if not p_values:
            return 1.0
        
        # 平均p値を返す
        return np.mean(p_values) 