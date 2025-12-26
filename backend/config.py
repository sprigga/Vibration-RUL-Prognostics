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
PHM_TEMPERATURE_DATABASE_PATH = os.path.join(BACKEND_DIR, "phm_temperature_data.db")

# 其他可能的配置
DATABASE_PATH = os.path.join(BACKEND_DIR, "vibration_analysis.db")

# API 配置
API_HOST = "0.0.0.0"
API_PORT = 8081

# CORS 配置
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000"
]

# 採樣率配置
DEFAULT_SAMPLING_RATE = 25600  # Hz

# 包絡分析濾波器配置
# 調整為軸承故障頻率範圍 (BPFI ~233 Hz, BPFO ~156 Hz)
# 舊值: 4000-10000 Hz (不適合軸承故障分析)
ENVELOPE_FILTER_LOWCUT = 10  # Hz
ENVELOPE_FILTER_HIGHCUT = 500  # Hz - 涵蓋基頻及諧波(2×BPFI = 466.86 Hz)

# 資料點顯示限制
SIGNAL_DISPLAY_LIMIT = 1000  # 前端顯示的最大資料點數
SPECTRUM_DISPLAY_LIMIT = 1000  # 頻譜顯示的最大資料點數
ENVELOPE_SPECTRUM_DISPLAY_LIMIT = 500  # 包絡頻譜顯示的最大資料點數

# PHM 數據目錄
PHM_DATA_DIR = os.path.join(Path(__file__).parent.parent, "phm-ieee-2012-data-challenge-dataset")
PHM_RESULTS_DIR = os.path.join(Path(__file__).parent.parent, "phm_analysis_results")

def get_phm_db_path() -> str:
    """獲取 PHM 振動資料庫路徑"""
    return PHM_DATABASE_PATH

def get_phm_temperature_db_path() -> str:
    """獲取 PHM 溫度資料庫路徑"""
    return PHM_TEMPERATURE_DATABASE_PATH

def get_db_path() -> str:
    """獲取主資料庫路徑"""
    return DATABASE_PATH
