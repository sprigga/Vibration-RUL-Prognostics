# Backend 配置說明

## 配置模組 (config.py)

`config.py` 提供了全域配置變數，供所有後端模組使用。

### 主要配置變數

#### 資料庫路徑
- `PHM_DATABASE_PATH`: PHM IEEE 2012 資料集的 SQLite 資料庫路徑
  - 預設: `backend/phm_data.db`
- `DATABASE_PATH`: 主振動分析系統的資料庫路徑
  - 預設: `backend/vibration_analysis.db`

#### API 配置
- `API_HOST`: API 伺服器主機 (預設: `"0.0.0.0"`)
- `API_PORT`: API 伺服器端口 (預設: `8081`)
- `CORS_ORIGINS`: 允許的 CORS 來源列表

#### 信號處理配置
- `DEFAULT_SAMPLING_RATE`: 預設採樣率 (25600 Hz)
- `ENVELOPE_FILTER_LOWCUT`: 包絡分析低切頻率 (4000 Hz)
- `ENVELOPE_FILTER_HIGHCUT`: 包絡分析高切頻率 (10000 Hz)

#### 資料顯示配置
- `SIGNAL_DISPLAY_LIMIT`: 信號顯示的最大資料點數 (1000)
- `SPECTRUM_DISPLAY_LIMIT`: 頻譜顯示的最大資料點數 (1000)
- `ENVELOPE_SPECTRUM_DISPLAY_LIMIT`: 包絡頻譜顯示的最大資料點數 (500)

### 使用方式

#### 在模組中導入配置

```python
# 方式 1: 導入特定變數
try:
    from backend.config import PHM_DATABASE_PATH, DEFAULT_SAMPLING_RATE
except ModuleNotFoundError:
    from config import PHM_DATABASE_PATH, DEFAULT_SAMPLING_RATE

# 方式 2: 使用函數獲取路徑
try:
    from backend.config import get_phm_db_path
except ModuleNotFoundError:
    from config import get_phm_db_path

db_path = get_phm_db_path()
```

#### 連接資料庫範例

```python
import sqlite3
from config import PHM_DATABASE_PATH

# 連接 PHM 資料庫
conn = sqlite3.connect(PHM_DATABASE_PATH)
# ... 執行查詢
conn.close()
```

#### API endpoint 範例

```python
from fastapi import APIRouter
from config import PHM_DATABASE_PATH, DEFAULT_SAMPLING_RATE

@app.get("/api/example")
async def example_endpoint(sampling_rate: int = DEFAULT_SAMPLING_RATE):
    conn = sqlite3.connect(PHM_DATABASE_PATH)
    # ... 處理邏輯
    return {"status": "ok"}
```

### 測試配置

運行測試腳本來驗證配置：

```bash
cd backend
uv run python test_config.py
```

### 已更新的模組

以下模組已更新為使用全域配置：

1. **main.py**
   - 使用 `PHM_DATABASE_PATH` 替代硬編碼路徑
   - 使用 `CORS_ORIGINS` 配置 CORS
   - 使用 `DEFAULT_SAMPLING_RATE` 作為預設採樣率

2. **phm_query.py**
   - `PHMDatabaseQuery` 類別預設使用 `PHM_DATABASE_PATH`

3. **所有演算法 API endpoints**
   - `/api/algorithms/time-domain/{bearing_name}/{file_number}`
   - `/api/algorithms/time-domain-trend/{bearing_name}`
   - `/api/algorithms/frequency-domain/{bearing_name}/{file_number}`
   - `/api/algorithms/envelope/{bearing_name}/{file_number}`

### 優點

1. **集中管理**: 所有配置在一個地方，易於維護
2. **易於測試**: 可以在測試時輕鬆覆蓋配置值
3. **避免硬編碼**: 減少魔術數字和硬編碼路徑
4. **跨模組共享**: 多個模組可以使用相同的配置值
5. **部署靈活性**: 可以根據環境輕鬆調整配置

### 未來擴展

可以考慮添加：
- 環境變數支援 (使用 `python-dotenv`)
- 不同環境的配置檔案 (開發、測試、生產)
- 配置驗證功能
- 配置熱重載
