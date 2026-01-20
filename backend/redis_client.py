"""
Async Redis client for caching and pub/sub

This module provides an asynchronous interface to Redis for:
- Streaming sensor data buffering
- Feature result caching
- Pub/Sub messaging
- Connection tracking
- Alert queuing
"""
# 原始寫法: import aioredis
# aioredis 已整合至 redis 套件中，改用 redis.asyncio
import redis.asyncio as aioredis
import json
import os
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# Redis URL from environment or default
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://:redis_pass@localhost:6379/0"
)


class RedisClient:
    """
    Async Redis client wrapper

    Provides high-level methods for common Redis operations
    used in real-time sensor data processing.
    """

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self._is_connected = False

    async def connect(self):
        """Initialize Redis connection"""
        if self._is_connected:
            logger.warning("Redis already connected")
            return

        try:
            self.redis = await aioredis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            self._is_connected = True
            logger.info(f"Redis connected: {REDIS_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self._is_connected = False
            logger.info("Redis connection closed")

    # ==================== Stream Operations ====================

    async def add_sensor_data(self, sensor_id: int, data: Dict):
        """
        Add data point to sensor stream

        Uses Redis Streams for time-series data storage with automatic
        cleanup after 24 hours.

        Args:
            sensor_id: Sensor identifier
            data: Data dictionary with timestamp, h_acc, v_acc
        """
        if not self._is_connected:
            logger.warning("Redis not connected, skipping stream add")
            return

        try:
            key = f"stream:sensor:{sensor_id}"
            # Convert dict to Redis stream format
            await self.redis.xadd(key, data)

            # Auto-cleanup after 24 hours
            await self.redis.expire(key, 86400)
        except Exception as e:
            logger.error(f"Error adding to stream: {e}")

    async def get_sensor_stream(self, sensor_id: int, count: int = 100) -> List[Dict]:
        """
        Read recent data from sensor stream

        Args:
            sensor_id: Sensor identifier
            count: Number of records to read

        Returns:
            List of stream entries
        """
        if not self._is_connected:
            return []

        try:
            key = f"stream:sensor:{sensor_id}"
            # Read from beginning of stream
            return await self.redis.xrange(key, count=count)
        except Exception as e:
            logger.error(f"Error reading stream: {e}")
            return []

    async def trim_sensor_stream(self, sensor_id: int, max_length: int = 10000):
        """
        Trim sensor stream to keep only recent data

        Args:
            sensor_id: Sensor identifier
            max_length: Maximum number of entries to keep
        """
        if not self._is_connected:
            return

        try:
            key = f"stream:sensor:{sensor_id}"
            await self.redis.xtrim(key, maxlen=max_length)
        except Exception as e:
            logger.error(f"Error trimming stream: {e}")

    # ==================== Cache Operations ====================

    async def cache_features(self, sensor_id: int, features: Dict, ttl: int = 300):
        """
        Cache latest computed features

        Args:
            sensor_id: Sensor identifier
            features: Feature dictionary
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        if not self._is_connected:
            return

        try:
            key = f"features:sensor:{sensor_id}:latest"

            # Convert all values to strings for Redis
            features_str = {k: str(v) if v is not None else "" for k, v in features.items()}

            await self.redis.hset(key, mapping=features_str)
            await self.redis.expire(key, ttl)

            logger.debug(f"Cached features for sensor {sensor_id}")
        except Exception as e:
            logger.error(f"Error caching features: {e}")

    async def get_cached_features(self, sensor_id: int) -> Optional[Dict]:
        """
        Get cached features for a sensor

        Args:
            sensor_id: Sensor identifier

        Returns:
            Cached feature dictionary or None
        """
        if not self._is_connected:
            return None

        try:
            key = f"features:sensor:{sensor_id}:latest"
            data = await self.redis.hgetall(key)

            if not data:
                return None

            # Convert strings back to appropriate types
            result = {}
            for k, v in data.items():
                try:
                    # Try to convert to float
                    result[k] = float(v)
                except (ValueError, TypeError):
                    # Keep as string if not a number
                    result[k] = v

            return result
        except Exception as e:
            logger.error(f"Error getting cached features: {e}")
            return None

    # ==================== Pub/Sub Operations ====================

    async def publish(self, channel: str, message: Dict):
        """
        Publish message to a channel

        Args:
            channel: Channel name
            message: Message dictionary (will be JSON serialized)
        """
        if not self._is_connected:
            return

        try:
            await self.redis.publish(channel, json.dumps(message))
            logger.debug(f"Published to channel {channel}")
        except Exception as e:
            logger.error(f"Error publishing message: {e}")

    async def subscribe(self, channel: str):
        """
        Subscribe to a channel

        Args:
            channel: Channel name

        Returns:
            PubSub object for receiving messages
        """
        if not self._is_connected:
            raise RuntimeError("Redis not connected")

        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(channel)
            logger.info(f"Subscribed to channel {channel}")
            return pubsub
        except Exception as e:
            logger.error(f"Error subscribing to channel: {e}")
            raise

    # ==================== Connection Management ====================

    async def add_active_connection(self, connection_id: str):
        """
        Track an active WebSocket connection

        Args:
            connection_id: Unique connection identifier
        """
        if not self._is_connected:
            return

        try:
            await self.redis.sadd("connections:active", connection_id)
        except Exception as e:
            logger.error(f"Error adding active connection: {e}")

    async def remove_active_connection(self, connection_id: str):
        """
        Remove a WebSocket connection from tracking

        Args:
            connection_id: Connection identifier
        """
        if not self._is_connected:
            return

        try:
            await self.redis.srem("connections:active", connection_id)
        except Exception as e:
            logger.error(f"Error removing active connection: {e}")

    async def get_active_connections(self) -> List[str]:
        """
        Get all active connection IDs

        Returns:
            List of connection IDs
        """
        if not self._is_connected:
            return []

        try:
            members = await self.redis.smembers("connections:active")
            return list(members) if members else []
        except Exception as e:
            logger.error(f"Error getting active connections: {e}")
            return []

    async def get_active_connection_count(self) -> int:
        """
        Get count of active connections

        Returns:
            Number of active connections
        """
        if not self._is_connected:
            return 0

        try:
            return await self.redis.scard("connections:active")
        except Exception as e:
            logger.error(f"Error getting connection count: {e}")
            return 0

    # ==================== Sensor Status ====================

    async def update_sensor_status(self, sensor_id: int, status: Dict):
        """
        Update real-time sensor status

        Args:
            sensor_id: Sensor identifier
            status: Status dictionary
        """
        if not self._is_connected:
            return

        try:
            key = f"status:sensor:{sensor_id}"

            # Convert all values to strings
            status_str = {k: str(v) if v is not None else "" for k, v in status.items()}

            await self.redis.hset(key, mapping=status_str)
            await self.redis.expire(key, 60)  # 1 minute TTL

            logger.debug(f"Updated status for sensor {sensor_id}")
        except Exception as e:
            logger.error(f"Error updating sensor status: {e}")

    async def get_sensor_status(self, sensor_id: int) -> Optional[Dict]:
        """
        Get sensor status

        Args:
            sensor_id: Sensor identifier

        Returns:
            Status dictionary or None
        """
        if not self._is_connected:
            return None

        try:
            key = f"status:sensor:{sensor_id}"
            return await self.redis.hgetall(key)
        except Exception as e:
            logger.error(f"Error getting sensor status: {e}")
            return None

    # ==================== Alert Queue ====================

    async def push_alert(self, alert: Dict):
        """
        Add alert to processing queue

        Args:
            alert: Alert dictionary
        """
        if not self._is_connected:
            return

        try:
            await self.redis.lpush("alerts:queue", json.dumps(alert))
            logger.debug(f"Added alert to queue")
        except Exception as e:
            logger.error(f"Error pushing alert: {e}")

    async def pop_alert(self) -> Optional[Dict]:
        """
        Get alert from queue

        Returns:
            Alert dictionary or None
        """
        if not self._is_connected:
            return None

        try:
            alert = await self.redis.rpop("alerts:queue")
            return json.loads(alert) if alert else None
        except Exception as e:
            logger.error(f"Error popping alert: {e}")
            return None

    async def get_alert_queue_length(self) -> int:
        """
        Get number of alerts in queue

        Returns:
            Queue length
        """
        if not self._is_connected:
            return 0

        try:
            return await self.redis.llen("alerts:queue")
        except Exception as e:
            logger.error(f"Error getting queue length: {e}")
            return 0

    # ==================== Utility Methods ====================

    async def delete_pattern(self, pattern: str):
        """
        Delete all keys matching a pattern

        Args:
            pattern: Key pattern (e.g., "features:*")
        """
        if not self._is_connected:
            return

        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                await self.redis.delete(*keys)
                logger.debug(f"Deleted {len(keys)} keys matching {pattern}")
        except Exception as e:
            logger.error(f"Error deleting pattern: {e}")

    async def get_info(self) -> Dict:
        """
        Get Redis server information

        Returns:
            Server info dictionary
        """
        if not self._is_connected:
            return {}

        try:
            info = await self.redis.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0),
                'redis_version': info.get('redis_version', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error getting Redis info: {e}")
            return {}

    async def ping(self) -> bool:
        """
        Check if Redis is responsive

        Returns:
            True if responsive, False otherwise
        """
        if not self._is_connected:
            return False

        try:
            result = await self.redis.ping()
            return result
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()
