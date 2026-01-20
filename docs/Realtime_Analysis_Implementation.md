# Real-Time Analysis System - Implementation Summary

## Overview

This document summarizes the implementation of a real-time streaming analysis system for the Viberation RUL Prognostics project. The system adds real-time sensor data processing capabilities to the existing batch analysis system.

## What Was Implemented

### ✅ Completed Requirements

1. **Backend Framework (FastAPI)**: The backend was already using FastAPI. Confirmed and enhanced with async capabilities.

2. **Real-Time Analysis API for Sensor Data**: Implemented complete WebSocket and REST API infrastructure for real-time data streaming.

3. **PostgreSQL + Redis + FastAPI Scalability**: Implemented with async PostgreSQL (asyncpg) and Redis (aioredis) for handling high-concurrency access.

4. **Async/Await for I/O**: Applied throughout the new components for database, Redis, and WebSocket operations.

5. **Frontend Real-Time Analysis Page**: Created `RealtimeAnalysis.vue` with live charts, feature displays, and alert panels.

## Architecture Changes

### Backend Components

#### New Files Created:

1. **backend/database_async.py** (405 lines)
   - Async PostgreSQL connection pool using asyncpg
   - Helper methods for sensor data, features, alerts, and sensor management
   - Optimized for concurrent access with connection pooling

2. **backend/redis_client.py** (482 lines)
   - Async Redis client for caching and pub/sub
   - Stream operations for sensor data buffering
   - Feature caching with TTL
   - Connection tracking and alert queuing

3. **backend/websocket_manager.py** (264 lines)
   - WebSocket connection manager for real-time streaming
   - Broadcast capabilities to sensor subscribers
   - Automatic dead connection cleanup
   - Connection statistics and monitoring

4. **backend/buffer_manager.py** (310 lines)
   - Circular buffer for high-frequency sensor data (25.6 kHz)
   - Time-windowed data access for analysis
   - Integration with Redis for temporary persistence
   - Batch database inserts for efficiency

5. **backend/realtime_analyzer.py** (420 lines)
   - Real-time feature extraction engine
   - Continuous analysis loop (10 Hz rate)
   - Time-domain and frequency-domain features
   - Alert detection and broadcasting

6. **scripts/init_postgres.sql** (264 lines)
   - Complete PostgreSQL schema for real-time data
   - Partitioned tables for performance (time-based)
   - Materialized views for common queries
   - Triggers for automatic timestamp updates

#### Modified Files:

1. **backend/main.py** (+244 lines)
   - Added WebSocket endpoints (`/ws/realtime/{sensor_id}`, `/ws/alerts`)
   - Added REST API endpoints for stream control
   - Async startup/shutdown handlers for PostgreSQL and Redis
   - Backward compatible - existing endpoints unchanged

2. **pyproject.toml**
   - Added dependencies: asyncpg, aioredis, websockets, aiofiles, celery, redis

3. **docker-compose.yml**
   - Added PostgreSQL 15 service
   - Added Redis 7.2 service
   - Updated backend service with new environment variables
   - Health checks for all services

4. **.env.example**
   - Configuration template for PostgreSQL, Redis, and real-time settings

### Frontend Components

#### New Files Created:

1. **frontend/src/services/websocket.js** (199 lines)
   - WebSocket client with automatic reconnection
   - Event-based message handling
   - Connection state management
   - Ping/pong for keep-alive

2. **frontend/src/stores/realtime.js** (254 lines)
   - Pinia store for real-time state management
   - Feature data buffers (last 100 points)
   - Alert history and management
   - Connection status tracking

3. **frontend/src/views/RealtimeAnalysis.vue** (346 lines)
   - Real-time monitoring UI with live charts
   - 8 feature display cards (RMS, Kurtosis, Peak, Crest Factor)
   - 4 ECharts line graphs for trends
   - Alert panel with severity indicators
   - Start/Stop controls for streaming

#### Modified Files:

1. **frontend/src/router/index.js**
   - Added route for `/realtime-analysis`

## API Endpoints

### WebSocket Endpoints

- `ws://localhost:8081/ws/realtime/{sensor_id}` - Real-time sensor data stream
- `ws://localhost:8081/ws/alerts` - Global alert stream

### REST API Endpoints

#### Stream Control
- `POST /api/stream/start` - Start streaming for a sensor
- `POST /api/stream/stop` - Stop streaming for a sensor
- `GET /api/stream/status` - Get status of all active streams

#### Real-Time Data
- `GET /api/realtime/features/{sensor_id}` - Get latest features from cache
- `GET /api/sensors` - List all registered sensors
- `GET /api/sensors/{sensor_id}/status` - Get detailed sensor status

#### Alerts
- `GET /api/alerts/active` - Get all active (unacknowledged) alerts
- `POST /api/alerts/acknowledge/{alert_id}` - Acknowledge an alert

## Database Schema

### PostgreSQL Tables

1. **sensors** - Sensor registry
2. **sensor_data** - Time-partitioned table for raw sensor data
3. **realtime_features** - Computed features from analysis
4. **alerts** - Alert records with acknowledgment status
5. **stream_sessions** - WebSocket session tracking
6. **alert_configurations** - Per-sensor alert thresholds

### Materialized Views

1. **v_latest_features** - Most recent features per sensor
2. **v_active_alerts** - Unacknowledged alerts with sensor names
3. **v_sensor_status** - Sensor status with connection counts

## Data Flow

```
┌─────────────┐
│  Sensor     │
│  Hardware   │
└──────┬──────┘
       │ 25.6 kHz data
       ▼
┌─────────────────────────────┐
│  Buffer Manager             │
│  - Circular buffer (1 sec)  │
│  - Redis stream backup      │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Real-Time Analyzer         │
│  - Feature extraction       │
│  - Alert detection          │
│  - 10 Hz processing rate    │
└──────┬──────────────────────┘
       │
       ├──► PostgreSQL (persistent storage)
       ├──► Redis (cache + pub/sub)
       └──► WebSocket (broadcast to clients)
```

## Key Features

### Performance Optimizations

1. **Connection Pooling**: PostgreSQL connection pool (10-50 connections)
2. **Async Processing**: All I/O operations use async/await
3. **Data Partitioning**: Time-based table partitioning for efficient queries
4. **Caching**: Redis for frequently accessed features
5. **Batch Inserts**: Database writes batched for efficiency

### Scalability

1. **Horizontal Scaling**: Multiple FastAPI workers supported
2. **Connection Management**: Automatic cleanup of dead connections
3. **Load Balancing Ready**: Redis for shared state across workers
4. **Resource Limits**: Configurable buffer sizes and connection limits

### Fault Tolerance

1. **Auto-Reconnection**: WebSocket client reconnects with exponential backoff
2. **Graceful Degradation**: System continues without real-time if dependencies unavailable
3. **Backward Compatibility**: All existing batch analysis features preserved

## How to Use

### 1. Start Services

```bash
# Copy environment file
cp .env.example .env

# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### 2. Access Real-Time Analysis

1. Open browser to `http://localhost:5173`
2. Navigate to "即時分析" (Real-time Analysis) page
3. Enter Sensor ID (e.g., 1)
4. Click "開始監控" (Start Monitoring)

### 3. Generate Test Data

```bash
# Run test data generator (if available)
uv run python scripts/test_data_generator.py
```

### 4. Monitor

- Watch real-time features update in UI
- View charts showing RMS, Kurtosis, Peak, and Crest Factor trends
- Receive alerts when thresholds are exceeded

## Testing Checklist

- [ ] PostgreSQL service starts successfully
- [ ] Redis service starts successfully
- [ ] Backend connects to PostgreSQL and Redis
- [ ] WebSocket endpoint accepts connections
- [ ] Frontend connects to WebSocket
- [ ] Features are calculated and displayed
- [ ] Charts update in real-time
- [ ] Alerts are generated when thresholds exceeded
- [ ] Reconnection works after disconnect
- [ ] Multiple concurrent users supported

## Next Steps (Future Enhancements)

1. **Sensor Data Ingestion API**: Create endpoint to receive data from physical sensors
2. **Background Tasks**: Implement Celery for long-running analysis tasks
3. **Historical Trends**: Add API to query historical feature data
4. **Advanced Analytics**: Machine learning models for RUL prediction
5. **Data Export**: CSV/JSON export for real-time data
6. **User Authentication**: Multi-user support with permissions
7. **Dashboard Widgets**: Configurable dashboard layouts

## Backward Compatibility

- ✅ All existing API endpoints preserved
- ✅ SQLite databases remain functional for historical data
- ✅ Batch analysis continues to work unchanged
- ✅ New real-time features are additive only
- ✅ Configuration flag (`ENABLE_REALTIME`) to disable if needed

## File Locations

### Backend
- `/home/ubuntu/Viberation-RUL-Prognostics/backend/database_async.py`
- `/home/ubuntu/Viberation-RUL-Prognostics/backend/redis_client.py`
- `/home/ubuntu/Viberation-RUL-Prognostics/backend/websocket_manager.py`
- `/home/ubuntu/Viberation-RUL-Prognostics/backend/buffer_manager.py`
- `/home/ubuntu/Viberation-RUL-Prognostics/backend/realtime_analyzer.py`
- `/home/ubuntu/Viberation-RUL-Prognostics/backend/main.py` (modified)

### Frontend
- `/home/ubuntu/Viberation-RUL-Prognostics/frontend/src/services/websocket.js`
- `/home/ubuntu/Viberation-RUL-Prognostics/frontend/src/stores/realtime.js`
- `/home/ubuntu/Viberation-RUL-Prognostics/frontend/src/views/RealtimeAnalysis.vue`
- `/home/ubuntu/Viberation-RUL-Prognostics/frontend/src/router/index.js` (modified)

### Configuration
- `/home/ubuntu/Viberation-RUL-Prognostics/docker-compose.yml` (modified)
- `/home/ubuntu/Viberation-RUL-Prognostics/pyproject.toml` (modified)
- `/home/ubuntu/Viberation-RUL-Prognostics/.env.example` (new)
- `/home/ubuntu/Viberation-RUL-Prognostics/scripts/init_postgres.sql` (new)

## Performance Targets

- WebSocket message delivery: < 50ms
- Feature calculation: < 100ms per 1-second window
- Alert detection: < 200ms
- Database writes: < 500ms (batch)
- API response: < 100ms

## Resource Requirements

### Minimum
- RAM: 4 GB
- CPU: 2 cores
- Disk: 10 GB

### Recommended
- RAM: 8 GB
- CPU: 4 cores
- Disk: 20 GB SSD

## Support

For issues or questions, refer to:
- Main project README
- API documentation (auto-generated by FastAPI at `/docs`)
- This implementation document

---

**Implementation Date**: 2026-01-20
**Version**: 2.0.0
**Status**: ✅ Complete - Ready for Testing
