"""
Real-time feature extraction and analysis engine

This module orchestrates continuous real-time analysis of streaming
sensor data, extracting features and detecting anomalies.
"""
import asyncio
import numpy as np
from typing import Dict, Optional
from datetime import datetime
import logging

from buffer_manager import BufferManager, buffer_manager
from websocket_manager import manager
from redis_client import redis_client
from database_async import db

# Import existing analysis modules
# These will need to be made async in a future iteration
try:
    from timedomain import TimeDomain
    from frequencydomain import FrequencyDomain
    from filterprocess import FilterProcess
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not import analysis modules: {e}")
    TimeDomain = None
    FrequencyDomain = None
    FilterProcess = None

logger = logging.getLogger(__name__)


class RealTimeAnalyzer:
    """
    Real-time analyzer for streaming sensor data

    Manages continuous feature extraction for multiple sensors,
    handles alert detection, and broadcasts results via WebSocket.
    """

    def __init__(self, buffer_manager: BufferManager):
        """
        Initialize analyzer

        Args:
            buffer_manager: BufferManager instance for data access
        """
        self.buffer_manager = buffer_manager
        self.running = False
        self.analysis_tasks: Dict[int, asyncio.Task] = {}

        # Initialize analysis modules if available
        self.time_domain = TimeDomain() if TimeDomain else None
        self.freq_domain = FrequencyDomain() if FrequencyDomain else None
        self.filter_process = FilterProcess() if FilterProcess else None

        logger.info("RealTimeAnalyzer initialized")

    async def start_analysis(self, sensor_id: int):
        """
        Start real-time analysis for a sensor

        Creates an async task that continuously processes data
        from the sensor's buffer.

        Args:
            sensor_id: Sensor identifier
        """
        if sensor_id in self.analysis_tasks:
            logger.warning(f"Analysis already running for sensor {sensor_id}")
            return

        self.analysis_tasks[sensor_id] = asyncio.create_task(
            self._analysis_loop(sensor_id)
        )
        logger.info(f"Started real-time analysis for sensor {sensor_id}")

    async def stop_analysis(self, sensor_id: int):
        """
        Stop real-time analysis for a sensor

        Args:
            sensor_id: Sensor identifier
        """
        if sensor_id not in self.analysis_tasks:
            logger.warning(f"No analysis running for sensor {sensor_id}")
            return

        task = self.analysis_tasks[sensor_id]
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass  # Expected when cancelled

        del self.analysis_tasks[sensor_id]
        logger.info(f"Stopped real-time analysis for sensor {sensor_id}")

    async def _analysis_loop(self, sensor_id: int):
        """
        Continuous analysis loop for a sensor

        Args:
            sensor_id: Sensor identifier
        """
        window_seconds = 1.0  # 1 second window
        min_samples = 10000   # Minimum samples for analysis

        logger.info(f"Analysis loop started for sensor {sensor_id}")
        iteration_count = 0

        while True:
            try:
                iteration_count += 1

                # Get latest window data from buffer
                window_data = await self.buffer_manager.get_window(
                    sensor_id, window_seconds
                )

                # 調試日誌：每 10 次循環打印一次狀態
                if iteration_count % 10 == 0:
                    if window_data:
                        logger.info(
                            f"Sensor {sensor_id}: Got window with "
                            f"{window_data['sample_count']} samples "
                            f"(need {min_samples})"
                        )
                    else:
                        logger.warning(
                            f"Sensor {sensor_id}: No data in buffer yet "
                            f"(iteration {iteration_count})"
                        )

                if window_data and window_data['sample_count'] >= min_samples:
                    # Extract features
                    features = await self._extract_features(window_data)

                    logger.info(
                        f"Sensor {sensor_id}: Extracted features - "
                        f"RMS_H={features.get('rms_h', 'N/A'):.4f}, "
                        f"RMS_V={features.get('rms_v', 'N/A'):.4f}"
                    )

                    # Save to database
                    await self._save_features(sensor_id, features)

                    # Broadcast to WebSocket clients
                    await manager.broadcast_feature_update(sensor_id, features)

                    logger.info(f"Sensor {sensor_id}: Broadcasted features to WebSocket")

                    # Cache in Redis
                    await redis_client.cache_features(sensor_id, features)

                    # Check for alerts
                    await self._check_alerts(sensor_id, features)

                # Wait before next analysis (10 Hz rate)
                await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                logger.info(f"Analysis loop cancelled for sensor {sensor_id}")
                break
            except Exception as e:
                logger.error(
                    f"Error in analysis loop for sensor {sensor_id}: {e}",
                    exc_info=True
                )
                # Wait before retrying
                await asyncio.sleep(1)

    async def _extract_features(self, window_data: Dict) -> Dict:
        """
        Extract all features from window data

        Performs time-domain, frequency-domain, and advanced
        feature extraction on the sensor data.

        Args:
            window_data: Window data dictionary with h_data, v_data arrays

        Returns:
            Feature dictionary
        """
        h_data = window_data['h_data']
        v_data = window_data['v_data']
        sampling_rate = 25600  # Hz

        features = {
            # 原始：直接使用 datetime 對象,導致 WebSocket 序列化失敗
            # 修改：轉換為 ISO 格式字串
            'window_start': window_data['window_start'].isoformat() if hasattr(window_data['window_start'], 'isoformat') else window_data['window_start'],
            'window_end': window_data['window_end'].isoformat() if hasattr(window_data['window_end'], 'isoformat') else window_data['window_end'],
            'sensor_id': window_data['sensor_id'],
            # 添加 timestamp 欄位供前端使用 (使用 window_end)
            'timestamp': window_data['window_end'].isoformat() if hasattr(window_data['window_end'], 'isoformat') else window_data['window_end']
        }

        # Time domain features
        if self.time_domain:
            try:
                # Calculate RMS
                rms_h = np.sqrt(np.mean(h_data ** 2))
                rms_v = np.sqrt(np.mean(v_data ** 2))

                # Calculate peak
                peak_h = np.max(np.abs(h_data))
                peak_v = np.max(np.abs(v_data))

                # Calculate kurtosis
                kurtosis_h = self._calculate_kurtosis(h_data)
                kurtosis_v = self._calculate_kurtosis(v_data)

                # Calculate crest factor
                crest_factor_h = peak_h / rms_h if rms_h > 0 else 0
                crest_factor_v = peak_v / rms_v if rms_v > 0 else 0

                features.update({
                    'rms_h': float(rms_h),
                    'rms_v': float(rms_v),
                    'peak_h': float(peak_h),
                    'peak_v': float(peak_v),
                    'kurtosis_h': float(kurtosis_h),
                    'kurtosis_v': float(kurtosis_v),
                    'crest_factor_h': float(crest_factor_h),
                    'crest_factor_v': float(crest_factor_v),
                })

                logger.debug(f"Time domain features extracted for sensor {window_data['sensor_id']}")
            except Exception as e:
                logger.error(f"Time domain analysis error: {e}")

        # Frequency domain features (basic FFT)
        try:
            freq_h = self._calculate_dominant_frequency(h_data, sampling_rate)
            freq_v = self._calculate_dominant_frequency(v_data, sampling_rate)

            features.update({
                'dominant_freq_h': float(freq_h),
                'dominant_freq_v': float(freq_v),
            })

            logger.debug(f"Frequency domain features extracted")
        except Exception as e:
            logger.error(f"Frequency domain analysis error: {e}")

        return features

    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """
        Calculate kurtosis of data

        Args:
            data: NumPy array

        Returns:
            Kurtosis value
        """
        mean = np.mean(data)
        std = np.std(data)

        if std == 0:
            return 0.0

        return np.mean(((data - mean) / std) ** 4)

    def _calculate_dominant_frequency(self, data: np.ndarray,
                                      sampling_rate: int) -> float:
        """
        Calculate dominant frequency using FFT

        Args:
            data: Signal data
            sampling_rate: Sampling rate in Hz

        Returns:
            Dominant frequency in Hz
        """
        # Perform FFT
        fft_result = np.fft.fft(data)
        fft_freq = np.fft.fftfreq(len(data), 1/sampling_rate)

        # Get magnitude (only positive frequencies)
        magnitude = np.abs(fft_result[:len(fft_freq)//2])
        freqs = fft_freq[:len(fft_freq)//2]

        # Find dominant frequency (excluding DC component)
        if len(magnitude) > 1:
            peak_idx = np.argmax(magnitude[1:]) + 1  # Skip DC
            return float(abs(freqs[peak_idx]))

        return 0.0

    async def _save_features(self, sensor_id: int, features: Dict):
        """
        Save features to database

        Args:
            sensor_id: Sensor identifier
            features: Feature dictionary
        """
        try:
            # 原始：直接使用 features,但 window_start/window_end 已轉為字串
            # 問題：PostgreSQL 需要 datetime 對象,不能接受 ISO 字串
            # 修改：在保存前將字串轉回 datetime 對象

            # 創建副本以避免修改原始 features
            features_for_db = features.copy()

            # 轉換 ISO 字串回 datetime 對象
            for key in ['window_start', 'window_end']:
                if isinstance(features_for_db.get(key), str):
                    try:
                        features_for_db[key] = datetime.fromisoformat(
                            features_for_db[key].replace('Z', '+00:00')
                        )
                    except (ValueError, AttributeError):
                        # 如果轉換失敗,保持原值
                        pass

            await db.insert_features(sensor_id, features_for_db)
            logger.debug(f"Saved features for sensor {sensor_id}")
        except Exception as e:
            logger.error(f"Error saving features: {e}")

    async def _check_alerts(self, sensor_id: int, features: Dict):
        """
        Check if any thresholds are exceeded and generate alerts

        Args:
            sensor_id: Sensor identifier
            features: Feature dictionary
        """
        try:
            # Get alert configurations for this sensor
            configs = await db.get_alert_configurations(sensor_id)

            for config in configs:
                feature_name = config['feature_name']
                value = features.get(feature_name)

                if value is None:
                    continue

                # Check thresholds
                threshold_min = config.get('threshold_min')
                threshold_max = config.get('threshold_max')

                if threshold_max and value > threshold_max:
                    await self._create_alert(
                        sensor_id, config, value, 'above', threshold_max
                    )

                if threshold_min and value < threshold_min:
                    await self._create_alert(
                        sensor_id, config, value, 'below', threshold_min
                    )

        except Exception as e:
            logger.error(f"Error checking alerts: {e}")

    async def _create_alert(self, sensor_id: int, config: Dict,
                           value: float, direction: str, threshold: float):
        """
        Create and broadcast an alert

        Args:
            sensor_id: Sensor identifier
            config: Alert configuration
            value: Current feature value
            direction: 'above' or 'below' threshold
            threshold: Threshold value
        """
        alert = {
            'sensor_id': sensor_id,
            'alert_type': 'threshold',
            'severity': config['severity'],
            'message': (
                f"{config['feature_name']} is {direction} threshold "
                f"({value:.4f} {direction} {threshold:.4f})"
            ),
            'feature_name': config['feature_name'],
            'current_value': value,
            'threshold_value': threshold
        }

        # Save to database
        try:
            await db.create_alert(alert)
            logger.warning(f"Alert created for sensor {sensor_id}: {alert['message']}")
        except Exception as e:
            logger.error(f"Error creating alert: {e}")

        # Broadcast to all clients
        await manager.broadcast_alert(alert)

    def get_status(self) -> Dict:
        """
        Get analyzer status

        Returns:
            Status dictionary with active sensors
        """
        return {
            'active_sensors': list(self.analysis_tasks.keys()),
            'sensor_count': len(self.analysis_tasks),
            'running': self.running
        }


# Global analyzer instance
analyzer = RealTimeAnalyzer(buffer_manager)
