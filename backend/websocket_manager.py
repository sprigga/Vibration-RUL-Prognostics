"""
WebSocket connection manager for real-time data streaming

This module manages WebSocket connections for broadcasting real-time
sensor data, features, and alerts to connected clients.

Now includes Redis Pub/Sub integration for multi-instance scaling.
"""
# 原始寫法: from fastapi import WebSocket
from fastapi import WebSocket
from typing import Dict, Set, Optional
import json
import logging
import asyncio
from redis_client import redis_client

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket connection manager with Redis Pub/Sub support

    Manages active WebSocket connections and handles broadcasting
    of messages to clients subscribed to specific sensors.

    Redis Pub/Sub channels:
    - sensor:{sensor_id}:features  - Feature updates
    - sensor:{sensor_id}:data      - Real-time sensor data
    - alerts:all                   - Global alerts
    - broadcast:all                - Global broadcast
    """

    # Redis 頻道命名常數
    CHANNEL_FEATURE_PREFIX = "sensor:"
    CHANNEL_FEATURE_SUFFIX = ":features"
    CHANNEL_DATA_SUFFIX = ":data"
    CHANNEL_ALERTS = "alerts:all"
    CHANNEL_BROADCAST = "broadcast:all"

    def __init__(self, use_redis_pubsub: bool = True):
        # sensor_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # websocket -> sensor_id mapping
        self.websocket_sensor_map: Dict[WebSocket, int] = {}

        # Redis Pub/Sub 相關
        self.use_redis_pubsub = use_redis_pubsub
        self._pubsub_task = None
        self._pubsub = None
        self._running = False

        # 訂閱的頻道集合
        self._subscribed_channels: Set[str] = set()

    # ==================== Redis Pub/Sub Methods ====================

    async def start_pubsub_listener(self):
        """
        啟動 Redis Pub/Sub 監聽器

        在背景持續監聽 Redis 頻道訊息，
        收到訊息後廣播給本地 WebSocket 客戶端
        """
        if not self.use_redis_pubsub or self._running:
            return

        self._running = True
        self._pubsub_task = asyncio.create_task(self._pubsub_listener_loop())
        logger.info("Redis Pub/Sub listener started")

    async def stop_pubsub_listener(self):
        """停止 Redis Pub/Sub 監聽器"""
        self._running = False

        if self._pubsub:
            await self._pubsub.unsubscribe(*list(self._subscribed_channels))
            self._subscribed_channels.clear()

        if self._pubsub_task:
            self._pubsub_task.cancel()
            try:
                await self._pubsub_task
            except asyncio.CancelledError:
                pass
            self._pubsub_task = None

        logger.info("Redis Pub/Sub listener stopped")

    async def _pubsub_listener_loop(self):
        """
        Pub/Sub 監聽循環

        持續從 Redis 接收訊息並廣播給本地 WebSocket 客戶端
        """
        try:
            # 訂閱全域頻道
            await self._subscribe_to_global_channels()

            while self._running:
                if self._pubsub is None:
                    await asyncio.sleep(0.1)
                    continue

                try:
                    # 等待訊息，設定超時以避免阻塞
                    message = await asyncio.wait_for(
                        self._pubsub.get_message(ignore_subscribe_messages=True),
                        timeout=1.0
                    )

                    if message:
                        await self._handle_pubsub_message(message)

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in pubsub listener: {e}")
                    await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("PubSub listener cancelled")
        except Exception as e:
            logger.error(f"PubSub listener error: {e}")

    async def _subscribe_to_global_channels(self):
        """訂閱全域頻道（警報和廣播）"""
        if not self.use_redis_pubsub or not redis_client._is_connected:
            return

        try:
            # 訂閱全域廣播和警報頻道
            self._pubsub = await redis_client.subscribe(self.CHANNEL_BROADCAST)
            self._subscribed_channels.add(self.CHANNEL_BROADCAST)
            self._subscribed_channels.add(self.CHANNEL_ALERTS)
            logger.info(f"Subscribed to global channels: {self.CHANNEL_BROADCAST}, {self.CHANNEL_ALERTS}")
        except Exception as e:
            logger.error(f"Error subscribing to global channels: {e}")

    async def _handle_pubsub_message(self, message: dict):
        """
        處理從 Redis 接收的 Pub/Sub 訊息

        Args:
            message: Redis 訊息字典，包含 type, channel, data
        """
        try:
            if message.get('type') == 'message':
                channel = message.get('channel', '')
                data_str = message.get('data', '')

                # 解析 JSON 數據
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in pubsub message: {data_str}")
                    return

                # 根據頻道類型處理
                if channel == self.CHANNEL_BROADCAST:
                    # 全域廣播
                    await self.broadcast_to_all(data)
                elif channel == self.CHANNEL_ALERTS:
                    # 警報廣播
                    await self.broadcast_alert(data)
                elif channel.startswith(self.CHANNEL_FEATURE_PREFIX):
                    # 感測器特定訊息
                    # 格式: sensor:{sensor_id}:features
                    try:
                        sensor_id = int(
                            channel.split(':')[1]
                        )
                        msg_type = channel.split(':')[2]

                        if msg_type == 'features':
                            await self.broadcast_feature_update(sensor_id, data)
                        elif msg_type == 'data':
                            await self._broadcast_sensor_data(sensor_id, data)
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Invalid channel format: {channel}")

        except Exception as e:
            logger.error(f"Error handling pubsub message: {e}")

    async def subscribe_sensor_channels(self, sensor_id: int):
        """
        當有客戶端連接感測器時，訂閱對應的 Redis 頻道

        Args:
            sensor_id: 感測器 ID
        """
        if not self.use_redis_pubsub:
            return

        feature_channel = f"{self.CHANNEL_FEATURE_PREFIX}{sensor_id}{self.CHANNEL_FEATURE_SUFFIX}"
        data_channel = f"{self.CHANNEL_FEATURE_PREFIX}{sensor_id}{self.CHANNEL_DATA_SUFFIX}"

        # 記錄需要訂閱的頻道（實際訂閱在 pubsub 監聽中處理）
        self._subscribed_channels.add(feature_channel)
        self._subscribed_channels.add(data_channel)

        logger.debug(f"Subscribed to Redis channels for sensor {sensor_id}")

    async def publish_to_channel(self, channel: str, message: dict):
        """
        發布訊息到 Redis 頻道

        Args:
            channel: 頻道名稱
            message: 訊息字典
        """
        if not self.use_redis_pubsub:
            return

        try:
            await redis_client.publish(channel, message)
        except Exception as e:
            logger.error(f"Error publishing to channel {channel}: {e}")

    async def connect(self, websocket: WebSocket, sensor_id: int):
        """
        Connect a WebSocket to a sensor

        Args:
            websocket: WebSocket connection object
            sensor_id: Sensor to subscribe to (use 0 for global)
        """
        await websocket.accept()

        if sensor_id not in self.active_connections:
            self.active_connections[sensor_id] = set()

        self.active_connections[sensor_id].add(websocket)
        self.websocket_sensor_map[websocket] = sensor_id

        # Track in Redis
        connection_id = f"ws_{id(websocket)}_{sensor_id}"
        await redis_client.add_active_connection(connection_id)

        # Update sensor status in Redis
        if sensor_id != 0:  # Don't update status for global subscriptions
            await redis_client.update_sensor_status(sensor_id, {
                "streaming": "true",
                "connections": str(len(self.active_connections[sensor_id]))
            })

        logger.info(
            f"WebSocket connected for sensor {sensor_id} "
            f"(total connections: {len(self.websocket_sensor_map)})"
        )

    async def disconnect(self, websocket: WebSocket):
        """
        Disconnect a WebSocket

        Args:
            websocket: WebSocket connection to disconnect
        """
        sensor_id = self.websocket_sensor_map.get(websocket)

        if sensor_id and sensor_id in self.active_connections:
            self.active_connections[sensor_id].discard(websocket)

            # Remove empty sensor entries
            if len(self.active_connections[sensor_id]) == 0:
                del self.active_connections[sensor_id]

        if websocket in self.websocket_sensor_map:
            del self.websocket_sensor_map[websocket]

        # Remove from Redis
        connection_id = f"ws_{id(websocket)}_{sensor_id}"
        await redis_client.remove_active_connection(connection_id)

        # Update sensor status
        if sensor_id and sensor_id != 0 and sensor_id in self.active_connections:
            await redis_client.update_sensor_status(sensor_id, {
                "streaming": "true",
                "connections": str(len(self.active_connections[sensor_id]))
            })
        elif sensor_id and sensor_id != 0:
            # No more connections for this sensor
            await redis_client.update_sensor_status(sensor_id, {
                "streaming": "false",
                "connections": "0"
            })

        logger.info(
            f"WebSocket disconnected for sensor {sensor_id} "
            f"(total connections: {len(self.websocket_sensor_map)})"
        )

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send message to a specific WebSocket

        Args:
            message: Message dictionary to send
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            await self.disconnect(websocket)

    async def broadcast_to_sensor(self, sensor_id: int, message: dict, use_redis: bool = True):
        """
        Broadcast message to all connections for a specific sensor

        原始邏輯: 僅廣播到本地 WebSocket 連線
        新增功能: 可選擇透過 Redis Pub/Sub 發布到其他實例

        Args:
            sensor_id: Target sensor ID
            message: Message dictionary to broadcast
            use_redis: 是否透過 Redis 發布（預設 True）
        """
        # 本地廣播
        if sensor_id not in self.active_connections:
            return

        # Remove disconnected websockets
        dead_connections = []
        for websocket in self.active_connections[sensor_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error for sensor {sensor_id}: {e}")
                dead_connections.append(websocket)

        # Clean up dead connections
        for ws in dead_connections:
            await self.disconnect(ws)

        if dead_connections:
            logger.warning(
                f"Removed {len(dead_connections)} dead connections "
                f"for sensor {sensor_id}"
            )

        # 透過 Redis 發布到其他實例
        if use_redis and self.use_redis_pubsub:
            # 根據訊息類型決定頻道
            msg_type = message.get("type", "")
            if msg_type == "feature_update":
                channel = f"{self.CHANNEL_FEATURE_PREFIX}{sensor_id}{self.CHANNEL_FEATURE_SUFFIX}"
            elif msg_type == "sensor_data":
                channel = f"{self.CHANNEL_FEATURE_PREFIX}{sensor_id}{self.CHANNEL_DATA_SUFFIX}"
            else:
                return  # 其他類型不透過 Redis 發布

            await self.publish_to_channel(channel, message)

    async def broadcast_to_all(self, message: dict, use_redis: bool = True):
        """
        Broadcast message to all active connections

        原始邏輯: 僅廣播到本地 WebSocket 連線
        新增功能: 可選擇透過 Redis Pub/Sub 發布到其他實例

        Args:
            message: Message dictionary to broadcast
            use_redis: 是否透過 Redis 發布（預設 True）
        """
        dead_connections = []

        for sensor_id, connections in self.active_connections.items():
            for websocket in connections:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Broadcast error: {e}")
                    dead_connections.append(websocket)

        # Clean up dead connections
        for ws in dead_connections:
            await self.disconnect(ws)

        if dead_connections:
            logger.warning(f"Removed {len(dead_connections)} dead connections")

        # 透過 Redis 發布到其他實例
        if use_redis and self.use_redis_pubsub:
            await self.publish_to_channel(self.CHANNEL_BROADCAST, message)

    async def broadcast_alert(self, alert: dict):
        """
        Broadcast alert to all connections

        原始邏輯: 僅廣播到本地 WebSocket 連線
        新增功能: 透過 Redis Pub/Sub 發布到其他實例

        Args:
            alert: Alert dictionary
        """
        message = {
            "type": "alert",
            "data": alert
        }

        await self.broadcast_to_all(message)
        # 同時發布到警報頻道
        if self.use_redis_pubsub:
            await self.publish_to_channel(self.CHANNEL_ALERTS, alert)

        logger.info(f"Broadcast alert to all clients: {alert.get('message', 'N/A')}")

    async def _broadcast_sensor_data(self, sensor_id: int, data: dict):
        """
        廣播感測器數據到訂閱該感測器的客戶端

        Args:
            sensor_id: 感測器 ID
            data: 數據字典
        """
        message = {
            "type": "sensor_data",
            "sensor_id": sensor_id,
            "data": data
        }
        await self.broadcast_to_sensor(sensor_id, message, use_redis=False)

    async def broadcast_feature_update(self, sensor_id: int, features: dict):
        """
        Broadcast feature update to sensor subscribers

        原始邏輯: 僅廣播到本地 WebSocket 連線
        新增功能: 透過 Redis Pub/Sub 發布到其他實例

        Args:
            sensor_id: Sensor ID
            features: Feature dictionary
        """
        message = {
            "type": "feature_update",
            "sensor_id": sensor_id,
            "data": features
        }

        # 調試日誌
        conn_count = self.get_connection_count(sensor_id)
        logger.info(
            f"Broadcasting feature_update for sensor {sensor_id} "
            f"to {conn_count} connections"
        )

        await self.broadcast_to_sensor(sensor_id, message)

    def get_connection_count(self, sensor_id: Optional[int] = None) -> int:
        """
        Get number of active connections

        Args:
            sensor_id: Optional sensor ID to count connections for

        Returns:
            Number of active connections
        """
        if sensor_id:
            return len(self.active_connections.get(sensor_id, set()))

        return sum(len(conns) for conns in self.active_connections.values())

    def get_active_sensors(self) -> list:
        """
        Get list of sensors with active connections

        Returns:
            List of sensor IDs with active connections
        """
        return list(self.active_connections.keys())

    def get_connection_info(self) -> dict:
        """
        Get connection statistics

        Returns:
            Dictionary with connection stats
        """
        return {
            "total_connections": len(self.websocket_sensor_map),
            "active_sensors": len(self.active_connections),
            "sensor_connections": {
                sensor_id: len(connections)
                for sensor_id, connections in self.active_connections.items()
            }
        }


# Global manager instance
manager = ConnectionManager()
