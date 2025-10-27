"""
測試配置模組
驗證全域配置是否正確設置
"""

import os
from config import (
    PHM_DATABASE_PATH,
    DATABASE_PATH,
    BACKEND_DIR,
    DEFAULT_SAMPLING_RATE,
    CORS_ORIGINS,
    get_phm_db_path,
    get_db_path
)

def test_config():
    print("=== 配置測試 ===\n")

    print(f"Backend 目錄: {BACKEND_DIR}")
    print(f"目錄存在: {os.path.exists(BACKEND_DIR)}\n")

    print(f"PHM 資料庫路徑: {PHM_DATABASE_PATH}")
    print(f"資料庫存在: {os.path.exists(PHM_DATABASE_PATH)}\n")

    print(f"主資料庫路徑: {DATABASE_PATH}")
    print(f"資料庫存在: {os.path.exists(DATABASE_PATH)}\n")

    print(f"預設採樣率: {DEFAULT_SAMPLING_RATE} Hz")
    print(f"CORS 來源: {CORS_ORIGINS}\n")

    # 測試函數
    print(f"get_phm_db_path(): {get_phm_db_path()}")
    print(f"get_db_path(): {get_db_path()}\n")

    # 驗證資料庫可以連接
    if os.path.exists(PHM_DATABASE_PATH):
        import sqlite3
        try:
            conn = sqlite3.connect(PHM_DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"PHM 資料庫表格: {[t[0] for t in tables]}")
            conn.close()
            print("✓ PHM 資料庫連接成功\n")
        except Exception as e:
            print(f"✗ PHM 資料庫連接失敗: {e}\n")
    else:
        print("✗ PHM 資料庫不存在\n")

    print("=== 測試完成 ===")

if __name__ == "__main__":
    test_config()
