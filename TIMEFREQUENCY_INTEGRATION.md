# 時頻域分析整合說明

## 概述

本次整合完成了時頻域分析算法到振動分析系統中，參照 `backend/timedomain.py` 和 `frontend/src/views/Algorithms.vue` 的實作模式。

## 已完成的工作

### 1. 後端模組 - `backend/timefrequency.py`

新建立的時頻分析模組包含以下主要功能：

#### 1.1 短時傅立葉轉換 (STFT)
```python
TimeFrequency.stft_analysis(x, fs=25600, window='hann', nperseg=256, noverlap=None)
```
- **功能**: 計算短時傅立葉轉換
- **參數**:
  - `x`: 輸入信號
  - `fs`: 採樣率 (默認 25600 Hz)
  - `window`: 窗函數類型 ('hann', 'flattop', 'hamming')
  - `nperseg`: 窗長 (默認 256)
  - `noverlap`: 重疊樣本數 (默認 95%)
- **返回值**:
  - NP4 特徵值
  - 最大頻率、時間、幅值
  - 總能量
  - 頻譜數據

#### 1.2 連續小波轉換 (CWT)
```python
TimeFrequency.cwt_analysis(x, fs=25600, wavelet='morl', scales=None)
```
- **功能**: 計算連續小波轉換
- **參數**:
  - `x`: 輸入信號
  - `fs`: 採樣率
  - `wavelet`: 小波基函數 ('morl' 為 Morlet, 'ricker' 等)
  - `scales`: 尺度數組 (默認 1-64)
- **返回值**:
  - NP4 特徵值
  - 最大尺度及對應頻率
  - 各尺度能量分布
  - 總能量

#### 1.3 包絡分析
```python
TimeFrequency.envelope_analysis(x, fs=25600, lowcut=4000, highcut=10000)
```
- **功能**: 希爾伯特轉換包絡分析
- **參數**:
  - `x`: 輸入信號
  - `fs`: 採樣率
  - `lowcut`: 帶通濾波器低截止頻率
  - `highcut`: 帶通濾波器高截止頻率
- **返回值**:
  - 包絡信號
  - 包絡頻譜
  - 峰值頻率
  - RMS 和總功率

#### 1.4 高階統計分析
```python
TimeFrequency.higher_order_statistics(x, fs=25600, M=8)
```
- **功能**: 計算高階統計特徵
- **參數**:
  - `x`: 輸入信號
  - `fs`: 採樣率
  - `M`: 分段數量
- **返回值**:
  - NA4: 正規化四次矩
  - FM4: 四次矩比值
  - M6A: 六次矩
  - M8A: 八次矩
  - ER: 能量比
  - Kurtosis: 峰度

#### 1.5 頻譜圖特徵
```python
TimeFrequency.spectrogram_features(x, fs=25600, window='hann', nperseg=256)
```
- **功能**: 計算頻譜圖及統計特徵
- **返回值**:
  - 功率譜密度 (dB)
  - 平均、最大、標準差功率
  - 峰值頻率和時間

#### 1.6 瞬時頻率
```python
TimeFrequency.instantaneous_frequency(x, fs=25600)
```
- **功能**: 計算瞬時頻率
- **返回值**:
  - 瞬時頻率序列
  - 統計特徵 (均值、標準差、最大/最小值)

### 2. 後端 API 端點 - `backend/main.py`

新增了以下 RESTful API 端點：

#### 2.1 STFT 計算
```
GET /api/algorithms/stft/{bearing_name}/{file_number}
參數: sampling_rate, window, nperseg
```

#### 2.2 CWT 計算
```
GET /api/algorithms/cwt/{bearing_name}/{file_number}
參數: sampling_rate, wavelet
```

#### 2.3 高階統計計算
```
GET /api/algorithms/higher-order/{bearing_name}/{file_number}
參數: sampling_rate
```

#### 2.4 頻譜圖計算
```
GET /api/algorithms/spectrogram/{bearing_name}/{file_number}
參數: sampling_rate
```

### 3. 前端整合 - `frontend/src/views/Algorithms.vue`

#### 3.1 新增的功能區塊

##### STFT 即時計算演示
- 選擇軸承和檔案編號
- 選擇窗函數 (Hann, Flattop, Hamming)
- 顯示計算結果:
  - 水平/垂直方向 NP4
  - 峰值頻率
  - 總能量
- 繪製 STFT 頻譜圖 (熱力圖)

##### CWT 即時計算演示
- 選擇軸承和檔案編號
- 選擇小波基 (Morlet, Ricker)
- 顯示計算結果:
  - 水平/垂直方向 NP4
  - 峰值尺度和頻率
- 繪製:
  - CWT 小波係數圖 (熱力圖)
  - 各尺度能量分布圖

##### 高階統計即時計算演示
- 選擇軸承和檔案編號
- 顯示計算結果:
  - NA4, FM4, M6A, M8A, ER
  - 水平/垂直方向對比
- 繪製高階統計特徵比較圖

#### 3.2 圖表類型

使用 ECharts 繪製:
1. **熱力圖 (Heatmap)**: STFT 和 CWT 時頻能量分布
2. **折線圖 (Line)**: CWT 各尺度能量分布
3. **柱狀圖 (Bar)**: 高階統計特徵比較

## 使用流程

### 後端啟動
```bash
cd backend
uv run uvicorn main:app --host 0.0.0.0 --port 8081 --reload
```

### 前端啟動
```bash
cd frontend
npm run dev
```

### 測試 API
```bash
uv run python test_timefrequency_api.py
```

## 數據流

```
SQLite Database (phm_data.db)
    ↓
API Endpoint (/api/algorithms/*)
    ↓
TimeFrequency 計算模組
    ↓
JSON 回傳給前端
    ↓
Vue.js 前端處理
    ↓
ECharts 視覺化
```

## 關鍵特徵說明

### NP4 特徵
```
NP4 = N · Σ(Z-μ)⁴ / [Σ(Z-μ)²]²
```
- 類似峰度的時頻域特徵
- 反映時頻能量分佈的集中程度
- 用於檢測瞬態衝擊和局部缺陷

### 高階統計特徵

1. **NA4** (正規化四次矩): 檢測諧波能量異常
2. **FM4** (四次矩比值): 檢測邊帶能量
3. **M6A/M8A** (六次矩/八次矩): 對極早期故障敏感
4. **ER** (能量比): 邊帶能量占比

## 應用場景

| 算法 | 適用場景 | 檢測對象 |
|------|----------|----------|
| STFT | 瞬態衝擊檢測 | 異物進入、早期微裂紋 |
| CWT | 非穩態信號分析 | 時變故障、瞬態事件 |
| 高階統計 | 早期故障檢測 | 微小缺陷、潤滑不良 |
| 包絡分析 | 週期性衝擊 | 滾動體缺陷、軌道剝落 |

## 診斷準則

### STFT/CWT
- NP4 異常升高 → 瞬態衝擊或局部缺陷
- 時頻能量集中在特定頻帶 → 共振或特徵頻率

### 高階統計
- NA4 > 3 → 早期微裂紋
- FM4 異常 → 邊帶能量增加
- M6A/M8A 上升 → 潤滑不良或極早期故障

## 技術細節

### 數據量控制
為了前端性能，API 回傳的數據經過限制:
- STFT 頻譜圖: 最多 100×100 點
- CWT 係數圖: 最多 64×500 點
- 頻譜圖: 最多 100×100 點

### 採樣率配置
在 `backend/config.py` 中定義:
```python
DEFAULT_SAMPLING_RATE = 25600  # Hz
ENVELOPE_FILTER_LOWCUT = 4000  # Hz
ENVELOPE_FILTER_HIGHCUT = 10000  # Hz
```

## 文件清單

### 新增文件
1. `backend/timefrequency.py` - 時頻分析核心模組
2. `test_timefrequency_api.py` - API 測試腳本
3. `TIMEFREQUENCY_INTEGRATION.md` - 本說明文件

### 修改文件
1. `backend/main.py` - 新增 4 個 API 端點
2. `frontend/src/views/Algorithms.vue` - 新增時頻分析 UI

## 未來改進方向

1. 新增更多小波基選項 (db4, db8, sym8 等)
2. 實作 WPT (Wavelet Packet Transform)
3. 新增自動特徵提取和異常檢測
4. 實作趨勢分析 (類似時域特徵的趨勢圖)
5. 增加批次處理功能

## 參考資料

- scipy.signal.stft - 短時傅立葉轉換
- scipy.signal.cwt - 連續小波轉換
- scipy.signal.hilbert - 希爾伯特轉換
- scipy.stats.kurtosis - 峰度計算

## 聯絡資訊

如有問題或建議，請參考專案 README.md 文件。
