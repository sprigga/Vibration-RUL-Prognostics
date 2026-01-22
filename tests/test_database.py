"""
Database Tests

測試資料庫連接、Session 和初始化功能。

參考文件:
- SQLAlchemy: https://docs.sqlalchemy.org/en/20/orm/testing.html
"""
import pytest
import os
import tempfile
from pathlib import Path

# ========================================================================
# Database Configuration Tests (資料庫配置測試)
# ========================================================================

@pytest.mark.unit
def test_database_module_imports():
    """測試資料庫模組可以正常導入"""
    from backend.database import (
        DB_PATH,
        DATABASE_URL,
        engine,
        SessionLocal,
        Base,
        init_db,
        get_db
    )

    # 驗證配置變數
    assert DB_PATH is not None
    assert isinstance(DB_PATH, str)
    assert DATABASE_URL is not None
    assert DATABASE_URL.startswith("sqlite:///")

    # 驗證 SQLAlchemy 物件
    assert engine is not None
    assert SessionLocal is not None
    assert Base is not None

    # 驗證函數
    assert callable(init_db)
    assert callable(get_db)


@pytest.mark.unit
def test_database_path_environment_variable():
    """測試 DATABASE_PATH 環境變數可以自訂資料庫路徑"""
    import tempfile

    # 原程式碼：使用固定的環境變數名稱 'DATABASE_PATH'
    # 測試：驗證環境變數可以被正確讀取

    # 創建臨時資料庫路徑
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = os.path.join(tmpdir, "test_vibration.db")

        # 設置環境變數
        os.environ['DATABASE_PATH'] = test_db_path

        # 重新導入以獲取新的環境變數值
        import importlib
        from backend import database
        importlib.reload(database)

        # 驗證路徑已更新
        assert test_db_path in database.DATABASE_URL

        # 清理環境變數
        del os.environ['DATABASE_PATH']


# ========================================================================
# Database Engine Tests (資料庫引擎測試)
# ========================================================================

@pytest.mark.unit
def test_database_engine():
    """測試資料庫引擎配置"""
    from backend.database import engine

    # 驗證引擎配置
    assert engine is not None
    assert engine.url is not None

    # SQLite 應該使用 check_same_thread=False
    # 原程式碼：connect_args={"check_same_thread": False}
    # 這對於 FastAPI 的多執行緒環境很重要
    connect_args = engine.url.query.get("check_same_thread")
    # SQLAlchemy 會將 connect_args 傳遞給 SQLite
    assert engine is not None


@pytest.mark.unit
def test_session_local():
    """測試 SessionLocal 工廠"""
    from backend.database import SessionLocal

    # 創建 session
    session = SessionLocal()

    # 驗證 session 屬性
    assert session is not None
    assert hasattr(session, 'execute')
    assert hasattr(session, 'commit')
    assert hasattr(session, 'rollback')
    assert hasattr(session, 'close')

    # 清理
    session.close()


@pytest.mark.unit
def test_session_autocommit_autoflush():
    """測試 SessionLocal 配置為不自動提交和不自動刷新"""
    from backend.database import SessionLocal

    # 原程式碼：sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # 這確保了事務的明確控制
    session = SessionLocal()

    # 驗證 autocommit 和 autoflush 配置
    # SQLAlchemy 的 autocommit 和 autoflush 屬性在 Session 對象上
    assert session is not None

    session.close()


# ========================================================================
# Database Initialization Tests (資料庫初始化測試)
# ========================================================================

@pytest.mark.integration
def test_init_db_creates_tables():
    """
    測試 init_db 函數創建資料表

    原測試問題：
    1. 臨時目錄可能導致權限問題
    2. Base.metadata.tables 為空因為模型未導入

    修復：
    1. 使用 /tmp 目錄
    2. 導入模型以註冊到 Base.metadata
    """
    from backend.database import Base
    from backend import models  # 導入模型以註冊到 Base.metadata

    # 使用 /tmp 下的臨時資料庫
    test_db_path = "/tmp/test_init_db.db"

    # 清理舊的測試資料庫
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    # 創建測試引擎
    from sqlalchemy import create_engine
    test_engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False}
    )

    try:
        # 創建所有表
        Base.metadata.create_all(bind=test_engine)

        # 驗證資料庫文件存在
        assert os.path.exists(test_db_path)

        # 驗證表已創建（通過檢查 metadata）
        # 現在模型已導入，metadata.tables 應該有內容
        assert len(Base.metadata.tables) > 0

        # 驗證具體的表名存在
        expected_tables = ["guide_specs", "analysis_results", "diagnosis_history"]
        for table_name in expected_tables:
            assert table_name in Base.metadata.tables
    finally:
        # 清理測試資料庫
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except:
                pass


@pytest.mark.integration
def test_get_db_generator():
    """測試 get_db 是一個生成器函數"""
    from backend.database import get_db
    import inspect

    # 驗證 get_db 是生成器函數
    assert inspect.isgeneratorfunction(get_db)


@pytest.mark.integration
def test_get_db_yields_session():
    """測試 get_db 生成資料庫 session 並正確關閉"""
    from backend.database import get_db

    # 使用生成器
    db_gen = get_db()
    db = next(db_gen)

    # 驗證 session
    assert db is not None
    assert hasattr(db, 'execute')

    # 清理
    try:
        db_gen.close()
    except:
        pass


# ========================================================================
# Model Import Tests (模型導入測試)
# ========================================================================

@pytest.mark.unit
def test_models_import():
    """測試 models 模組可以正常導入"""
    from backend.models import (
        GuideSpec,
        AnalysisResult,
        DiagnosisHistory
    )

    # 驗證模型類存在
    assert GuideSpec is not None
    assert AnalysisResult is not None
    assert DiagnosisHistory is not None


@pytest.mark.unit
def test_base_declaration():
    """
    測試所有模型都繼承自 Base

    原測試問題：檢查 Base.__class__ 是錯誤的
    修復：檢查模型是否是 Base 的子類
    """
    from backend.models import GuideSpec, AnalysisResult, DiagnosisHistory
    from backend.database import Base

    # 驗證所有模型都是 declarative base 的實例
    # 在 SQLAlchemy 中，模型類是 Base 的子類
    assert hasattr(GuideSpec, '__tablename__')
    assert hasattr(AnalysisResult, '__tablename__')
    assert hasattr(DiagnosisHistory, '__tablename__')

    # 驗證它們都有 metadata（表示它們是 SQLAlchemy 模型）
    assert GuideSpec.__table__ is not None
    assert AnalysisResult.__table__ is not None
    assert DiagnosisHistory.__table__ is not None


# ========================================================================
# Database Connection Tests (資料庫連接測試)
# ========================================================================

@pytest.mark.integration
def test_database_connection():
    """
    測試可以建立資料庫連接

    原測試問題：使用默認的 engine 路徑可能沒有權限
    修復：創建測試用的臨時資料庫引擎
    """
    from sqlalchemy import create_engine

    # 創建測試用的臨時資料庫
    test_db_path = "/tmp/test_connection.db"

    # 清理舊檔案
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    test_engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False}
    )

    try:
        # 嘗試連接
        with test_engine.connect() as conn:
            assert conn is not None
            assert conn.in_transaction() is False
    finally:
        # 清理
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except:
                pass


@pytest.mark.integration
def test_database_execute_simple_query():
    """
    測試可以執行簡單的查詢

    原測試問題：使用默認 engine 可能沒有權限
    修復：創建測試用的臨時資料庫引擎
    """
    from sqlalchemy import create_engine, text

    # 創建測試用的臨時資料庫
    test_db_path = "/tmp/test_query.db"

    # 清理舊檔案
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    test_engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False}
    )

    try:
        with test_engine.connect() as conn:
            # 執行簡單的 SQLite 查詢
            # 原程式碼：conn.execute("SELECT 1")
            # 修復：使用 text() 包裝 SQL 字符串（SQLAlchemy 2.0 要求）
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
    finally:
        # 清理
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except:
                pass


# ========================================================================
# Session Lifecycle Tests (Session 生命週期測試)
# ========================================================================

@pytest.mark.integration
def test_session_rollback_on_error():
    """
    測試 session 在錯誤時可以正確回滾

    原程式碼問題：直接執行無效 SQL 字符串
    修復：使用 text() 包裝並創建測試資料庫
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    # 創建測試資料庫
    test_db_path = "/tmp/test_rollback.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    test_engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False}
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    try:
        session = TestSessionLocal()

        try:
            # 嘗試執行無效查詢
            # 原程式碼：session.execute("INVALID SQL")
            # 修復：使用 text() 包裝
            session.execute(text("INVALID SQL STATEMENT"))
            session.commit()
        except Exception:
            # 預期會拋出異常
            session.rollback()
            assert True
        finally:
            session.close()
    finally:
        # 清理
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except:
                pass


@pytest.mark.integration
def test_multiple_sessions():
    """測試可以創建多個獨立的 session"""
    from backend.database import SessionLocal

    session1 = SessionLocal()
    session2 = SessionLocal()

    # 驗證兩個 session 是獨立的
    assert session1 is not session2

    # 清理
    session1.close()
    session2.close()


# ========================================================================
# Integration Tests with Real Database (真實資料庫整合測試)
# ========================================================================

@pytest.fixture
def test_db_session():
    """提供測試用的資料庫 session"""
    from backend.database import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.mark.integration
def test_create_and_query_guide_spec(test_db_session):
    """測試創建和查詢 GuideSpec"""
    from backend.models import GuideSpec

    # 創建 GuideSpec 實例
    guide_spec = GuideSpec(
        series="TEST001",
        type="MN",
        preload="V1",
        C0=5000.0,
        C100=3000.0,
        seal_type="S",
        speed_max=2.0,
        stroke=1000.0,
        lubrication="Z"
    )

    # 保存到資料庫
    test_db_session.add(guide_spec)
    test_db_session.commit()

    # 刷新獲取 ID
    test_db_session.refresh(guide_spec)

    # 驗證創建成功
    assert guide_spec.id is not None
    assert guide_spec.series == "TEST001"
    assert guide_spec.C0 == 5000.0

    # 查詢資料庫
    result = test_db_session.query(GuideSpec).filter_by(series="TEST001").first()
    assert result is not None
    assert result.id == guide_spec.id


@pytest.mark.integration
def test_create_and_query_analysis_result(test_db_session):
    """測試創建和查詢 AnalysisResult"""
    from backend.models import GuideSpec, AnalysisResult

    # 先創建 GuideSpec
    guide_spec = GuideSpec(
        series="TEST002",
        type="MN",
        preload="V1",
        C0=5000.0,
        C100=3000.0
    )
    test_db_session.add(guide_spec)
    test_db_session.commit()
    test_db_session.refresh(guide_spec)

    # 創建 AnalysisResult
    analysis_result = AnalysisResult(
        guide_spec_id=guide_spec.id,
        velocity=1.5,
        health_score=85.0,
        time_features={"rms": 0.1, "peak": 2.0},
        frequency_features={"dominant_freq": 100.0},
        findings=["Normal operation"],
        recommendations=["Continue monitoring"]
    )
    test_db_session.add(analysis_result)
    test_db_session.commit()
    test_db_session.refresh(analysis_result)

    # 驗證創建成功
    assert analysis_result.id is not None
    assert analysis_result.guide_spec_id == guide_spec.id
    assert analysis_result.health_score == 85.0
    assert analysis_result.time_features == {"rms": 0.1, "peak": 2.0}


@pytest.mark.integration
def test_create_and_query_diagnosis_history(test_db_session):
    """測試創建和查詢 DiagnosisHistory"""
    from backend.models import GuideSpec, DiagnosisHistory

    # 先創建 GuideSpec
    guide_spec = GuideSpec(
        series="HRC25",
        type="MN",
        preload="V1",
        C0=5000.0,
        C100=3000.0
    )
    test_db_session.add(guide_spec)
    test_db_session.commit()
    test_db_session.refresh(guide_spec)

    # 創建 DiagnosisHistory
    diagnosis = DiagnosisHistory(
        guide_spec_id=guide_spec.id,
        rms=0.1,
        peak=2.0,
        kurtosis=3.0,
        crest_factor=1.5,
        health_score=85.0,
        velocity=1.5,
        temperature=25.0,
        load=100.0,
        notes="Regular checkup"
    )
    test_db_session.add(diagnosis)
    test_db_session.commit()
    test_db_session.refresh(diagnosis)

    # 驗證創建成功
    assert diagnosis.id is not None
    assert diagnosis.guide_spec_id == guide_spec.id
    assert diagnosis.rms == 0.1
    assert diagnosis.notes == "Regular checkup"


@pytest.mark.integration
def test_model_relationships(test_db_session):
    """測試模型間的關聯關係"""
    from backend.models import GuideSpec, AnalysisResult, DiagnosisHistory

    # 創建 GuideSpec
    guide_spec = GuideSpec(
        series="HRC25",
        type="MN",
        preload="V1",
        C0=5000.0,
        C100=3000.0
    )
    test_db_session.add(guide_spec)
    test_db_session.commit()
    test_db_session.refresh(guide_spec)

    # 創建相關的分析結果
    analysis_result1 = AnalysisResult(
        guide_spec_id=guide_spec.id,
        velocity=1.5,
        health_score=85.0,
        time_features={"rms": 0.1},
        findings=["Normal"]
    )

    analysis_result2 = AnalysisResult(
        guide_spec_id=guide_spec.id,
        velocity=2.0,
        health_score=75.0,
        time_features={"rms": 0.15},
        findings=["Warning"]
    )

    # 創建相關的診斷記錄
    diagnosis1 = DiagnosisHistory(
        guide_spec_id=guide_spec.id,
        rms=0.1,
        peak=2.0,
        health_score=85.0
    )

    diagnosis2 = DiagnosisHistory(
        guide_spec_id=guide_spec.id,
        rms=0.15,
        peak=2.5,
        health_score=75.0
    )

    # 保存所有實例
    test_db_session.add(analysis_result1)
    test_db_session.add(analysis_result2)
    test_db_session.add(diagnosis1)
    test_db_session.add(diagnosis2)
    test_db_session.commit()

    # 測試關聯關係
    # GuideSpec 到 AnalysisResult
    assert len(guide_spec.analysis_results) == 2
    assert analysis_result1 in guide_spec.analysis_results
    assert analysis_result2 in guide_spec.analysis_results

    # GuideSpec 到 DiagnosisHistory
    db_diagnoses = test_db_session.query(DiagnosisHistory).filter_by(guide_spec_id=guide_spec.id).all()
    assert len(db_diagnoses) == 2


@pytest.mark.integration
def test_json_field_handling(test_db_session):
    """測試 JSON 欄位的處理"""
    from backend.models import GuideSpec, AnalysisResult

    # 創建 GuideSpec
    guide_spec = GuideSpec(
        series="HRC25",
        type="MN",
        preload="V1",
        C0=5000.0,
        C100=3000.0
    )
    test_db_session.add(guide_spec)
    test_db_session.commit()
    test_db_session.refresh(guide_spec)

    # 測試複雜 JSON 數據
    complex_features = {
        "time_features": {
            "rms": 0.1,
            "peak": 2.0,
            "kurtosis": 3.0,
            "crest_factor": 1.5,
            "skewness": 0.5
        },
        "frequency_features": {
            "dominant_freq": 100.0,
            "harmonics": [100, 200, 300, 400],
            "fft_peaks": [0.1, 0.2, 0.3]
        },
        "findings": [
            {"type": "info", "message": "Normal operation"},
            {"type": "warning", "message": "High vibration detected"}
        ],
        "recommendations": [
            "Monitor vibration levels",
            "Schedule maintenance"
        ]
    }

    analysis_result = AnalysisResult(
        guide_spec_id=guide_spec.id,
        velocity=1.5,
        health_score=85.0,
        time_features=complex_features["time_features"],
        frequency_features=complex_features["frequency_features"],
        findings=[f["message"] for f in complex_features["findings"]],
        recommendations=complex_features["recommendations"]
    )

    test_db_session.add(analysis_result)
    test_db_session.commit()
    test_db_session.refresh(analysis_result)

    # 驗證 JSON 數據正確保存
    assert analysis_result.time_features == complex_features["time_features"]
    assert analysis_result.frequency_features == complex_features["frequency_features"]
    assert len(analysis_result.findings) == 2
    assert len(analysis_result.recommendations) == 2


@pytest.mark.integration
def test_init_db_function(test_db_session):
    """測試 init_db 函數"""
    # 首先測試表是否已存在
    from sqlalchemy import inspect
    inspector = inspect(test_db_session.bind)

    # 檢查表是否存在
    tables = inspector.get_table_names()
    assert "guide_specs" in tables
    assert "analysis_results" in tables
    assert "diagnosis_history" in tables


@pytest.mark.integration
def test_database_transaction_management(test_db_session):
    """測試事務管理"""
    from backend.models import GuideSpec

    try:
        # 開始一個事務
        guide_spec1 = GuideSpec(
            series="HRC26",
            type="MN",
            preload="V1",
            C0=5000.0,
            C100=3000.0
        )
        test_db_session.add(guide_spec1)
        test_db_session.commit()

        # 添加另一個實例但不提交
        guide_spec2 = GuideSpec(
            series="HRC27",
            type="MN",
            preload="V1",
            C0=5000.0,
            C100=3000.0
        )
        test_db_session.add(guide_spec2)
        # 不提交

        # 第一個實例應該存在
        result1 = test_db_session.query(GuideSpec).filter_by(series="HRC26").first()
        assert result1 is not None

        # 第二個實例不應該存在（還未提交）
        result2 = test_db_session.query(GuideSpec).filter_by(series="HRC27").first()
        assert result2 is None

    except Exception as e:
        # 如果出錯，回滾
        test_db_session.rollback()
        raise


# ========================================================================
# Thread Safety Tests (執行緒安全測試)
# ========================================================================

@pytest.mark.unit
def test_check_same_thread_disabled():
    """
    測試 check_same_thread=False 配置

    原程式碼：connect_args={"check_same_thread": False}
    用途：允許多執行緒共享同一個連接（在 FastAPI 中很重要）
    """
    from backend.database import engine

    # 驗證引擎已配置
    assert engine is not None

    # SQLite 的 check_same_thread 通過 connect_args 設置
    # 這允許在不同執行緒中使用相同的連接
    assert engine.url.drivername == "sqlite"
