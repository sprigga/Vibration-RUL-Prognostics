"""
WebSocket connection manager for real-time data streaming

This module manages WebSocket connections for broadcasting real-time
sensor data, features, and alerts to connected clients.
"""
from fastapi import WebSocket
from typing import Dict, Set
import json
import logging
from redis_client import redis_client

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket connection manager

    Manages active WebSocket connections and handles broadcasting
    of messages to clients subscribed to specific sensors.
    """

    def __init__(self):
        # sensor_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # websocket -> sensor_id mapping
        self.websocket_sensor_map: Dict[WebSocket, int] = {}

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

    async def broadcast_to_sensor(self, sensor_id: int, message: dict):
        """
        Broadcast message to all connections for a specific sensor

        Args:
            sensor_id: Target sensor ID
            message: Message dictionary to broadcast
        """
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

    async def broadcast_to_all(self, message: dict):
        """
        Broadcast message to all active connections

        Args:
            message: Message dictionary to broadcast
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

    async def broadcast_alert(self, alert: dict):
        """
        Broadcast alert to all connections

        Args:
            alert: Alert dictionary
        """
        message = {
            "type": "alert",
            "data": alert
        }

        await self.broadcast_to_all(message)
        logger.info(f"Broadcast alert to all clients: {alert.get('message', 'N/A')}")

    async def broadcast_feature_update(self, sensor_id: int, features: dict):
        """
        Broadcast feature update to sensor subscribers

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

    def get_connection_count(self, sensor_id: int = None) -> int:
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
