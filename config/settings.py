# アプリケーション設定

# データファイルマッピング
DATA_MAPPING = {
    "2024年": "data/USDJPY_2024_15min.csv",
    "2023年": "data/USDJPY_2023_15min.csv", 
    "2022年": "data/USDJPY_2022_15min.csv"
}

# チャート設定
CHART_CONFIG = {
    'displayModeBar': True,
    'modeBarButtonsToRemove': [
        'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
        'pan2d', 'select2d', 'lasso2d', 'toggleSpikelines', 'hoverCompareCartesian', 'hoverClosestCartesian'
    ]
}

# ページ設定
PAGE_CONFIG = {
    'page_title': "FX移動平均線分析",
    'page_icon': "📈",
    'layout': "wide"
}

# デフォルト設定
DEFAULT_SETTINGS = {
    'n_continued_options': [1, 2, 3, 4, 5],
    'n_continued_default': 0,
    'rsi_period': 14,
    'year_options': ["2024年", "2023年", "2022年"]
} 