# Sensor 資料檢查工具說明

## 資料流程架構

```
機台 (Sensor 1)
    ↓
WebSocket: ws://localhost:8081/ws/realtime/1
    ↓
REST API: POST /api/sensor/data 或 /api/sensor/data/stream
    ↓
BufferManager (記憶體循環緩衝區)
    ↓
    ├→ Redis Streams (sensor:1:data) [24小時 TTL]
    │       ↓
    │   RealtimeAnalyzer (特徵提取)
    │       ↓
    └→ PostgreSQL realtime_features 表 (永久儲存)
```

## 使用方式

### 1. 檢查所有資料來源

```bash
uv run python scripts/check_sensor_data.py --sensor-id 1
```

### 2. 只檢查特定資料來源

```bash
# 只檢查 PostgreSQL
uv run python scripts/check_sensor_data.py --sensor-id 1 --postgres

# 只檢查 Redis
uv run python scripts/check_sensor_data.py --sensor-id 1 --redis

# 只檢查 Buffer Manager
uv run python scripts/check_sensor_data.py --sensor-id 1 --buffer
```

## 檢查項目說明

### 1. Buffer Manager (記憶體緩衝區)

- **用途**: 暫存高頻 sensor 資料 (25.6 kHz)
- **容量**: 預設 25600 筆資料 (約 1 秒)
- **檢查重點**:
  - Buffer 是否有資料
  - Buffer 使用率
  - 最新資料時間戳

### 2. Redis Streams

- **用途**: 臨時持久化 sensor 原始資料
- **保存時間**: 24 小時 (TTL)
- **Stream Key 格式**: `sensor:{sensor_id}:data`
- **檢查重點**:
  - Stream 是否存在
  - Stream 資料筆數
  - 最新資料內容

### 3. PostgreSQL - sensor_data 表

**重要**: 這個表**不會**儲存原始 sensor 資料!

系統設計:
- ✅ **會儲存**: 特徵資料 → `realtime_features` 表
- ❌ **不會儲存**: 原始資料 → 不寫入 `sensor_data` 表

**原因**:
- 原始資料頻率太高 (25.6 kHz), 直接存入 PostgreSQL 會造成嚴重效能問題
- 原始資料存放在 Redis Streams (24小時後自動刪除)
- 只有計算後的特徵值 (每 0.1 秒一次) 會永久儲存在 PostgreSQL

### 4. PostgreSQL - realtime_features 表

- **用途**: 儲存計算後的特徵值
- **頻率**: 約每 0.1 秒一次 (10 Hz)
- **特徵欄位**:
  - `rms_h`, `rms_v`: RMS 值
  - `kurtosis_h`, `kurtosis_v`: 峰度
  - `peak_h`, `peak_v`: 峰值
  - `crest_factor_h`, `crest_factor_v`: 峰值因數
  - `dominant_freq_h`, `dominant_freq_v`: 主頻率

## 診斷建議

### 情況 1: Buffer Manager 無資料

**症狀**: 所有檢查都顯示無資料

**可能原因**:
1. 機台未推送資料
2. WebSocket 連線未建立
3. API endpoint 未正確呼叫

**解決方式**:
1. 確認前端顯示 "已連接" 狀態
2. 檢查瀏覽器 console 是否有 WebSocket 連線訊息
3. 確認機台模擬器是否正在運行

### 情況 2: Buffer 有資料但 Redis 無

**可能原因**:
1. Redis 服務未啟動
2. Redis 連線設定錯誤

**解決方式**:
```bash
# 檢查 Redis 是否運行
docker-compose ps redis

# 查看 Redis 連線設定
cat backend/redis_client.py
```

### 情況 3: Redis 有資料但 PostgreSQL 無特徵

**可能原因**:
1. Buffer 資料量不足 (需要至少 10000 筆)
2. RealtimeAnalyzer 未啟動
3. 資料收集時間不夠長

**解決方式**:
1. 等待更長時間 (至少 1 秒的資料)
2. 檢查後端 log 是否有特徵提取訊息
3. 確認 WebSocket 連線後 analyzer 是否啟動

## 手動查詢資料庫

### PostgreSQL 查詢

```bash
# 連接到 PostgreSQL
docker exec -it postgres psql -U vibration -d vibration_analysis

# 查詢 sensor 註冊資訊
SELECT * FROM sensors WHERE sensor_id = 1;

# 查詢最新特徵資料
SELECT * FROM realtime_features
WHERE sensor_id = 1
ORDER BY window_end DESC
LIMIT 10;

# 查詢特徵數量統計
SELECT
    sensor_id,
    COUNT(*) as feature_count,
    MIN(window_start) as first_window,
    MAX(window_end) as last_window
FROM realtime_features
WHERE sensor_id = 1
GROUP BY sensor_id;
```

### Redis 查詢

```bash
# 連接到 Redis
docker exec -it redis redis-cli

# 查看所有 sensor streams
KEYS sensor:*

# 查看 sensor 1 的 stream 資訊
XINFO STREAM sensor:1:data

# 讀取最新 5 筆資料
XREVRANGE sensor:1:data + - COUNT 5

# 讀取資料範圍
XRANGE sensor:1:data - +
```

## 預期結果範例

正常運作時的輸出:

```
############################################################
# 🔍 Sensor 資料檢查工具
# Sensor ID: 1
# 檢查時間: 2026-01-21 10:30:00
############################################################

============================================================
📊 檢查 Buffer Manager 狀態 (Sensor ID: 1)
============================================================
✅ Sensor 1 Buffer 狀態:
   Buffer Size: 25600
   Current Size: 25600
   Sample Count: 128000
   Window Start: 2026-01-21T10:29:59
   Latest Timestamp: 2026-01-21T10:30:00
   Buffer Usage: 100.0%

============================================================
📊 檢查 Redis Streams (Sensor ID: 1)
============================================================
✅ Stream 存在: sensor:1:data
   長度: 128000
   最後一筆 ID: 1768959043578-0

============================================================
📊 檢查 PostgreSQL - realtime_features 表 (Sensor ID: 1)
============================================================
✅ 找到 150 筆特徵資料:

  🆔 Feature ID: 12345
  ⏰ Window: 2026-01-21T10:29:59 ~ 2026-01-21T10:30:00
  📊 RMS: H=0.1234, V=0.0987
  📈 Kurtosis: H=2.5678, V=2.3456
  ...

📈 統計資訊:
  總筆數: 150
  最早時間: 2026-01-21T10:28:15
  最新時間: 2026-01-21T10:30:00
```

## 故障排除流程圖

```
開始監控
    ↓
前端顯示 "已連接"?
    否 → 檢查 WebSocket URL 和後端服務
    是 ↓
WebSocket 訊息中有收到資料?
    否 → 機台未推送資料
    是 ↓
Buffer Manager 有資料?
    否 → 檢查 BufferManager.add_data() 是否被呼叫
    是 ↓
Redis 有資料?
    否 → 檢查 Redis 服務
    是 ↓
PostgreSQL realtime_features 有資料?
    否 → 檢查 RealtimeAnalyzer 和資料量是否足夠
    是 → ✅ 系統正常運作
```
