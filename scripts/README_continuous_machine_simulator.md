# 持續數據推送模擬機台

## 概述

`continuous_machine_simulator.py` 是根據 `docs/RealTimeAnalysis.md` 第 970-1045 行的範例實作的完整機台模擬程式。

## 功能特點

- ✅ **持續推送**: 模擬機台持續推送振動數據 (25.6 kHz 採樣率)
- ✅ **真實信號**: 生成正弦波疊加 + 高斯噪音的模擬振動信號
- ✅ **多線程**: 在獨立的 daemon 線程中運行，不阻塞主程序
- ✅ **統計資訊**: 實時追蹤推送速率、數據量、成功率
- ✅ **錯誤處理**: 自動重試機制，優雅的中斷處理
- ✅ **靈活配置**: 支持命令行參數配置

## 安裝依賴

```bash
# 使用 uv (推薦)
uv pip install requests numpy

# 或使用 pip
pip install requests numpy
```

## 使用方法

### 1. 基本用法

使用預設配置啟動 (感測器 ID=1, 本地後端):

```bash
uv run python scripts/continuous_machine_simulator.py
```

### 2. 指定感測器 ID

```bash
uv run python scripts/continuous_machine_simulator.py --sensor-id 2
```

### 3. 指定後端 URL

```bash
uv run python scripts/continuous_machine_simulator.py --url http://192.168.1.100:8081
```

### 4. 指定運行時長

自動在指定秒數後停止:

```bash
# 運行 60 秒後自動停止
uv run python scripts/continuous_machine_simulator.py --duration 60

# 運行 5 分鐘
uv run python scripts/continuous_machine_simulator.py --duration 300
```

### 5. 查看幫助

```bash
uv run python scripts/continuous_machine_simulator.py --help
```

## 命令行參數

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `--sensor-id` | int | 1 | 感測器 ID |
| `--url` | string | http://localhost:8081 | 後端 API 基礎 URL |
| `--duration` | int | 無限制 | 運行時長（秒） |

## 輸出示例

```
2026-01-21 10:30:00 - __main__ - INFO - ✓ 後端伺服器運行正常: http://localhost:8081
2026-01-21 10:30:00 - __main__ - INFO - ==================================================
2026-01-21 10:30:00 - __main__ - INFO - 持續數據推送已啟動
2026-01-21 10:30:00 - __main__ - INFO -   感測器 ID: 1
2026-01-21 10:30:00 - __main__ - INFO -   採樣率: 25600 Hz
2026-01-21 10:30:00 - __main__ - INFO -   批次大小: 25600 樣本 (1 秒)
2026-01-21 10:30:00 - __main__ - INFO -   API 端點: http://localhost:8081/api/sensor/data
2026-01-21 10:30:00 - __main__ - INFO -   按 Ctrl+C 停止
2026-01-21 10:30:00 - __main__ - INFO - ==================================================
2026-01-21 10:30:10 - __main__ - INFO - 已推送 10 批次 (256000 點) - 平均速率: 0.99 批次/秒
2026-01-21 10:30:20 - __main__ - INFO - 已推送 20 批次 (512000 點) - 平均速率: 1.00 批次/秒
...
^C2026-01-21 10:31:00 - __main__ - INFO -
收到中斷信號
2026-01-21 10:31:00 - __main__ - INFO - 正在停止數據推送...
2026-01-21 10:31:00 - __main__ - INFO - ==================================================
2026-01-21 10:31:00 - __main__ - INFO - 數據推送已停止
2026-01-21 10:31:00 - __main__ - INFO - 統計摘要:
2026-01-21 10:31:00 - __main__ - INFO -   總推送批次: 60
2026-01-21 10:31:00 - __main__ - INFO -   總數據點數: 1536000
2026-01-21 10:31:00 - __main__ - INFO -   運行時間: 60.12 秒
2026-01-21 10:31:00 - __main__ - INFO -   平均速率: 0.99 批次/秒
2026-01-21 10:31:00 - __main__ - INFO -   成功次數: 60
2026-01-21 10:31:00 - __main__ - INFO -   錯誤次數: 0
2026-01-21 10:31:00 - __main__ - INFO -   成功率: 100.0%
2026-01-21 10:31:00 - __main__ - INFO - ==================================================
```

## 程式架構

### 類別: ContinuousDataStreamer

```python
streamer = ContinuousDataStreamer(
    sensor_id=1,                    # 感測器 ID
    api_url="http://localhost:8081" # 後端 URL
)

# 啟動推送
streamer.start()

# 停止推送
streamer.stop()

# 獲取統計
stats = streamer.get_stats()
```

### 主要方法

| 方法 | 說明 |
|------|------|
| `start()` | 啟動持續推送 (在獨立線程中運行) |
| `stop()` | 停止推送並輸出統計 |
| `get_stats()` | 獲取當前統計資訊 |

### 模擬信號生成

程式使用 `_generate_vibration_signal()` 方法生成真實的振動信號:

```python
# 多個頻率的正弦波疊加 + 高斯噪音
h_acc = (
    0.05 * np.sin(2 * np.pi * 10 * t) +      # 基頻 10 Hz
    0.02 * np.sin(2 * np.pi * 50 * t) +      # 諧波 50 Hz
    0.01 * np.sin(2 * np.pi * 100 * t) +     # 諧波 100 Hz
    np.random.normal(0, 0.1, num_samples)     # 高斯噪音
)
```

## 與其他測試工具的比較

| 工具 | 適用場景 | 特點 |
|------|----------|------|
| `test_sensor_data_push.py` | 單次測試、短時間測試 | 支持多種模式 (single/stream/continuous) |
| `continuous_machine_simulator.py` | 長時間穩定運行、壓力測試 | 專注於持續推送，更真實的機台模擬 |

## 整合到真實機台

若要整合到真實的機台 DAQ 系統，修改 `_stream_loop()` 方法:

```python
def _stream_loop(self):
    from daq_module import DAQDevice  # 你的 DAQ 庫

    # 初始化 DAQ 設備
    daq = DAQDevice(port="/dev/ttyUSB0", baudrate=115200)

    while self.running:
        # 1. 從機台讀取數據
        raw_data = daq.read_samples(
            channels=["h_acc", "v_acc"],
            num_samples=self.batch_size
        )

        # 2. 轉換格式並推送
        # ... (其餘邏輯不變)
```

## 故障排除

### 後端未運行

```
✗ 無法連接到後端伺服器: Connection refused
```

**解決方法**: 先啟動後端服務

```bash
cd backend
uv run uvicorn main:app --host 0.0.0.0 --port 8081
```

### 推送失敗

```
推送失敗: HTTP 500 Internal Server Error
```

**解決方法**: 檢查後端日誌，確認 Buffer Manager 和數據庫正常運行

### 採樣率不匹配

確保機台採樣率與程式配置一致 (預設 25600 Hz)

## 相關文檔

- [即時分析與監控機制](../docs/RealTimeAnalysis.md) - 完整的即時系統說明
- [機台 Sensor Data 推送指南](../docs/SensorDataPushGuide.md) - API 使用說明
- [測試腳本](./test_sensor_data_push.py) - 其他測試工具

## 授權

本程式碼根據專案授權條款使用。
