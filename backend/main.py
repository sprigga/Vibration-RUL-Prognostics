"""
FastAPI backend for Linear Guide Vibration Analysis System
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import numpy as np
import pandas as pd
from datetime import datetime
import os
import json
import sys
import sqlite3

# 動態路徑處理：兼容本地開發和容器環境
# 獲取當前檔案所在目錄
_current_dir = os.path.dirname(os.path.abspath(__file__))
# 如果當前目錄不在 sys.path 中，添加它
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# 使用直接導入（適合兩種環境）
from phm_processor import PHMDataProcessor
from phm_query import PHMDatabaseQuery
from phm_temperature_query import PHMTemperatureQuery
from config import (
    PHM_DATABASE_PATH,
    PHM_TEMPERATURE_DATABASE_PATH,
    CORS_ORIGINS,
    DEFAULT_SAMPLING_RATE,
    ENVELOPE_FILTER_LOWCUT,
    ENVELOPE_FILTER_HIGHCUT,
    SIGNAL_DISPLAY_LIMIT,
    SPECTRUM_DISPLAY_LIMIT,
    ENVELOPE_SPECTRUM_DISPLAY_LIMIT
)
from timefrequency import TimeFrequency
from hilberttransform import HilbertTransform
from filterprocess import FilterProcess
from timedomain import TimeDomain
from frequencydomain import FrequencyDomain

# ========================================
# Database Connection Manager
# ========================================

import contextlib
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

    Args:
        db_path: 資料庫路徑，預設使用 PHM_DATABASE_PATH

    Yields:
        sqlite3.Connection: 資料庫連接對象
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

app = FastAPI(
    title="Linear Guide Vibration Analysis API",
    description="API for CPC Linear Guide health monitoring and fault diagnosis",
    version="1.0.0"
)

# 在應用關閉時清理連接
@app.on_event("shutdown")
def shutdown_event():
    """應用關閉時清理資料庫連接"""
    close_db_connection()

# CORS middleware for Vue.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class AnalysisRequest(BaseModel):
    signal_data: List[float]
    fs: int
    velocity: float
    guide_spec_id: int




# Health check
@app.get("/")
async def root():
    return {
        "message": "Linear Guide Vibration Analysis API",
        "version": "1.0.0",
        "status": "running"
    }




# Analysis endpoints (commented out - requires VibrationAnalyzer)
# @app.post("/api/analyze", response_model=Dict)
# async def analyze_vibration(request: AnalysisRequest):
#     """Perform vibration analysis on signal data"""
#     pass


# @app.post("/api/upload-csv", response_model=Dict)
# async def upload_csv(...):
#     """Upload and analyze CSV file - requires VibrationAnalyzer"""
#     pass


# ========================================
# PHM 2012 Challenge Endpoints
# ========================================

@app.get("/api/phm/training-summary", response_model=Dict)
async def get_phm_training_summary():
    """獲取 PHM 訓練集摘要"""
    try:
        processor = PHMDataProcessor()
        summary = processor.get_training_summary()
        return {
            "total_bearings": len(summary),
            "bearings": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/api/phm/analysis-data", response_model=Dict)
async def get_phm_analysis_data():
    """獲取預處理的 PHM 分析數據（從 JSON 文件）"""
    try:
        # 獲取項目根目錄
        # 在容器中，main.py 位於 /app/backend/main.py 或 /app/main.py
        # phm_analysis_results 目錄掛載在 /app/phm_analysis_results
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 判斷是否在 backend 子目錄中
        if os.path.basename(current_dir) == 'backend':
            project_root = os.path.dirname(current_dir)
        else:
            project_root = current_dir

        # 讀取生成的分析結果
        summary_path = os.path.join(project_root, "phm_analysis_results", "summary.json")
        stats_path = os.path.join(project_root, "phm_analysis_results", "vibration_statistics.csv")

        print(f"Looking for summary at: {summary_path}")
        print(f"Looking for stats at: {stats_path}")
        print(f"Summary exists: {os.path.exists(summary_path)}")
        print(f"Stats exists: {os.path.exists(stats_path)}")

        if not os.path.exists(summary_path):
            raise HTTPException(
                status_code=404,
                detail=f"Analysis results not found at {summary_path}"
            )

        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = json.load(f)

        # 讀取統計數據
        stats_data = []
        if os.path.exists(stats_path):
            df = pd.read_csv(stats_path)
            stats_data = df.to_dict('records')

        return {
            "summary": summary,
            "statistics": stats_data
        }
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in get_phm_analysis_data: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))




# ========================================
# PHM Database Query Endpoints
# ========================================

@app.get("/api/phm/database/bearings", response_model=Dict)
async def get_phm_database_bearings():
    """獲取 PHM 資料庫中所有軸承列表及統計"""
    try:
        query = PHMDatabaseQuery()
        bearings = query.get_bearings()
        return {
            "total_bearings": len(bearings),
            "bearings": bearings
        }
    except FileNotFoundError as e:
        # 資料庫不存在時返回友善訊息
        raise HTTPException(
            status_code=404,
            detail="PHM 資料庫尚未建立。請先執行資料庫建立腳本來導入 PHM 數據。"
        )
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in get_phm_database_bearings: {error_detail}")
        raise HTTPException(
            status_code=500,
            detail=f"資料庫查詢錯誤: {str(e)}"
        )


@app.get("/api/phm/database/bearing/{bearing_name}", response_model=Dict)
async def get_phm_bearing_info(bearing_name: str):
    """獲取特定軸承的詳細資訊"""
    try:
        query = PHMDatabaseQuery()
        bearing = query.get_bearing_info(bearing_name)

        if bearing is None:
            raise HTTPException(
                status_code=404,
                detail=f"Bearing {bearing_name} not found"
            )

        return bearing
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/database/bearing/{bearing_name}/files", response_model=Dict)
async def get_phm_bearing_files(
    bearing_name: str,
    offset: int = 0,
    limit: int = 100
):
    """獲取軸承的檔案列表（分頁）"""
    try:
        query = PHMDatabaseQuery()
        result = query.get_file_list(bearing_name, offset, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/database/bearing/{bearing_name}/measurements",
         response_model=Dict)
async def get_phm_bearing_measurements(
    bearing_name: str,
    file_number: Optional[int] = None,
    offset: int = 0,
    limit: int = 1000
):
    """獲取軸承的測量資料（分頁）"""
    try:
        query = PHMDatabaseQuery()
        result = query.get_measurements(
            bearing_name,
            file_number,
            offset,
            limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/database/bearing/{bearing_name}/file/{file_number}/data",
         response_model=Dict)
async def get_phm_file_data(bearing_name: str, file_number: int):
    """獲取完整的檔案資料用於分析"""
    try:
        query = PHMDatabaseQuery()
        data = query.get_file_data_for_analysis(bearing_name, file_number)

        if data is None:
            raise HTTPException(
                status_code=404,
                detail=f"File {file_number} not found for {bearing_name}"
            )

        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/database/bearing/{bearing_name}/statistics",
         response_model=Dict)
async def get_phm_bearing_statistics(bearing_name: str):
    """獲取軸承的統計資訊"""
    try:
        query = PHMDatabaseQuery()
        stats = query.get_bearing_file_statistics(bearing_name)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/database/bearing/{bearing_name}/anomalies",
         response_model=Dict)
async def search_phm_anomalies(
    bearing_name: str,
    threshold_h: float = 10.0,
    threshold_v: float = 10.0,
    limit: int = 100
):
    """搜尋異常振動資料"""
    try:
        query = PHMDatabaseQuery()
        anomalies = query.search_anomalies(
            bearing_name,
            threshold_h,
            threshold_v,
            limit
        )
        return {
            "bearing_name": bearing_name,
            "threshold_horizontal": threshold_h,
            "threshold_vertical": threshold_v,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# Algorithm Calculation Endpoints
# ========================================

@app.get("/api/algorithms/time-domain/{bearing_name}/{file_number}", response_model=Dict)
async def calculate_time_domain_features(bearing_name: str, file_number: int):
    """計算時域特徵"""
    try:
        # 使用連接管理器獲取資料庫連接
        with get_db_connection() as conn:

            # 查詢數據
            query = """
            SELECT m.horizontal_acceleration, m.vertical_acceleration
            FROM measurements m
            JOIN measurement_files mf ON m.file_id = mf.file_id
            JOIN bearings b ON mf.bearing_id = b.bearing_id
            WHERE b.bearing_name = ? AND mf.file_number = ?
            """

            df = pd.read_sql_query(query, conn, params=(bearing_name, file_number))

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")

        # 計算水平和垂直方向的時域特徵
        horiz = df['horizontal_acceleration'].values
        vert = df['vertical_acceleration'].values

        # 原始數據轉換為 DataFrame 以供 EO 方法使用
        horiz_df = pd.DataFrame({'horizontal_acceleration': horiz})
        vert_df = pd.DataFrame({'vertical_acceleration': vert})

        td = TimeDomain()

        features = {
            "bearing_name": bearing_name,
            "file_number": file_number,
            "data_points": len(df),
            "horizontal": {
                "peak": float(td.peak(horiz)),
                "avg": float(td.avg(horiz)),
                "rms": float(td.rms(horiz)),
                "crest_factor": float(td.cf(horiz)),
                "kurtosis": float(td.kurt(horiz)),
                "eo": float(td.eo(horiz_df, 'horizontal_acceleration'))
            },
            "vertical": {
                "peak": float(td.peak(vert)),
                "avg": float(td.avg(vert)),
                "rms": float(td.rms(vert)),
                "crest_factor": float(td.cf(vert)),
                "kurtosis": float(td.kurt(vert)),
                "eo": float(td.eo(vert_df, 'vertical_acceleration'))
            },
            "signal_data": {
                "horizontal": horiz[:SIGNAL_DISPLAY_LIMIT].tolist(),  # 使用配置參數限制顯示點數
                "vertical": vert[:SIGNAL_DISPLAY_LIMIT].tolist(),
                "time": list(range(min(SIGNAL_DISPLAY_LIMIT, len(horiz))))
            }
        }

        return features

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in calculate_time_domain_features: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/time-domain-trend/{bearing_name}", response_model=Dict)
async def calculate_time_domain_trend(bearing_name: str, max_files: int = 50):
    """計算時域特徵趨勢（多個檔案）"""
    try:
        # 使用連接管理器獲取資料庫連接
        with get_db_connection() as conn:

            # 獲取檔案列表
            cursor = conn.cursor()
            cursor.execute("""
                SELECT mf.file_number, mf.file_id
                FROM measurement_files mf
                JOIN bearings b ON mf.bearing_id = b.bearing_id
                WHERE b.bearing_name = ?
                ORDER BY mf.file_number
                LIMIT ?
            """, (bearing_name, max_files))

            files = cursor.fetchall()

            if not files:
                raise HTTPException(status_code=404, detail="No files found")

            trend_data = {
                "bearing_name": bearing_name,
                "file_count": len(files),
                "horizontal": {
                    "rms": [],
                    "peak": [],
                    "avg": [],
                    "kurtosis": [],
                    "crest_factor": [],
                    "eo": []
                },
                "vertical": {
                    "rms": [],
                    "peak": [],
                    "avg": [],
                    "kurtosis": [],
                    "crest_factor": [],
                    "eo": []
                },
                "file_numbers": []
            }

            td = TimeDomain()

            for file_num, file_id in files:
                # 查詢該檔案的數據
                query = f"""
                SELECT horizontal_acceleration, vertical_acceleration
                FROM measurements
                WHERE file_id = {file_id}
                """
                df = pd.read_sql_query(query, conn)

                if not df.empty:
                    horiz = df['horizontal_acceleration'].values
                    vert = df['vertical_acceleration'].values

                    # 轉換為 DataFrame 以供 EO 方法使用
                    horiz_df = pd.DataFrame({'horizontal_acceleration': horiz})
                    vert_df = pd.DataFrame({'vertical_acceleration': vert})

                    trend_data["file_numbers"].append(file_num)
                    trend_data["horizontal"]["rms"].append(float(td.rms(horiz)))
                    trend_data["horizontal"]["peak"].append(float(td.peak(horiz)))
                    trend_data["horizontal"]["avg"].append(float(td.avg(horiz)))
                    trend_data["horizontal"]["kurtosis"].append(float(td.kurt(horiz)))
                    trend_data["horizontal"]["crest_factor"].append(float(td.cf(horiz)))
                    trend_data["horizontal"]["eo"].append(float(td.eo(horiz_df, 'horizontal_acceleration')))

                    trend_data["vertical"]["rms"].append(float(td.rms(vert)))
                    trend_data["vertical"]["peak"].append(float(td.peak(vert)))
                    trend_data["vertical"]["avg"].append(float(td.avg(vert)))
                    trend_data["vertical"]["kurtosis"].append(float(td.kurt(vert)))
                    trend_data["vertical"]["crest_factor"].append(float(td.cf(vert)))
                    trend_data["vertical"]["eo"].append(float(td.eo(vert_df, 'vertical_acceleration')))

        return trend_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/frequency-domain/{bearing_name}/{file_number}", response_model=Dict)
async def calculate_frequency_domain(bearing_name: str, file_number: int, sampling_rate: int = DEFAULT_SAMPLING_RATE):
    """計算頻域特徵（FFT）"""
    try:
        from scipy import signal as scipy_signal
        from scipy.fft import fft, fftfreq

        # 使用連接管理器獲取資料庫連接
        with get_db_connection() as conn:

            query = """
            SELECT m.horizontal_acceleration, m.vertical_acceleration
            FROM measurements m
            JOIN measurement_files mf ON m.file_id = mf.file_id
            JOIN bearings b ON mf.bearing_id = b.bearing_id
            WHERE b.bearing_name = ? AND mf.file_number = ?
            """

            df = pd.read_sql_query(query, conn, params=(bearing_name, file_number))

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")

        horiz = df['horizontal_acceleration'].values
        vert = df['vertical_acceleration'].values

        # 計算 FFT
        n = len(horiz)
        freq = fftfreq(n, 1/sampling_rate)[:n//2]

        horiz_fft = fft(horiz)
        vert_fft = fft(vert)

        horiz_magnitude = 2.0/n * np.abs(horiz_fft[:n//2])
        vert_magnitude = 2.0/n * np.abs(vert_fft[:n//2])

        # 找出峰值頻率（前10個）
        horiz_peaks_idx = np.argsort(horiz_magnitude)[-10:][::-1]
        vert_peaks_idx = np.argsort(vert_magnitude)[-10:][::-1]

        features = {
            "bearing_name": bearing_name,
            "file_number": file_number,
            "sampling_rate": sampling_rate,
            "frequency_resolution": float(freq[1] - freq[0]) if len(freq) > 1 else 0,
            "horizontal": {
                "peak_frequencies": [float(freq[i]) for i in horiz_peaks_idx],
                "peak_magnitudes": [float(horiz_magnitude[i]) for i in horiz_peaks_idx],
                "total_power": float(np.sum(horiz_magnitude**2))
            },
            "vertical": {
                "peak_frequencies": [float(freq[i]) for i in vert_peaks_idx],
                "peak_magnitudes": [float(vert_magnitude[i]) for i in vert_peaks_idx],
                "total_power": float(np.sum(vert_magnitude**2))
            },
            "spectrum_data": {
                "frequency": freq[:SPECTRUM_DISPLAY_LIMIT].tolist(),  # 使用配置參數限制顯示點數
                "horizontal_magnitude": horiz_magnitude[:SPECTRUM_DISPLAY_LIMIT].tolist(),
                "vertical_magnitude": vert_magnitude[:SPECTRUM_DISPLAY_LIMIT].tolist()
            }
        }

        return features

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/frequency-domain-trend/{bearing_name}", response_model=Dict)
async def calculate_frequency_domain_trend(
    bearing_name: str,
    sampling_rate: int = DEFAULT_SAMPLING_RATE
):
    """計算頻域特徵趨勢（所有檔案）"""
    try:
        import sqlite3
        try:
            from backend.frequencydomain import FrequencyDomain
        except ModuleNotFoundError:
            from frequencydomain import FrequencyDomain

        # 創建 FrequencyDomain 實例
        fd = FrequencyDomain()

        # 定義進度追蹤函數
        def progress_tracker(current: int, total: int, file_number: int):
            """追蹤處理進度"""
            percentage = (current / total) * 100
            print(f"Processing: {current}/{total} ({percentage:.1f}%) - File {file_number}")

        # 計算趨勢
        result = fd.calculate_frequency_domain_trend(
            bearing_name=bearing_name,
            sampling_rate=sampling_rate,
            progress_callback=progress_tracker
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in calculate_frequency_domain_trend: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/envelope/{bearing_name}/{file_number}", response_model=Dict)
async def calculate_envelope_spectrum(
    bearing_name: str,
    file_number: int,
    sampling_rate: int = DEFAULT_SAMPLING_RATE,
    lowcut: float = ENVELOPE_FILTER_LOWCUT,
    highcut: float = ENVELOPE_FILTER_HIGHCUT
):
    """計算包絡頻譜"""
    try:
        import sqlite3
        from scipy import signal as scipy_signal
        from scipy.fft import fft, fftfreq

        # 連接資料庫（使用全域配置）
        conn = sqlite3.connect(PHM_DATABASE_PATH)

        query = """
        SELECT m.horizontal_acceleration, m.vertical_acceleration
        FROM measurements m
        JOIN measurement_files mf ON m.file_id = mf.file_id
        JOIN bearings b ON mf.bearing_id = b.bearing_id
        WHERE b.bearing_name = ? AND mf.file_number = ?
        """

        df = pd.read_sql_query(query, conn, params=(bearing_name, file_number))
        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")

        horiz = df['horizontal_acceleration'].values
        vert = df['vertical_acceleration'].values

        # 設計帶通濾波器
        nyquist = sampling_rate / 2
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = scipy_signal.butter(4, [low, high], btype='band')

        # 帶通濾波
        horiz_filtered = scipy_signal.filtfilt(b, a, horiz)
        vert_filtered = scipy_signal.filtfilt(b, a, vert)

        # 希爾伯特轉換提取包絡
        horiz_envelope = np.abs(scipy_signal.hilbert(horiz_filtered))
        vert_envelope = np.abs(scipy_signal.hilbert(vert_filtered))

        # 對包絡做 FFT
        n = len(horiz_envelope)
        freq = fftfreq(n, 1/sampling_rate)[:n//2]

        horiz_env_fft = fft(horiz_envelope)
        vert_env_fft = fft(vert_envelope)

        horiz_env_magnitude = 2.0/n * np.abs(horiz_env_fft[:n//2])
        vert_env_magnitude = 2.0/n * np.abs(vert_env_fft[:n//2])

        # 找出峰值
        horiz_peaks_idx = np.argsort(horiz_env_magnitude)[-10:][::-1]
        vert_peaks_idx = np.argsort(vert_env_magnitude)[-10:][::-1]

        features = {
            "bearing_name": bearing_name,
            "file_number": file_number,
            "filter_band": {"lowcut": lowcut, "highcut": highcut},
            "horizontal": {
                "peak_frequencies": [float(freq[i]) for i in horiz_peaks_idx if freq[i] > 0],
                "peak_magnitudes": [float(horiz_env_magnitude[i]) for i in horiz_peaks_idx if freq[i] > 0],
                "envelope_rms": float(np.sqrt(np.mean(horiz_envelope**2)))
            },
            "vertical": {
                "peak_frequencies": [float(freq[i]) for i in vert_peaks_idx if freq[i] > 0],
                "peak_magnitudes": [float(vert_env_magnitude[i]) for i in vert_peaks_idx if freq[i] > 0],
                "envelope_rms": float(np.sqrt(np.mean(vert_envelope**2)))
            },
            "envelope_spectrum": {
                "frequency": freq[:ENVELOPE_SPECTRUM_DISPLAY_LIMIT].tolist(),
                "horizontal_magnitude": horiz_env_magnitude[:ENVELOPE_SPECTRUM_DISPLAY_LIMIT].tolist(),
                "vertical_magnitude": vert_env_magnitude[:ENVELOPE_SPECTRUM_DISPLAY_LIMIT].tolist()
            }
        }

        return features

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# Time-Frequency Analysis Endpoints
# ========================================

@app.get("/api/algorithms/stft/{bearing_name}/{file_number}", response_model=Dict)
async def calculate_stft(
    bearing_name: str,
    file_number: int,
    sampling_rate: int = DEFAULT_SAMPLING_RATE,
    window: str = 'hann',
    nperseg: int = 256
):
    """計算短時傅立葉轉換（STFT）"""
    try:
        import sqlite3

        conn = sqlite3.connect(PHM_DATABASE_PATH)

        query = """
        SELECT m.horizontal_acceleration, m.vertical_acceleration
        FROM measurements m
        JOIN measurement_files mf ON m.file_id = mf.file_id
        JOIN bearings b ON mf.bearing_id = b.bearing_id
        WHERE b.bearing_name = ? AND mf.file_number = ?
        """

        df = pd.read_sql_query(query, conn, params=(bearing_name, file_number))
        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")

        horiz = df['horizontal_acceleration'].values
        vert = df['vertical_acceleration'].values

        tf = TimeFrequency()

        # 計算水平和垂直方向的 STFT
        horiz_stft = tf.stft_analysis(horiz, fs=sampling_rate, window=window, nperseg=nperseg)
        vert_stft = tf.stft_analysis(vert, fs=sampling_rate, window=window, nperseg=nperseg)

        # 限制返回的數據量（用於繪圖）
        freq_limit = min(100, len(horiz_stft['frequencies']))
        time_limit = min(100, len(horiz_stft['time']))

        features = {
            "bearing_name": bearing_name,
            "file_number": file_number,
            "sampling_rate": sampling_rate,
            "window": window,
            "nperseg": nperseg,
            "horizontal": {
                "np4": horiz_stft['np4'],
                "max_freq": horiz_stft['max_freq'],
                "max_time": horiz_stft['max_time'],
                "max_magnitude": horiz_stft['max_magnitude'],
                "total_energy": horiz_stft['total_energy']
            },
            "vertical": {
                "np4": vert_stft['np4'],
                "max_freq": vert_stft['max_freq'],
                "max_time": vert_stft['max_time'],
                "max_magnitude": vert_stft['max_magnitude'],
                "total_energy": vert_stft['total_energy']
            },
            "spectrogram_data": {
                "frequencies": horiz_stft['frequencies'][:freq_limit].tolist(),
                "time": horiz_stft['time'][:time_limit].tolist(),
                "horizontal_magnitude": horiz_stft['magnitude'][:freq_limit, :time_limit].tolist(),
                "vertical_magnitude": vert_stft['magnitude'][:freq_limit, :time_limit].tolist()
            }
        }

        return features

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in calculate_stft: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/cwt/{bearing_name}/{file_number}", response_model=Dict)
async def calculate_cwt(
    bearing_name: str,
    file_number: int,
    sampling_rate: int = DEFAULT_SAMPLING_RATE,
    wavelet: str = 'morl'
):
    """計算連續小波轉換（CWT）"""
    try:
        import sqlite3

        conn = sqlite3.connect(PHM_DATABASE_PATH)

        query = """
        SELECT m.horizontal_acceleration, m.vertical_acceleration
        FROM measurements m
        JOIN measurement_files mf ON m.file_id = mf.file_id
        JOIN bearings b ON mf.bearing_id = b.bearing_id
        WHERE b.bearing_name = ? AND mf.file_number = ?
        """

        df = pd.read_sql_query(query, conn, params=(bearing_name, file_number))
        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")

        horiz = df['horizontal_acceleration'].values
        vert = df['vertical_acceleration'].values

        tf = TimeFrequency()

        # 計算 CWT
        scales = np.arange(1, 65)
        horiz_cwt = tf.cwt_analysis(horiz, fs=sampling_rate, wavelet=wavelet, scales=scales)
        vert_cwt = tf.cwt_analysis(vert, fs=sampling_rate, wavelet=wavelet, scales=scales)

        # 限制返回的數據量
        scale_limit = min(64, len(scales))
        time_limit = min(500, horiz_cwt['magnitude'].shape[1])

        features = {
            "bearing_name": bearing_name,
            "file_number": file_number,
            "sampling_rate": sampling_rate,
            "wavelet": wavelet,
            "horizontal": {
                "np4": horiz_cwt['np4'],
                "max_scale": horiz_cwt['max_scale'],
                "max_freq": horiz_cwt['max_freq'],
                "total_energy": horiz_cwt['total_energy'],
                "energy_per_scale": horiz_cwt['energy_per_scale'].tolist()
            },
            "vertical": {
                "np4": vert_cwt['np4'],
                "max_scale": vert_cwt['max_scale'],
                "max_freq": vert_cwt['max_freq'],
                "total_energy": vert_cwt['total_energy'],
                "energy_per_scale": vert_cwt['energy_per_scale'].tolist()
            },
            "cwt_data": {
                "scales": scales[:scale_limit].tolist(),
                "frequencies": horiz_cwt['frequencies'][:scale_limit].tolist(),
                "horizontal_magnitude": horiz_cwt['magnitude'][:scale_limit, :time_limit].tolist(),
                "vertical_magnitude": vert_cwt['magnitude'][:scale_limit, :time_limit].tolist()
            }
        }

        return features

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in calculate_cwt: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/higher-order/{bearing_name}/{file_number}", response_model=Dict)
async def calculate_higher_order_stats(
    bearing_name: str,
    file_number: int,
    sampling_rate: int = DEFAULT_SAMPLING_RATE,
    segment_count: int = 10
):
    """
    計算高階統計特徵 (已整合至進階濾波特徵)

    此端點已整合至 /api/algorithms/filter-features
    為了向後兼容性保留，內部委託給 FilterProcess
    """
    try:
        import sqlite3

        conn = sqlite3.connect(PHM_DATABASE_PATH)

        query = """
        SELECT m.horizontal_acceleration, m.vertical_acceleration
        FROM measurements m
        JOIN measurement_files mf ON m.file_id = mf.file_id
        JOIN bearings b ON mf.bearing_id = b.bearing_id
        WHERE b.bearing_name = ? AND mf.file_number = ?
        """

        df = pd.read_sql_query(query, conn, params=(bearing_name, file_number))
        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")

        horiz = df['horizontal_acceleration'].values
        vert = df['vertical_acceleration'].values

        # 使用 FilterProcess 的統一實現（更精確）
        horiz_stats = FilterProcess.calculate_all_features(horiz, sampling_rate, segment_count)
        vert_stats = FilterProcess.calculate_all_features(vert, sampling_rate, segment_count)

        features = {
            "bearing_name": bearing_name,
            "file_number": file_number,
            "data_points": len(df),
            "sampling_rate": sampling_rate,
            "segment_count": segment_count,
            "horizontal": horiz_stats,
            "vertical": vert_stats,
            "_note": "此 API 已整合至 /api/algorithms/filter-features，建議使用該端點"
        }

        return features

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in calculate_higher_order_stats: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/spectrogram/{bearing_name}/{file_number}", response_model=Dict)
async def calculate_spectrogram(
    bearing_name: str,
    file_number: int,
    sampling_rate: int = DEFAULT_SAMPLING_RATE
):
    """計算頻譜圖"""
    try:
        import sqlite3

        conn = sqlite3.connect(PHM_DATABASE_PATH)

        query = """
        SELECT m.horizontal_acceleration, m.vertical_acceleration
        FROM measurements m
        JOIN measurement_files mf ON m.file_id = mf.file_id
        JOIN bearings b ON mf.bearing_id = b.bearing_id
        WHERE b.bearing_name = ? AND mf.file_number = ?
        """

        df = pd.read_sql_query(query, conn, params=(bearing_name, file_number))
        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")

        horiz = df['horizontal_acceleration'].values
        vert = df['vertical_acceleration'].values

        tf = TimeFrequency()

        # 計算頻譜圖
        horiz_spec = tf.spectrogram_features(horiz, fs=sampling_rate)
        vert_spec = tf.spectrogram_features(vert, fs=sampling_rate)

        # 限制返回的數據量
        freq_limit = min(100, len(horiz_spec['frequencies']))
        time_limit = min(100, len(horiz_spec['time']))

        features = {
            "bearing_name": bearing_name,
            "file_number": file_number,
            "sampling_rate": sampling_rate,
            "horizontal": {
                "mean_power": horiz_spec['mean_power'],
                "max_power": horiz_spec['max_power'],
                "std_power": horiz_spec['std_power'],
                "peak_freq": horiz_spec['peak_freq'],
                "peak_time": horiz_spec['peak_time']
            },
            "vertical": {
                "mean_power": vert_spec['mean_power'],
                "max_power": vert_spec['max_power'],
                "std_power": vert_spec['std_power'],
                "peak_freq": vert_spec['peak_freq'],
                "peak_time": vert_spec['peak_time']
            },
            "spectrogram_data": {
                "frequencies": horiz_spec['frequencies'][:freq_limit].tolist(),
                "time": horiz_spec['time'][:time_limit].tolist(),
                "horizontal_power_db": horiz_spec['power_db'][:freq_limit, :time_limit].tolist(),
                "vertical_power_db": vert_spec['power_db'][:freq_limit, :time_limit].tolist()
            }
        }

        return features

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in calculate_spectrogram: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/frequency-fft/{bearing_name}/{file_number}", response_model=Dict)
async def calculate_frequency_fft(bearing_name: str, file_number: int, sampling_rate: int = DEFAULT_SAMPLING_RATE):
    """計算低頻FFT特徵（FM0）"""
    try:
        import sqlite3

        # 連接資料庫（使用全域配置）
        conn = sqlite3.connect(PHM_DATABASE_PATH)

        query = """
        SELECT m.horizontal_acceleration, m.vertical_acceleration
        FROM measurements m
        JOIN measurement_files mf ON m.file_id = mf.file_id
        JOIN bearings b ON mf.bearing_id = b.bearing_id
        WHERE b.bearing_name = ? AND mf.file_number = ?
        """

        df = pd.read_sql_query(query, conn, params=(bearing_name, file_number))
        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")

        horiz = df['horizontal_acceleration'].values
        vert = df['vertical_acceleration'].values

        fd = FrequencyDomain()

        # 計算低頻FM0特徵
        horiz_fftoutput, horiz_total_fft_mgs, horiz_total_fft_bi, horiz_low_fm0 = fd.fft_fm0_si(horiz, sampling_rate)
        vert_fftoutput, vert_total_fft_mgs, vert_total_fft_bi, vert_low_fm0 = fd.fft_fm0_si(vert, sampling_rate)

        features = {
            "bearing_name": bearing_name,
            "file_number": file_number,
            "sampling_rate": sampling_rate,
            "horizontal": {
                "low_fm0": float(horiz_low_fm0),
                "total_fft_mgs": float(horiz_total_fft_mgs),
                "total_fft_bi": float(horiz_total_fft_bi)
            },
            "vertical": {
                "low_fm0": float(vert_low_fm0),
                "total_fft_mgs": float(vert_total_fft_mgs),
                "total_fft_bi": float(vert_total_fft_bi)
            },
            "fft_spectrum": {
                "frequencies": horiz_fftoutput['freqs'].tolist()[:SPECTRUM_DISPLAY_LIMIT],  # 使用配置參數限制须譜顯示點數
                "horizontal_magnitude": horiz_fftoutput['abs_fft_n'].tolist()[:SPECTRUM_DISPLAY_LIMIT],
                "vertical_magnitude": vert_fftoutput['abs_fft_n'].tolist()[:SPECTRUM_DISPLAY_LIMIT]
            }
        }

        return features

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in calculate_frequency_fft: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/frequency-tsa/{bearing_name}/{file_number}", response_model=Dict)
async def calculate_frequency_tsa(bearing_name: str, file_number: int, sampling_rate: int = DEFAULT_SAMPLING_RATE):
    """計算TSA高頻FFT特徵（FM0）"""
    try:
        import sqlite3

        # 連接資料庫（使用全域配置）
        conn = sqlite3.connect(PHM_DATABASE_PATH)

        query = """
        SELECT m.horizontal_acceleration, m.vertical_acceleration
        FROM measurements m
        JOIN measurement_files mf ON m.file_id = mf.file_id
        JOIN bearings b ON mf.bearing_id = b.bearing_id
        WHERE b.bearing_name = ? AND mf.file_number = ?
        """

        df = pd.read_sql_query(query, conn, params=(bearing_name, file_number))
        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")

        horiz = df['horizontal_acceleration'].values
        vert = df['vertical_acceleration'].values

        fd = FrequencyDomain()

        # 首先計算基本FFT（用於TSA）
        horiz_fftoutput, _, _, horiz_low_fm0 = fd.fft_fm0_si(horiz, sampling_rate)
        vert_fftoutput, _, _, vert_low_fm0 = fd.fft_fm0_si(vert, sampling_rate)

        # 計算TSA高頻特徵
        horiz_tsa_fftoutput, horiz_total_tsa_fft_mgs, horiz_total_tsa_fft_bi, horiz_high_fm0 = fd.tsa_fft_fm0_slf(horiz, sampling_rate, horiz_fftoutput)
        vert_tsa_fftoutput, vert_total_tsa_fft_mgs, vert_total_tsa_fft_bi, vert_high_fm0 = fd.tsa_fft_fm0_slf(vert, sampling_rate, vert_fftoutput)

        features = {
            "bearing_name": bearing_name,
            "file_number": file_number,
            "sampling_rate": sampling_rate,
            "horizontal": {
                "low_fm0": float(horiz_low_fm0),
                "high_fm0": float(horiz_high_fm0),
                "total_tsa_fft_mgs": float(horiz_total_tsa_fft_mgs),
                "total_tsa_fft_bi": float(horiz_total_tsa_fft_bi)
            },
            "vertical": {
                "low_fm0": float(vert_low_fm0),
                "high_fm0": float(vert_high_fm0),
                "total_tsa_fft_mgs": float(vert_total_tsa_fft_mgs),
                "total_tsa_fft_bi": float(vert_total_tsa_fft_bi)
            },
            "tsa_spectrum": {
                "frequencies": horiz_tsa_fftoutput['multiply_freqs'].tolist()[:SPECTRUM_DISPLAY_LIMIT],  # 使用配置參數限制頻譜顯示點數
                "horizontal_magnitude": horiz_tsa_fftoutput['tsa_abs_fft_n'].tolist()[:SPECTRUM_DISPLAY_LIMIT],
                "vertical_magnitude": vert_tsa_fftoutput['tsa_abs_fft_n'].tolist()[:SPECTRUM_DISPLAY_LIMIT]
            }
        }

        return features

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in calculate_frequency_tsa: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/hilbert/{bearing_name}/{file_number}", response_model=Dict)
async def calculate_hilbert_transform(
    bearing_name: str,
    file_number: int,
    segment_count: int = 10
):
    """計算希爾伯特轉換特徵（包絡分析與NB4）"""
    try:
        import sqlite3

        # 連接資料庫（使用全域配置）
        conn = sqlite3.connect(PHM_DATABASE_PATH)

        query = """
        SELECT m.horizontal_acceleration, m.vertical_acceleration
        FROM measurements m
        JOIN measurement_files mf ON m.file_id = mf.file_id
        JOIN bearings b ON mf.bearing_id = b.bearing_id
        WHERE b.bearing_name = ? AND mf.file_number = ?
        """

        df = pd.read_sql_query(query, conn, params=(bearing_name, file_number))
        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")

        horiz = df['horizontal_acceleration'].values
        vert = df['vertical_acceleration'].values

        ht = HilbertTransform()

        # 計算水平和垂直方向的希爾伯特轉換
        horiz_result = ht.analyze_signal(horiz, segment_count)
        vert_result = ht.analyze_signal(vert, segment_count)

        features = {
            "bearing_name": bearing_name,
            "file_number": file_number,
            "data_points": len(df),
            "segment_count": segment_count,
            "horizontal": {
                "nb4": float(horiz_result['nb4']),
                "envelope_mean": float(horiz_result['envelope_stats']['mean']),
                "envelope_std": float(horiz_result['envelope_stats']['std']),
                "envelope_max": float(horiz_result['envelope_stats']['max']),
                "envelope_min": float(horiz_result['envelope_stats']['min']),
                "envelope_rms": float(horiz_result['envelope_stats']['rms']),
                "envelope_peak_to_peak": float(horiz_result['envelope_stats']['peak_to_peak'])
            },
            "vertical": {
                "nb4": float(vert_result['nb4']),
                "envelope_mean": float(vert_result['envelope_stats']['mean']),
                "envelope_std": float(vert_result['envelope_stats']['std']),
                "envelope_max": float(vert_result['envelope_stats']['max']),
                "envelope_min": float(vert_result['envelope_stats']['min']),
                "envelope_rms": float(vert_result['envelope_stats']['rms']),
                "envelope_peak_to_peak": float(vert_result['envelope_stats']['peak_to_peak'])
            },
            "envelope_data": {
                "horizontal": horiz_result['envelope'][:SIGNAL_DISPLAY_LIMIT].tolist(),
                "vertical": vert_result['envelope'][:SIGNAL_DISPLAY_LIMIT].tolist(),
                "time": list(range(min(SIGNAL_DISPLAY_LIMIT, len(horiz_result['envelope']))))
            },
            "instantaneous_frequency": {
                "horizontal": horiz_result['instantaneous_frequency'][:SIGNAL_DISPLAY_LIMIT].tolist(),
                "vertical": vert_result['instantaneous_frequency'][:SIGNAL_DISPLAY_LIMIT].tolist()
            }
        }

        return features

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in calculate_hilbert_transform: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# Advanced Filter Process Endpoints (NA4, FM4, M6A, M8A, ER)
# ========================================

@app.get("/api/algorithms/filter-features/{bearing_name}/{file_number}",
         response_model=Dict)
async def calculate_filter_features(
    bearing_name: str,
    file_number: int,
    sampling_rate: int = DEFAULT_SAMPLING_RATE,
    segment_count: int = 10
):
    """計算進階濾波特徵 (NA4, FM4, M6A, M8A, ER)"""
    try:
        import sqlite3

        # 連接資料庫
        conn = sqlite3.connect(PHM_DATABASE_PATH)

        query = """
        SELECT m.horizontal_acceleration, m.vertical_acceleration
        FROM measurements m
        JOIN measurement_files mf ON m.file_id = mf.file_id
        JOIN bearings b ON mf.bearing_id = b.bearing_id
        WHERE b.bearing_name = ? AND mf.file_number = ?
        """

        df = pd.read_sql_query(query, conn, params=(bearing_name, file_number))
        conn.close()

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")

        horiz = df['horizontal_acceleration'].values
        vert = df['vertical_acceleration'].values

        # 計算水平和垂直方向的進階特徵
        horiz_features = FilterProcess.calculate_all_features(
            horiz, sampling_rate, segment_count
        )
        vert_features = FilterProcess.calculate_all_features(
            vert, sampling_rate, segment_count
        )

        features = {
            "bearing_name": bearing_name,
            "file_number": file_number,
            "data_points": len(df),
            "sampling_rate": sampling_rate,
            "segment_count": segment_count,
            "horizontal": horiz_features,
            "vertical": vert_features
        }

        return features

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in calculate_filter_features: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/filter-trend/{bearing_name}", response_model=Dict)
async def calculate_filter_trend(
    bearing_name: str,
    max_files: int = 50,
    sampling_rate: int = DEFAULT_SAMPLING_RATE
):
    """計算進階濾波特徵趨勢（多個檔案）"""
    try:
        import sqlite3

        # 連接資料庫
        conn = sqlite3.connect(PHM_DATABASE_PATH)

        # 獲取檔案列表
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mf.file_number, mf.file_id
            FROM measurement_files mf
            JOIN bearings b ON mf.bearing_id = b.bearing_id
            WHERE b.bearing_name = ?
            ORDER BY mf.file_number
            LIMIT ?
        """, (bearing_name, max_files))

        files = cursor.fetchall()

        if not files:
            raise HTTPException(status_code=404, detail="No files found")

        trend_data = {
            "bearing_name": bearing_name,
            "file_count": len(files),
            "horizontal": {
                "na4": [],
                "fm4": [],
                "m6a": [],
                "m8a": [],
                "er": []
            },
            "vertical": {
                "na4": [],
                "fm4": [],
                "m6a": [],
                "m8a": [],
                "er": []
            },
            "file_numbers": []
        }

        for file_num, file_id in files:
            # 查詢該檔案的數據
            query = f"""
            SELECT horizontal_acceleration, vertical_acceleration
            FROM measurements
            WHERE file_id = {file_id}
            """
            df = pd.read_sql_query(query, conn)

            if not df.empty:
                horiz = df['horizontal_acceleration'].values
                vert = df['vertical_acceleration'].values

                horiz_features = FilterProcess.calculate_all_features(
                    horiz, sampling_rate
                )
                vert_features = FilterProcess.calculate_all_features(
                    vert, sampling_rate
                )

                trend_data["file_numbers"].append(file_num)
                trend_data["horizontal"]["na4"].append(horiz_features["na4"])
                trend_data["horizontal"]["fm4"].append(horiz_features["fm4"])
                trend_data["horizontal"]["m6a"].append(horiz_features["m6a"])
                trend_data["horizontal"]["m8a"].append(horiz_features["m8a"])
                trend_data["horizontal"]["er"].append(horiz_features["er"])

                trend_data["vertical"]["na4"].append(vert_features["na4"])
                trend_data["vertical"]["fm4"].append(vert_features["fm4"])
                trend_data["vertical"]["m6a"].append(vert_features["m6a"])
                trend_data["vertical"]["m8a"].append(vert_features["m8a"])
                trend_data["vertical"]["er"].append(vert_features["er"])

        conn.close()
        return trend_data

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in calculate_filter_trend: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Temperature Data API Endpoints ====================

# Initialize temperature query instance
temp_query = PHMTemperatureQuery()

@app.get("/api/temperature/bearings")
async def get_temperature_bearings():
    """獲取所有有溫度資料的軸承"""
    try:
        bearings = temp_query.get_all_bearings()
        return {"bearings": bearings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving temperature bearings: {str(e)}")

@app.get("/api/temperature/bearing/{bearing_name}")
async def get_temperature_bearing_info(bearing_name: str):
    """獲取特定軸承的溫度資訊"""
    try:
        bearing_info = temp_query.get_bearing_info(bearing_name)
        if not bearing_info:
            raise HTTPException(status_code=404, detail=f"Bearing {bearing_name} not found")

        # 獲取文件列表
        files = temp_query.get_bearing_files(bearing_name)

        # 獲取統計資訊
        stats = temp_query.get_temperature_statistics(bearing_name)

        return {
            "bearing_info": bearing_info,
            "files": files,
            "statistics": stats[0] if stats else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving bearing info: {str(e)}")

@app.get("/api/temperature/data/{bearing_name}")
async def get_temperature_data(
    bearing_name: str,
    file_number: Optional[int] = None,
    limit: int = 1000
):
    """獲取溫度測量資料"""
    try:
        data = temp_query.get_temperature_data(bearing_name, file_number, limit)
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving temperature data: {str(e)}")

@app.get("/api/temperature/trends/{bearing_name}")
async def get_temperature_trends(bearing_name: str, file_count: int = 50):
    """獲取溫度趨勢資料"""
    try:
        trends = temp_query.get_temperature_trends(bearing_name, file_count)
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving temperature trends: {str(e)}")

@app.get("/api/temperature/statistics")
async def get_temperature_statistics(bearing_name: Optional[str] = None):
    """獲取溫度統計資訊"""
    try:
        stats = temp_query.get_temperature_statistics(bearing_name)
        return {"statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving temperature statistics: {str(e)}")

@app.get("/api/temperature/database/info")
async def get_temperature_database_info():
    """獲取溫度資料庫基本資訊"""
    try:
        info = temp_query.get_database_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving database info: {str(e)}")

@app.get("/api/temperature/search")
async def search_temperature_data(
    bearing_name: Optional[str] = None,
    min_temperature: Optional[float] = None,
    max_temperature: Optional[float] = None,
    file_start: Optional[int] = None,
    file_end: Optional[int] = None,
    limit: int = 1000
):
    """搜尋溫度資料"""
    try:
        file_range = (file_start, file_end) if file_start is not None and file_end is not None else None

        results = temp_query.search_temperature_data(
            bearing_name=bearing_name,
            min_temperature=min_temperature,
            max_temperature=max_temperature,
            file_number_range=file_range,
            limit=limit
        )

        return {
            "results": results,
            "count": len(results),
            "search_params": {
                "bearing_name": bearing_name,
                "min_temperature": min_temperature,
                "max_temperature": max_temperature,
                "file_range": file_range,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching temperature data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081, reload=True)
