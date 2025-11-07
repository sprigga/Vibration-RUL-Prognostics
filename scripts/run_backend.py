"""
簡化的 Backend 啟動腳本
只啟動 PHM 相關的 API
"""
import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import json
import tempfile

# 導入 PHM 相關模組
from backend.phm_processor import PHMDataProcessor
from backend.database import init_db, get_db
from backend.phm_models import PHMTestData, PHMPrediction
from backend.phm_query import PHMDatabaseQuery

app = FastAPI(
    title="PHM 2012 Analysis API",
    description="API for PHM bearing RUL prediction",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/")
async def root():
    return {
        "message": "PHM 2012 Analysis API",
        "version": "1.0.0",
        "status": "running"
    }


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


@app.post("/api/phm/upload-bearing-data", response_model=Dict)
async def upload_bearing_data(
    file: UploadFile = File(...),
    bearing_name: str = "Unknown"
):
    """上傳單個 PHM CSV 文件並分析"""
    try:
        processor = PHMDataProcessor()

        # 創建臨時文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # 分析文件
        result = processor.analyze_bearing_file(tmp_path)

        # 清理臨時文件
        os.remove(tmp_path)

        # 保存到數據庫
        db = next(get_db())
        try:
            test_data = PHMTestData(
                bearing_name=bearing_name,
                file_index=0,
                time_min=0,
                horiz_rms=result['horiz_rms'],
                vert_rms=result['vert_rms'],
                horiz_peak=result['horiz_peak'],
                vert_peak=result['vert_peak'],
                horiz_kurtosis=result['horiz_kurtosis'],
                vert_kurtosis=result['vert_kurtosis']
            )
            db.add(test_data)
            db.commit()
            db.refresh(test_data)

            return {
                "id": test_data.id,
                "bearing_name": bearing_name,
                "analysis": result,
                "message": "File analyzed successfully"
            }
        finally:
            db.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phm/analysis-data", response_model=Dict)
async def get_phm_analysis_data():
    """獲取預處理的 PHM 分析數據（從 JSON 文件）"""
    try:
        # 讀取生成的分析結果
        summary_path = "phm_analysis_results/summary.json"
        stats_path = "phm_analysis_results/vibration_statistics.csv"

        if not os.path.exists(summary_path):
            raise HTTPException(
                status_code=404,
                detail="Analysis results not found"
            )

        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = json.load(f)

        # 讀取統計數據
        import pandas as pd
        stats_data = []
        if os.path.exists(stats_path):
            df = pd.read_csv(stats_path)
            stats_data = df.to_dict('records')

        return {
            "summary": summary,
            "statistics": stats_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/phm/predict-rul", response_model=Dict)
async def predict_rul(
    bearing_name: str,
    model_type: str = "baseline"
):
    """預測軸承 RUL（簡單基線模型）"""
    db = next(get_db())
    try:
        # 獲取測試數據
        data = db.query(PHMTestData).filter(
            PHMTestData.bearing_name == bearing_name
        ).order_by(PHMTestData.time_min).all()

        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {bearing_name}"
            )

        # 簡單基線預測：基於峰度趨勢
        kurtosis_values = [d.horiz_kurtosis for d in data]
        latest_kurtosis = kurtosis_values[-1] if kurtosis_values else 3

        # 簡化的 RUL 估計（基於峰度閾值）
        if latest_kurtosis > 10:
            predicted_rul = 500  # 嚴重異常，接近故障
        elif latest_kurtosis > 5:
            predicted_rul = 2000  # 中度異常
        else:
            predicted_rul = 5000  # 正常

        # 保存預測結果
        prediction = PHMPrediction(
            bearing_name=bearing_name,
            predicted_RUL_min=predicted_rul,
            model_type=model_type,
            confidence=0.7,
            features={
                "latest_kurtosis": latest_kurtosis,
                "data_points": len(data)
            }
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        return {
            "id": prediction.id,
            "bearing_name": bearing_name,
            "predicted_RUL_min": predicted_rul,
            "model_type": model_type,
            "confidence": 0.7,
            "features": prediction.features
        }
    finally:
        db.close()


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
    file_number: int = None,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
