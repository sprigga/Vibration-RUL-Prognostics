# 即時分析與監控機制

## 概述

本專案實現了完整的即時振動數據分析與監控系統，能夠在 25.6 kHz 高採樣率下實時處理感測器數據，進行特徵提取、異常檢測並通過 WebSocket 推送結果給前端。系統採用非同步架構，結合 PostgreSQL、Redis 和 WebSocket 技術，實現高效能的即時數據處理。

## 系統架構

```
┌─────────────┐
│  前端應用   │
│  (Vue 3)   │
└──────┬──────┘
       │ WebSocket
       ▼
┌─────────────────────────────────────────────┐
│           FastAPI 後端                       │
│  ┌──────────────┐  ┌─────────────┐        │
│  │ WebSocket   │  │ RealTime    │        │
│  │ Manager     │◄─┤ Analyzer    │        │
│  └──────┬───────┘  └──────┬──────┘        │
│         │                  │                │
│         │            ┌─────▼──────┐        │
│         │            │  Buffer    │        │
│         │            │  Manager   │        │
│         │            └─────┬──────┘        │
│         │                  │                │
│  ┌──────▼──────────┐  ┌───▼──────────┐   │
│  │  Redis Client  │  │ Async DB     │   │
│  └──────┬──────────┘  └───┬──────────┘   │
└─────────┼────────────────┼────────────────┘
          │                │
    ┌─────▼─────┐   ┌────▼─────────┐
    │   Redis   │   │ PostgreSQL  │
    │ (快取/流) │   │ (持久化)    │
    └───────────┘   └─────────────┘
```

## 核心組件

### 1. BufferManager (緩衝區管理器)

**檔案位置**: `backend/buffer_manager.py`

#### 功能概述
- 使用循環緩衝區 (Circular Buffer) 管理高頻率感測器數據
- 預設緩衝區大小：25,600 個樣本點 (1 秒 @ 25.6 kHz)
- 提供時間窗口數據訪問接口
- 同步數據到 Redis Streams
- 支持多感測器並發緩衝

#### 關鍵類別

##### SensorBuffer
單一感測器的循環緩衝區實作。

**初始化參數**:
- `sensor_id`: 感測器 ID
- `buffer_size`: 緩衝區大小 (預設 25600)

**主要方法**:
```python
# 添加單一樣本
add_sample(timestamp, h_acc, v_acc)

# 批量添加樣本
add_batch(samples)

# 獲取時間窗口數據
get_window(window_seconds=1.0) -> Dict

# 檢查是否就緒
is_ready(min_samples=10000) -> bool

# 獲取統計信息
get_stats() -> Dict
```

**返回的窗口數據結構**:
```python
{
    'sensor_id': int,
    'window_start': datetime,
    'window_end': datetime,
    'h_data': np.ndarray,  # 水平加速度數組
    'v_data': np.ndarray,  # 垂直加速度數組
    'sample_count': int
}
```

##### BufferManager
多感測器緩衝區管理器。

**關鍵功能**:
- 線程安全的緩衝區訪問 (`asyncio.Lock`)
- 自動數據持久化到 Redis
- 支持清理舊緩衝區 (預設 60 分鐘)

**主要方法**:
```python
# 獲取或創建緩衝區
async get_buffer(sensor_id) -> SensorBuffer

# 添加數據到緩衝區
async add_data(sensor_id, data)

# 獲取窗口數據
async get_window(sensor_id, window_seconds) -> Dict

# 保存窗口數據到數據庫
async save_to_database(sensor_id, window_data)

# 清理舊緩衝區
async cleanup_old_buffers(max_age_minutes=60)
```

### 2. RealTimeAnalyzer (即時分析引擎)

**檔案位置**: `backend/realtime_analyzer.py`

#### 功能概述
- 連續的特徵提取循環 (10 Hz 更新頻率)
- 時域、頻域特徵計算
- 閾值監控與警報生成
- 實時特徵推送

#### 分析流程

```
1. 啟動分析 (start_analysis)
   └─ 創建異步任務 _analysis_loop

2. 分析循環 (_analysis_loop)
   ├─ 獲取窗口數據 (1 秒窗口)
   ├─ 檢查樣本數量 (>= 10000)
   ├─ 提取特徵 (_extract_features)
   ├─ 保存到數據庫
   ├─ 廣播到 WebSocket
   ├─ 快取到 Redis
   ├─ 檢查閾值 (_check_alerts)
   └─ 等待 0.1 秒 (10 Hz)

3. 提取特徵 (_extract_features)
   ├─ 時域特徵
   │  ├─ RMS (均方根)
   │  ├─ Peak (峰值)
   │  ├─ Kurtosis (峰度)
   │  └─ Crest Factor (波峰因數)
   └─ 頻域特徵
      └─ Dominant Frequency (主頻)

4. 警報檢測 (_check_alerts)
   └─ 對比數據庫中的閾值配置
      ├─ 超過上限 → 生成警報
      └─ 低於下限 → 生成警報
```

#### 關鍵方法

```python
# 啟動分析
async start_analysis(sensor_id)

# 停止分析
async stop_analysis(sensor_id)

# 提取特徵
async _extract_features(window_data) -> Dict

# 保存特徵
async _save_features(sensor_id, features)

# 檢查警報
async _check_alerts(sensor_id, features)

# 獲取狀態
get_status() -> Dict
```

#### 特徵計算

**時域特徵**:
- **RMS (Root Mean Square)**:
  ```python
  rms = sqrt(mean(x^2))
  ```
- **Peak**: 最大絕對值
  ```python
  peak = max(|x|)
  ```
- **Kurtosis**: 峰度
  ```python
  kurtosis = mean(((x - mean) / std)^4)
  ```
- **Crest Factor**: 波峰因數
  ```python
  crest_factor = peak / rms
  ```

**頻域特徵**:
- **Dominant Frequency**: 使用 FFT 計算主頻
  ```python
  fft_result = fft(data)
  peak_idx = argmax(|fft_result|)
  dominant_freq = freqs[peak_idx]
  ```

### 3. WebSocketManager (WebSocket 連線管理)

**檔案位置**: `backend/websocket_manager.py`

#### 功能概述
- 管理多個 WebSocket 連線
- 按感測器 ID 組織連線
- 廣播消息到訂閱客戶端
- 自動清理斷開的連線
- 連線狀態追蹤

#### 連線模型

```
sensor_id=1: [WS1, WS2, WS3]
sensor_id=2: [WS4]
sensor_id=0: [WS5, WS6]  # 全局訂閱 (警報)
```

#### 關鍵方法

```python
# 連接客戶端
async connect(websocket, sensor_id)

# 斷開連接
async disconnect(websocket)

# 發送個人消息
async send_personal_message(message, websocket)

# 廣播到特定感測器
async broadcast_to_sensor(sensor_id, message)

# 廣播到所有連線
async broadcast_to_all(message)

# 廣播警報
async broadcast_alert(alert)

# 廣播特徵更新
async broadcast_feature_update(sensor_id, features)

# 獲取連線數量
get_connection_count(sensor_id=None) -> int

# 獲取活躍感測器
get_active_sensors() -> list

# 獲取連線信息
get_connection_info() -> dict
```

#### 消息格式

**特徵更新消息**:
```json
{
  "type": "feature_update",
  "sensor_id": 1,
  "data": {
    "rms_h": 0.1234,
    "rms_v": 0.0987,
    "window_start": "2026-01-20T10:30:00",
    "window_end": "2026-01-20T10:30:01"
  }
}
```

**警報消息**:
```json
{
  "type": "alert",
  "data": {
    "sensor_id": 1,
    "alert_type": "threshold",
    "severity": "critical",
    "message": "rms_h is above threshold (0.5000 above 0.3000)",
    "feature_name": "rms_h",
    "current_value": 0.5000,
    "threshold_value": 0.3000
  }
}
```

### 4. RedisClient (Redis 客戶端)

**檔案位置**: `backend/redis_client.py`

#### 功能概述
- Streams: 時間序列數據存儲
- Hash: 特徵快取
- Pub/Sub: 消息發布訂閱
- Set: 連線追蹤
- List: 警報隊列

#### 關鍵操作

**Streams 操作**:
```python
# 添加數據點
async add_sensor_data(sensor_id, data)

# 讀取最近的數據
async get_sensor_stream(sensor_id, count=100)

# 截斷流
async trim_sensor_stream(sensor_id, max_length=10000)
```

**快取操作**:
```python
# 快取特徵
async cache_features(sensor_id, features, ttl=300)

# 獲取快取特徵
async get_cached_features(sensor_id) -> Dict
```

**Pub/Sub 操作**:
```python
# 發布消息
async publish(channel, message)

# 訂閱頻道
async subscribe(channel) -> PubSub
```

**連線管理**:
```python
# 添加活躍連線
async add_active_connection(connection_id)

# 移除連線
async remove_active_connection(connection_id)

# 獲取活躍連線數
async get_active_connection_count() -> int
```

**感測器狀態**:
```python
# 更新狀態
async update_sensor_status(sensor_id, status)

# 獲取狀態
async get_sensor_status(sensor_id) -> Dict
```

**警報隊列**:
```python
# 推入警報
async push_alert(alert)

# 彈出警報
async pop_alert() -> Dict

# 獲取隊列長度
async get_alert_queue_length() -> int
```

### 5. AsyncDatabase (PostgreSQL 資料庫)

**檔案位置**: `backend/database_async.py`

#### 功能概述
- 使用 asyncpg 實現非同步 PostgreSQL 訪問
- 連線池管理 (最小 10，最大 50 連線)
- 批量數據插入優化
- 視圖查詢優化

#### 連線池配置

```python
await asyncpg.create_pool(
    DATABASE_URL,
    min_size=10,                    # 最小連線數
    max_size=50,                    # 最大連線數
    max_queries=50000,              # 每連線最大查詢數
    max_inactive_connection_lifetime=300.0,  # 5 分鐘
    command_timeout=60              # 查詢超時
)
```

#### 關鍵方法

```python
# 批量插入感測器數據
async insert_sensor_data(sensor_id, data)

# 插入特徵
async insert_features(sensor_id, features)

# 獲取最新特徵
async get_latest_features(sensor_id) -> Dict

# 獲取活躍警報
async get_active_alerts(limit=100) -> List[Dict]

# 創建警報
async create_alert(alert) -> int

# 確認警報
async acknowledge_alert(alert_id, acknowledged_by) -> bool

# 獲取警報配置
async get_alert_configurations(sensor_id) -> List[Dict]

# 註冊感測器
async register_sensor(sensor_id, sensor_name, sensor_type, sampling_rate)

# 獲取感測器狀態
async get_sensor_status(sensor_id) -> Dict
```

## 資料流程

### 1. 數據採集與緩衝

```
感測器數據
    │
    ▼
┌──────────────────┐
│  BufferManager  │
│  .add_data()    │
└────────┬─────────┘
         │
         ├─► 記憶體循環緩衝區
         │
         └─► Redis Streams
            (臨時持久化, 24h TTL)
```

### 2. 即時分析循環

```
分析任務 (10 Hz)
    │
    ▼
┌─────────────────────┐
│  獲取窗口數據      │
│  (1秒, >=10000樣本)│
└────────┬──────────┘
         │
         ▼
┌─────────────────────┐
│  特徵提取          │
│  - 時域特徵        │
│  - 頻域特徵        │
└────────┬──────────┘
         │
         ├─► PostgreSQL
         │   (持久化)
         │
         ├─► Redis Cache
         │   (快速查詢)
         │
         ├─► WebSocket
         │   (推送到前端)
         │
         └─► 閾值檢查
             │
             ▼
         警報生成
             │
             ├─► PostgreSQL
             │   (警報記錄)
             │
             └─► WebSocket
                 (推送到前端)
```

### 3. WebSocket 通訊

```
前端 ←─→ 後端

連接建立:
  前端: connect(sensorId)
    └─► ws://localhost:8081/ws/realtime/{sensorId}
        └─► manager.connect()
            └─► analyzer.start_analysis()

數據推送:
  後端: analyzer._analysis_loop()
    └─► manager.broadcast_feature_update()
        └─► 所有訂閱該感測器的客戶端

警報推送:
  後端: analyzer._create_alert()
    └─► manager.broadcast_alert()
        └─► 所有客戶端 (sensor_id=0)

連接斷開:
  前端: disconnect()
    └─► manager.disconnect()
        └─► analyzer.stop_analysis() (如果是最後一個連線)
```

## 前端實作

### 1. WebSocket Service

**檔案位置**: `frontend/src/services/websocket.js`

#### 關鍵功能
- 自動重連機制 (最多 10 次，指數退避)
- 事件驅動架構
- Ping/Pong 保活機制
- 錯誤處理

#### 主要方法

```javascript
// 連接到感測器
connect(sensorId)

// 斷開連接
disconnect()

// 發送消息
send(message)

// Ping
ping()

// 事件監聽
on(event, callback)

// 移除監聽器
off(event, callback)

// 獲取連線狀態
getConnectionStatus() -> boolean
```

#### 事件類型

```javascript
// 連接建立
'connected'

// 連接斷開
'disconnected'

// 特徵更新
'feature_update'

// 警報
'alert'

// Pong 響應
'pong'

// 錯誤
'error'

// 重連失敗
'reconnect_failed'
```

#### 重連策略

```javascript
reconnectAttempts < maxReconnectAttempts (10)
  └─ 指數退避: min(1000 * 2^(n-1), 30000ms)
      └─ 1s → 2s → 4s → 8s → ... → 30s
```

### 2. Pinia Store (狀態管理)

**檔案位置**: `frontend/src/stores/realtime.js`

#### 狀態

```javascript
{
  isConnected: boolean,        // 連線狀態
  currentSensor: number,       // 當前感測器 ID
  latestFeatures: {},          // 最新特徵
  alertHistory: [],           // 警報歷史
  isStreaming: boolean,       // 是否在流傳輸
  connectionStatus: string,   // 連線狀態字串
  signalBuffer: {},           // 信號緩衝區
  featureBuffer: {},          // 特徵緩衝區
  MAX_BUFFER_POINTS: 100      // 緩衝區最大點數
}
```

#### 計算屬性

```javascript
// 是否有警報
hasAlerts

// 最新警報
latestAlert

// 特徵數量
featureCount
```

#### 關鍵操作

```javascript
// 連接到感測器
connect(sensorId)

// 斷開連接
disconnect()

// 更新特徵
updateFeatures(data)

// 添加警報
addAlert(alert)

// 清空緩衝區
clearBuffers()

// 確認警報
acknowledgeAlert(alertId)

// 格式化特徵值
formatFeature(key) -> string
```

#### 緩衝區結構

**signalBuffer**:
```javascript
{
  timestamps: [],
  horizontal: [],
  vertical: []
}
```

**featureBuffer**:
```javascript
{
  timestamps: [],
  rms_h: [],
  rms_v: [],
  kurtosis_h: [],
  kurtosis_v: [],
  peak_h: [],
  peak_v: []
}
```

### 3. Vue Component (即時分析介面)

**檔案位置**: `frontend/src/views/RealtimeAnalysis.vue`

#### 介面組件

1. **控制面板**
   - 感測器 ID 輸入
   - 開始/停止監控按鈕
   - 連線狀態標籤

2. **警報面板**
   - 顯示最近 5 條警報
   - 嚴重程度標籤
   - 時間戳顯示

3. **特徵卡片** (8 個)
   - RMS (水平/垂直)
   - Kurtosis (水平/垂直)
   - Peak (水平/垂直)
   - Crest Factor (水平/垂直)

4. **即時圖表** (4 個)
   - RMS 趨勢
   - Kurtosis 趨勢
   - Peak 趨勢
   - Crest Factor 趨勢

#### 關鍵方法

```javascript
// 開始流傳輸
async startStreaming()

// 停止流傳輸
stopStreaming()

// 格式化特徵值
formatFeatureValue(key) -> string

// 格式化時間
formatTime(timestamp) -> string

// 獲取警報類型
getAlertType(severity) -> string

// 初始化圖表
initCharts()

// 更新圖表
updateCharts()
```

#### 圖表配置

使用 ECharts 實現，包含以下配置：
- 深色主題背景
- 白色文字與軸線
- 平滑曲線
- 響應式調整
- Tooltip 顯示

#### 生命週期

```javascript
onMounted()
  ├─ initCharts()
  └─ window resize 監聽

onUnmounted()
  ├─ dispose charts
  └─ disconnect WebSocket
```

## API 端點

### Sensor Data 推送端點 (機台數據注入)

這是專案中**新增的端點**，用於將機台的 sensor data 推送到 Buffer Manager。

#### POST `/api/sensor/data`
**用途**: 接收批量感測器數據並添加到 Buffer Manager

**請求格式**:
```json
{
  "sensor_id": 1,
  "data": [
    {
      "timestamp": "2026-01-20T10:30:00.123",
      "h_acc": 0.1234,
      "v_acc": 0.0987
    },
    {
      "timestamp": "2026-01-20T10:30:00.125",
      "h_acc": 0.1256,
      "v_acc": 0.1001
    }
  ]
}
```

**欄位說明**:
- `sensor_id`: 感測器 ID (integer)
- `data`: 數據點陣列
  - `timestamp`: ISO 8601 格式時間戳 (datetime)
  - `h_acc`: 水平加速度值 (float)
  - `v_acc`: 垂直加速度值 (float)

**響應**:
```json
{
  "status": "success",
  "sensor_id": 1,
  "processed": 2,
  "message": "Successfully processed 2 data points"
}
```

**數據處理流程**:
```
機台數據
    │
    ▼
POST /api/sensor/data
    │
    ├─► BufferManager.add_data()
    │   ├─► 記憶體循環緩衝區
    │   └─► Redis Streams (臨時持久化)
    │
    └─► RealTimeAnalyzer._analysis_loop()
        └─► 特徵提取與分析
```

#### POST `/api/sensor/data/stream`
**用途**: 流式接收高頻感測器數據（陣列形式）

適用於需要高效傳輸大量數據的場景，如每秒 25600 樣本的高頻採集。

**請求格式** (Query Parameters):
```
sensor_id=1
h_acc=[0.1234, 0.1256, 0.1278, ...]
v_acc=[0.0987, 0.1001, 0.1015, ...]
timestamp_start=2026-01-20T10:30:00.123
sampling_rate=25600.0
```

**參數說明**:
- `sensor_id`: 感測器 ID (integer)
- `h_acc`: 水平加速度陣列 (array of floats)
- `v_acc`: 垂直加速度陣列 (array of floats)
- `timestamp_start`: 起始時間戳 (ISO 8601 datetime)
- `sampling_rate`: 採樣率 Hz，預設 25600 (float)

**響應**:
```json
{
  "status": "success",
  "sensor_id": 1,
  "processed": 25600,
  "time_range": [
    "2026-01-20T10:30:00.123000",
    "2026-01-20T10:31:00.123000"
  ]
}
```

**計算邏輯**:
- 根據起始時間和採樣率自動計算每個樣本的時間戳
- 確保 h_acc 和 v_acc 陣列長度一致

---

## 機台數據推送實作範例

### Python 範例 (使用 requests)

```python
import requests
from datetime import datetime
import random

# API 端點
API_URL = "http://localhost:8081/api/sensor/data"

# 準備數據 (模擬機台數據)
sensor_id = 1
data_points = []

# 生成 1 秒的數據 (25600 Hz 採樣率)
sampling_rate = 25600
start_time = datetime.now()

for i in range(sampling_rate):
    timestamp = start_time + timedelta(microseconds=i * (1000000 / sampling_rate))
    data_points.append({
        "timestamp": timestamp.isoformat(),
        "h_acc": random.gauss(0, 0.1),  # 模擬振動數據
        "v_acc": random.gauss(0, 0.1)
    })

# 批量推送到後端
payload = {
    "sensor_id": sensor_id,
    "data": data_points
}

response = requests.post(API_URL, json=payload)
print(response.json())
```

### Python 範例 (流式推送 - 高頻數據)

```python
import requests
from datetime import datetime
import numpy as np

# API 端點
API_URL = "http://localhost:8081/api/sensor/data/stream"

# 準備 1 秒的高頻數據
sampling_rate = 25600
h_acc = np.random.normal(0, 0.1, sampling_rate).tolist()
v_acc = np.random.normal(0, 0.1, sampling_rate).tolist()
timestamp_start = datetime.now()

# 推送數據
params = {
    "sensor_id": 1,
    "h_acc": h_acc,
    "v_acc": v_acc,
    "timestamp_start": timestamp_start.isoformat(),
    "sampling_rate": sampling_rate
}

response = requests.post(API_URL, params=params)
print(response.json())
```

### JavaScript / Node.js 範例

```javascript
const axios = require('axios');

// API 端點
const API_URL = 'http://localhost:8081/api/sensor/data';

// 準備數據
const sensorId = 1;
const dataPoints = [];
const samplingRate = 25600;
const startTime = new Date();

for (let i = 0; i < samplingRate; i++) {
  const timestamp = new Date(startTime.getTime() + i * (1000000 / samplingRate) / 1000);
  dataPoints.push({
    timestamp: timestamp.toISOString(),
    h_acc: parseFloat((Math.random() * 0.2 - 0.1).toFixed(6)),
    v_acc: parseFloat((Math.random() * 0.2 - 0.1).toFixed(6))
  });
}

// 推送數據
const payload = {
  sensor_id: sensorId,
  data: dataPoints
};

axios.post(API_URL, payload)
  .then(response => console.log(response.data))
  .catch(error => console.error(error));
```

### cURL 範例

```bash
# 推送單條數據
curl -X POST http://localhost:8081/api/sensor/data \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": 1,
    "data": [
      {
        "timestamp": "2026-01-20T10:30:00.123",
        "h_acc": 0.1234,
        "v_acc": 0.0987
      }
    ]
  }'

# 推送陣列數據 (流式)
curl -X POST "http://localhost:8081/api/sensor/data/stream?sensor_id=1&h_acc=0.1234,0.1256&v_acc=0.0987,0.1001&timestamp_start=2026-01-20T10:30:00.123&sampling_rate=25600"
```

### 持續數據推送 (模擬機台)

```python
import requests
import time
import numpy as np
from datetime import datetime, timedelta
import threading

API_URL = "http://localhost:8081/api/sensor/data"
SENSOR_ID = 1
SAMPLING_RATE = 25600  # 25.6 kHz
BATCH_SIZE = 25600      # 每次推送 1 秒數據

class ContinuousDataStreamer:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        """啟動持續數據推送"""
        self.running = True
        self.thread = threading.Thread(target=self._stream_loop)
        self.thread.daemon = True
        self.thread.start()
        print("Data streamer started")

    def stop(self):
        """停止數據推送"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("Data streamer stopped")

    def _stream_loop(self):
        """持續推送數據的循環"""
        counter = 0
        while self.running:
            try:
                # 生成 1 秒的模擬數據
                start_time = datetime.now()
                h_acc = np.random.normal(0, 0.1, BATCH_SIZE).tolist()
                v_acc = np.random.normal(0, 0.1, BATCH_SIZE).tolist()

                # 準備數據點
                data_points = []
                for i in range(BATCH_SIZE):
                    timestamp = start_time + timedelta(microseconds=i * (1000000 / SAMPLING_RATE))
                    data_points.append({
                        "timestamp": timestamp.isoformat(),
                        "h_acc": round(h_acc[i], 6),
                        "v_acc": round(v_acc[i], 6)
                    })

                # 推送到後端
                payload = {
                    "sensor_id": SENSOR_ID,
                    "data": data_points
                }

                response = requests.post(API_URL, json=payload, timeout=5)
                if response.status_code == 200:
                    counter += 1
                    if counter % 10 == 0:  # 每 10 秒打印一次
                        print(f"Sent {counter} batches ({counter} seconds of data)")
                else:
                    print(f"Error: {response.status_code} - {response.text}")

                # 控制推送頻率 (大約實時)
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed < 1.0:
                    time.sleep(1.0 - elapsed)

            except Exception as e:
                print(f"Error in stream loop: {e}")
                time.sleep(1)

# 使用範例
if __name__ == "__main__":
    streamer = ContinuousDataStreamer()

    try:
        streamer.start()

        # 保持運行 (按 Ctrl+C 停止)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        streamer.stop()
```

---

### WebSocket 端點

#### `/ws/realtime/{sensor_id}`
**用途**: 特定感測器的即時數據流

**功能**:
- 接收特徵更新
- 接收警報通知
- Ping/Pong 保活

**範例**:
```
ws://localhost:8081/ws/realtime/1
```

#### `/ws/alerts`
**用途**: 全局警報流

**功能**:
- 接收所有感測器的警報

**範例**:
```
ws://localhost:8081/ws/alerts
```

### REST API 端點

#### POST `/api/stream/start`
**用途**: 開始即時流傳輸

**請求體**:
```json
{
  "sensor_id": 1,
  "sampling_rate": 25600
}
```

**響應**:
```json
{
  "status": "started",
  "sensor_id": 1,
  "message": "Real-time analysis started",
  "sampling_rate": 25600
}
```

#### POST `/api/stream/stop`
**用途**: 停止即時流傳輸

**參數**: `sensor_id` (query parameter)

**響應**:
```json
{
  "status": "stopped",
  "sensor_id": 1,
  "message": "Real-time analysis stopped"
}
```

#### GET `/api/stream/status`
**用途**: 獲取流傳輸狀態

**響應**:
```json
{
  "active_streams": 2,
  "active_connections": 5,
  "active_sensors": [1, 2],
  "sensor_connections": {
    "1": 3,
    "2": 2
  }
}
```

#### GET `/api/realtime/features/{sensor_id}`
**用途**: 獲取最新特徵

**響應**:
```json
{
  "sensor_id": 1,
  "window_start": "2026-01-20T10:30:00",
  "window_end": "2026-01-20T10:30:01",
  "rms_h": 0.1234,
  "rms_v": 0.0987,
  "kurtosis_h": 3.4567,
  "kurtosis_v": 3.2345,
  "peak_h": 0.8901,
  "peak_v": 0.7654,
  "crest_factor_h": 7.2123,
  "crest_factor_v": 7.7543,
  "dominant_freq_h": 123.45,
  "dominant_freq_v": 123.45
}
```

#### GET `/api/alerts/active`
**用途**: 獲取活躍警報

**參數**: `limit` (預設 100)

**響應**:
```json
{
  "alerts": [
    {
      "alert_id": 1,
      "sensor_id": 1,
      "alert_type": "threshold",
      "severity": "critical",
      "message": "rms_h is above threshold",
      "feature_name": "rms_h",
      "current_value": 0.5000,
      "threshold_value": 0.3000,
      "created_at": "2026-01-20T10:30:00",
      "is_acknowledged": false
    }
  ],
  "count": 1
}
```

#### POST `/api/alerts/acknowledge/{alert_id}`
**用途**: 確認警報

**請求體**:
```json
{
  "acknowledged_by": "user"
}
```

**響應**:
```json
{
  "status": "acknowledged",
  "alert_id": 1
}
```

## 監控流程詳解

### 完整數據流

```
1. 用戶操作
   前端輸入感測器 ID
     │
     ▼
   點擊 "開始監控"
     │
     ▼
   websocketService.connect(sensorId)

2. WebSocket 連接建立
   ws://localhost:8081/ws/realtime/{sensorId}
     │
     ▼
   FastAPI 接收連接
     │
     ├─► manager.connect(websocket, sensorId)
     │   └─► 追蹤連線 (Redis)
     │
     └─► analyzer.start_analysis(sensorId)
         └─► 創建異步分析任務

3. 數據採集 (假設外部數據源)
   感測器 → BufferManager.add_data()
     │
     ├─► 記憶體循環緩衝區
     └─► Redis Streams

4. 分析循環 (10 Hz)
   analyzer._analysis_loop()
     │
     ├─► buffer_manager.get_window(1.0s)
     │   └─► 檢查樣本數 >= 10000
     │
     ├─► _extract_features()
     │   ├─► 時域: RMS, Peak, Kurtosis, Crest
     │   └─► 頻域: Dominant Freq
     │
     ├─► db.insert_features()
     │   └─► PostgreSQL
     │
     ├─► redis_client.cache_features()
     │   └─► Redis Hash (TTL 300s)
     │
     ├─► manager.broadcast_feature_update()
     │   └─► WebSocket 客戶端
     │
     └─► _check_alerts()
         └─► 對比閾值
             ├─► 超過/低於 → db.create_alert()
             └─► manager.broadcast_alert()
                 └─► 所有客戶端

5. 前端處理
   websocketService.on('feature_update')
     │
     ├─► realtimeStore.updateFeatures(data)
     │   ├─► 更新 latestFeatures
     │   ├─► 更新 featureBuffer
     │   └─► trimBuffers() (保持 100 點)
     │
     └─► Vue watch → updateCharts()
         └─► ECharts 更新

   websocketService.on('alert')
     │
     └─► realtimeStore.addAlert(alert)
         ├─► 更新 alertHistory
         └─► Vue 重新渲染警報列表

6. 用戶斷開
   點擊 "停止監控"
     │
     ▼
   websocketService.disconnect()
     │
     ▼
   FastAPI manager.disconnect(websocket)
     │
     ├─► 檢查連線數
     └─► 如果為 0 → analyzer.stop_analysis()
         └─► 取消異步任務
```

### 時間序列

```
T=0s:    用戶連接
T=0.1s:  WebSocket 建立
T=0.1s:  分析任務啟動
T=0.2s:  緩衝區累積數據
T=1.0s:  第一次分析 (10000 樣本)
T=1.1s:  特徵推送到前端
T=1.2s:  前端圖表更新
T=2.0s:  第二次分析
T=2.1s:  特徵推送
...
T=10s:   檢測到異常
T=10.1s: 生成警報
T=10.1s: 警報推送
T=10.2s:  前端警報面板更新
...
T=Ns:    用戶斷開
```

## 警報機制

### 警報配置

警報配置存儲在 `alert_configurations` 表中：

```sql
CREATE TABLE alert_configurations (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER,
    feature_name VARCHAR(50),      -- 特徵名稱 (rms_h, kurtosis_v, etc.)
    threshold_min NUMERIC,         -- 下限閾值
    threshold_max NUMERIC,         -- 上限閾值
    severity VARCHAR(20),          -- 嚴重程度: critical, warning, info
    enabled BOOLEAN DEFAULT true
);
```

### 警報生成流程

```
1. 特徵計算完成
   └─► _check_alerts(sensor_id, features)

2. 獲取配置
   db.get_alert_configurations(sensor_id)
   └─► 返回該感測器的所有啟用配置

3. 逐個檢查
   對每個配置:
     ├─► 獲取特徵值: features[feature_name]
     ├─► 檢查上限: value > threshold_max?
     │   └─► 是 → _create_alert(direction='above')
     └─► 檢查下限: value < threshold_min?
         └─► 是 → _create_alert(direction='below')

4. 創建警報
   db.create_alert(alert)
   └─► 插入 alerts 表

5. 廣播警報
   manager.broadcast_alert(alert)
   └─► 推送到所有 WebSocket 客戶端
```

### 警報結構

```javascript
{
  sensor_id: 1,
  alert_type: "threshold",
  severity: "critical",
  message: "rms_h is above threshold (0.5000 above 0.3000)",
  feature_name: "rms_h",
  current_value: 0.5000,
  threshold_value: 0.3000
}
```

### 警報確認

用戶可以確認警報以標記為已處理：

```javascript
async function acknowledgeAlert(alertId) {
  await fetch(`/api/alerts/acknowledge/${alertId}`, {
    method: 'POST',
    body: JSON.stringify({ acknowledged_by: 'user' })
  })
  // 從本地歷史中移除
  alertHistory.value = alertHistory.value.filter(a => a.alert_id !== alertId)
}
```

## 效能優化策略

### 1. 記憶體優化

**循環緩衝區**:
- 使用 `collections.deque(maxlen=25600)`
- 自動覆蓋舊數據，無需手動清理
- 固定記憶體佔用

**數據類型優化**:
- 使用 NumPy 數組 (連續記憶體)
- 批量操作減少循環開銷

### 2. 並發處理

**異步 I/O**:
- 所有數據庫操作使用 asyncpg
- Redis 使用 redis.asyncio
- WebSocket 使用 FastAPI 異步處理

**連線池**:
- PostgreSQL 連線池 (10-50 連線)
- 自動連線復用
- 連線超時管理

### 3. 快取策略

**Redis 多層快取**:
```
L1: 記憶體緩衝區 (1 秒)
  └─► 最快，容量小

L2: Redis Hash (5 分鐘 TTL)
  └─► 跨進程共享，中等容量

L3: PostgreSQL (持久化)
  └─► 最慢，無限容量
```

**查詢優化**:
```python
# 視圖查詢 (預計算)
SELECT * FROM v_latest_features WHERE sensor_id = $1

# 索引優化
CREATE INDEX idx_sensor_data_timestamp ON sensor_data(sensor_id, timestamp);
```

### 4. 數據傳輸優化

**WebSocket**:
- 二進制數據壓縮 (可選)
- 批量消息合併
- 心跳檢測 (ping/pong)

**Redis Streams**:
- 自動過期 (24h TTL)
- 流截斷 (保留最近 10000 條)
- 高效追加操作

### 5. 前端優化

**虛擬滾動**:
- 圖表只渲染 100 個點
- 超過後自動截斷

**響應式更新**:
- 使用 Vue 的響應式系統
- 局部更新避免全量重渲染

**請求防抖**:
- 用戶輸入防抖
- 滾動事件節流

### 6. 監控指標

**系統指標**:
```
- 活躍連線數
- 分析任務數
- 緩衝區使用率
- 警報隊列長度
```

**性能指標**:
```
- 分析延遲 (目標 < 100ms)
- 端到端延遲 (目標 < 500ms)
- 特徵提取吞吐量 (10 Hz)
- WebSocket 消息延遲
```

## 故障處理

### 1. 連線故障

**WebSocket 斷開**:
```python
# 自動重連 (最多 10 次)
reconnectAttempts < maxReconnectAttempts
  └─ 指數退避重試
```

**Redis 故障**:
```python
# 優雅降級
if not redis_client._is_connected:
    logger.warning("Redis not connected, skipping cache")
    # 繼續處理，只跳過 Redis 操作
```

**PostgreSQL 故障**:
```python
# 重試機制
try:
    await db.insert_features(sensor_id, features)
except Exception as e:
    logger.error(f"Error saving to database: {e}")
    # 記錄錯誤，不中斷分析循環
```

### 2. 數據異常

**樣本不足**:
```python
if sample_count < min_samples:
    # 等待更多數據
    continue
```

**NaN/Inf 處理**:
```python
# 特徵計算中處理異常值
rms = np.sqrt(np.mean(h_data ** 2))
if np.isnan(rms) or np.isinf(rms):
    rms = 0.0
```

### 3. 資源洩漏防護

**任務清理**:
```python
async def stop_analysis(sensor_id):
    task = self.analysis_tasks[sensor_id]
    task.cancel()  # 取消異步任務
    del self.analysis_tasks[sensor_id]  # 清除引用
```

**緩衝區清理**:
```python
async def cleanup_old_buffers(max_age_minutes=60):
    # 自動清理 60 分鐘未更新的緩衝區
    ...
```

## 部署建議

### Docker Compose 配置

```yaml
services:
  backend:
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL_POSTGRESQL=postgresql://...
      - REDIS_URL=redis://...

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=vibration_analysis
      - POSTGRES_USER=vibration
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass redis_pass
    volumes:
      - redis_data:/data
```

### 環境變數

```bash
# 資料庫
DATABASE_URL_POSTGRESQL=postgresql://user:pass@host:5432/db

# Redis
REDIS_URL=redis://:pass@host:6379/0

# 應用
FASTAPI_PORT=8081
LOG_LEVEL=INFO
```

### 監控與日誌

**結構化日誌**:
```python
import logging

logger = logging.getLogger(__name__)
logger.info(
    "Feature extracted",
    extra={
        "sensor_id": sensor_id,
        "rms_h": rms_h,
        "window_start": window_start
    }
)
```

**Prometheus 指標** (建議擴展):
```python
from prometheus_client import Counter, Histogram

feature_extraction_counter = Counter(
    'feature_extraction_total',
    'Total feature extractions',
    ['sensor_id']
)

analysis_duration_histogram = Histogram(
    'analysis_duration_seconds',
    'Analysis duration',
    ['sensor_id']
)
```

## 總結

本專案的即時分析與監控系統採用了現代化的異步架構，具備以下特點：

✅ **高效能**: 25.6 kHz 採樣率，10 Hz 分析頻率
✅ **可擴展**: 支持多感測器並發，連線池優化
✅ **可靠性**: 自動重連，優雅降級，故障恢復
✅ **實時性**: WebSocket 推送，Redis 快取，低延遲
✅ **監控性**: 完整的警報機制，狀態追蹤
✅ **可維護**: 模塊化設計，清晰的資料流

系統透過精心的架構設計和效能優化，能夠穩定地處理高頻振動數據，並提供即時的監控與警報功能。
