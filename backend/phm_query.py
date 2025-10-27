"""
PHM Database Query Module
Provides query functionality for PHM IEEE 2012 data stored in SQLite.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from backend.config import PHM_DATABASE_PATH
except ModuleNotFoundError:
    from config import PHM_DATABASE_PATH


class PHMDatabaseQuery:
    """Query interface for PHM database."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            # 使用全域配置的資料庫路徑
            self.db_path = Path(PHM_DATABASE_PATH)
        else:
            self.db_path = Path(db_path)

        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def get_bearings(self) -> List[Dict[str, Any]]:
        """Get all bearings with statistics."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    b.bearing_id,
                    b.bearing_name,
                    b.condition_id,
                    b.description,
                    COUNT(DISTINCT mf.file_id) as file_count,
                    COUNT(m.measurement_id) as measurement_count
                FROM bearings b
                LEFT JOIN measurement_files mf ON b.bearing_id = mf.bearing_id
                LEFT JOIN measurements m ON mf.file_id = m.file_id
                GROUP BY b.bearing_id, b.bearing_name, b.condition_id,
                         b.description
                ORDER BY b.bearing_name
            """)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_bearing_info(self, bearing_name: str) -> Dict[str, Any]:
        """Get detailed information for a specific bearing."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Get bearing basic info
            cursor.execute("""
                SELECT * FROM bearings WHERE bearing_name = ?
            """, (bearing_name,))
            result = cursor.fetchone()

            if not result:
                return None

            bearing = dict(result)

            # Get file count
            cursor.execute("""
                SELECT COUNT(*) as file_count
                FROM measurement_files
                WHERE bearing_id = ?
            """, (bearing['bearing_id'],))
            bearing['file_count'] = cursor.fetchone()[0]

            # Get measurement count
            cursor.execute("""
                SELECT COUNT(*) as measurement_count
                FROM measurements m
                JOIN measurement_files mf ON m.file_id = mf.file_id
                WHERE mf.bearing_id = ?
            """, (bearing['bearing_id'],))
            bearing['measurement_count'] = cursor.fetchone()[0]

            # Get acceleration statistics
            cursor.execute("""
                SELECT
                    AVG(m.horizontal_acceleration) as avg_h_acc,
                    AVG(m.vertical_acceleration) as avg_v_acc,
                    MIN(m.horizontal_acceleration) as min_h_acc,
                    MIN(m.vertical_acceleration) as min_v_acc,
                    MAX(m.horizontal_acceleration) as max_h_acc,
                    MAX(m.vertical_acceleration) as max_v_acc,
                    AVG(ABS(m.horizontal_acceleration)) as avg_abs_h_acc,
                    AVG(ABS(m.vertical_acceleration)) as avg_abs_v_acc
                FROM measurements m
                JOIN measurement_files mf ON m.file_id = mf.file_id
                WHERE mf.bearing_id = ?
            """, (bearing['bearing_id'],))

            stats = dict(cursor.fetchone())
            bearing['acceleration_stats'] = stats

            return bearing
        finally:
            conn.close()

    def get_file_list(
        self,
        bearing_name: str,
        offset: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get list of files for a bearing with pagination."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Get total count
            cursor.execute("""
                SELECT COUNT(*)
                FROM measurement_files mf
                JOIN bearings b ON mf.bearing_id = b.bearing_id
                WHERE b.bearing_name = ?
            """, (bearing_name,))
            total_count = cursor.fetchone()[0]

            # Get files with statistics
            cursor.execute("""
                SELECT
                    mf.file_id,
                    mf.file_name,
                    mf.file_number,
                    mf.record_count,
                    MIN(m.hour) as start_hour,
                    MIN(m.minute) as start_minute,
                    MAX(m.hour) as end_hour,
                    MAX(m.minute) as end_minute,
                    AVG(m.horizontal_acceleration) as avg_h_acc,
                    AVG(m.vertical_acceleration) as avg_v_acc,
                    MAX(ABS(m.horizontal_acceleration)) as max_abs_h_acc,
                    MAX(ABS(m.vertical_acceleration)) as max_abs_v_acc
                FROM measurement_files mf
                JOIN bearings b ON mf.bearing_id = b.bearing_id
                JOIN measurements m ON mf.file_id = m.file_id
                WHERE b.bearing_name = ?
                GROUP BY mf.file_id, mf.file_name, mf.file_number,
                         mf.record_count
                ORDER BY mf.file_number
                LIMIT ? OFFSET ?
            """, (bearing_name, limit, offset))

            files = [dict(row) for row in cursor.fetchall()]

            return {
                "total_count": total_count,
                "offset": offset,
                "limit": limit,
                "files": files
            }
        finally:
            conn.close()

    def get_measurements(
        self,
        bearing_name: str,
        file_number: Optional[int] = None,
        offset: int = 0,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Get measurement data for a bearing."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            if file_number is not None:
                # Get specific file measurements
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM measurements m
                    JOIN measurement_files mf ON m.file_id = mf.file_id
                    JOIN bearings b ON mf.bearing_id = b.bearing_id
                    WHERE b.bearing_name = ? AND mf.file_number = ?
                """, (bearing_name, file_number))
                total_count = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT
                        m.measurement_id,
                        m.hour,
                        m.minute,
                        m.second,
                        m.microsecond,
                        m.horizontal_acceleration,
                        m.vertical_acceleration,
                        mf.file_name,
                        mf.file_number
                    FROM measurements m
                    JOIN measurement_files mf ON m.file_id = mf.file_id
                    JOIN bearings b ON mf.bearing_id = b.bearing_id
                    WHERE b.bearing_name = ? AND mf.file_number = ?
                    ORDER BY m.measurement_id
                    LIMIT ? OFFSET ?
                """, (bearing_name, file_number, limit, offset))
            else:
                # Get all measurements
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM measurements m
                    JOIN measurement_files mf ON m.file_id = mf.file_id
                    JOIN bearings b ON mf.bearing_id = b.bearing_id
                    WHERE b.bearing_name = ?
                """, (bearing_name,))
                total_count = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT
                        m.measurement_id,
                        m.hour,
                        m.minute,
                        m.second,
                        m.microsecond,
                        m.horizontal_acceleration,
                        m.vertical_acceleration,
                        mf.file_name,
                        mf.file_number
                    FROM measurements m
                    JOIN measurement_files mf ON m.file_id = mf.file_id
                    JOIN bearings b ON mf.bearing_id = b.bearing_id
                    WHERE b.bearing_name = ?
                    ORDER BY mf.file_number, m.measurement_id
                    LIMIT ? OFFSET ?
                """, (bearing_name, limit, offset))

            measurements = [dict(row) for row in cursor.fetchall()]

            return {
                "total_count": total_count,
                "offset": offset,
                "limit": limit,
                "measurements": measurements
            }
        finally:
            conn.close()

    def get_file_data_for_analysis(
        self,
        bearing_name: str,
        file_number: int
    ) -> Dict[str, Any]:
        """Get complete file data for analysis (returns all measurements)."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Get all measurements from the file
            cursor.execute("""
                SELECT
                    m.hour,
                    m.minute,
                    m.second,
                    m.microsecond,
                    m.horizontal_acceleration,
                    m.vertical_acceleration
                FROM measurements m
                JOIN measurement_files mf ON m.file_id = mf.file_id
                JOIN bearings b ON mf.bearing_id = b.bearing_id
                WHERE b.bearing_name = ? AND mf.file_number = ?
                ORDER BY m.measurement_id
            """, (bearing_name, file_number))

            rows = cursor.fetchall()

            if not rows:
                return None

            # Convert to lists for easier processing
            data = {
                "bearing_name": bearing_name,
                "file_number": file_number,
                "record_count": len(rows),
                "timestamps": [
                    {
                        "hour": row[0],
                        "minute": row[1],
                        "second": row[2],
                        "microsecond": row[3]
                    }
                    for row in rows
                ],
                "horizontal_acceleration": [row[4] for row in rows],
                "vertical_acceleration": [row[5] for row in rows]
            }

            return data
        finally:
            conn.close()

    def get_bearing_file_statistics(
        self,
        bearing_name: str
    ) -> Dict[str, Any]:
        """Get statistical summary across all files for a bearing."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(DISTINCT mf.file_id) as total_files,
                    SUM(mf.record_count) as total_records,
                    AVG(mf.record_count) as avg_records_per_file,
                    MIN(mf.file_number) as first_file_number,
                    MAX(mf.file_number) as last_file_number
                FROM measurement_files mf
                JOIN bearings b ON mf.bearing_id = b.bearing_id
                WHERE b.bearing_name = ?
            """, (bearing_name,))

            result = dict(cursor.fetchone())
            result['bearing_name'] = bearing_name

            return result
        finally:
            conn.close()

    def search_anomalies(
        self,
        bearing_name: str,
        threshold_h: float = 10.0,
        threshold_v: float = 10.0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for anomalous measurements above threshold."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    m.measurement_id,
                    m.hour,
                    m.minute,
                    m.second,
                    m.microsecond,
                    m.horizontal_acceleration,
                    m.vertical_acceleration,
                    mf.file_name,
                    mf.file_number
                FROM measurements m
                JOIN measurement_files mf ON m.file_id = mf.file_id
                JOIN bearings b ON mf.bearing_id = b.bearing_id
                WHERE b.bearing_name = ?
                  AND (ABS(m.horizontal_acceleration) > ?
                       OR ABS(m.vertical_acceleration) > ?)
                ORDER BY mf.file_number, m.measurement_id
                LIMIT ?
            """, (bearing_name, threshold_h, threshold_v, limit))

            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
