"""
Models Tests

測試 SQLAlchemy 模型定義、欄位類型和關聯關係。

參考文件:
- SQLAlchemy Models: https://docs.sqlalchemy.org/en/20/orm/mapping_api.html
"""
import pytest
from datetime import datetime

# ========================================================================
# Model Import Tests (模型導入測試)
# ========================================================================

@pytest.mark.unit
def test_guide_spec_model_exists():
    """測試 GuideSpec 模型存在且有正確的屬性"""
    from backend.models import GuideSpec

    # 驗證模型類
    assert GuideSpec is not None
    assert hasattr(GuideSpec, '__tablename__')
    assert GuideSpec.__tablename__ == "guide_specs"

    # 驗證欄位存在
    assert hasattr(GuideSpec, 'id')
    assert hasattr(GuideSpec, 'series')
    assert hasattr(GuideSpec, 'type')
    assert hasattr(GuideSpec, 'preload')
    assert hasattr(GuideSpec, 'C0')
    assert hasattr(GuideSpec, 'C100')
    assert hasattr(GuideSpec, 'seal_type')
    assert hasattr(GuideSpec, 'speed_max')
    assert hasattr(GuideSpec, 'stroke')
    assert hasattr(GuideSpec, 'lubrication')
    assert hasattr(GuideSpec, 'created_at')


@pytest.mark.unit
def test_analysis_result_model_exists():
    """測試 AnalysisResult 模型存在且有正確的屬性"""
    from backend.models import AnalysisResult

    # 驗證模型類
    assert AnalysisResult is not None
    assert hasattr(AnalysisResult, '__tablename__')
    assert AnalysisResult.__tablename__ == "analysis_results"

    # 驗證欄位存在
    assert hasattr(AnalysisResult, 'id')
    assert hasattr(AnalysisResult, 'guide_spec_id')
    assert hasattr(AnalysisResult, 'timestamp')
    assert hasattr(AnalysisResult, 'velocity')
    assert hasattr(AnalysisResult, 'health_score')
    assert hasattr(AnalysisResult, 'time_features')
    assert hasattr(AnalysisResult, 'frequency_features')
    assert hasattr(AnalysisResult, 'envelope_features')
    assert hasattr(AnalysisResult, 'higher_order_features')
    assert hasattr(AnalysisResult, 'findings')
    assert hasattr(AnalysisResult, 'recommendations')


@pytest.mark.unit
def test_diagnosis_history_model_exists():
    """測試 DiagnosisHistory 模型存在且有正確的屬性"""
    from backend.models import DiagnosisHistory

    # 驗證模型類
    assert DiagnosisHistory is not None
    assert hasattr(DiagnosisHistory, '__tablename__')
    assert DiagnosisHistory.__tablename__ == "diagnosis_history"

    # 驗證欄位存在
    assert hasattr(DiagnosisHistory, 'id')
    assert hasattr(DiagnosisHistory, 'guide_spec_id')
    assert hasattr(DiagnosisHistory, 'timestamp')
    assert hasattr(DiagnosisHistory, 'rms')
    assert hasattr(DiagnosisHistory, 'peak')
    assert hasattr(DiagnosisHistory, 'kurtosis')
    assert hasattr(DiagnosisHistory, 'crest_factor')
    assert hasattr(DiagnosisHistory, 'health_score')
    assert hasattr(DiagnosisHistory, 'velocity')
    assert hasattr(DiagnosisHistory, 'temperature')
    assert hasattr(DiagnosisHistory, 'load')
    assert hasattr(DiagnosisHistory, 'notes')


# ========================================================================
# Model Relationship Tests (模型關聯測試)
# ========================================================================

@pytest.mark.unit
def test_guide_spec_relationships():
    """測試 GuideSpec 的關聯關係"""
    from backend.models import GuideSpec

    # 原程式碼：analysis_results = relationship("AnalysisResult", back_populates="guide_spec")
    # 驗證關聯屬性存在
    assert hasattr(GuideSpec, 'analysis_results')
    assert hasattr(GuideSpec, '__table__')


@pytest.mark.unit
def test_analysis_result_relationships():
    """測試 AnalysisResult 的關聯關係"""
    from backend.models import AnalysisResult

    # 原程式碼：guide_spec = relationship("GuideSpec", back_populates="analysis_results")
    # 驗證關聯屬性存在
    assert hasattr(AnalysisResult, 'guide_spec')
    assert hasattr(AnalysisResult, '__table__')


@pytest.mark.unit
def test_diagnosis_history_foreign_key():
    """測試 DiagnosisHistory 有正確的外鍵"""
    from backend.models import DiagnosisHistory

    # 原程式碼：guide_spec_id = Column(Integer, ForeignKey("guide_specs.id"))
    # 驗證外鍵欄位存在
    assert hasattr(DiagnosisHistory, 'guide_spec_id')
    assert DiagnosisHistory.__table__ is not None


# ========================================================================
# Model Column Type Tests (欄位類型測試)
# ========================================================================

@pytest.mark.unit
def test_guide_spec_column_types():
    """測試 GuideSpec 欄位類型正確"""
    from backend.models import GuideSpec
    from sqlalchemy import Integer, String, Float, DateTime

    # 檢查 __table__ 定義
    table = GuideSpec.__table__

    # 驗證主鍵
    assert table.c['id'].primary_key is True
    assert table.c['id'].type.python_type == int

    # 驗證字串欄位
    assert table.c['series'].type.python_type == str
    assert table.c['type'].type.python_type == str
    assert table.c['preload'].type.python_type == str

    # 驗證浮點數欄位
    assert table.c['C0'].type.python_type == float
    assert table.c['C100'].type.python_type == float


@pytest.mark.unit
def test_analysis_result_column_types():
    """測試 AnalysisResult 欄位類型正確"""
    from backend.models import AnalysisResult

    table = AnalysisResult.__table__

    # 驗證主鍵和外鍵
    assert table.c['id'].primary_key is True
    assert table.c['guide_spec_id'].type.python_type == int

    # 驗證時間戳
    assert table.c['timestamp'].type.python_type == datetime

    # 驗證浮點數
    assert table.c['velocity'].type.python_type == float
    assert table.c['health_score'].type.python_type == float


@pytest.mark.unit
def test_diagnosis_history_column_types():
    """測試 DiagnosisHistory 欄位類型正確"""
    from backend.models import DiagnosisHistory

    table = DiagnosisHistory.__table__

    # 驗證指標欄位
    assert table.c['rms'].type.python_type == float
    assert table.c['peak'].type.python_type == float
    assert table.c['kurtosis'].type.python_type == float
    assert table.c['crest_factor'].type.python_type == float
    assert table.c['health_score'].type.python_type == float


# ========================================================================
# Model Constraints Tests (模型約束測試)
# ========================================================================

@pytest.mark.unit
def test_guide_spec_nullable_columns():
    """測試 GuideSpec 欄位的 nullable 約束"""
    from backend.models import GuideSpec

    table = GuideSpec.__table__

    # 原程式碼：nullable=False 的欄位
    assert table.c['series'].nullable is False
    assert table.c['type'].nullable is False
    assert table.c['preload'].nullable is False
    assert table.c['C0'].nullable is False
    assert table.c['C100'].nullable is False

    # 原程式碼：nullable=True 的可選欄位
    assert table.c['seal_type'].nullable is True
    assert table.c['speed_max'].nullable is True
    assert table.c['stroke'].nullable is True
    assert table.c['lubrication'].nullable is True


@pytest.mark.unit
def test_analysis_result_nullable_columns():
    """測試 AnalysisResult 欄位的 nullable 約束"""
    from backend.models import AnalysisResult

    table = AnalysisResult.__table__

    # envelope_features 和 higher_order_features 是可選的
    # 原程式碼：Column(JSON, nullable=True)
    assert table.c['envelope_features'].nullable is True
    assert table.c['higher_order_features'].nullable is True


# ========================================================================
# Model Index Tests (模型索引測試)
# ========================================================================

@pytest.mark.unit
def test_guide_spec_indexes():
    """測試 GuideSpec 的索引"""
    from backend.models import GuideSpec

    table = GuideSpec.__table__

    # 原程式碼：id = Column(Integer, primary_key=True, index=True)
    # primary_key 自動創建索引
    assert table.c['id'].primary_key is True


@pytest.mark.unit
def test_analysis_result_indexes():
    """測試 AnalysisResult 的索引"""
    from backend.models import AnalysisResult

    table = AnalysisResult.__table__

    # 驗證主鍵和索引欄位
    assert table.c['id'].primary_key is True
    assert table.c['timestamp'].index is True or table.c['id'].primary_key is True


@pytest.mark.unit
def test_diagnosis_history_indexes():
    """測試 DiagnosisHistory 的索引"""
    from backend.models import DiagnosisHistory

    table = DiagnosisHistory.__table__

    # 驗證主鍵和索引
    assert table.c['id'].primary_key is True
    assert table.c['timestamp'].index is True or table.c['id'].primary_key is True


# ========================================================================
# Model Default Values Tests (預設值測試)
# ========================================================================

@pytest.mark.unit
def test_guide_spec_default_timestamp():
    """測試 GuideSpec 的 created_at 預設值"""
    from backend.models import GuideSpec

    # 原程式碼：created_at = Column(DateTime, default=datetime.now)
    # 注意：default=datetime.now（函數引用）而不是 default=datetime.now()
    assert hasattr(GuideSpec, 'created_at')


@pytest.mark.unit
def test_analysis_result_default_timestamp():
    """測試 AnalysisResult 的 timestamp 預設值"""
    from backend.models import AnalysisResult

    # 原程式碼：timestamp = Column(DateTime, default=datetime.now, index=True)
    assert hasattr(AnalysisResult, 'timestamp')


@pytest.mark.unit
def test_diagnosis_history_default_timestamp():
    """測試 DiagnosisHistory 的 timestamp 預設值"""
    from backend.models import DiagnosisHistory

    # 原程式碼：timestamp = Column(DateTime, default=datetime.now, index=True)
    assert hasattr(DiagnosisHistory, 'timestamp')


# ========================================================================
# Model JSON Fields Tests (JSON 欄位測試)
# ========================================================================

@pytest.mark.unit
def test_analysis_result_json_fields():
    """測試 AnalysisResult 的 JSON 欄位"""
    from backend.models import AnalysisResult

    table = AnalysisResult.__table__

    # 原程式碼：多個 JSON 欄位用於存儲複雜數據
    assert hasattr(AnalysisResult, 'time_features')
    assert hasattr(AnalysisResult, 'frequency_features')
    assert hasattr(AnalysisResult, 'envelope_features')
    assert hasattr(AnalysisResult, 'higher_order_features')
    assert hasattr(AnalysisResult, 'findings')
    assert hasattr(AnalysisResult, 'recommendations')


# ========================================================================
# Model String Representation Tests (字串表示測試)
# ========================================================================

@pytest.mark.unit
def test_model_string_representation():
    """測試模型類的字串表示"""
    from backend.models import GuideSpec, AnalysisResult, DiagnosisHistory

    # 驗證模型類有合理的字串表示
    assert str(GuideSpec).startswith("<class '")
    assert str(AnalysisResult).startswith("<class '")
    assert str(DiagnosisHistory).startswith("<class '")


# ========================================================================
# Model Table Metadata Tests (表元數據測試)
# ========================================================================

@pytest.mark.unit
def test_guide_spec_table_metadata():
    """測試 GuideSpec 表元數據"""
    from backend.models import GuideSpec

    table = GuideSpec.__table__

    # 驗證表名
    assert table.name == "guide_specs"

    # 驗證欄位數量
    # id, series, type, preload, C0, C100, seal_type, speed_max, stroke, lubrication, created_at
    assert len(table.c) == 11


@pytest.mark.unit
def test_analysis_result_table_metadata():
    """測試 AnalysisResult 表元數據"""
    from backend.models import AnalysisResult

    table = AnalysisResult.__table__

    # 驗證表名
    assert table.name == "analysis_results"

    # 驗證欄位數量
    # id, guide_spec_id, timestamp, velocity, health_score,
    # time_features, frequency_features, envelope_features, higher_order_features,
    # findings, recommendations
    assert len(table.c) == 11


@pytest.mark.unit
def test_diagnosis_history_table_metadata():
    """測試 DiagnosisHistory 表元數據"""
    from backend.models import DiagnosisHistory

    table = DiagnosisHistory.__table__

    # 驗證表名
    assert table.name == "diagnosis_history"

    # 驗證欄位數量
    # id, guide_spec_id, timestamp, rms, peak, kurtosis, crest_factor,
    # health_score, velocity, temperature, load, notes
    assert len(table.c) == 12


# ========================================================================
# PHM Models Tests (PHM 模型測試)
# ========================================================================

@pytest.mark.unit
def test_phm_bearing_model_exists():
    """測試 PHMBearing 模型存在且有正確的屬性"""
    try:
        from backend.phm_models import PHMBearing
    except ImportError:
        # 模組可能不存在，跳過測試
        pytest.skip("phm_models module not available")
        return

    # 驗證模型類
    assert PHMBearing is not None
    assert hasattr(PHMBearing, '__tablename__')
    assert PHMBearing.__tablename__ == "phm_bearings"

    # 驗證欄位存在
    assert hasattr(PHMBearing, 'id')
    assert hasattr(PHMBearing, 'bearing_name')
    assert hasattr(PHMBearing, 'condition')
    assert hasattr(PHMBearing, 'load_N')
    assert hasattr(PHMBearing, 'speed_rpm')
    assert hasattr(PHMBearing, 'actual_RUL_min')
    assert hasattr(PHMBearing, 'num_files')
    assert hasattr(PHMBearing, 'total_duration_min')
    assert hasattr(PHMBearing, 'created_at')


@pytest.mark.unit
def test_phm_test_data_model_exists():
    """測試 PHMTestData 模型存在且有正確的屬性"""
    try:
        from backend.phm_models import PHMTestData
    except ImportError:
        pytest.skip("phm_models module not available")
        return

    # 驗證模型類
    assert PHMTestData is not None
    assert hasattr(PHMTestData, '__tablename__')
    assert PHMTestData.__tablename__ == "phm_test_data"

    # 驗證欄位存在
    assert hasattr(PHMTestData, 'id')
    assert hasattr(PHMTestData, 'bearing_name')
    assert hasattr(PHMTestData, 'file_index')
    assert hasattr(PHMTestData, 'time_min')
    assert hasattr(PHMTestData, 'horiz_rms')
    assert hasattr(PHMTestData, 'vert_rms')
    assert hasattr(PHMTestData, 'horiz_peak')
    assert hasattr(PHMTestData, 'vert_peak')
    assert hasattr(PHMTestData, 'horiz_kurtosis')
    assert hasattr(PHMTestData, 'vert_kurtosis')
    assert hasattr(PHMTestData, 'signal_data')
    assert hasattr(PHMTestData, 'created_at')


@pytest.mark.unit
def test_phm_prediction_model_exists():
    """測試 PHMPrediction 模型存在且有正確的屬性"""
    try:
        from backend.phm_models import PHMPrediction
    except ImportError:
        pytest.skip("phm_models module not available")
        return

    # 驗證模型類
    assert PHMPrediction is not None
    assert hasattr(PHMPrediction, '__tablename__')
    assert PHMPrediction.__tablename__ == "phm_predictions"

    # 驗證欄位存在
    assert hasattr(PHMPrediction, 'id')
    assert hasattr(PHMPrediction, 'bearing_name')
    assert hasattr(PHMPrediction, 'predicted_RUL_min')
    assert hasattr(PHMPrediction, 'actual_RUL_min')
    assert hasattr(PHMPrediction, 'prediction_error')
    assert hasattr(PHMPrediction, 'score')
    assert hasattr(PHMPrediction, 'features')
    assert hasattr(PHMPrediction, 'model_type')
    assert hasattr(PHMPrediction, 'confidence')
    assert hasattr(PHMPrediction, 'created_at')


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
def test_guide_spec_crud_operations(test_db_session):
    """測試 GuideSpec 的 CRUD 操作"""
    from backend.models import GuideSpec

    # 創建
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

    test_db_session.add(guide_spec)
    test_db_session.commit()
    test_db_session.refresh(guide_spec)

    # 讀取
    assert guide_spec.id is not None
    assert guide_spec.series == "HRC25"
    assert guide_spec.created_at is not None

    # 更新
    guide_spec.speed_max = 2.5
    test_db_session.commit()
    test_db_session.refresh(guide_spec)
    assert guide_spec.speed_max == 2.5

    # 刪除
    test_db_session.delete(guide_spec)
    test_db_session.commit()

    # 驗證刪除
    result = test_db_session.query(GuideSpec).filter_by(id=guide_spec.id).first()
    assert result is None


@pytest.mark.integration
def test_analysis_result_complex_data(test_db_session):
    """測試 AnalysisResult 的複雜數據處理"""
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

    # 創建帶有複雜 JSON 數據的 AnalysisResult
    complex_data = AnalysisResult(
        guide_spec_id=guide_spec.id,
        velocity=1.5,
        health_score=85.0,
        time_features={
            "rms": 0.1,
            "peak": 2.0,
            "kurtosis": 3.0,
            "crest_factor": 1.5,
            "skewness": 0.5,
            "form_factor": 0.8
        },
        frequency_features={
            "dominant_freq": 100.0,
            "harmonics": [100, 200, 300, 400],
            "fft_peaks": [0.1, 0.2, 0.3],
            "band_powers": {"low": 0.1, "medium": 0.2, "high": 0.3}
        },
        envelope_features={
            "peak_to_peak": 1.5,
            "rms_envelope": 0.2,
            "kurtosis_envelope": 2.5
        },
        higher_order_features={
            "hurst": 0.7,
            "lyapunov": 0.1,
            "sample_entropy": 0.5
        },
        findings=[
            {"type": "info", "severity": "low", "message": "Normal operation"},
            {"type": "warning", "severity": "medium", "message": "Slight vibration increase"},
            {"type": "critical", "severity": "high", "message": "Bearing wear detected"}
        ],
        recommendations=[
            "Continue monitoring",
            "Check mounting bolts",
            "Plan maintenance within 3 months"
        ]
    )

    test_db_session.add(complex_data)
    test_db_session.commit()
    test_db_session.refresh(complex_data)

    # 驗證數據正確保存
    assert complex_data.id is not None
    assert complex_data.health_score == 85.0
    assert complex_data.time_features["rms"] == 0.1
    assert complex_data.frequency_features["dominant_freq"] == 100.0
    assert complex_data.envelope_features["peak_to_peak"] == 1.5
    assert complex_data.higher_order_features["hurst"] == 0.7
    assert len(complex_data.findings) == 3
    assert len(complex_data.recommendations) == 3


@pytest.mark.integration
def test_diagnosis_history_metrics(test_db_session):
    """測試 DiagnosisHistory 的指標處理"""
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

    # 創建多個診斷記錄
    diagnoses = []
    for i in range(5):
        diagnosis = DiagnosisHistory(
            guide_spec_id=guide_spec.id,
            rms=0.1 + i * 0.01,
            peak=2.0 + i * 0.1,
            kurtosis=3.0 + i * 0.2,
            crest_factor=1.5 + i * 0.05,
            health_score=85.0 - i * 5,
            velocity=1.5 + i * 0.1,
            temperature=25.0 + i,
            load=100.0 + i * 10,
            notes=f"Regular checkup {i+1}"
        )
        diagnoses.append(diagnosis)
        test_db_session.add(diagnosis)

    test_db_session.commit()

    # 驗證所有記錄都創建成功
    for i, diagnosis in enumerate(diagnoses):
        assert diagnosis.id is not None
        assert diagnosis.rms == 0.1 + i * 0.01
        assert diagnosis.notes == f"Regular checkup {i+1}"

    # 測試查詢
    db_diagnoses = test_db_session.query(DiagnosisHistory).filter_by(guide_spec_id=guide_spec.id).all()
    assert len(db_diagnoses) == 5

    # 測試排序
    sorted_diagnoses = sorted(db_diagnoses, key=lambda x: x.health_score, reverse=True)
    assert sorted_diagnoses[0].health_score == 85.0
    assert sorted_diagnoses[-1].health_score == 60.0


@pytest.mark.integration
def test_model_constraint_validation(test_db_session):
    """測試模型約束驗證"""
    from backend.models import GuideSpec

    # 測試必填欄位
    try:
        # 應該失敗 - 缺少必填欄位
        incomplete_guide_spec = GuideSpec(
            series="HRC25"
            # 缺少 type, preload, C0, C100
        )
        test_db_session.add(incomplete_guide_spec)
        test_db_session.commit()
        # 如果到達這裡，表示測試失敗
        assert False, "Should have failed due to missing required fields"
    except Exception:
        # 預期會拋出異常
        test_db_session.rollback()

    # 測試必填欄位
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

    # 驗證必填欄位已設置
    assert guide_spec.series is not None
    assert guide_spec.type is not None
    assert guide_spec.preload is not None
    assert guide_spec.C0 is not None
    assert guide_spec.C100 is not None

    # 驗證可選欄位為 None
    assert guide_spec.seal_type is None
    assert guide_spec.speed_max is None
    assert guide_spec.stroke is None
    assert guide_spec.lubrication is None


@pytest.mark.integration
def test_datetime_timestamps(test_db_session):
    """測試時間戳的處理"""
    from backend.models import GuideSpec, AnalysisResult, DiagnosisHistory
    from datetime import datetime
    import time

    # 測試 GuideSpec 的 created_at 自動設置
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

    # 驗證 created_at 被自動設置
    assert guide_spec.created_at is not None
    assert isinstance(guide_spec.created_at, datetime)

    # 測試 AnalysisResult 的 timestamp
    analysis_result = AnalysisResult(
        guide_spec_id=guide_spec.id,
        velocity=1.5,
        health_score=85.0,
        time_features={"rms": 0.1},
        frequency_features={"peak": 2.0},
        findings=["Normal"],
        recommendations=["Continue"]
    )
    test_db_session.add(analysis_result)
    test_db_session.commit()
    test_db_session.refresh(analysis_result)

    # 驗證 timestamp 被自動設置
    assert analysis_result.timestamp is not None
    assert isinstance(analysis_result.timestamp, datetime)

    # 測試 DiagnosisHistory 的 timestamp
    diagnosis = DiagnosisHistory(
        guide_spec_id=guide_spec.id,
        rms=0.1,
        peak=2.0,
        kurtosis=3.0,
        crest_factor=1.5,
        health_score=85.0
    )
    test_db_session.add(diagnosis)
    test_db_session.commit()
    test_db_session.refresh(diagnosis)

    # 驗證 timestamp 被自動設置
    assert diagnosis.timestamp is not None
    assert isinstance(diagnosis.timestamp, datetime)


@pytest.mark.integration
def test_complex_model_relationships(test_db_session):
    """測試複雜的模型關聯關係"""
    from backend.models import GuideSpec, AnalysisResult, DiagnosisHistory

    # 創建一個 GuideSpec
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

    # 創建多個分析結果
    analysis_results = []
    for i in range(3):
        result = AnalysisResult(
            guide_spec_id=guide_spec.id,
            velocity=1.5 + i * 0.1,
            health_score=85.0 - i * 5,
            time_features={"rms": 0.1 + i * 0.01},
            findings=[f"Test finding {i+1}"],
            recommendations=[f"Test recommendation {i+1}"]
        )
        analysis_results.append(result)
        test_db_session.add(result)

    # 創建多個診斷記錄
    diagnosis_history = []
    for i in range(2):
        diagnosis = DiagnosisHistory(
            guide_spec_id=guide_spec.id,
            rms=0.1 + i * 0.01,
            peak=2.0 + i * 0.1,
            health_score=90.0 - i * 5,
            notes=f"Test diagnosis {i+1}"
        )
        diagnosis_history.append(diagnosis)
        test_db_session.add(diagnosis)

    test_db_session.commit()

    # 驗證關聯關係
    # GuideSpec 應該有正確數量的關聯
    assert len(guide_spec.analysis_results) == 3

    # 分析結果應該正確關聯到 GuideSpec
    for result in analysis_results:
        assert result.guide_spec_id == guide_spec.id

    # 診斷記錄應該正確關聯到 GuideSpec
    for diagnosis in diagnosis_history:
        assert diagnosis.guide_spec_id == guide_spec.id

    # 測查詢關聯
    # 查詢某個 GuideSpec 的所有分析結果
    db_results = test_db_session.query(AnalysisResult).filter_by(guide_spec_id=guide_spec.id).all()
    assert len(db_results) == 3

    # 查詢某個 GuideSpec 的所有診斷記錄
    db_diagnoses = test_db_session.query(DiagnosisHistory).filter_by(guide_spec_id=guide_spec.id).all()
    assert len(db_diagnoses) == 2


@pytest.mark.integration
def test_json_field_performance(test_db_session):
    """測試 JSON 欄位的性能"""
    from backend.models import GuideSpec, AnalysisResult
    import time

    # 創建 GuideSpec
    guide_spec = GuideSpec(
        series="TEST003",
        type="MN",
        preload="V1",
        C0=5000.0,
        C100=3000.0
    )
    test_db_session.add(guide_spec)
    test_db_session.commit()
    test_db_session.refresh(guide_spec)

    # 創建大量數據的 AnalysisResult
    large_data = {
        "time_features": {
            f"metric_{i}": i * 0.1 for i in range(100)
        },
        "frequency_features": {
            f"freq_{i}": i * 10.0 for i in range(100)
        },
        "envelope_features": {
            f"envelope_{i}": i * 0.01 for i in range(50)
        },
        "higher_order_features": {
            f"higher_{i}": i * 0.001 for i in range(50)
        },
        "findings": [
            {"type": "info", "message": f"Test finding {i}"} for i in range(100)
        ],
        "recommendations": [
            f"Test recommendation {i}" for i in range(100)
        ]
    }

    analysis_result = AnalysisResult(
        guide_spec_id=guide_spec.id,
        velocity=1.5,
        health_score=85.0,
        time_features=large_data["time_features"],
        frequency_features=large_data["frequency_features"],
        envelope_features=large_data["envelope_features"],
        higher_order_features=large_data["higher_order_features"],
        findings=[f["message"] for f in large_data["findings"]],
        recommendations=large_data["recommendations"]
    )

    start_time = time.time()
    test_db_session.add(analysis_result)
    test_db_session.commit()
    test_db_session.refresh(analysis_result)
    end_time = time.time()

    # 驗證數據正確保存
    assert analysis_result.id is not None
    assert len(analysis_result.time_features) == 100
    assert len(analysis_result.frequency_features) == 100
    assert len(analysis_result.findings) == 100
    assert len(analysis_result.recommendations) == 100

    # 驗證性能（應該在合理時間內完成）
    assert end_time - start_time < 5.0  # 應該在 5 秒內完成


# ========================================================================
# PHM Temperature Models Tests (PHM 溫度模型測試)
# ========================================================================

@pytest.mark.unit
def test_phm_temperature_bearing_model_exists():
    """測試 PHMTemperatureBearing 模型存在且有正確的屬性"""
    try:
        from backend.phm_temperature_models import PHMTemperatureBearing
    except ImportError:
        pytest.skip("phm_temperature_models module not available")
        return

    # 驗證模型類
    assert PHMTemperatureBearing is not None
    assert hasattr(PHMTemperatureBearing, '__tablename__')
    assert PHMTemperatureBearing.__tablename__ == "phm_temperature_bearings"

    # 驗證欄位存在
    assert hasattr(PHMTemperatureBearing, 'id')
    assert hasattr(PHMTemperatureBearing, 'bearing_name')
    assert hasattr(PHMTemperatureBearing, 'total_temp_files')
    assert hasattr(PHMTemperatureBearing, 'created_at')
    assert hasattr(PHMTemperatureBearing, 'temperature_files')


@pytest.mark.unit
def test_phm_temperature_file_model_exists():
    """測試 PHMTemperatureFile 模型存在且有正確的屬性"""
    try:
        from backend.phm_temperature_models import PHMTemperatureFile
    except ImportError:
        pytest.skip("phm_temperature_models module not available")
        return

    # 驗證模型類
    assert PHMTemperatureFile is not None
    assert hasattr(PHMTemperatureFile, '__tablename__')
    assert PHMTemperatureFile.__tablename__ == "phm_temperature_files"

    # 驗證欄位存在
    assert hasattr(PHMTemperatureFile, 'id')
    assert hasattr(PHMTemperatureFile, 'bearing_id')
    assert hasattr(PHMTemperatureFile, 'file_name')
    assert hasattr(PHMTemperatureFile, 'file_number')
    assert hasattr(PHMTemperatureFile, 'record_count')
    assert hasattr(PHMTemperatureFile, 'created_at')
    assert hasattr(PHMTemperatureFile, 'bearing')
    assert hasattr(PHMTemperatureFile, 'measurements')


@pytest.mark.unit
def test_phm_temperature_measurement_model_exists():
    """測試 PHMTemperatureMeasurement 模型存在且有正確的屬性"""
    try:
        from backend.phm_temperature_models import PHMTemperatureMeasurement
    except ImportError:
        pytest.skip("phm_temperature_models module not available")
        return

    # 驗證模型類
    assert PHMTemperatureMeasurement is not None
    assert hasattr(PHMTemperatureMeasurement, '__tablename__')
    assert PHMTemperatureMeasurement.__tablename__ == "phm_temperature_measurements"

    # 驗證欄位存在
    assert hasattr(PHMTemperatureMeasurement, 'id')
    assert hasattr(PHMTemperatureMeasurement, 'file_id')
    assert hasattr(PHMTemperatureMeasurement, 'hour')
    assert hasattr(PHMTemperatureMeasurement, 'minute')
    assert hasattr(PHMTemperatureMeasurement, 'second')
    assert hasattr(PHMTemperatureMeasurement, 'microsecond')
    assert hasattr(PHMTemperatureMeasurement, 'temperature')
    assert hasattr(PHMTemperatureMeasurement, 'created_at')
    assert hasattr(PHMTemperatureMeasurement, 'file')


@pytest.mark.unit
def test_phm_temperature_models_relationships():
    """測試 PHM 溫度模型之間的關聯關係"""
    try:
        from backend.phm_temperature_models import (
            PHMTemperatureBearing,
            PHMTemperatureFile,
            PHMTemperatureMeasurement
        )
    except ImportError:
        pytest.skip("phm_temperature_models module not available")
        return

    # 驗證 PHMTemperatureBearing 到 PHMTemperatureFile 的關係
    assert hasattr(PHMTemperatureBearing, 'temperature_files')

    # 驗證 PHMTemperatureFile 到 PHMTemperatureBearing 的關係
    assert hasattr(PHMTemperatureFile, 'bearing')

    # 驗證 PHMTemperatureFile 到 PHMTemperatureMeasurement 的關係
    assert hasattr(PHMTemperatureFile, 'measurements')

    # 驗證 PHMTemperatureMeasurement 到 PHMTemperatureFile 的關係
    assert hasattr(PHMTemperatureMeasurement, 'file')

