# 高階統計與進階濾波特徵整合文件

## 整合概述

本次整合將原本分散在「高階統計 (Higher Order Statistics)」和「進階濾波特徵 (Advanced Filter Features)」兩個模組中的重複功能進行統一，以提高代碼可維護性和用戶體驗。

## 整合前的問題

### 1. 功能重複
兩個模組計算完全相同的特徵：
- **NA4** (正規化四次矩)
- **FM4** (四次矩特徵)
- **M6A** (六次矩特徵)
- **M8A** (八次矩特徵)
- **ER** (能量比)
- **Kurtosis** (峰度)

### 2. 實現分散
- `backend/timefrequency.py::higher_order_statistics()` - 簡化版實現
- `backend/filterprocess.py::FilterProcess` - 精確版實現
- 兩個獨立的 API 端點
- 前端兩個獨立的界面區塊

### 3. 計算方法差異
`FilterProcess` 的實現更精確：
- NA4 的分段計算更準確
- M6A/M8A 使用正確的正規化公式
- ER 能量比計算更合理

## 整合方案

### 後端整合

#### 1. TimeFrequency 模組 ([timefrequency.py:229-256](backend/timefrequency.py))

**修改前：**
```python
@staticmethod
def higher_order_statistics(x, fs=25600, M=8):
    # 內部實現所有計算邏輯（77行代碼）
    return {
        'na4': na4,
        'fm4': fm4,
        'm6a': m6a,
        'm8a': m8a,
        'er': er,
        'kurtosis': kurt,
        'rms': float(rms_total)
    }
```

**修改後：**
```python
@staticmethod
def higher_order_statistics(x, fs=25600, M=10):
    """
    高階統計分析 (已整合至 FilterProcess)

    此方法已棄用，請使用 FilterProcess.calculate_all_features() 代替
    為了向後兼容性保留此方法，內部委託給 FilterProcess
    """
    from filterprocess import FilterProcess
    return FilterProcess.calculate_all_features(x, fs, M)
```

**優點：**
- 消除重複代碼
- 使用更精確的 FilterProcess 實現
- 保持向後兼容性

#### 2. API 端點整合 ([main.py:800-856](backend/main.py))

**修改前：**
- `/api/algorithms/higher-order/{bearing}/{file}` - 使用 TimeFrequency
- `/api/algorithms/filter-features/{bearing}/{file}` - 使用 FilterProcess

**修改後：**
- `/api/algorithms/higher-order/...` 內部委託給 FilterProcess（向後兼容）
- `/api/algorithms/filter-features/...` 作為主要端點
- 返回結果添加 `_note` 欄位提示使用新端點

### 前端整合

#### 修改前 ([Algorithms.vue:760-1017](frontend/src/views/Algorithms.vue))

兩個獨立的 collapse 區塊：
1. `<el-collapse-item title="高階統計（Higher Order Statistics）" name="higher-order">`
2. `<el-collapse-item title="進階濾波特徵 (NA4, FM4, M6A, M8A, ER)" name="filter-features">`

#### 修改後

單一整合區塊：
```vue
<el-collapse-item title="高階統計特徵分析 (NA4, FM4, M6A, M8A, ER)" name="higher-order-stats">
```

**功能整合：**
- 統一的原理說明（使用更完整的 FilterProcess 描述）
- 單一的計算界面
- 統一的圖表展示
- 保留趨勢分析功能

## 特徵詳細說明

### NA4 (正規化四次矩 - 分段)
```
公式: NA4 = N·Σ(x-μ)⁴ / [Σ(x-μ_segment)²/M]²
```
- **用途**: 檢測諧波能量異常
- **診斷閾值**: NA4 > 3 表示早期微裂紋
- **優勢**: 對早期故障高度敏感

### FM4 (四次矩特徵)
```
公式: FM4 = N·Σ(x-μ)⁴ / [Σ(x-μ)²]²
```
- **用途**: 檢測邊帶能量異常
- **診斷閾值**: FM4 異常上升表示調製現象
- **應用**: 判斷是否存在邊帶能量增加

### M6A (六次矩特徵)
```
公式: M6A = N²·Σ(x-μ)⁶ / [Σ(x-μ)²]³
```
- **用途**: 極早期故障檢測
- **敏感度**: 對微小缺陷高度敏感
- **應用**: 預防性維護指標

### M8A (八次矩特徵)
```
公式: M8A = N³·Σ(x-μ)⁸ / [Σ(x-μ)²]⁴
```
- **用途**: 潤滑狀態監測
- **敏感度**: 對潤滑不良極度敏感
- **應用**: 檢測潤滑問題和極早期故障

### ER (能量比)
```
公式: ER = E_band / E_total
```
- **用途**: 特定頻帶能量占比分析
- **頻帶**: 默認 1000-5000 Hz
- **應用**: 邊帶能量分析

### Kurtosis (峰度)
```
公式: Kurt = E[(X-μ)⁴] / σ⁴
```
- **用途**: 衝擊性檢測
- **診斷閾值**: Kurt > 8 表示嚴重衝擊
- **應用**: 配合其他特徵使用

## API 使用指南

### 推薦端點（主要）
```
GET /api/algorithms/filter-features/{bearing_name}/{file_number}
```

**參數：**
- `bearing_name`: 軸承名稱 (例: "Bearing1_1")
- `file_number`: 檔案編號 (1-100)
- `sampling_rate`: 採樣率 (默認: 25600 Hz)
- `segment_count`: 分段數量 (默認: 10，用於 NA4 計算)

**返回格式：**
```json
{
  "bearing_name": "Bearing1_1",
  "file_number": 1,
  "data_points": 20480,
  "sampling_rate": 25600,
  "segment_count": 10,
  "horizontal": {
    "na4": 3.2456,
    "fm4": 3.1234,
    "m6a": 15.6789,
    "m8a": 245.1234,
    "er": 0.2345,
    "kurtosis": 3.4567,
    "peak": 2.3456,
    "rms": 0.5678
  },
  "vertical": {
    "na4": 2.9876,
    "fm4": 2.8765,
    "m6a": 14.2345,
    "m8a": 230.4567,
    "er": 0.2123,
    "kurtosis": 3.2345,
    "peak": 2.1234,
    "rms": 0.4567
  }
}
```

### 向後兼容端點
```
GET /api/algorithms/higher-order/{bearing_name}/{file_number}
```

此端點保留以維持向後兼容，內部委託給 FilterProcess。返回結果包含 `_note` 欄位提示使用新端點。

## 趨勢分析

### 端點
```
GET /api/algorithms/filter-trend/{bearing_name}
```

**參數：**
- `bearing_name`: 軸承名稱
- `max_files`: 最大檔案數量 (默認: 50)
- `sampling_rate`: 採樣率 (默認: 25600 Hz)

**返回格式：**
```json
{
  "bearing_name": "Bearing1_1",
  "file_count": 50,
  "file_numbers": [1, 2, 3, ..., 50],
  "horizontal": {
    "na4": [3.1, 3.2, 3.3, ...],
    "fm4": [3.0, 3.1, 3.2, ...],
    "m6a": [15.1, 15.5, 16.2, ...],
    "m8a": [240, 245, 252, ...],
    "er": [0.22, 0.23, 0.24, ...]
  },
  "vertical": {
    // 同上結構
  }
}
```

## 前端使用指南

### 單次計算
1. 選擇軸承名稱
2. 輸入檔案編號
3. 設定分段數量（可選，默認 10）
4. 點擊「計算濾波特徵」按鈕
5. 查看結果和圖表

### 趨勢分析
1. 選擇軸承名稱
2. 點擊「計算趨勢分析」按鈕
3. 查看 NA4, FM4, M6A, M8A, ER 隨時間變化的趨勢圖

### 圖表說明
**特徵比較圖：**
- 柱狀圖顯示水平和垂直方向的各項特徵
- ER 值乘以 10 以便於顯示
- 適合比較不同方向的特徵差異

**趨勢分析圖：**
- 折線圖顯示特徵隨檔案編號的變化
- 多條線代表不同特徵
- 適合觀察退化趨勢

## 診斷準則

### 正常狀態
- NA4 < 3
- FM4 在基準範圍內
- M6A, M8A 穩定
- ER 穩定
- Kurtosis < 8

### 早期故障
- NA4 > 3 → 可能存在早期微裂紋
- FM4 異常 → 邊帶能量增加
- M6A/M8A 開始上升 → 潤滑問題或極早期故障

### 明顯故障
- NA4 顯著升高 (>5)
- FM4 持續增大
- M6A/M8A 急劇上升
- ER 明顯增大
- Kurtosis > 8 → 嚴重衝擊

## 應用場景

### 1. 早期微裂紋檢測
- 主要指標：**NA4**
- 輔助指標：M6A, M8A
- 監測頻率：每日或每週

### 2. 潤滑狀態監測
- 主要指標：**M8A**
- 輔助指標：M6A, ER
- 監測頻率：每週

### 3. 調製信號分析
- 主要指標：**FM4, ER**
- 輔助指標：NA4
- 監測頻率：當懷疑有調製現象時

### 4. 綜合健康評估
- 使用所有指標的組合
- 趨勢分析
- 監測頻率：定期健康檢查

## 遷移指南

### 對於現有用戶

**後端 API 調用：**
```python
# 舊方式（仍然可用）
response = requests.get(
    f"/api/algorithms/higher-order/{bearing}/{file}"
)

# 新方式（推薦）
response = requests.get(
    f"/api/algorithms/filter-features/{bearing}/{file}",
    params={"segment_count": 10}
)
```

**前端界面：**
- 原「高階統計」和「進階濾波特徵」已合併為「高階統計特徵分析」
- 所有功能保留，界面更簡潔
- 圖表展示保持一致

### 對於開發者

**Python 代碼：**
```python
# 舊方式
from timefrequency import TimeFrequency
tf = TimeFrequency()
result = tf.higher_order_statistics(signal, fs=25600)

# 新方式（推薦）
from filterprocess import FilterProcess
result = FilterProcess.calculate_all_features(
    signal,
    fs=25600,
    segment_count=10
)
```

## 測試建議

### 1. 功能測試
- ✅ 測試 `/api/algorithms/filter-features/` 端點
- ✅ 測試 `/api/algorithms/higher-order/` 向後兼容性
- ✅ 驗證計算結果一致性
- ✅ 測試前端界面操作

### 2. 性能測試
- 測試大量數據計算時間
- 驗證趨勢分析性能（50+ 文件）
- 確認內存使用合理

### 3. 回歸測試
- 對比整合前後的計算結果
- 確認數值誤差在可接受範圍內
- 驗證所有圖表正常顯示

## 已知限制

1. **分段數量影響**
   - NA4 計算依賴分段數量
   - 建議使用默認值 10
   - 過小(<5)或過大(>20)可能影響敏感度

2. **頻帶選擇**
   - ER 默認使用 1000-5000 Hz
   - 可能需要根據實際應用調整

3. **計算時間**
   - 高階矩計算複雜度較高
   - 大數據量時可能需要等待

## 未來改進方向

1. **自適應參數**
   - 自動選擇最佳分段數量
   - 自動優化頻帶範圍

2. **特徵組合**
   - 開發綜合健康指標
   - 多特徵融合診斷

3. **實時監控**
   - WebSocket 推送
   - 實時特徵更新

4. **機器學習集成**
   - 基於歷史數據訓練模型
   - 自動異常檢測

## 總結

本次整合成功地：
- ✅ 消除了功能重複
- ✅ 統一了計算方法（使用更精確的 FilterProcess）
- ✅ 簡化了 API 結構
- ✅ 改善了用戶體驗
- ✅ 保持了向後兼容性
- ✅ 提高了代碼可維護性

用戶可以繼續使用原有端點，但建議逐步遷移到新的統一端點以獲得更好的性能和體驗。
