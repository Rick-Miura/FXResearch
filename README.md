# FX移動平均線分析アプリ

15分足USDJPYデータを使用した移動平均線分析のStreamlitアプリケーション。

## 📁 プロジェクト構造

```
FXResearch/
├── app.py                                    # メインアプリ
├── requirements.txt                          # 依存関係
├── README.md                                # 説明書
│
├── data/                                    # データ・処理
│   ├── USDJPY_2022_15min.csv
│   ├── USDJPY_2023_15min.csv
│   ├── USDJPY_2024_15min.csv
│   └── fx_data_loader.py                    # データ読み込み
│
├── indicator/                               # テクニカル指標
│   ├── moving_averages.py                   # 移動平均線
│   ├── rsi_indicator.py                     # RSI
│   └── atr_indicator.py                     # ATR
│
├── strategy/                                # 戦略
│   └── perfect_order_strategy.py            # パーフェクトオーダー
│
├── chart/                                   # チャート
│   └── candlestick_charts.py               # ローソク足
│
├── component/                               # UI
│   └── sidebar_component.py                 # サイドバー
│
└── test/                                   # テスト
```

## 📋 命名ルール

- **ディレクトリ**: 単数形（`indicator/`, `strategy/`）
- **ファイル**: 機能を明確に表現（`fx_data_loader.py`）

## 🚀 使用方法

```bash
# 環境セットアップ
conda activate research
pip install -r requirements.txt

# アプリ実行
streamlit run app.py
```

## 🎯 機能

- **移動平均線分析**: MA25、MA75、MA200
- **パーフェクトオーダー戦略**: エントリー・決済シグナル
- **RSI・ATR分析**: 補助指標
- **インタラクティブチャート**: Plotly
- **年別データ選択**: 2022-2024年

## 🔧 技術スタック

- Python 3.8+
- Streamlit
- Pandas
- Plotly
- NumPy 