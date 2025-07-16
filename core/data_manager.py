import streamlit as st
import pandas as pd
import os
from data_processor import load_fx_data

class DataManager:
    """データ管理クラス"""
    
    def __init__(self):
        pass
    
    def load_data(self):
        """データを読み込み"""
        # サイドバーから年選択
        years = ["全期間", "2022", "2023", "2024"]
        selected_year = st.sidebar.selectbox("年を選択", years, index=0)
        
        # パーフェクトオーダー連続回数設定
        st.sidebar.markdown("### 📊 パーフェクトオーダー設定")
        n_continued = st.sidebar.slider(
            "パーフェクトオーダー連続回数",
            min_value=1,
            max_value=5,
            value=1,
            step=1,
            help="パーフェクトオーダーが何回連続した場合にエントリーするか"
        )
        
        # セッション状態に保存
        st.session_state['selected_year'] = selected_year
        st.session_state['n_continued'] = n_continued
        
        # 全期間データ再生成ボタン
        if selected_year == "全期間":
            st.sidebar.markdown("### 🔄 全期間データ管理")
            if st.sidebar.button("🔄 全期間データを再生成"):
                self.regenerate_all_years_data()
                # キャッシュをクリア
                self.clear_cache()
        
        # キャッシュ管理
        st.sidebar.markdown("### ⚡ キャッシュ管理")
        if st.sidebar.button("🗑️ キャッシュをクリア"):
            self.clear_cache()
        
        try:
            if selected_year == "全期間":
                # 全期間のデータを結合
                df = self.load_all_years_data()
            else:
                # 単一年のデータを読み込み
                file_path = f"data/USDJPY_{selected_year}_15min.csv"
                df = load_fx_data(file_path)
            
            return df, n_continued
        except Exception as e:
            st.error(f"データ読み込みエラー: {e}")
            return None, None
    
    def load_all_years_data(self):
        """全期間のデータを結合して読み込み"""
        # まず保存済みの全期間データがあるかチェック
        combined_file_path = "data/USDJPY_all_years_15min.csv"
        
        try:
            # 保存済みの全期間データを読み込み
            if pd.io.common.file_exists(combined_file_path):
                st.sidebar.info("📁 保存済みの全期間データを読み込み中...")
                combined_df = load_fx_data(combined_file_path)
                st.sidebar.success(f"📊 全期間データ読み込み完了: {len(combined_df):,}件")
                return combined_df
        except Exception as e:
            st.sidebar.warning(f"⚠️ 保存済みデータ読み込みエラー: {e}")
        
        # 保存済みデータがない場合は各年データを結合
        years = ["2022", "2023", "2024"]
        all_data = []
        
        st.sidebar.info("🔄 各年データを結合中...")
        for year in years:
            try:
                file_path = f"data/USDJPY_{year}_15min.csv"
                year_data = load_fx_data(file_path)
                if not year_data.empty:
                    all_data.append(year_data)
                    st.sidebar.success(f"✅ {year}年データ読み込み完了")
            except Exception as e:
                st.sidebar.warning(f"⚠️ {year}年データ読み込みエラー: {e}")
        
        if not all_data:
            st.error("全期間のデータが読み込めませんでした")
            return pd.DataFrame()
        
        # データを結合（日時順にソート）
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.sort_values('datetime').reset_index(drop=True)
        
        # 結合したデータを保存
        try:
            combined_df.to_csv(combined_file_path, index=False)
            st.sidebar.success(f"💾 全期間データを保存しました: {combined_file_path}")
        except Exception as e:
            st.sidebar.warning(f"⚠️ データ保存エラー: {e}")
        
        st.sidebar.success(f"📊 全期間データ結合完了: {len(combined_df):,}件")
        return combined_df
    
    def regenerate_all_years_data(self):
        """全期間データを再生成"""
        combined_file_path = "data/USDJPY_all_years_15min.csv"
        
        # 既存のファイルを削除
        if os.path.exists(combined_file_path):
            os.remove(combined_file_path)
            st.sidebar.success("🗑️ 既存の全期間データを削除しました")
        
        # 新しいデータを生成
        st.sidebar.info("🔄 全期間データを再生成中...")
        self.load_all_years_data()
        st.sidebar.success("✅ 全期間データの再生成が完了しました")
    
    def clear_cache(self):
        """セッション状態のキャッシュをクリア"""
        keys_to_remove = []
        for key in st.session_state.keys():
            if key.startswith('processed_data_') or key.startswith('trades_data_') or key.startswith('performance_stats_'):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        st.sidebar.info("��️ キャッシュをクリアしました") 