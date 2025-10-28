"""
PHM Temperature Database Query Module
Provides query functionality for PHM IEEE 2012 temperature data stored in SQLite.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

try:
    from backend.config import PHM_TEMPERATURE_DATABASE_PATH
except ModuleNotFoundError:
    from config import PHM_TEMPERATURE_DATABASE_PATH

logger = logging.getLogger(__name__)


class PHMTemperatureQuery:
    """Query interface for PHM temperature database."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            # 使用全域配置的溫度資料庫路徑
            self.db_path = Path(PHM_TEMPERATURE_DATABASE_PATH)
        else:
            self.db_path = Path(db_path)

    def _get_connection(self) -> sqlite3.Connection:
        """獲取資料庫連接"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Temperature database not found: {self.db_path}")
        
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_bearings(self) -> List[Dict[str, Any]]:
        """獲取所有軸承的溫度資訊"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, bearing_name, total_temp_files, created_at
                FROM phm_temperature_bearings
                ORDER BY bearing_name
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_bearing_info(self, bearing_name: str) -> Optional[Dict[str, Any]]:
        """獲取特定軸承的詳細資訊"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, bearing_name, total_temp_files, created_at
                FROM phm_temperature_bearings
                WHERE bearing_name = ?
            """, (bearing_name,))
            
            result = cursor.fetchone()
            return dict(result) if result else None

    def get_bearing_files(self, bearing_name: str) -> List[Dict[str, Any]]:
        """獲取特定軸承的所有溫度文件"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.id, f.file_name, f.file_number, f.record_count, f.created_at
                FROM phm_temperature_files f
                JOIN phm_temperature_bearings b ON f.bearing_id = b.id
                WHERE b.bearing_name = ?
                ORDER BY f.file_number
            """, (bearing_name,))
            return [dict(row) for row in cursor.fetchall()]

    def get_temperature_data(self, bearing_name: str, file_number: int = None, 
                           limit: int = 1000) -> List[Dict[str, Any]]:
        """獲取溫度測量資料"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if file_number is not None:
                # 獲取特定文件的溫度資料
                cursor.execute("""
                    SELECT m.hour, m.minute, m.second, m.microsecond, m.temperature,
                           f.file_name, f.file_number
                    FROM phm_temperature_measurements m
                    JOIN phm_temperature_files f ON m.file_id = f.id
                    JOIN phm_temperature_bearings b ON f.bearing_id = b.id
                    WHERE b.bearing_name = ? AND f.file_number = ?
                    ORDER BY m.hour, m.minute, m.second, m.microsecond
                    LIMIT ?
                """, (bearing_name, file_number, limit))
            else:
                # 獲取軸承的最新溫度資料
                cursor.execute("""
                    SELECT m.hour, m.minute, m.second, m.microsecond, m.temperature,
                           f.file_name, f.file_number
                    FROM phm_temperature_measurements m
                    JOIN phm_temperature_files f ON m.file_id = f.id
                    JOIN phm_temperature_bearings b ON f.bearing_id = b.id
                    WHERE b.bearing_name = ?
                    ORDER BY f.file_number DESC, m.hour, m.minute, m.second, m.microsecond
                    LIMIT ?
                """, (bearing_name, limit))
            
            return [dict(row) for row in cursor.fetchall()]

    def get_temperature_statistics(self, bearing_name: str = None) -> List[Dict[str, Any]]:
        """獲取溫度統計資訊"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if bearing_name:
                # 特定軸承的統計
                cursor.execute("""
                    SELECT 
                        b.bearing_name,
                        COUNT(m.id) as total_measurements,
                        COUNT(DISTINCT f.id) as total_files,
                        MIN(m.temperature) as min_temperature,
                        MAX(m.temperature) as max_temperature,
                        AVG(m.temperature) as avg_temperature,
                        MIN(f.file_number) as first_file,
                        MAX(f.file_number) as last_file
                    FROM phm_temperature_bearings b
                    JOIN phm_temperature_files f ON b.id = f.bearing_id
                    JOIN phm_temperature_measurements m ON f.id = m.file_id
                    WHERE b.bearing_name = ?
                    GROUP BY b.bearing_name
                """, (bearing_name,))
            else:
                # 所有軸承的統計
                cursor.execute("""
                    SELECT 
                        b.bearing_name,
                        COUNT(m.id) as total_measurements,
                        COUNT(DISTINCT f.id) as total_files,
                        MIN(m.temperature) as min_temperature,
                        MAX(m.temperature) as max_temperature,
                        AVG(m.temperature) as avg_temperature,
                        MIN(f.file_number) as first_file,
                        MAX(f.file_number) as last_file
                    FROM phm_temperature_bearings b
                    JOIN phm_temperature_files f ON b.id = f.bearing_id
                    JOIN phm_temperature_measurements m ON f.id = m.file_id
                    GROUP BY b.bearing_name
                    ORDER BY b.bearing_name
                """)
            
            return [dict(row) for row in cursor.fetchall()]

    def get_temperature_trends(self, bearing_name: str, file_count: int = 50) -> List[Dict[str, Any]]:
        """獲取溫度趨勢資料（按文件編號）"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    f.file_number,
                    f.file_name,
                    COUNT(m.id) as measurement_count,
                    MIN(m.temperature) as min_temperature,
                    MAX(m.temperature) as max_temperature,
                    AVG(m.temperature) as avg_temperature
                FROM phm_temperature_files f
                JOIN phm_temperature_bearings b ON f.bearing_id = b.id
                JOIN phm_temperature_measurements m ON f.id = m.file_id
                WHERE b.bearing_name = ?
                GROUP BY f.file_number, f.file_name
                ORDER BY f.file_number
                LIMIT ?
            """, (bearing_name, file_count))
            
            return [dict(row) for row in cursor.fetchall()]

    def get_database_info(self) -> Dict[str, Any]:
        """獲取資料庫基本資訊"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 獲取各表的記錄數
            cursor.execute("SELECT COUNT(*) FROM phm_temperature_bearings")
            bearing_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM phm_temperature_files")
            file_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM phm_temperature_measurements")
            measurement_count = cursor.fetchone()[0]
            
            # 獲取資料庫檔案大小
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            return {
                "database_path": str(self.db_path),
                "database_size_mb": round(db_size / (1024 * 1024), 2),
                "bearing_count": bearing_count,
                "file_count": file_count,
                "measurement_count": measurement_count,
                "avg_measurements_per_file": round(measurement_count / file_count, 1) if file_count > 0 else 0
            }

    def search_temperature_data(self, bearing_name: str = None, 
                              min_temperature: float = None,
                              max_temperature: float = None,
                              file_number_range: tuple = None,
                              limit: int = 1000) -> List[Dict[str, Any]]:
        """搜尋溫度資料"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if bearing_name:
                conditions.append("b.bearing_name = ?")
                params.append(bearing_name)
            
            if min_temperature is not None:
                conditions.append("m.temperature >= ?")
                params.append(min_temperature)
            
            if max_temperature is not None:
                conditions.append("m.temperature <= ?")
                params.append(max_temperature)
            
            if file_number_range:
                conditions.append("f.file_number BETWEEN ? AND ?")
                params.extend(file_number_range)
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            params.append(limit)
            
            query = f"""
                SELECT 
                    b.bearing_name,
                    f.file_number,
                    f.file_name,
                    m.hour, m.minute, m.second, m.microsecond,
                    m.temperature
                FROM phm_temperature_measurements m
                JOIN phm_temperature_files f ON m.file_id = f.id
                JOIN phm_temperature_bearings b ON f.bearing_id = b.id
                {where_clause}
                ORDER BY b.bearing_name, f.file_number, m.hour, m.minute, m.second, m.microsecond
                LIMIT ?
            """
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]


# 全域查詢實例
temperature_query = PHMTemperatureQuery()