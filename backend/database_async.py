"""
Async PostgreSQL database layer using asyncpg

This module provides an asynchronous interface to PostgreSQL database
for real-time sensor data processing and analysis.

Original synchronous SQLite database (database.py) is preserved for
backward compatibility with existing batch analysis functionality.
"""
import asyncpg
from contextlib import asynccontextmanager
from typing import Optional, Dict, List, Any
import os
import logging

logger = logging.getLogger(__name__)

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL_POSTGRESQL",
    "postgresql://vibration:vibration_pass@localhost:5432/vibration_analysis"
)


class AsyncDatabase:
    """
    Async PostgreSQL database connection pool manager

    Provides connection pooling, query execution, and helper methods
    for common database operations.
    """

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._is_connected = False

    async def init_pool(self):
        """
        Initialize asyncpg connection pool

        Creates a pool of connections to PostgreSQL database with
        optimized settings for concurrent access.
        """
        if self._is_connected:
            logger.warning("Database pool already initialized")
            return

        try:
            self.pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=10,          # Minimum number of connections
                max_size=50,          # Maximum number of connections
                max_queries=50000,    # Queries per connection before recycling
                max_inactive_connection_lifetime=300.0,  # 5 minutes
                command_timeout=60    # Query timeout in seconds
            )
            self._is_connected = True
            logger.info(f"PostgreSQL connection pool initialized: {DATABASE_URL}")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise

    async def close_pool(self):
        """Close all connections in the pool"""
        if self.pool:
            await self.pool.close()
            self._is_connected = False
            logger.info("PostgreSQL connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """
        Get a connection from the pool

        Yields:
            asyncpg.Connection: Database connection
        """
        if not self._is_connected:
            raise RuntimeError("Database pool not initialized. Call init_pool() first.")

        async with self.pool.acquire() as connection:
            yield connection

    async def execute(self, query: str, *args) -> str:
        """
        Execute a SQL query that doesn't return data (INSERT, UPDATE, DELETE)

        Args:
            query: SQL query with $1, $2, etc. parameter placeholders
            *args: Query parameters

        Returns:
            str: Execution result status
        """
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[Dict]:
        """
        Fetch multiple rows from a query

        Args:
            query: SQL SELECT query
            *args: Query parameters

        Returns:
            List[Dict]: List of rows as dictionaries
        """
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def fetchone(self, query: str, *args) -> Optional[Dict]:
        """
        Fetch a single row from a query

        Args:
            query: SQL SELECT query
            *args: Query parameters

        Returns:
            Optional[Dict]: Row as dictionary, or None if not found
        """
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def fetchval(self, query: str, *args, column: int = 0):
        """
        Fetch a single value from a query

        Args:
            query: SQL SELECT query
            *args: Query parameters
            column: Column index to return (default: 0)

        Returns:
            Single value from the query result
        """
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args, column=column)

    async def insert_sensor_data(self, sensor_id: int, data: List[Dict]):
        """
        Batch insert sensor data into PostgreSQL

        Args:
            sensor_id: Sensor identifier
            data: List of data points with 'timestamp', 'h_acc', 'v_acc' keys
        """
        query = """
            INSERT INTO sensor_data (sensor_id, timestamp, horizontal_acceleration, vertical_acceleration)
            VALUES ($1, $2, $3, $4)
        """

        # Prepare data for batch insert
        records = [
            (sensor_id, d['timestamp'], d['h_acc'], d['v_acc'])
            for d in data
        ]

        async with self.get_connection() as conn:
            async with conn.transaction():
                await conn.executemany(query, records)

        logger.debug(f"Inserted {len(data)} sensor data points for sensor {sensor_id}")

    async def insert_features(self, sensor_id: int, features: Dict):
        """
        Insert computed features into PostgreSQL

        Args:
            sensor_id: Sensor identifier
            features: Dictionary of computed features
        """
        query = """
            INSERT INTO realtime_features
            (sensor_id, window_start, window_end, rms_h, rms_v, peak_h, peak_v,
             kurtosis_h, kurtosis_v, crest_factor_h, crest_factor_v,
             fm0_h, fm0_v, dominant_freq_h, dominant_freq_v)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
        """

        try:
            await self.execute(
                query,
                sensor_id,
                features['window_start'],
                features['window_end'],
                features.get('rms_h'),
                features.get('rms_v'),
                features.get('peak_h'),
                features.get('peak_v'),
                features.get('kurtosis_h'),
                features.get('kurtosis_v'),
                features.get('crest_factor_h'),
                features.get('crest_factor_v'),
                features.get('fm0_h'),
                features.get('fm0_v'),
                features.get('dominant_freq_h'),
                features.get('dominant_freq_v')
            )
            logger.debug(f"Inserted features for sensor {sensor_id}")
        except Exception as e:
            logger.error(f"Error inserting features: {e}")
            raise

    async def get_latest_features(self, sensor_id: int) -> Optional[Dict]:
        """
        Get the most recent features for a sensor

        Args:
            sensor_id: Sensor identifier

        Returns:
            Latest feature dictionary or None
        """
        # Try the view first (more efficient)
        query = """
            SELECT * FROM v_latest_features
            WHERE sensor_id = $1
        """

        return await self.fetchone(query, sensor_id)

    async def get_active_alerts(self, limit: int = 100) -> List[Dict]:
        """
        Get all active (unacknowledged) alerts

        Args:
            limit: Maximum number of alerts to return

        Returns:
            List of active alerts
        """
        query = """
            SELECT * FROM v_active_alerts
            ORDER BY created_at DESC
            LIMIT $1
        """

        return await self.fetch(query, limit)

    async def create_alert(self, alert: Dict) -> int:
        """
        Create a new alert

        Args:
            alert: Alert dictionary with alert details

        Returns:
            alert_id: ID of created alert
        """
        query = """
            INSERT INTO alerts
            (sensor_id, alert_type, severity, message, feature_name, current_value, threshold_value)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING alert_id
        """

        result = await self.fetchone(
            query,
            alert['sensor_id'],
            alert['alert_type'],
            alert['severity'],
            alert['message'],
            alert.get('feature_name'),
            alert.get('current_value'),
            alert.get('threshold_value')
        )

        return result['alert_id'] if result else None

    async def acknowledge_alert(self, alert_id: int, acknowledged_by: str) -> bool:
        """
        Acknowledge an alert

        Args:
            alert_id: Alert identifier
            acknowledged_by: User who acknowledged the alert

        Returns:
            True if successful, False otherwise
        """
        query = """
            UPDATE alerts
            SET is_acknowledged = true,
                acknowledged_by = $2,
                acknowledged_at = NOW()
            WHERE alert_id = $1
        """

        result = await self.execute(query, alert_id, acknowledged_by)
        return "UPDATE 1" in result

    async def get_alert_configurations(self, sensor_id: int) -> List[Dict]:
        """
        Get alert configurations for a sensor

        Args:
            sensor_id: Sensor identifier

        Returns:
            List of alert configurations
        """
        query = """
            SELECT * FROM alert_configurations
            WHERE sensor_id = $1 AND enabled = true
        """

        return await self.fetch(query, sensor_id)

    async def register_sensor(self, sensor_id: int, sensor_name: str,
                             sensor_type: str, sampling_rate: float) -> bool:
        """
        Register a new sensor or update existing one

        Args:
            sensor_id: Sensor identifier
            sensor_name: Sensor name
            sensor_type: Type of sensor (e.g., 'accelerometer')
            sampling_rate: Sampling rate in Hz

        Returns:
            True if successful
        """
        query = """
            INSERT INTO sensors (sensor_id, sensor_name, sensor_type, sampling_rate, is_active)
            VALUES ($1, $2, $3, $4, true)
            ON CONFLICT (sensor_id) DO UPDATE
            SET is_active = true,
                sensor_name = EXCLUDED.sensor_name,
                sensor_type = EXCLUDED.sensor_type,
                sampling_rate = EXCLUDED.sampling_rate
        """

        result = await self.execute(query, sensor_id, sensor_name, sensor_type, sampling_rate)
        return "INSERT" in result or "UPDATE" in result

    async def get_sensor_status(self, sensor_id: int) -> Optional[Dict]:
        """
        Get sensor status and statistics

        Args:
            sensor_id: Sensor identifier

        Returns:
            Sensor status dictionary
        """
        query = """
            SELECT * FROM v_sensor_status
            WHERE sensor_id = $1
        """

        return await self.fetchone(query, sensor_id)

    async def stream_session_create(self, sensor_id: int, client_id: str) -> str:
        """
        Create a new WebSocket streaming session

        Args:
            sensor_id: Sensor identifier
            client_id: Client identifier (IP or session ID)

        Returns:
            session_id: UUID of created session
        """
        query = """
            INSERT INTO stream_sessions (sensor_id, client_id)
            VALUES ($1, $2)
            RETURNING session_id
        """

        result = await self.fetchone(query, sensor_id, client_id)
        return result['session_id'] if result else None

    async def stream_session_update(self, session_id: str, status: str,
                                    bytes_received: int = None,
                                    data_points: int = None):
        """
        Update a streaming session

        Args:
            session_id: Session UUID
            status: New status ('active', 'closed', 'error')
            bytes_received: Optional bytes received count
            data_points: Optional data points count
        """
        updates = ["status = $2"]
        params = [status]
        param_count = 2

        if bytes_received is not None:
            param_count += 1
            updates.append(f"bytes_received = ${param_count}")
            params.append(bytes_received)

        if data_points is not None:
            param_count += 1
            updates.append(f"data_points_received = ${param_count}")
            params.append(data_points)

        if status in ('closed', 'error'):
            updates.append("disconnected_at = NOW()")

        query = f"""
            UPDATE stream_sessions
            SET {', '.join(updates)}
            WHERE session_id = $1
        """

        await self.execute(query, session_id, *params)


# Global database instance
db = AsyncDatabase()
