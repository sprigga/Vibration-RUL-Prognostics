# 機台 Sensor Data 推送指南

## 概述

本指南說明如何將機台的振動感測器數據推送到後端 Buffer Manager，以進行即時分析與監控。

## API 端點

### 1. 批量推送端點

**端點**: `POST /api/sensor/data`

**用途**: 接收批量感測器數據並添加到 Buffer Manager

#### 請求格式

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

#### 參數說明

| 參數 | 類型 | 說明 |
|------|------|------|
| sensor_id | integer | 感測器 ID |
| data | array | 數據點陣列 |
| data[].timestamp | string | ISO 8601 格式時間戳 |
| data[].h_acc | float | 水平加速度值 |
| data[].v_acc | float | 垂直加速度值 |

#### 響應格式

```json
{
  "status": "success",
  "sensor_id": 1,
  "processed": 2,
  "message": "Successfully processed 2 data points"
}
```

---

### 2. 流式推送端點

**端點**: `POST /api/sensor/data/stream`

**用途**: 接收高頻感測器數據（陣列形式，適用於大批量數據）

#### 請求格式

使用 Query Parameters:

```
POST /api/sensor/data/stream?sensor_id=1&h_acc=0.1234,0.1256&v_acc=0.0987,0.1001&timestamp_start=2026-01-20T10:30:00.123&sampling_rate=25600
```

#### 參數說明

| 參數 | 類型 | 說明 | 預設值 |
|------|------|------|--------|
| sensor_id | integer | 感測器 ID | - |
| h_acc | array of float | 水平加速度陣列 | - |
| v_acc | array of float | 垂直加速度陣列 | - |
| timestamp_start | string | 起始時間戳 (ISO 8601) | - |
| sampling_rate | float | 採樣率 Hz | 25600.0 |

#### 響應格式

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

---

## 數據處理流程

```
機台數據
    │
    ▼
POST /api/sensor/data 或 /api/sensor/data/stream
    │
    ├─► BufferManager.add_data()
    │   ├─► 記憶體循環緩衝區 (1 秒 @ 25.6 kHz)
    │   └─► Redis Streams (臨時持久化, 24h TTL)
    │
    └─► RealTimeAnalyzer._analysis_loop() (10 Hz)
        ├─► 提取特徵 (RMS, Kurtosis, etc.)
        ├─► 儲存到 PostgreSQL
        ├─► 快取到 Redis
        ├─► 廣播到 WebSocket (前端接收)
        └─► 檢查閾值 (生成警報)
```

---

## 使用範例

### Python 範例 1: 單次推送

```python
import requests
from datetime import datetime

API_URL = "http://localhost:8081/api/sensor/data"

# 準備數據
payload = {
    "sensor_id": 1,
    "data": [
        {
            "timestamp": datetime.now().isoformat(),
            "h_acc": 0.1234,
            "v_acc": 0.0987
        },
        {
            "timestamp": datetime.now().isoformat(),
            "h_acc": 0.1256,
            "v_acc": 0.1001
        }
    ]
}

# 推送數據
response = requests.post(API_URL, json=payload)
print(response.json())
```

### Python 範例 2: 批量推送

```python
import requests
from datetime import datetime, timedelta

API_URL = "http://localhost:8081/api/sensor/data"
sampling_rate = 25600

# 生成 1 秒的數據
data_points = []
start_time = datetime.now()

for i in range(sampling_rate):
    timestamp = start_time + timedelta(microseconds=i * (1000000 / sampling_rate))
    data_points.append({
        "timestamp": timestamp.isoformat(),
        "h_acc": 0.1234 + i * 0.0001,  # 模擬數據
        "v_acc": 0.0987 + i * 0.00005
    })

# 推送數據
payload = {
    "sensor_id": 1,
    "data": data_points
}

response = requests.post(API_URL, json=payload)
print(response.json())
```

### Python 範例 3: 流式推送 (高效)

```python
import requests
from datetime import datetime
import numpy as np

API_URL = "http://localhost:8081/api/sensor/data/stream"

# 生成陣列數據
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

const API_URL = 'http://localhost:8081/api/sensor/data';

// 準備數據
const sensorId = 1;
const dataPoints = [];

for (let i = 0; i < 100; i++) {
  const timestamp = new Date();
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

---

## 使用測試腳本

專案提供了完整的測試腳本，位於 `scripts/test_sensor_data_push.py`。

### 安裝依賴

```bash
uv pip install requests
```

### 基本用法

```bash
# 查看幫助
uv run python scripts/test_sensor_data_push.py --help

# 推送單次小批量 (100 點)
uv run python scripts/test_sensor_data_push.py --mode single --samples 100

# 推送大批量流式數據 (25600 點 = 1 秒 @ 25.6 kHz)
uv run python scripts/test_sensor_data_push.py --mode stream --samples 25600

# 持續推送 1 分鐘
uv run python scripts/test_sensor_data_push.py --mode continuous --duration 60

# 持續推送無限時間 (按 Ctrl+C 停止)
uv run python scripts/test_sensor_data_push.py --mode continuous

# 自訂後端 URL
uv run python scripts/test_sensor_data_push.py --mode continuous --url http://192.168.1.100:8081

# 指定感測器 ID
uv run python scripts/test_sensor_data_push.py --mode continuous --sensor-id 2

# 調整推送間隔
uv run python scripts/test_sensor_data_push.py --mode continuous --interval 0.5
```

### 輸出示例

```
檢查伺服器: http://localhost:8081
✓ 伺服器運行正常

開始持續推送模式...
  - 感測器 ID: 1
  - 批次大小: 25600
  - 推送間隔: 1.0 秒
  - 按 Ctrl+C 停止
--------------------------------------------------
已推送 5 批次 (128000 點) - 平均速率: 4.95 批次/秒
已推送 10 批次 (256000 點) - 平均速率: 4.97 批次/秒
...
--------------------------------------------------
總計:
  - 推送批次: 60
  - 數據點數: 1536000
  - 運行時間: 60.12 秒
  - 平均速率: 0.99 批次/秒
```

---

## 機台整合

### 推薦架構

```
┌──────────┐
│  機台   │
│ (DAQ)   │
└────┬─────┘
     │ 採集
     ▼
┌──────────────┐
│  Python     │
│  推送程式   │
└────┬───────┘
     │ HTTP POST
     ▼
┌────────────────────────┐
│  Buffer Manager      │
│  (記憶體 + Redis)   │
└────┬───────────────┘
     │ 10 Hz 分析
     ▼
┌──────────────────────┐
│  RealTime Analyzer  │
│  (特徵提取 + 警報) │
└──────────────────────┘
```

### 整合步驟

1. **資料獲取**: 從機台 DAQ 系統讀取振動數據
2. **資料轉換**: 轉換為 API 要求的格式
3. **資料推送**: 使用批量或流式 API 推送
4. **監控**: 通過 WebSocket 接收即時特徵和警報

### 程式碼範例 (真實機台整合)

```python
import requests
import time
import numpy as np
from datetime import datetime, timedelta
from daq_module import DAQDevice  # 假設的 DAQ 庫

# 配置
API_URL = "http://localhost:8081/api/sensor/data"
SENSOR_ID = 1
SAMPLING_RATE = 25600  # 25.6 kHz
BATCH_SIZE = 25600     # 1 秒每批次

# 初始化 DAQ 設備
daq = DAQDevice(port="/dev/ttyUSB0", baudrate=115200)

class MachineDataStreamer:
    def __init__(self, sensor_id, sampling_rate, batch_size):
        self.sensor_id = sensor_id
        self.sampling_rate = sampling_rate
        self.batch_size = batch_size
        self.running = False

    def start(self):
        """啟動機台數據推送"""
        self.running = True
        counter = 0

        while self.running:
            try:
                # 1. 從機台採集數據
                raw_data = daq.read_samples(
                    channels=["h_acc", "v_acc"],
                    num_samples=self.batch_size
                )

                # 2. 轉換為 API 格式
                start_time = datetime.now()
                data_points = []

                for i in range(self.batch_size):
                    timestamp = start_time + timedelta(
                        microseconds=i * (1000000 / self.sampling_rate)
                    )
                    data_points.append({
                        "timestamp": timestamp.isoformat(),
                        "h_acc": raw_data["h_acc"][i],
                        "v_acc": raw_data["v_acc"][i]
                    })

                # 3. 推送到後端
                payload = {
                    "sensor_id": self.sensor_id,
                    "data": data_points
                }

                response = requests.post(API_URL, json=payload, timeout=10)
                if response.status_code == 200:
                    counter += 1
                    if counter % 10 == 0:
                        print(f"已推送 {counter} 批次 ({counter * self.batch_size} 點)")
                else:
                    print(f"推送失敗: {response.status_code}")

            except Exception as e:
                print(f"錯誤: {e}")
                time.sleep(1)

    def stop(self):
        """停止推送"""
        self.running = False

# 使用範例
if __name__ == "__main__":
    streamer = MachineDataStreamer(SENSOR_ID, SAMPLING_RATE, BATCH_SIZE)

    try:
        print("啟動機台數據推送...")
        streamer.start()
    except KeyboardInterrupt:
        print("\n停止推送...")
        streamer.stop()
```

---

## 注意事項

### 效能建議

1. **批次大小**: 建議每次推送 25600 點（1 秒 @ 25.6 kHz）或更大
2. **推送頻率**: 保持與採樣率一致的頻率（如每秒推送一次）
3. **網路延遲**: 確保機台與後端之間的網路延遲 < 50ms
4. **資料壓縮**: 如需傳輸大量數據，可考慮使用壓縮

### 數據品質

1. **時間同步**: 確保時間戳準確，使用 NTP 同步
2. **數值精度**: 使用 6 位小數精確度
3. **缺失值**: 不要發送 NaN 或 Inf，使用 null 或過濾掉
4. **採樣率**: 保持穩定的採樣率，避免抖動

### 錯誤處理

1. **重試機制**: 網路失敗時實施指數退避重試
2. **緩衝機制**: 在機台端緩衝數據，防止網路中斷時數據丟失
3. **日誌記錄**: 記錄推送成功/失敗的統計
4. **狀態監控**: 監控後端 `/api/stream/status` 以確保系統正常

### 安全性

1. **API 認證**: 如需安全，在後端添加 API Key 或 JWT 驗證
2. **HTTPS**: 生產環境使用 HTTPS
3. **速率限制**: 在後端實施速率限制以防濫用

---

## 故障排除

### 常見問題

**Q: 推送失敗，返回 500 錯誤**
- 檢查後端是否正在運行
- 檢查數據格式是否正確
- 查看後端日誌了解具體錯誤

**Q: 數據推送後看不到分析結果**
- 確認已透過 WebSocket 連接 (`ws://localhost:8081/ws/realtime/{sensor_id}`)
- 確認分析任務已啟動 (`POST /api/stream/start`)
- 檢查數據量是否足夠（>= 10000 樣本）

**Q: 延遲過高**
- 檢查網路連接
- 考慮使用流式 API (`/api/sensor/data/stream`)
- 增大批次大小減少請求次數

---

## 相關文檔

- [即時分析與監控機制](./RealTimeAnalysis.md) - 完整的即時系統說明
- [API 說明](./API.md) - 完整 API 文檔 (如存在)
