"""
Circular buffer for high-frequency sensor data

This module manages circular buffers for streaming sensor data,
providing time-windowed data access for real-time analysis.
"""
import numpy as np
from collections import deque
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging

from redis_client import redis_client
from database_async import db

logger = logging.getLogger(__name__)


class SensorBuffer:
    """
    Circular buffer for a single sensor

    Stores high-frequency sensor data (25.6 kHz) in memory
    for efficient time-windowed access.
    """

    def __init__(self, sensor_id: int, buffer_size: int = 25600):
        """
        Initialize circular buffer for sensor data

        Args:
            sensor_id: Sensor identifier
            buffer_size: Number of samples to buffer
                       (default: 1 second at 25.6 kHz)
        """
        self.sensor_id = sensor_id
        self.buffer_size = buffer_size
        self.buffer = deque(maxlen=buffer_size)
        self.timestamps = deque(maxlen=buffer_size)
        self.window_start: Optional[datetime] = None
        self.sample_count = 0

    def add_sample(self, timestamp: datetime, h_acc: float, v_acc: float):
        """
        Add a single sample to buffer

        Args:
            timestamp: Sample timestamp
            h_acc: Horizontal acceleration
            v_acc: Vertical acceleration
        """
        self.buffer.append({'h': h_acc, 'v': v_acc})
        self.timestamps.append(timestamp)
        self.sample_count += 1

        if self.window_start is None:
            self.window_start = timestamp

    def add_batch(self, samples: List[Dict]):
        """
        Add multiple samples at once

        Args:
            samples: List of sample dictionaries with
                     'timestamp', 'h_acc', 'v_acc' keys
        """
        for sample in samples:
            self.add_sample(sample['timestamp'], sample['h_acc'], sample['v_acc'])

    def get_window(self, window_seconds: float = 1.0) -> Optional[Dict]:
        """
        Get data for a time window

        Args:
            window_seconds: Window duration in seconds

        Returns:
            Dict with arrays and time range, or None if insufficient data
        """
        if len(self.buffer) == 0:
            return None

        # Calculate cutoff time
        window_end = self.timestamps[-1]
        window_start = window_end - timedelta(seconds=window_seconds)

        # Filter data within window
        window_data = []
        window_timestamps = []

        for ts, data in zip(self.timestamps, self.buffer):
            if ts >= window_start:
                window_data.append(data)
                window_timestamps.append(ts)

        if len(window_data) == 0:
            return None

        # Convert to numpy arrays for efficient processing
        h_array = np.array([d['h'] for d in window_data])
        v_array = np.array([d['v'] for d in window_data])

        return {
            'sensor_id': self.sensor_id,
            'window_start': window_timestamps[0],
            'window_end': window_timestamps[-1],
            'h_data': h_array,
            'v_data': v_array,
            'sample_count': len(window_data)
        }

    def is_ready(self, min_samples: int = 10000) -> bool:
        """
        Check if buffer has enough data for processing

        Args:
            min_samples: Minimum number of samples required

        Returns:
            True if buffer has sufficient data
        """
        return len(self.buffer) >= min_samples

    def clear(self):
        """Clear buffer and reset counters"""
        self.buffer.clear()
        self.timestamps.clear()
        self.window_start = None
        self.sample_count = 0

    def get_stats(self) -> Dict:
        """
        Get buffer statistics

        Returns:
            Dictionary with buffer stats
        """
        return {
            'sensor_id': self.sensor_id,
            'buffer_size': self.buffer_size,
            'current_size': len(self.buffer),
            'sample_count': self.sample_count,
            'window_start': self.window_start.isoformat() if self.window_start else None,
            'latest_timestamp': self.timestamps[-1].isoformat() if self.timestamps else None
        }


class BufferManager:
    """
    Manages buffers for multiple sensors

    Provides thread-safe access to sensor buffers and
    coordinates data persistence to Redis and PostgreSQL.
    """

    def __init__(self):
        self.buffers: Dict[int, SensorBuffer] = {}
        self.lock = asyncio.Lock()

    async def get_buffer(self, sensor_id: int) -> SensorBuffer:
        """
        Get or create buffer for a sensor

        Args:
            sensor_id: Sensor identifier

        Returns:
            SensorBuffer instance
        """
        async with self.lock:
            if sensor_id not in self.buffers:
                self.buffers[sensor_id] = SensorBuffer(sensor_id)
                logger.info(f"Created buffer for sensor {sensor_id}")
            return self.buffers[sensor_id]

    async def add_data(self, sensor_id: int, data: List[Dict]):
        """
        Add data to sensor buffer

        Also stores data in Redis stream for persistence and
        potential recovery.

        Args:
            sensor_id: Sensor identifier
            data: List of data samples
        """
        buffer = await self.get_buffer(sensor_id)
        buffer.add_batch(data)

        # Store in Redis stream for temporary persistence
        for sample in data:
            try:
                await redis_client.add_sensor_data(sensor_id, {
                    'timestamp': sample['timestamp'].isoformat(),
                    'h_acc': str(sample['h_acc']),
                    'v_acc': str(sample['v_acc'])
                })
            except Exception as e:
                logger.error(f"Error storing in Redis stream: {e}")

        logger.debug(f"Added {len(data)} samples to buffer for sensor {sensor_id}")

    async def get_window(self, sensor_id: int, window_seconds: float = 1.0):
        """
        Get time window data from buffer

        Args:
            sensor_id: Sensor identifier
            window_seconds: Window duration in seconds

        Returns:
            Window data dict or None
        """
        buffer = await self.get_buffer(sensor_id)
        return buffer.get_window(window_seconds)

    async def save_to_database(self, sensor_id: int, window_data: Dict):
        """
        Save window data to PostgreSQL

        Converts numpy arrays to database records and performs
        batch insert for efficiency.

        Args:
            sensor_id: Sensor identifier
            window_data: Window data dictionary with h_data, v_data arrays
        """
        if not window_data or window_data['sample_count'] == 0:
            return

        # Prepare data for batch insert
        db_data = []
        sampling_rate = 25600  # Hz

        for i in range(len(window_data['h_data'])):
            # Calculate timestamp based on sampling rate
            time_offset = timedelta(microseconds=i * (1000000 / sampling_rate))
            ts = window_data['window_start'] + time_offset

            db_data.append({
                'timestamp': ts,
                'h_acc': float(window_data['h_data'][i]),
                'v_acc': float(window_data['v_data'][i])
            })

        try:
            await db.insert_sensor_data(sensor_id, db_data)
            logger.debug(
                f"Saved {len(db_data)} samples to database for sensor {sensor_id}"
            )
        except Exception as e:
            logger.error(f"Error saving to database: {e}")

    async def clear_buffer(self, sensor_id: int):
        """
        Clear buffer for a sensor

        Args:
            sensor_id: Sensor identifier
        """
        if sensor_id in self.buffers:
            self.buffers[sensor_id].clear()
            logger.info(f"Cleared buffer for sensor {sensor_id}")

    async def get_all_buffer_stats(self) -> List[Dict]:
        """
        Get statistics for all buffers

        Returns:
            List of buffer statistics
        """
        stats = []
        for sensor_id, buffer in self.buffers.items():
            stats.append(buffer.get_stats())
        return stats

    async def remove_buffer(self, sensor_id: int):
        """
        Remove buffer for a sensor

        Args:
            sensor_id: Sensor identifier
        """
        async with self.lock:
            if sensor_id in self.buffers:
                del self.buffers[sensor_id]
                logger.info(f"Removed buffer for sensor {sensor_id}")

    async def cleanup_old_buffers(self, max_age_minutes: int = 60):
        """
        Remove buffers for sensors that haven't been updated recently

        Args:
            max_age_minutes: Maximum age of buffer in minutes
        """
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)

        async with self.lock:
            sensors_to_remove = []

            for sensor_id, buffer in self.buffers.items():
                if buffer.window_start and buffer.window_start < cutoff_time:
                    sensors_to_remove.append(sensor_id)

            for sensor_id in sensors_to_remove:
                await self.remove_buffer(sensor_id)

            if sensors_to_remove:
                logger.info(
                    f"Cleaned up {len(sensors_to_remove)} old buffers: "
                    f"{sensors_to_remove}"
                )


# Global buffer manager instance
buffer_manager = BufferManager()
