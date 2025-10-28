# 測試指南 - 進階濾波特徵整合

## 測試環境準備

### 1. 確認 Python 環境

```bash
cd /home/ubuntu/vibration_signals
uv sync
```

### 2. 確認資料庫存在

```bash
ls -lh phm_ieee_2012.db
```

應該看到資料庫文件存在。

## 後端測試

### 測試 1: 模組導入測試

```bash
uv run python -c "from backend.filterprocess import FilterProcess; print('Module imported successfully')"
```

預期輸出: `Module imported successfully`

### 測試 2: 基本功能測試

```bash
uv run python << 'EOF'
from backend.filterprocess import FilterProcess
import numpy as np

# 生成測試信號
signal = np.random.randn(1000)

# 計算所有特徵
result = FilterProcess.calculate_all_features(signal, fs=25600, segment_count=10)

# 顯示結果
print("Filter Features Test Results:")
print(f"  NA4: {result['na4']:.4f}")
print(f"  FM4: {result['fm4']:.4f}")
print(f"  M6A: {result['m6a']:.6f}")
print(f"  M8A: {result['m8a']:.8f}")
print(f"  ER:  {result['er']:.4f}")
print("\nTest PASSED ✓")
EOF
```

預期輸出: 所有特徵值應該有合理的數值（不是 NaN 或 Inf）

### 測試 3: API 端點測試

#### 啟動後端服務

在一個終端中執行:

```bash
cd /home/ubuntu/vibration_signals
uv run python -m uvicorn backend.main:app --host 0.0.0.0 --port 8081 --reload
```

#### 測試單一檔案計算

在另一個終端中執行:

```bash
# 測試 filter-features 端點
curl -s "http://localhost:8081/api/algorithms/filter-features/Bearing1_1/1?segment_count=10" | python -m json.tool
```

預期輸出: 應該看到包含 horizontal 和 vertical 特徵的 JSON 響應

#### 測試趨勢計算

```bash
# 測試 filter-trend 端點（限制5個檔案以加快測試）
curl -s "http://localhost:8081/api/algorithms/filter-trend/Bearing1_1?max_files=5" | python -m json.tool
```

預期輸出: 應該看到包含 file_numbers 和各個特徵陣列的 JSON 響應

### 測試 4: 完整流程測試

```bash
uv run python << 'EOF'
import sqlite3
import numpy as np
import pandas as pd
from backend.filterprocess import FilterProcess
from backend.config import PHM_DATABASE_PATH

print("="*60)
print("Complete Integration Test")
print("="*60)

# 連接資料庫
conn = sqlite3.connect(PHM_DATABASE_PATH)

# 查詢數據
query = """
SELECT m.horizontal_acceleration, m.vertical_acceleration
FROM measurements m
JOIN measurement_files mf ON m.file_id = mf.file_id
JOIN bearings b ON mf.bearing_id = b.bearing_id
WHERE b.bearing_name = 'Bearing1_1' AND mf.file_number = 1
LIMIT 1000
"""

df = pd.read_sql_query(query, conn)
conn.close()

if df.empty:
    print("ERROR: No data found in database")
    exit(1)

print(f"\nData loaded: {len(df)} points")

# 計算水平方向特徵
horiz = df['horizontal_acceleration'].values
horiz_features = FilterProcess.calculate_all_features(horiz, fs=25600, segment_count=10)

print("\nHorizontal Features:")
print(f"  NA4:      {horiz_features['na4']:.4f}")
print(f"  FM4:      {horiz_features['fm4']:.4f}")
print(f"  M6A:      {horiz_features['m6a']:.6f}")
print(f"  M8A:      {horiz_features['m8a']:.8f}")
print(f"  ER:       {horiz_features['er']:.4f}")
print(f"  Kurtosis: {horiz_features['kurtosis']:.4f}")
print(f"  RMS:      {horiz_features['rms']:.4f}")

# 計算垂直方向特徵
vert = df['vertical_acceleration'].values
vert_features = FilterProcess.calculate_all_features(vert, fs=25600, segment_count=10)

print("\nVertical Features:")
print(f"  NA4:      {vert_features['na4']:.4f}")
print(f"  FM4:      {vert_features['fm4']:.4f}")
print(f"  M6A:      {vert_features['m6a']:.6f}")
print(f"  M8A:      {vert_features['m8a']:.8f}")
print(f"  ER:       {vert_features['er']:.4f}")
print(f"  Kurtosis: {vert_features['kurtosis']:.4f}")
print(f"  RMS:      {vert_features['rms']:.4f}")

print("\n" + "="*60)
print("Integration Test PASSED ✓")
print("="*60)
EOF
```

## 前端測試

### 測試 1: 確認前端依賴

```bash
cd /home/ubuntu/vibration_signals/frontend
npm install
```

### 測試 2: 啟動開發服務器

```bash
npm run dev
```

### 測試 3: 瀏覽器測試

1. 打開瀏覽器訪問 `http://localhost:5173` (或顯示的 URL)
2. 導航到「演算法原理與應用展示」頁面
3. 找到「進階濾波特徵 (NA4, FM4, M6A, M8A, ER)」折疊區塊
4. 展開該區塊

#### 測試單一檔案計算

1. 選擇軸承: Bearing1_1
2. 檔案編號: 1
3. 分段數量: 10
4. 點擊「計算濾波特徵」按鈕
5. 等待計算完成（約1-2秒）
6. 確認:
   - 結果表格顯示所有特徵值
   - 「進階濾波特徵比較」圖表顯示柱狀圖
   - 水平和垂直方向的數值都有顯示

#### 測試趨勢分析

1. 保持軸承選擇: Bearing1_1
2. 點擊「計算趨勢分析」按鈕
3. 等待計算完成（約10-15秒，處理50個檔案）
4. 確認:
   - 「進階濾波特徵趨勢分析」卡片顯示檔案數量
   - 趨勢圖顯示線圖
   - 可以看到 NA4 和 FM4 的趨勢變化

### 測試 4: 控制台錯誤檢查

打開瀏覽器開發者工具（F12），檢查 Console 標籤頁:
- 應該沒有紅色錯誤訊息
- API 請求應該返回 200 狀態碼

## 常見問題排除

### 問題 1: 模組導入失敗

```
ModuleNotFoundError: No module named 'backend.filterprocess'
```

**解決方案**:
```bash
cd /home/ubuntu/vibration_signals
uv sync
```

### 問題 2: 資料庫連接失敗

```
FileNotFoundError: [Errno 2] No such file or directory: 'phm_ieee_2012.db'
```

**解決方案**:
確認資料庫文件存在於項目根目錄，或檢查 `backend/config.py` 中的路徑設定。

### 問題 3: API 返回 500 錯誤

**診斷步驟**:
1. 檢查後端控制台輸出的錯誤訊息
2. 確認資料庫中有對應的軸承和檔案
3. 查看詳細的 traceback 訊息

**常見原因**:
- 資料庫中沒有請求的軸承或檔案
- 計算過程中除以零錯誤
- 數據格式不正確

### 問題 4: 前端無法連接後端

```
Failed to fetch
```

**解決方案**:
1. 確認後端服務正在運行 (`http://localhost:8081`)
2. 檢查 CORS 設定
3. 確認前端請求的 URL 正確

### 問題 5: 圖表不顯示

**解決方案**:
1. 確認計算成功返回數據
2. 檢查瀏覽器控制台是否有 JavaScript 錯誤
3. 確認 ECharts 已正確加載

## 效能基準測試

### 單一檔案計算

```bash
time curl -s "http://localhost:8081/api/algorithms/filter-features/Bearing1_1/1" > /dev/null
```

預期時間: < 2 秒

### 趨勢計算（50個檔案）

```bash
time curl -s "http://localhost:8081/api/algorithms/filter-trend/Bearing1_1?max_files=50" > /dev/null
```

預期時間: 10-30 秒（取決於硬體）

## 驗收標準

✓ 所有模組導入測試通過
✓ 基本功能測試返回合理數值
✓ API 端點返回正確的 JSON 格式
✓ 完整流程測試成功計算特徵
✓ 前端可以正確顯示結果
✓ 圖表正常渲染
✓ 無控制台錯誤
✓ 效能在可接受範圍內

## 測試報告範本

```
測試日期: YYYY-MM-DD
測試人員: [姓名]

後端測試:
  [ ] 模組導入測試
  [ ] 基本功能測試
  [ ] API 端點測試
  [ ] 完整流程測試

前端測試:
  [ ] 依賴安裝
  [ ] 服務器啟動
  [ ] 單一檔案計算
  [ ] 趨勢分析
  [ ] 控制台檢查

問題記錄:
  1. [問題描述] - [解決方案]
  2. ...

效能測試:
  單一檔案: [時間] 秒
  趨勢分析: [時間] 秒

結論:
  [ ] 通過 / [ ] 失敗

備註:
  [其他觀察或建議]
```
