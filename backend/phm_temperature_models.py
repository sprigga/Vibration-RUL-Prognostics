"""
PHM 2012 溫度數據模型
用於儲存軸承溫度測量數據
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
try:
    from backend.database import Base
except ModuleNotFoundError:
    from database import Base


class PHMTemperatureBearing(Base):
    """PHM 軸承溫度數據表 - 軸承基本信息"""
    __tablename__ = "phm_temperature_bearings"

    id = Column(Integer, primary_key=True, index=True)
    bearing_name = Column(String, unique=True, index=True)  # e.g., "Bearing1_4"
    total_temp_files = Column(Integer)  # 溫度文件總數
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    temperature_files = relationship("PHMTemperatureFile", back_populates="bearing")


class PHMTemperatureFile(Base):
    """PHM 溫度文件信息表"""
    __tablename__ = "phm_temperature_files"

    id = Column(Integer, primary_key=True, index=True)
    bearing_id = Column(Integer, ForeignKey("phm_temperature_bearings.id"), index=True)
    file_name = Column(String, index=True)  # e.g., "temp_00005.csv"
    file_number = Column(Integer, index=True)  # 從文件名解析的編號
    record_count = Column(Integer)  # 該文件中的記錄數
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    bearing = relationship("PHMTemperatureBearing", back_populates="temperature_files")
    measurements = relationship("PHMTemperatureMeasurement", back_populates="file")


class PHMTemperatureMeasurement(Base):
    """PHM 溫度測量數據表"""
    __tablename__ = "phm_temperature_measurements"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("phm_temperature_files.id"), index=True)
    hour = Column(Integer)
    minute = Column(Integer)
    second = Column(Integer)
    microsecond = Column(Integer)
    temperature = Column(Float)  # 溫度值
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    file = relationship("PHMTemperatureFile", back_populates="measurements")