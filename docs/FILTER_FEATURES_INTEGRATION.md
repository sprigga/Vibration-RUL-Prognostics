# 進階濾波特徵整合文件

## 概述

本文件說明如何將 `filterprocess.py` 中的進階濾波演算法整合到振動信號分析系統中。

## 整合的演算法

### 1. NA4（分段正規化四次矩）
- **公式**: `NA4 = N·Σ(x-μ)⁴ / [Σ(x-μ_segment)²/M]²`
- **用途**: 通過分段計算檢測諧波能量異常
- **應用**: 早期微裂紋檢測
- **診斷閾值**: NA4 > 3 表示存在早期微裂紋

### 2. FM4（四次矩特徵）
- **公式**: `FM4 = N·Σ(x-μ)⁴ / [Σ(x-μ)²]²`
- **用途**: 檢測邊帶能量異常
- **應用**: 判斷是否存在調製現象
- **診斷**: FM4 異常表示邊帶能量增加

### 3. M6A（六次矩特徵）
- **公式**: `M6A = N²·Σ(x-μ)⁶ / [Σ(x-μ)²]³`
- **用途**: 對極早期故障敏感
- **應用**: 極早期故障檢測
- **診斷**: M6A 上升表示潤滑不良或極早期故障

### 4. M8A（八次矩特徵）
- **公式**: `M8A = N³·Σ(x-μ)⁸ / [Σ(x-μ)²]⁴`
- **用途**: 對潤滑不良和極早期故障高度敏感
- **應用**: 潤滑狀態監測
- **診斷**: M8A 上升表示嚴重潤滑問題

### 5. ER（能量比）
- **公式**: `ER = E_band / E_total`
- **用途**: 特定頻帶能量占總能量的比例
- **應用**: 特定故障頻率能量分析
- **診斷**: ER 增大表示特定頻帶能量集中

## 後端實作

### 新增模組
```
backend/filterprocess.py
```

主要功能:
- `FilterProcess.NA4()`: 計算分段正規化四次矩
- `FilterProcess.FM4()`: 計算四次矩特徵
- `FilterProcess.M6A()`: 計算六次矩特徵
- `FilterProcess.M8A()`: 計算八次矩特徵
- `FilterProcess.ER_simple()`: 計算簡化能量比
- `FilterProcess.calculate_all_features()`: 計算所有特徵

### API 端點

#### 1. 計算進階濾波特徵
```
GET /api/algorithms/filter-features/{bearing_name}/{file_number}
```

參數:
- `bearing_name`: 軸承名稱 (例如: Bearing1_1)
- `file_number`: 檔案編號
- `sampling_rate`: 採樣頻率 (可選，默認 25600 Hz)
- `segment_count`: 分段數量 (可選，默認 10)

返回:
```json
{
  "bearing_name": "Bearing1_1",
  "file_number": 1,
  "data_points": 20480,
  "sampling_rate": 25600,
  "segment_count": 10,
  "horizontal": {
    "na4": 2.45,
    "fm4": 3.12,
    "m6a": 0.0234,
    "m8a": 0.000567,
    "er": 0.123,
    "kurtosis": 3.45,
    "peak": 2.34,
    "rms": 0.456
  },
  "vertical": {
    "na4": 2.67,
    "fm4": 3.34,
    "m6a": 0.0256,
    "m8a": 0.000623,
    "er": 0.145,
    "kurtosis": 3.67,
    "peak": 2.56,
    "rms": 0.478
  }
}
```

#### 2. 計算進階濾波特徵趨勢
```
GET /api/algorithms/filter-trend/{bearing_name}
```

參數:
- `bearing_name`: 軸承名稱
- `max_files`: 最大檔案數 (可選，默認 50)
- `sampling_rate`: 採樣頻率 (可選，默認 25600 Hz)

返回:
```json
{
  "bearing_name": "Bearing1_1",
  "file_count": 50,
  "horizontal": {
    "na4": [2.34, 2.45, 2.56, ...],
    "fm4": [3.12, 3.23, 3.34, ...],
    "m6a": [0.0234, 0.0245, 0.0256, ...],
    "m8a": [0.000567, 0.000589, 0.000612, ...],
    "er": [0.123, 0.134, 0.145, ...]
  },
  "vertical": {
    "na4": [2.45, 2.56, 2.67, ...],
    "fm4": [3.23, 3.34, 3.45, ...],
    "m6a": [0.0245, 0.0256, 0.0267, ...],
    "m8a": [0.000589, 0.000612, 0.000634, ...],
    "er": [0.134, 0.145, 0.156, ...]
  },
  "file_numbers": [1, 2, 3, ..., 50]
}
```

## 前端實作

### 新增區塊

在 `frontend/src/views/Algorithms.vue` 中新增「進階濾波特徵」折疊區塊。

### 功能特性

1. **即時計算演示**
   - 選擇軸承
   - 設定檔案編號
   - 設定分段數量
   - 執行計算

2. **結果顯示**
   - NA4, FM4, M6A, M8A, ER 的水平和垂直方向數值
   - 結果以表格形式呈現
   - 高精度數值顯示（M8A 顯示到小數點後8位）

3. **視覺化圖表**
   - **比較圖**: 水平與垂直方向的特徵值柱狀圖比較
   - **趨勢圖**: 多個檔案的特徵值變化趨勢線圖

### JavaScript 函數

- `calculateFilterFeatures()`: 計算單一檔案的進階濾波特徵
- `calculateFilterTrend()`: 計算多個檔案的趨勢
- `drawFilterChart()`: 繪製特徵比較柱狀圖
- `drawFilterTrendChart()`: 繪製趨勢線圖

## 使用方式

### 1. 啟動後端服務

使用 uv 切換到正確的 Python 環境:

```bash
cd /home/ubuntu/vibration_signals
uv run python -m uvicorn backend.main:app --host 0.0.0.0 --port 8081 --reload
```

### 2. 啟動前端服務

```bash
cd frontend
npm run dev
```

### 3. 訪問演算法頁面

1. 開啟瀏覽器訪問前端地址
2. 導航到「演算法原理與應用展示」頁面
3. 找到「進階濾波特徵 (NA4, FM4, M6A, M8A, ER)」折疊區塊
4. 選擇軸承和檔案編號
5. 點擊「計算濾波特徵」或「計算趨勢分析」按鈕

## 測試範例

### 測試單一檔案計算

```bash
# 使用 curl 測試 API
curl "http://localhost:8081/api/algorithms/filter-features/Bearing1_1/1?segment_count=10"
```

### 測試趨勢計算

```bash
curl "http://localhost:8081/api/algorithms/filter-trend/Bearing1_1?max_files=20"
```

## 診斷應用範例

### 早期微裂紋檢測
```
IF horizontal.na4 > 3 OR vertical.na4 > 3:
    → 可能存在早期微裂紋
    → 建議: 增加監測頻率，進行包絡分析確認
```

### 潤滑狀態評估
```
IF horizontal.m8a > 0.001 OR vertical.m8a > 0.001:
    → 潤滑狀態可能不良
    → 建議: 檢查潤滑系統，必要時補充潤滑劑
```

### 調製現象檢測
```
IF horizontal.fm4 > 5 OR vertical.fm4 > 5:
    → 存在明顯調製現象
    → 建議: 進行邊帶分析，檢查是否有鬆動或安裝問題
```

## 技術細節

### 資料流程

1. 前端發送 API 請求
2. 後端從 SQLite 資料庫讀取振動數據
3. 使用 `FilterProcess` 類別計算各項特徵
4. 返回 JSON 格式結果
5. 前端使用 ECharts 繪製圖表

### 性能考量

- 單一檔案計算通常在 1 秒內完成
- 趨勢分析（50 個檔案）約需 10-30 秒
- 大型數據集建議使用分批處理

### 錯誤處理

- 資料庫連接錯誤
- 檔案不存在錯誤
- 計算過程中的數值錯誤（除以零等）
- 所有錯誤都會返回詳細的錯誤訊息

## 相關文件

- `backend/filterprocess.py`: 濾波處理模組源碼
- `backend/main.py`: API 端點定義
- `frontend/src/views/Algorithms.vue`: 前端視覺化組件
- `docs/ALGORITHMS_INTEGRATION.md`: 整體演算法整合文件

## 更新日誌

### 2025-01-XX
- 初始版本
- 整合 NA4, FM4, M6A, M8A, ER 五種進階濾波特徵
- 新增單一檔案計算和趨勢分析API
- 前端新增視覺化圖表展示

## 後續改進建議

1. **性能優化**: 使用多進程處理大量檔案的趨勢計算
2. **快取機制**: 對已計算的結果進行快取
3. **自動診斷**: 根據特徵值自動生成診斷建議
4. **匯出功能**: 支援將計算結果匯出為 CSV 或 Excel
5. **批次分析**: 支援一次分析多個軸承
