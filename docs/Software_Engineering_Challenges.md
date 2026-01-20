# 軟體工程觀點下的程式碼困難點分析

## 專案概述

本文件從軟體工程的角度，深入分析「軸承 RUL 預測與振動信號分析平台」程式碼庫中遇到的技術困難點，以及專案目前採用的解決方案。

---

## 一、模組導入與環境兼容性困難

### 1.1 困難點描述

專案需要在兩種不同的環境中運行：
- **本地開發環境**：直接從當前目錄導入模組
- **Docker 容器環境**：模組位於 `/app/backend/` 目錄下

這導致相同的導入語句在不同環境下會失敗。

### 1.2 現有解決方案

```python
# 所有演算法模組都採用這個模式
try:
    from backend.initialization import InitParameter as ip
    from backend.timedomain import TimeDomain as td
    from backend.harmonic_sildband_table import HarmonicSildband as hs
except ModuleNotFoundError:
    from initialization import InitParameter as ip
    from timedomain import TimeDomain as td
    from harmonic_sildband_table import HarmonicSildband as hs
```

**在 main.py 中的動態路徑處理：**

```python
# 動態路徑處理：兼容本地開發和容器環境
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)
```

### 1.3 解決方案評估

| 優點 | 缺點 |
|------|------|
| ✅ 簡單直觀，易於理解 | ❌ 重複程式碼，每個模組都要寫 try-except |
| ✅ 不依賴外部配置 | ❌ 違反 DRY 原則 |
| ✅ 運行時動態適應 | ❌ 導入錯誤只有在運行時才會發現 |

### 1.4 改進建議

**方案一：使用 Python 路徑操作模組**

```python
# 在專案根目錄建立 utils/path_helper.py
import sys
from pathlib import Path

def ensure_backend_in_path():
    """確保 backend 目錄在 sys.path 中"""
    backend_dir = Path(__file__).parent / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

# 在所有模組頂部統一調用
from utils.path_helper import ensure_backend_in_path
ensure_backend_in_path()

# 然後可以直接導入
from initialization import InitParameter as ip
```

**方案二：使用相對導入（推薦用於包結構）**

```python
# 將 backend 改為 Python package
# 添加 __init__.py
# 然後使用相對導入
from .initialization import InitParameter as ip
from .timedomain import TimeDomain as td
```

---

## 二、數值計算穩定性困難

### 2.1 困難點描述

振動信號分析涉及複雜的數學計算，可能遇到：
- **除以零錯誤**：在計算比例、歸一化時
- **空資料集**：濾波後沒有符合條件的資料
- **數值溢出**：高階矩計算可能導致數值溢出
- **NaN/Inf 傳播**：計算鏈中一個錯誤導致整個結果失效

### 2.2 現有解決方案

#### 2.2.1 除以零保護

```python
# FilterProcess.NA4 中的保護
na4 = total_sum_all / division_total_sum_segment if division_total_sum_segment != 0 else np.nan

# FilterProcess.FM4 中的保護
denominator = np.sum(difference ** 2) ** 2
fm4 = (n * np.sum(difference ** 4)) / denominator if denominator != 0 else np.nan

# FilterProcess.M6A 中的保護
denominator = np.sum(difference ** 2) ** 3
m6a = ((n ** 2) * np.sum(difference ** 6)) / denominator if denominator != 0 else np.nan

# TimeFrequency._calculate_np4 中的保護
if sum_2 > 0:
    np4 = N * sum_4 / (sum_2**2)
else:
    np4 = 0.0
```

#### 2.2.2 空資料集保護

```python
# frequencydomain.py 中的空 DataFrame 處理
max_mortor_gear = fftoutput[mask1 & mask2]

# Safety check for empty DataFrame
if max_mortor_gear.empty:
    max_mortor_gear = fftoutput.iloc[0:1]  # Use first row as fallback
else:
    max_mortor_gear = fftoutput[fftoutput['abs_fft']==np.max(max_mortor_gear['abs_fft'])]
```

#### 2.2.3 頻譜和諧波保護

```python
# frequencydomain.py 中的和諧波和為零保護
low_filter_sum,_ = hs.Harmonic(fftoutput)

# Safety check: if harmonic sum is 0, use peak value to avoid division by zero
if low_filter_sum == 0:
    low_filter_sum = 1.0  # Default value to avoid division by zero

# TSA FFT 中的保護
high_filter_sum,_ = hs.Sildband(tsa_fftoutput)

# Safety check: if sideband sum is 0, use default value to avoid division by zero
if high_filter_sum == 0:
    high_filter_sum = 1.0
```

#### 2.2.4 RMS 歸一化保護

```python
# frequencydomain.py 中的 RMS 保護
rms_val = td.rms(amp)
if rms_val == 0:
    rms_val = 1.0  # Avoid division by zero
```

### 2.3 解決方案評估

| 優點 | 缺點 |
|------|------|
| ✅ 防止程式崩潰 | ❌ 使用硬編碼的預設值（1.0）可能不符合業務邏輯 |
| ✅ 使用 np.nan 標記無效計算 | ❌ NaN 需要前端額外處理 |
| ✅ 明確的安全檢查註釋 | ❌ 每個計算點都要檢查，程式碼冗餘 |

### 2.4 改進建議

**方案一：使用裝飾器模式統一處理**

```python
# utils/safety.py
import functools
import numpy as np

def safe_division(default_value=np.nan):
    """安全除法裝飾器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, (float, np.floating)):
                if np.isnan(result) or np.isinf(result):
                    return default_value
            return result
        return wrapper
    return decorator

# 使用
@safe_division(default_value=1.0)
def calculate_ratio(numerator, denominator):
    return numerator / denominator
```

**方案二：使用 numpy 的安全運算函數**

```python
# 使用 np.divide 的 where 參數
result = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator!=0)

# 或者使用 np.errstate 上下文
with np.errstate(divide='ignore', invalid='ignore'):
    result = numerator / denominator
result[~np.isfinite(result)] = default_value
```

---

## 三、大量資料處理困難

### 3.1 困難點描述

- **資料庫查詢結果龐大**：單個檔案可能有數十萬筆測量數據
- **頻譜計算產生大量數據**：FFT 結果與輸入信號長度相同
- **網路傳輸負擔**：前端不需要所有原始數據點
- **記憶體消耗**：同時處理多個檔案可能導致記憶體不足

### 3.2 現有解決方案

#### 3.2.1 配置顯示限制

```python
# config.py 中定義顯示限制
SIGNAL_DISPLAY_LIMIT = 1000  # 前端顯示的最大資料點數
SPECTRUM_DISPLAY_LIMIT = 1000  # 頻譜顯示的最大資料點數
ENVELOPE_SPECTRUM_DISPLAY_LIMIT = 500  # 包絡頻譜顯示的最大資料點數

# main.py 中使用
"spectrum_data": {
    "frequency": freq[:SPECTRUM_DISPLAY_LIMIT].tolist(),
    "horizontal_magnitude": horiz_magnitude[:SPECTRUM_DISPLAY_LIMIT].tolist(),
    "vertical_magnitude": vert_magnitude[:SPECTRUM_DISPLAY_LIMIT].tolist()
}
```

#### 3.2.2 分頁查詢

```python
# phm_query.py 中的分頁實現
def get_file_list(
    self,
    bearing_name: str,
    offset: int = 0,
    limit: int = 100
) -> Dict[str, Any]:
    # Get total count
    cursor.execute("""
        SELECT COUNT(*)
        FROM measurement_files mf
        JOIN bearings b ON mf.bearing_id = b.bearing_id
        WHERE b.bearing_name = ?
    """, (bearing_name,))
    total_count = cursor.fetchone()[0]

    # Get files with pagination
    cursor.execute("""
        SELECT ...
        ORDER BY mf.file_number
        LIMIT ? OFFSET ?
    """, (bearing_name, limit, offset))
```

#### 3.2.3 頻譜圖資料降採樣

```python
# main.py 中限制 STFT 和 Spectrogram 返回的資料量
freq_limit = min(100, len(horiz_stft['frequencies']))
time_limit = min(100, len(horiz_stft['time']))

features = {
    "spectrogram_data": {
        "frequencies": horiz_stft['frequencies'][:freq_limit].tolist(),
        "time": horiz_stft['time'][:time_limit].tolist(),
        "horizontal_magnitude": horiz_stft['magnitude'][:freq_limit, :time_limit].tolist(),
        "vertical_magnitude": vert_stft['magnitude'][:freq_limit, :time_limit].tolist()
    }
}
```

### 3.3 解決方案評估

| 優點 | 缺點 |
|------|------|
| ✅ 顯著減少網路傳輸量 | ❌ 前端無法查看完整資料 |
| ✅ 降低前端渲染負擔 | ❌ 損失資料細節 |
| ✅ 分頁支援大資料集 | ❌ 需要前端實現分頁邏輯 |
| ✅ 配置集中管理 | ❌ 硬編碼的限制值可能不適用所有場景 |

### 3.4 改進建議

**方案一：動態降採樣**

```python
def downsample_data(data, max_points=1000):
    """智能降採樣，保留重要特徵"""
    if len(data) <= max_points:
        return data
    
    # 使用 scipy.signal.resample 進行降採樣
    from scipy import signal
    return signal.resample(data, max_points)

# 或者使用 Peak 檢測降採樣
def peak_preserving_downsample(data, max_points=1000):
    """保留峰值的降採樣"""
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(np.abs(data))
    
    # 確保包含峰值點
    indices = sorted(set(peaks[:max_points]))
    return data[indices]
```

**方案二：資料壓縮**

```python
import gzip
import base64

def compress_data(data_dict):
    """壓縮 JSON 響應"""
    json_str = json.dumps(data_dict)
    compressed = gzip.compress(json_str.encode('utf-8'))
    return base64.b64encode(compressed).decode('utf-8')

# 在 FastAPI 中啟用壓縮
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## 四、複雜頻域計算困難

### 4.1 困難點描述

頻域分析涉及多層次計算：
- **FM0（Frequency Magnitude 0）**：需要識別馬達齒輪和皮帶的主要頻率
- **TSA（Time Synchronous Averaging）**：需要對頻譜進行時域同步平均
- **邊帶檢測**：在主要頻率周圍識別邊帶成分
- **諧波分析**：識別主要頻率的整數倍頻率

### 4.2 現有解決方案

#### 4.2.1 多重遮罩篩選

```python
# frequencydomain.py 中的複雜遮罩邏輯
# 先計算 mortor gear 的主要頻率
mask1 = fftoutput['freqs']>=ip.mortor_gear-ip.side_band_range
mask2 = fftoutput['freqs']<=ip.mortor_gear+ip.side_band_range
max_mortor_gear=fftoutput[mask1 & mask2]

# 用 mortor gear 的主要頻率來找出周圍的頻率
mask7 = fftoutput['freqs']>=float(max_mortor_gear1['freqs'].values[0]) - ip.harmonic_gmf_range
mask8 = fftoutput['freqs']<float(max_mortor_gear1['freqs'].values[0])
mask9 = fftoutput['freqs']>float(max_mortor_gear1['freqs'].values[0])
mask10 = fftoutput['freqs']<=float(max_mortor_gear1['freqs'].values[0]) + ip.harmonic_gmf_range

# 篩選 motor gear 和皮帶的數值
fft_mgs1=fftoutput[mask7 & mask8]
fft_mgs2=fftoutput[mask9 & mask10]
```

#### 4.2.2 諧波與邊帶表格計算

```python
# harmonic_sildband_table.py 中獨立處理
class HarmonicSildband():
    def Harmonic(fft):
        """計算諧波和"""
        # 遍歷諧波頻率範圍
        # 計算每個諧波的貢獻
        # 返回總和
        pass
    
    def Sildband(tsa_fft):
        """計算邊帶和"""
        # 識別邊帶頻率
        # 計算邊帶能量
        # 返回總和
        pass
```

#### 4.2.3 TSA 頻譜倍率調整

```python
# 計算 TSA FFT 和原始 FFT 頻率的倍率
max1=fftoutput[fftoutput['abs_fft']==np.max(fftoutput['abs_fft'])]
max2=tsa_fftoutput[tsa_fftoutput['tsa_abs_fft']==np.max(tsa_fftoutput['tsa_abs_fft'])]

max4_freq = float(max4['tsa_freqs1'].values[0])
if max4_freq == 0:
    max_freqs = 1.0
else:
    max_freqs = float(max3['freqs1'].values[0]) / max4_freq

# 調整 TSA 頻譜的頻率刻度
tsa_fftoutput=pd.DataFrame({
    'tsa_freqs':np.round(tsa_freqs,3),
    'multiply_freqs':np.round(tsa_freqs*max_freqs,5),
    'tsa_abs_fft':tsa_abs_fft,
    'tsa_abs_fft_n': tsa_abs_fft_n,
    'tsa_fft':tsa_fft_value
})
```

### 4.3 解決方案評估

| 優點 | 缺點 |
|------|------|
| ✅ 完整實現了 FM0 和 TSA 算法 | ❌ 遮罩邏輯複雜，難以理解和維護 |
| ✅ 將諧波/邊帶計算獨立出來 | ❌ 頻率範圍硬編碼在 initialization.py |
| ✅ 處理了 TSA 頻譜的頻率刻度調整 | ❌ 計算步驟多，容易出錯 |

### 4.4 改進建議

**方案一：使用頻譜分析工具包**

```python
# 使用專業的信號處理庫
from scipy.signal import find_peaks, peak_widths

def find_dominant_frequencies(fft_output, prominence=1.0):
    """使用峰值檢測找出主要頻率"""
    peaks, properties = find_peaks(
        fft_output['abs_fft_n'],
        prominence=prominence
    )
    
    # 返回峰值頻率和幅值
    return pd.DataFrame({
        'frequency': fft_output['freqs'].iloc[peaks],
        'magnitude': fft_output['abs_fft_n'].iloc[peaks],
        'prominence': properties['prominences']
    })
```

**方案二：建立頻譜分析類**

```python
class SpectrumAnalyzer:
    """頻譜分析封裝類"""
    
    def __init__(self, fs, signal):
        self.fs = fs
        self.signal = signal
        self.fft_result = self._compute_fft()
    
    def _compute_fft(self):
        """計算 FFT"""
        n = len(self.signal)
        freq = fftfreq(n, 1/self.fs)
        fft_values = fft(self.signal)
        return pd.DataFrame({
            'freqs': freq[:n//2],
            'abs_fft': np.abs(fft_values[:n//2])
        })
    
    def find_peaks_around(self, center_freq, bandwidth):
        """找出指定頻率周圍的峰值"""
        mask = (self.fft_result['freqs'] >= center_freq - bandwidth) & \
                (self.fft_result['freqs'] <= center_freq + bandwidth)
        return self.fft_result[mask]
    
    def calculate_sidebands(self, center_freq, num_sidebands=2):
        """計算邊帶"""
        sideband_freqs = []
        for i in range(1, num_sidebands + 1):
            sideband_freqs.extend([
                center_freq - i * self.fs / n,
                center_freq + i * self.fs / n
            ])
        return sideband_freqs
```

---

## 五、批量處理錯誤處理困難

### 5.1 困難點描述

處理多個檔案時，可能遇到：
- 某些檔案資料缺失
- 計算過程中出現異常
- 資料格式不一致
- 需要繼續處理其他檔案

### 5.2 現有解決方案

```python
# frequencydomain.py 中的 calculate_frequency_domain_trend 方法
for idx, (file_num, file_id) in enumerate(files):
    try:
        # 更新進度
        if progress_callback:
            progress_callback(idx + 1, total_files, file_num)
        
        # 查詢資料
        query = f"""
            SELECT horizontal_acceleration, vertical_acceleration
            FROM measurements
            WHERE file_id = {file_id}
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print(f"Warning: File {file_num} has no data, skipping")
            # 插入 NaN 值
            for key in feature_keys:
                trend_data["horizontal"][key].append(float('nan'))
                trend_data["vertical"][key].append(float('nan'))
            trend_data["file_numbers"].append(file_num)
            continue
        
        # ... 計算邏輯 ...
        
    except Exception as e:
        print(f"Error processing file {file_num}: {str(e)}")
        # 插入 NaN 值
        for key in feature_keys:
            trend_data["horizontal"][key].append(float('nan'))
            trend_data["vertical"][key].append(float('nan'))
        trend_data["file_numbers"].append(file_num)
        continue
```

### 5.3 解決方案評估

| 優點 | 缺點 |
|------|------|
| ✅ 單個檔案錯誤不會中斷整體處理 | ❌ 使用 print 輸出錯誤，不適合生產環境 |
| ✅ 插入 NaN 保持資料結構完整 | ❌ 錯誤資訊丟失，難以追蹤問題 |
| ✅ 進度回調機制 | ❌ 異常捕獲太寬泛，可能隱藏邏輯錯誤 |

### 5.4 改進建議

**方案一：使用日誌系統**

```python
import logging

logger = logging.getLogger(__name__)

for idx, (file_num, file_id) in enumerate(files):
    try:
        # 處理邏輯
        pass
    except pd.errors.EmptyDataError as e:
        logger.warning(f"File {file_num} has no data: {e}")
        # 插入 NaN
    except ValueError as e:
        logger.error(f"Calculation error in file {file_num}: {e}")
        # 插入 NaN
    except Exception as e:
        logger.exception(f"Unexpected error processing file {file_num}")
        # 插入 NaN
```

**方案二：錯誤收集與報告**

```python
class ProcessingResult:
    def __init__(self):
        self.success_files = []
        self.failed_files = []
        self.errors = {}
    
    def add_success(self, file_num, data):
        self.success_files.append(file_num)
    
    def add_failure(self, file_num, error):
        self.failed_files.append(file_num)
        self.errors[file_num] = str(error)
    
    def get_summary(self):
        return {
            'total': len(self.success_files) + len(self.failed_files),
            'success': len(self.success_files),
            'failed': len(self.failed_files),
            'error_rate': len(self.failed_files) / (len(self.success_files) + len(self.failed_files)) if len(self.failed_files) > 0 else 0
        }

# 使用
result = ProcessingResult()
for file_num, file_id in files:
    try:
        data = process_file(file_id)
        result.add_success(file_num, data)
    except Exception as e:
        result.add_failure(file_num, e)

# 返回結果和錯誤摘要
return {
    'data': trend_data,
    'summary': result.get_summary(),
    'errors': result.errors
}
```

---

## 六、資料庫連線管理困難

### 6.1 困難點描述

- FastAPI 是異步框架，但 SQLite 是同步資料庫
- 多個請求同時訪問資料庫可能導致競爭條件
- 頻繁創建/關閉連接影響性能
- 需要線程安全的連線管理

### 6.2 現有解決方案

```python
# main.py 中的連線管理器
import threading
from typing import Generator

# Thread-local storage for database connections
_db_local = threading.local()

@contextlib.contextmanager
def get_db_connection(db_path: str = PHM_DATABASE_PATH) -> Generator[sqlite3.Connection, None, None]:
    """
    資料庫連接上下文管理器
    
    使用線程本地存儲確保每個線程有自己的連接，
    並在上下文退出時自動關閉連接。
    """
    # 檢查線程本地存儲中是否已有連接
    conn = getattr(_db_local, 'conn', None)
    
    if conn is None:
        # 創建新連接
        conn = sqlite3.connect(db_path)
        _db_local.conn = conn
    
    try:
        yield conn
    finally:
        # 注意：不在此處關閉連接，讓連接在線程結束時關閉
        # 這樣可以提高性能，避免頻繁創建/關閉連接
        pass

def close_db_connection():
    """關閉當前線程的資料庫連接"""
    conn = getattr(_db_local, 'conn', None)
    if conn is not None:
        conn.close()
        _db_local.conn = None

# 在應用關閉時清理連接
@app.on_event("shutdown")
def shutdown_event():
    """應用關閉時清理資料庫連接"""
    close_db_connection()
```

### 6.3 解決方案評估

| 優點 | 缺點 |
|------|------|
| ✅ 線程安全的連接管理 | ❌ SQLite 不支援高併發寫入 |
| ✅ 上下文管理器確保資源清理 | ❌ 連接不立即關閉可能導致資源洩漏 |
| ✅ 應用關閉時清理連接 | ❌ 不適合真正的異步場景 |

### 6.4 改進建議

**方案一：使用連接池**

```python
import sqlite3
from queue import Queue

class SQLiteConnectionPool:
    def __init__(self, db_path, pool_size=5):
        self.db_path = db_path
        self.pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            self.pool.put(sqlite3.connect(db_path))
    
    def get_connection(self):
        return self.pool.get()
    
    def return_connection(self, conn):
        self.pool.put(conn)
    
    def close_all(self):
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()

# 使用
connection_pool = SQLiteConnectionPool(PHM_DATABASE_PATH)
```

**方案二：使用異步資料庫驅動**

```python
# 使用 aiosqlite 替代 sqlite3
import aiosqlite

async def get_db_connection():
    conn = await aiosqlite.connect(PHM_DATABASE_PATH)
    return conn

@app.get("/api/example")
async def example_endpoint():
    async with get_db_connection() as conn:
        cursor = await conn.execute("SELECT * FROM bearings")
        rows = await cursor.fetchall()
    return rows
```

**方案三：使用 PostgreSQL 替代 SQLite（適合生產環境）**

```python
# 使用 SQLAlchemy + asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/dbname",
    echo=False
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        yield session
```

---

## 七、跨平台路徑處理困難

### 7.1 困難點描述

- Windows 使用 `\` 路徑分隔符，Linux/Mac 使用 `/`
- Docker 容器內路徑與本地不同
- 相對路徑與絕對路徑混用導致混亂

### 7.2 現有解決方案

```python
# config.py 中的路徑處理
from pathlib import Path

# 獲取 backend 目錄的絕對路徑
BACKEND_DIR = Path(__file__).parent.absolute()

# 使用 os.path.join 連接路徑（兼容所有平台）
PHM_DATABASE_PATH = os.path.join(BACKEND_DIR, "phm_data.db")
PHM_TEMPERATURE_DATABASE_PATH = os.path.join(BACKEND_DIR, "phm_temperature_data.db")

# main.py 中的動態路徑處理
current_dir = os.path.dirname(os.path.abspath(__file__))

# 判斷是否在 backend 子目錄中
if os.path.basename(current_dir) == 'backend':
    project_root = os.path.dirname(current_dir)
else:
    project_root = current_dir

# 讀取生成的分析結果
summary_path = os.path.join(project_root, "phm_analysis_results", "summary.json")
```

### 7.3 解決方案評估

| 優點 | 缺點 |
|------|------|
| ✅ 使用 Path 和 os.path 處理路徑 | ❌ 混用 Path 和 os.path |
| ✅ 動態判斷目錄結構 | ❌ 邏輯複雜，難以理解 |
| ✅ 絕對路徑避免相對路徑問題 | ❌ 硬編碼目錄名稱 'backend' |

### 7.4 改進建議

**方案一：統一使用 pathlib**

```python
# config.py
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BACKEND_DIR.parent if BACKEND_DIR.name == 'backend' else BACKEND_DIR

# 使用 / 操作符連接路徑
PHM_DATABASE_PATH = BACKEND_DIR / "phm_data.db"
PHM_TEMPERATURE_DATABASE_PATH = BACKEND_DIR / "phm_temperature_data.db"
PHM_RESULTS_DIR = PROJECT_ROOT / "phm_analysis_results"
```

**方案二：環境變量配置**

```python
# 使用環境變量指定路徑
import os
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get(
    'PROJECT_ROOT',
    Path(__file__).parent.parent
))

BACKEND_DIR = Path(os.environ.get(
    'BACKEND_DIR',
    PROJECT_ROOT / 'backend'
))
```

---

## 八、總結與建議

### 8.1 主要困難點總結

| 困難點 | 複雜度 | 現有解決效果 |
|--------|--------|--------------|
| 模組導入兼容性 | ⭐⭐ | ⭐⭐⭐ 可用但重複 |
| 數值計算穩定性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ 防護完善 |
| 大量資料處理 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ 有效但損失細節 |
| 複雜頻域計算 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ 功能完整但維護難 |
| 批量處理錯誤 | ⭐⭐⭐ | ⭐⭐ 容錯但日誌不足 |
| 資料庫連接管理 | ⭐⭐⭐⭐ | ⭐⭐⭐ 線程安全但不適合異步 |
| 跨平台路徑處理 | ⭐⭐ | ⭐⭐⭐ 處理完善 |

### 8.2 優先改進建議

**短期（1-2 週）**
1. ✅ 引入 logging 模組替換 print
2. ✅ 統一使用 pathlib 處理路徑
3. ✅ 建立安全除法裝飾器
4. ✅ 改進錯誤收集與報告機制

**中期（1-2 個月）**
1. 🔄 使用 aiosqlite 實現真正的異步資料庫訪問
2. 🔄 重構頻域計算，使用 SpectrumAnalyzer 類
3. 🔄 實現智能降採樣演算法
4. 🔄 添加單元測試覆蓋關鍵計算

**長期（3-6 個月）**
1. 🔄 遷移至 PostgreSQL 以支援高併發
2. 🔄 實現微服務架構
3. 🔄 添加快取機制（Redis）
4. 🔄 實現異步任務隊列（Celery）

### 8.3 架構改進建議

```
當前架構：
┌─────────────┐
│   FastAPI  │ (同步處理)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   SQLite   │ (不支援高併發)
└─────────────┘

建議架構：
┌─────────────┐
│   FastAPI  │ (異步處理)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ PostgreSQL  │ (支援高併發)
└─────────────┘
       ↑
       │
┌──────┴──────┐
│   Redis    │ (快取層)
└─────────────┘
```

---

## 結論

本專案在面對軟體工程挑戰時，採用了務實的解決方案。雖然某些解決方案可以進一步優化，但整體上已經建立起一個功能完整、穩定運行的系統。通過持續改進和架構升級，專案將能更好地支援大規模資料處理和高併發訪問。
