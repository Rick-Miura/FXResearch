from data_processor.fx_data_processor import FXDataProcessor

_fx_data_processor = FXDataProcessor()

def load_fx_data(file_path):
    """FXデータを読み込み、市場クローズ中のデータを除外"""
    return _fx_data_processor.load_fx_data(file_path)

def get_data_range(df):
    """データの範囲を取得"""
    return _fx_data_processor.get_data_range(df) 