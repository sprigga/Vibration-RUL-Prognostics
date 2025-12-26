#!/usr/bin/env python3
"""
建立 PHM 溫度資料庫架構
建立空的資料表結構，準備供未來溫度資料匯入使用
"""
import sqlite3
from pathlib import Path

try:
    from backend.config import PHM_TEMPERATURE_DATABASE_PATH
except ModuleNotFoundError:
    from config import PHM_TEMPERATURE_DATABASE_PATH


def create_temperature_database():
    """建立溫度資料庫架構"""
    db_path = Path(PHM_TEMPERATURE_DATABASE_PATH)

    print(f"建立資料庫: {db_path}")

    # 確保目錄存在
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # 建立連接
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # 建立溫度軸承表
        print("建立 phm_temperature_bearings 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phm_temperature_bearings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bearing_name TEXT UNIQUE NOT NULL,
                total_temp_files INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 建立溫度檔案表
        print("建立 phm_temperature_files 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phm_temperature_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bearing_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_number INTEGER,
                record_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bearing_id) REFERENCES phm_temperature_bearings(id)
            )
        """)

        # 建立溫度測量資料表
        print("建立 phm_temperature_measurements 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phm_temperature_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                hour INTEGER NOT NULL,
                minute INTEGER NOT NULL,
                second INTEGER NOT NULL,
                microsecond INTEGER NOT NULL,
                temperature REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES phm_temperature_files(id)
            )
        """)

        # 建立索引
        print("建立索引...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_temp_files_bearing_id
            ON phm_temperature_files(bearing_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_temp_measurements_file_id
            ON phm_temperature_measurements(file_id)
        """)

        conn.commit()

        # 驗證資料表
        print("\n驗證資料庫架構...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"\n✅ 溫度資料庫建立成功！")
        print(f"資料庫路徑: {db_path}")
        print(f"資料庫大小: {db_path.stat().st_size} bytes")
        print(f"建立的資料表: {', '.join(tables)}")

        return True

    except Exception as e:
        print(f"❌ 建立資料庫時發生錯誤: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    create_temperature_database()
