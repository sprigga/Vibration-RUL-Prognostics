# 振動分析演算法整合說明

本文件說明如何將 `backend/timefrequency.py` 的各種演算法整合到前後端系統中。

## 整合概覽

所有演算法已完整整合到 **Algorithms.vue** 頁面中，使用者可以透過網頁介面即時計算和視覺化各種振動分析結果。

## 已整合的演算法

### 1. 時域特徵分析 (Time Domain Features)
- **後端 API**: `/api/algorithms/time-domain/{bearing_name}/{file_number}`
- **實作模組**: `backend/timedomain.py`
- **計算特徵**:
  - Peak（峰值）
  - RMS（均方根值）
  - Crest Factor（波峰因數）
  - Kurtosis（峰度）
- **視覺化**: 振動信號波形圖
- **趨勢分析**: `/api/algorithms/time-domain-trend/{bearing_name}`

### 2. 頻域特徵分析 (Frequency Domain Features)

#### 2.1 低頻 FFT (FM0)
- **後端 API**: `/api/algorithms/frequency-fft/{bearing_name}/{file_number}`
- **實作模組**: `backend/frequencydomain.py`
- **計算特徵**:
  - Low FM0（低頻正規化峰值）
  - Total FFT Magnitude
  - Total FFT BI
- **視覺化**: FFT 頻譜圖

#### 2.2 高頻 TSA (FM0)
- **後端 API**: `/api/algorithms/frequency-tsa/{bearing_name}/{file_number}`
- **實作模組**: `backend/frequencydomain.py`
- **計算特徵**:
  - High FM0（高頻正規化峰值）
  - TSA FFT Magnitude
  - TSA FFT BI
- **視覺化**: TSA 頻譜圖

### 3. 包絡分析 (Envelope Analysis)
- **後端 API**: `/api/algorithms/envelope/{bearing_name}/{file_number}`
- **實作模組**: `backend/timefrequency.py` → `envelope_analysis()`
- **處理流程**:
  1. 帶通濾波（預設 4000-10000 Hz）
  2. 希爾伯特轉換
  3. 提取包絡
  4. FFT 分析
- **計算特徵**:
  - Envelope RMS
  - Peak Frequencies
  - Peak Magnitudes
- **視覺化**: 包絡頻譜圖
- **應用**: 滾動體缺陷檢測

### 4. 短時傅立葉轉換 (STFT)
- **後端 API**: `/api/algorithms/stft/{bearing_name}/{file_number}`
- **實作模組**: `backend/timefrequency.py` → `stft_analysis()`
- **參數**:
  - 窗函數: Hann / Flattop / Hamming
  - 窗長: 256 點
  - 重疊: 95%
- **計算特徵**:
  - NP4（正規化四次矩）
  - Max Frequency
  - Max Time
  - Total Energy
- **視覺化**: 時頻熱力圖（Heatmap）
- **應用**: 時頻能量分佈分析

### 5. 連續小波轉換 (CWT)
- **後端 API**: `/api/algorithms/cwt/{bearing_name}/{file_number}`
- **實作模組**: `backend/timefrequency.py` → `cwt_analysis()`
- **參數**:
  - 小波基: Morlet / Ricker
  - 尺度: 1-64
- **計算特徵**:
  - NP4
  - Max Scale
  - Max Frequency
  - Energy per Scale
  - Total Energy
- **視覺化**:
  - 小波係數熱力圖
  - 各尺度能量分布圖
- **應用**: 瞬態衝擊檢測、非穩態信號分析

### 6. 高階統計 (Higher Order Statistics)
- **後端 API**: `/api/algorithms/higher-order/{bearing_name}/{file_number}`
- **實作模組**: `backend/timefrequency.py` → `higher_order_statistics()`
- **計算特徵**:
  - NA4（正規化四次矩，帶分段）
  - FM4（四次矩比值）
  - M6A（六次矩）
  - M8A（八次矩）
  - ER（能量比）
  - Kurtosis（峰度）
- **視覺化**: 特徵比較柱狀圖
- **應用**: 早期故障檢測、微小缺陷識別

### 7. 頻譜圖 (Spectrogram)
- **後端 API**: `/api/algorithms/spectrogram/{bearing_name}/{file_number}`
- **實作模組**: `backend/timefrequency.py` → `spectrogram_features()`
- **計算特徵**:
  - Mean Power (dB)
  - Max Power (dB)
  - Std Power (dB)
  - Peak Frequency
  - Peak Time
- **視覺化**: 時頻功率熱力圖
- **應用**: 整體時頻特徵分析

## 資料流程

```
SQLite Database (phm_data.db)
    ↓
Backend API (FastAPI)
    ↓ [查詢振動數據]
TimeFrequency Module
    ↓ [演算法計算]
JSON Response
    ↓ [HTTP]
Frontend (Vue.js)
    ↓ [ECharts]
視覺化圖表
```

## 前端使用方式

### 操作步驟：

1. **開啟 Algorithms 頁面**
   - 導航至 `/algorithms` 路由

2. **選擇演算法**
   - 點擊折疊面板展開特定演算法區塊

3. **設定參數**
   - 選擇軸承（Bearing1_1, Bearing1_2 等）
   - 選擇檔案編號（1-100）
   - 設定演算法特定參數（如窗函數、濾波頻率等）

4. **執行計算**
   - 點擊「計算」按鈕
   - 系統自動呼叫後端 API

5. **查看結果**
   - 特徵數值顯示在右側卡片
   - 視覺化圖表顯示在下方

## 圖表類型

| 演算法 | 圖表類型 | ECharts 配置 |
|--------|----------|--------------|
| Time Domain | 折線圖 (Line) | 水平/垂直方向波形 |
| Time Domain Trend | 雙軸折線圖 | RMS + Kurtosis 趨勢 |
| Frequency FFT/TSA | 折線圖 + DataZoom | 頻譜圖 |
| Envelope | 折線圖 + DataZoom | 包絡頻譜 |
| STFT | 熱力圖 (Heatmap) | 時頻能量分布 |
| CWT | 熱力圖 + 折線圖 | 小波係數 + 能量分布 |
| Higher Order | 柱狀圖 (Bar) | 特徵比較 |
| Spectrogram | 熱力圖 (Heatmap) | 時頻功率分布 |

## 後端實作細節

### API 端點模式

所有演算法端點遵循相同模式：

```python
@app.get("/api/algorithms/{algorithm_name}/{bearing_name}/{file_number}")
async def calculate_algorithm(bearing_name: str, file_number: int, ...):
    # 1. 連接資料庫
    conn = sqlite3.connect(PHM_DATABASE_PATH)

    # 2. 查詢數據
    query = """
    SELECT m.horizontal_acceleration, m.vertical_acceleration
    FROM measurements m
    JOIN measurement_files mf ON m.file_id = mf.file_id
    JOIN bearings b ON mf.bearing_id = b.bearing_id
    WHERE b.bearing_name = ? AND mf.file_number = ?
    """
    df = pd.read_sql_query(query, conn, params=(bearing_name, file_number))

    # 3. 計算特徵
    horiz = df['horizontal_acceleration'].values
    vert = df['vertical_acceleration'].values

    tf = TimeFrequency()
    horiz_result = tf.algorithm_method(horiz, fs=sampling_rate, ...)
    vert_result = tf.algorithm_method(vert, fs=sampling_rate, ...)

    # 4. 組織回應
    return {
        "bearing_name": bearing_name,
        "file_number": file_number,
        "horizontal": horiz_result,
        "vertical": vert_result,
        "visualization_data": {...}
    }
```

### 資料庫查詢優化

- 使用 JOIN 減少查詢次數
- 使用參數化查詢防止 SQL 注入
- 只查詢需要的欄位

### 回應資料限制

為避免前端性能問題，返回的視覺化數據有限制：

- STFT/CWT 熱力圖：最多 100×100 點
- FFT 頻譜：前 500 個頻率點
- 時域信號：前 1000 個樣本點

## 測試

執行整合測試：

```bash
# 確保後端服務運行
cd backend
uvicorn main:app --host 0.0.0.0 --port 8081 --reload

# 執行測試腳本（另一個終端）
cd /home/ubuntu/vibration_signals
python test_algorithms_integration.py
```

測試涵蓋：
- ✓ 所有 API 端點可訪問
- ✓ 回應格式正確
- ✓ 必要欄位完整
- ✓ 數據類型正確

## 診斷準則參考

### 時域特徵
- RMS 緩慢上升 → 磨損加劇
- Kurtosis > 8 → 嚴重衝擊
- RMS 突然下降 → 預壓失效

### 頻域特徵
- 出現 BPF 及諧波 → 滾動體缺陷
- 邊帶能量增加 → 調變現象

### 包絡分析
- 包絡譜出現 BPF → 滾動體或軌道缺陷
- SNR > 3 → 缺陷顯著

### 高階統計
- NA4 > 3 → 早期微裂紋
- FM4 異常 → 邊帶能量增加
- M6A/M8A 上升 → 潤滑不良

## 進階功能建議

### 1. 批次分析
可擴展為批次處理多個軸承/檔案：

```python
@app.post("/api/algorithms/batch-analysis")
async def batch_analysis(request: BatchAnalysisRequest):
    results = []
    for bearing, file_num in request.items:
        result = calculate_all_features(bearing, file_num)
        results.append(result)
    return {"results": results}
```

### 2. 匯出功能
增加結果匯出為 CSV/Excel：

```python
@app.get("/api/algorithms/export/{bearing_name}/{file_number}")
async def export_results(...):
    # 計算所有特徵
    # 組織成 DataFrame
    # 匯出為 CSV
    return FileResponse(csv_path)
```

### 3. 即時監控
使用 WebSocket 實現即時資料推送：

```python
@app.websocket("/ws/realtime-monitoring")
async def realtime_monitoring(websocket: WebSocket):
    # 持續推送最新計算結果
    pass
```

## 相關文件

- [backend/main.py](../backend/main.py) - API 端點定義（L330-L919）
- [backend/timefrequency.py](../backend/timefrequency.py) - 時頻分析模組
- [backend/timedomain.py](../backend/timedomain.py) - 時域分析模組
- [backend/frequencydomain.py](../backend/frequencydomain.py) - 頻域分析模組
- [frontend/src/views/Algorithms.vue](../frontend/src/views/Algorithms.vue) - 前端介面
- [test_algorithms_integration.py](../test_algorithms_integration.py) - 整合測試

## 聯絡資訊

如有問題或建議，請參考專案 README 或提交 Issue。
