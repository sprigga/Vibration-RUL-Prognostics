"""
Database configuration for SQLite
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use /tmp for database in Docker, current directory otherwise
DB_PATH = os.environ.get('DATABASE_PATH', '/tmp/vibration_analysis.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """Initialize database tables"""
    try:
        from .models import GuideSpec, AnalysisResult, DiagnosisHistory
    except ImportError:
        pass  # Optional models
    try:
        from .phm_models import PHMBearing, PHMTestData, PHMPrediction
    except ImportError:
        pass  # Optional models
    try:
        from .phm_temperature_models import PHMTemperatureBearing, PHMTemperatureFile, PHMTemperatureMeasurement
    except ImportError:
        pass  # Optional models
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
