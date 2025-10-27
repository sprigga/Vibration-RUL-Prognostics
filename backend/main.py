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

try:
    from backend.database import init_db, get_db
    from backend.models import AnalysisResult, GuideSpec
    from backend.phm_models import PHMBearing
    from backend.phm_processor import PHMDataProcessor
    from backend.phm_query import PHMDatabaseQuery
    from backend.config import PHM_DATABASE_PATH, CORS_ORIGINS, DEFAULT_SAMPLING_RATE
    from backend.timefrequency import TimeFrequency
except ModuleNotFoundError:
    from database import init_db, get_db
    from models import AnalysisResult, GuideSpec
    from phm_models import PHMBearing
    from phm_processor import PHMDataProcessor
    from phm_query import PHMDatabaseQuery
    from config import PHM_DATABASE_PATH, CORS_ORIGINS, DEFAULT_SAMPLING_RATE
    from timefrequency import TimeFrequency
import json

app = FastAPI(
    title="Linear Guide Vibration Analysis API",
    description="API for CPC Linear Guide health monitoring and fault diagnosis",
    version="1.0.0"
)

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


class FrequencyCalculationRequest(BaseModel):
    v: float  # velocity m/s
    D: float  # ball diameter mm
    L: float  # slider length mm
    n_balls: int
    contact_angle: float
    raceway_diameter: float


# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()


# Health check
@app.get("/")
async def root():
    return {
        "message": "Linear Guide Vibration Analysis API",
        "version": "1.0.0",
        "status": "running"
    }


# Frequency calculation endpoint
@app.post("/api/calculate-frequencies", response_model=Dict)
async def calculate_frequencies(params: FrequencyCalculationRequest):
    """Calculate theoretical fault frequencies for linear guide"""
    try:
        v = params.v
        D = params.D / 1000  # convert to meters
        ball_spacing = params.L / params.n_balls / 1000  # meters

        # Ball Pass Frequency
        BPF = v / ball_spacing if ball_spacing > 0 else 0

        # Ball Spin Frequency
        BSF = v / (np.pi * D) if D > 0 else 0

        # Cage Frequency
        cage_freq = v / (params.L / 1000) if params.L > 0 else 0

        return {
            "BPF": round(BPF, 2),
            "BSF": round(BSF, 2),
            "Cage_Freq": round(cage_freq, 2),
            "2xBPF": round(2 * BPF, 2),
            "3xBPF": round(3 * BPF, 2),
            "harmonics": [
                {"order": i, "frequency": round(i * BPF, 2)}
                for i in range(1, 6)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")


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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)

        # 讀取生成的分析結果
        summary_path = os.path.join(project_root, "phm_analysis_results", "summary.json")
        stats_path = os.path.join(project_root, "phm_analysis_results", "vibration_statistics.csv")

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
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        import sqlite3
        try:
            from backend.timedomain import TimeDomain
        except ModuleNotFoundError:
            from timedomain import TimeDomain

        # 連接資料庫（使用全域配置）
        conn = sqlite3.connect(PHM_DATABASE_PATH)

        # 查詢數據
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

        # 計算水平和垂直方向的時域特徵
        horiz = df['horizontal_acceleration'].values
        vert = df['vertical_acceleration'].values

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
                "kurtosis": float(td.kurt(horiz))
            },
            "vertical": {
                "peak": float(td.peak(vert)),
                "avg": float(td.avg(vert)),
                "rms": float(td.rms(vert)),
                "crest_factor": float(td.cf(vert)),
                "kurtosis": float(td.kurt(vert))
            },
            "signal_data": {
                "horizontal": horiz[:1000].tolist(),  # 只返回前1000個點用於繪圖
                "vertical": vert[:1000].tolist(),
                "time": list(range(min(1000, len(horiz))))
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
        import sqlite3
        try:
            from backend.timedomain import TimeDomain
        except ModuleNotFoundError:
            from timedomain import TimeDomain

        # 連接資料庫（使用全域配置）
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
                "rms": [],
                "peak": [],
                "kurtosis": [],
                "crest_factor": []
            },
            "vertical": {
                "rms": [],
                "peak": [],
                "kurtosis": [],
                "crest_factor": []
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

                trend_data["file_numbers"].append(file_num)
                trend_data["horizontal"]["rms"].append(float(td.rms(horiz)))
                trend_data["horizontal"]["peak"].append(float(td.peak(horiz)))
                trend_data["horizontal"]["kurtosis"].append(float(td.kurt(horiz)))
                trend_data["horizontal"]["crest_factor"].append(float(td.cf(horiz)))

                trend_data["vertical"]["rms"].append(float(td.rms(vert)))
                trend_data["vertical"]["peak"].append(float(td.peak(vert)))
                trend_data["vertical"]["kurtosis"].append(float(td.kurt(vert)))
                trend_data["vertical"]["crest_factor"].append(float(td.cf(vert)))

        conn.close()
        return trend_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/frequency-domain/{bearing_name}/{file_number}", response_model=Dict)
async def calculate_frequency_domain(bearing_name: str, file_number: int, sampling_rate: int = DEFAULT_SAMPLING_RATE):
    """計算頻域特徵（FFT）"""
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
                "frequency": freq[:1000].tolist(),  # 只返回前1000個點
                "horizontal_magnitude": horiz_magnitude[:1000].tolist(),
                "vertical_magnitude": vert_magnitude[:1000].tolist()
            }
        }

        return features

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/algorithms/envelope/{bearing_name}/{file_number}", response_model=Dict)
async def calculate_envelope_spectrum(
    bearing_name: str,
    file_number: int,
    sampling_rate: int = DEFAULT_SAMPLING_RATE,
    lowcut: float = 4000,
    highcut: float = 10000
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
                "frequency": freq[:500].tolist(),
                "horizontal_magnitude": horiz_env_magnitude[:500].tolist(),
                "vertical_magnitude": vert_env_magnitude[:500].tolist()
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
    sampling_rate: int = DEFAULT_SAMPLING_RATE
):
    """計算高階統計特徵"""
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

        # 計算高階統計
        horiz_stats = tf.higher_order_statistics(horiz, fs=sampling_rate)
        vert_stats = tf.higher_order_statistics(vert, fs=sampling_rate)

        features = {
            "bearing_name": bearing_name,
            "file_number": file_number,
            "data_points": len(df),
            "horizontal": horiz_stats,
            "vertical": vert_stats
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
        try:
            from backend.frequencydomain import FrequencyDomain
        except ModuleNotFoundError:
            from frequencydomain import FrequencyDomain

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
                "frequencies": horiz_fftoutput['freqs'].tolist()[:500],  # 只返回前500個頻率點
                "horizontal_magnitude": horiz_fftoutput['abs_fft_n'].tolist()[:500],
                "vertical_magnitude": vert_fftoutput['abs_fft_n'].tolist()[:500]
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
        try:
            from backend.frequencydomain import FrequencyDomain
        except ModuleNotFoundError:
            from frequencydomain import FrequencyDomain

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
                "frequencies": horiz_tsa_fftoutput['multiply_freqs'].tolist()[:500],  # 只返回前500個頻率點
                "horizontal_magnitude": horiz_tsa_fftoutput['tsa_abs_fft_n'].tolist()[:500],
                "vertical_magnitude": vert_tsa_fftoutput['tsa_abs_fft_n'].tolist()[:500]
            }
        }

        return features

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error in calculate_frequency_tsa: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
