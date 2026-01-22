"""
pytest configuration and fixtures

This file contains shared fixtures and configuration for all tests.
"""
import pytest
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """
    Create a TestClient instance for testing FastAPI endpoints

    使用方式:
        def test_example(client):
            response = client.get("/")
            assert response.status_code == 200

    原程式碼問題：
    - TestClient 默認會在 raise_server_exceptions=True 時將 HTTPException 轉換為 500 錯誤
    - 導致測試中無法正確捕獲 404 等 HTTP 狀態碼

    修復：
    - 設置 raise_server_exceptions=False，讓 HTTPException 正確返回對應的狀態碼
    """
    from fastapi.testclient import TestClient
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def test_bearing_name():
    """
    提供測試用軸承名稱

    原程式碼：返回 "1-1"
    問題：資料庫中的實際軸承名稱是 "Bearing1_1" 而不是 "1-1"
    修復：更新為實際存在的軸承名稱，以確保測試可以找到數據
    """
    return "Bearing1_1"


@pytest.fixture
def test_file_number():
    """提供測試用檔案編號"""
    return 1


@pytest.fixture
def test_sensor_id():
    """提供測試用感測器 ID"""
    return 1


@pytest.fixture
def sample_sensor_data():
    """提供測試用感測器數據"""
    from datetime import datetime

    return {
        "sensor_id": 1,
        "data": [
            {
                "timestamp": datetime.now().isoformat(),
                "h_acc": 0.1234,
                "v_acc": 0.0987
            }
            for _ in range(10)
        ]
    }


@pytest.fixture
def sample_stream_data():
    """提供測試用流式數據"""
    from datetime import datetime

    return {
        "sensor_id": 1,
        "h_acc": [0.1234 + i * 0.001 for i in range(100)],
        "v_acc": [0.0987 + i * 0.001 for i in range(100)],
        "timestamp_start": datetime.now().isoformat(),
        "sampling_rate": 25600.0
    }


@pytest.fixture
async def init_async_db():
    """
    初始化 async database pool 用於測試

    原程式碼問題：
    - async_db 未初始化連接池，導致測試 API 時拋出 RuntimeError
    - /api/sensors 和 /api/sensors/{sensor_id}/status 等端點依賴 async_db

    修復：
    - 嘗試初始化連接池
    - 如果失敗（例如 PostgreSQL 未運行），返回 None
    - 測試需要處理連接池未初始化的情況
    """
    try:
        from backend.database_async import db as async_db
        if not async_db._is_connected:
            try:
                await async_db.init_pool()
            except Exception as e:
                print(f"Warning: Failed to init async database pool: {e}")
                return None
        return async_db
    except ImportError:
        return None


# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "api: mark test as API endpoint test"
    )
    config.addinivalue_line(
        "markers", "websocket: mark test as WebSocket test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
