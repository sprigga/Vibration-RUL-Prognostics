"""
Configuration module for the vibration analysis backend.
Provides global configuration variables for database paths and other settings.
"""
import os
from pathlib import Path

# 獲取 backend 目錄的絕對路徑
BACKEND_DIR = Path(__file__).parent.absolute()

# PHM 資料庫路徑 (全域變數)
PHM_DATABASE_PATH = os.path.join(BACKEND_DIR, "phm_data.db")

# 其他可能的配置
DATABASE_PATH = os.path.join(BACKEND_DIR, "vibration_analysis.db")

# API 配置
API_HOST = "0.0.0.0"
API_PORT = 8081

# CORS 配置
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000"
]

# 採樣率配置
DEFAULT_SAMPLING_RATE = 25600  # Hz

# 包絡分析濾波器配置
ENVELOPE_FILTER_LOWCUT = 4000  # Hz
ENVELOPE_FILTER_HIGHCUT = 10000  # Hz

# 資料點顯示限制
SIGNAL_DISPLAY_LIMIT = 1000  # 前端顯示的最大資料點數
SPECTRUM_DISPLAY_LIMIT = 1000  # 頻譜顯示的最大資料點數
ENVELOPE_SPECTRUM_DISPLAY_LIMIT = 500  # 包絡頻譜顯示的最大資料點數

# PHM 數據目錄
PHM_DATA_DIR = os.path.join(Path(__file__).parent.parent, "phm-ieee-2012-data-challenge-dataset")
PHM_RESULTS_DIR = os.path.join(Path(__file__).parent.parent, "phm_analysis_results")

def get_phm_db_path() -> str:
    """獲取 PHM 資料庫路徑"""
    return PHM_DATABASE_PATH

def get_db_path() -> str:
    """獲取主資料庫路徑"""
    return DATABASE_PATH
