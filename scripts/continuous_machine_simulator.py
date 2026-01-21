#!/usr/bin/env python3
"""
持續數據推送模擬機台

根據 docs/RealTimeAnalysis.md 中的 "持續數據推送 (模擬機台)" 章節實作
模擬真實機台持續將振動數據推送到後端 Buffer Manager

功能特點:
- 持續推送模擬振動數據 (25.6 kHz 採樣率)
- 支持多線程異步運行
- 自動生成正弦波 + 噪音的模擬信號
- 統計推送速率和數據量
- 優雅的中斷處理
"""

import requests
import time
import numpy as np
from datetime import datetime, timedelta
import threading
import logging
import sys

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContinuousDataStreamer:
    """
    持續數據推送器 - 模擬機台

    根據 RealTimeAnalysis.md 文檔第 970-1045 行的範例實作
    """

    def __init__(self, sensor_id: int = 1, api_url: str = "http://localhost:8081"):
        """
        初始化數據推送器

        Args:
            sensor_id: 感測器 ID
            api_url: 後端 API 基礎 URL
        """
        self.sensor_id = sensor_id
        self.api_url = api_url
        self.running = False
        self.thread = None

        # 採樣配置
        self.sampling_rate = 25600  # 25.6 kHz
        self.batch_size = 25600     # 每次推送 1 秒數據

        # 統計資訊
        self.stats = {
            'total_batches': 0,
            'total_points': 0,
            'start_time': None,
            'success_count': 0,
            'error_count': 0
        }

    def _generate_vibration_signal(self, num_samples: int) -> tuple:
        """
        生成模擬振動信號 (正弦波 + 高斯噪音)

        Args:
            num_samples: 樣本數量

        Returns:
            (h_acc, v_acc) 水平和垂直加速度陣列
        """
        # 時間軸
        t = np.linspace(0, num_samples / self.sampling_rate, num_samples)

        # 模擬振動訊號: 多個頻率的正弦波疊加 + 噪音
        # 基頻 10 Hz + 諧波
        h_acc = (
            0.05 * np.sin(2 * np.pi * 10 * t) +      # 基頻
            0.02 * np.sin(2 * np.pi * 50 * t) +      # 諧波 1
            0.01 * np.sin(2 * np.pi * 100 * t) +     # 諧波 2
            np.random.normal(0, 0.1, num_samples)     # 高斯噪音
        )

        v_acc = (
            0.04 * np.cos(2 * np.pi * 10 * t) +      # 基頻 (相位差)
            0.015 * np.cos(2 * np.pi * 50 * t) +     # 諧波 1
            0.008 * np.cos(2 * np.pi * 100 * t) +    # 諧波 2
            np.random.normal(0, 0.08, num_samples)    # 高斯噪音
        )

        return h_acc.tolist(), v_acc.tolist()

    def _stream_loop(self):
        """持續推送數據的循環 (在獨立線程中運行)"""
        logger.info(f"數據推送線程已啟動 for sensor {self.sensor_id}")

        counter = 0

        while self.running:
            try:
                # 記錄批次開始時間
                batch_start = time.time()

                # 生成 1 秒的模擬數據
                start_time = datetime.now()
                h_acc, v_acc = self._generate_vibration_signal(self.batch_size)

                # 準備數據點
                data_points = []
                for i in range(self.batch_size):
                    timestamp = start_time + timedelta(
                        microseconds=i * (1000000 / self.sampling_rate)
                    )
                    data_points.append({
                        "timestamp": timestamp.isoformat(),
                        "h_acc": round(float(h_acc[i]), 6),
                        "v_acc": round(float(v_acc[i]), 6)
                    })

                # 推送到後端
                payload = {
                    "sensor_id": self.sensor_id,
                    "data": data_points
                }

                # 原程式碼使用 timeout=10，但對於 25600 個數據點的批次可能不夠
                # 增加超時時間至 60 秒以確保大批次數據能夠成功處理
                response = requests.post(
                    f"{self.api_url}/api/sensor/data",
                    json=payload,
                    timeout=60  # 原值: 10
                )

                if response.status_code == 200:
                    counter += 1
                    self.stats['success_count'] += 1
                    self.stats['total_batches'] += 1
                    self.stats['total_points'] += self.batch_size

                    # 每 10 秒打印一次統計
                    if counter % 10 == 0:
                        elapsed = time.time() - self.stats['start_time']
                        rate = self.stats['total_batches'] / elapsed if elapsed > 0 else 0
                        logger.info(
                            f"已推送 {counter} 批次 ({self.stats['total_points']} 點) - "
                            f"平均速率: {rate:.2f} 批次/秒"
                        )
                else:
                    self.stats['error_count'] += 1
                    logger.warning(
                        f"推送失敗: HTTP {response.status_code} - {response.text}"
                    )

                # 控制推送頻率 (大約實時)
                elapsed = time.time() - batch_start
                if elapsed < 1.0:
                    time.sleep(1.0 - elapsed)

            except requests.exceptions.RequestException as e:
                self.stats['error_count'] += 1
                logger.error(f"網路錯誤: {e}")
                time.sleep(1)  # 錯誤後等待 1 秒再重試

            except Exception as e:
                self.stats['error_count'] += 1
                logger.error(f"未知錯誤: {e}")
                time.sleep(1)

    def start(self):
        """
        啟動持續數據推送

        在獨立的 daemon 線程中運行，不阻塞主程序
        """
        if self.running:
            logger.warning("數據推送器已在運行中")
            return

        self.running = True
        self.stats['start_time'] = time.time()
        self.thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.thread.start()

        logger.info("=" * 50)
        logger.info("持續數據推送已啟動")
        logger.info(f"  感測器 ID: {self.sensor_id}")
        logger.info(f"  採樣率: {self.sampling_rate} Hz")
        logger.info(f"  批次大小: {self.batch_size} 樣本 (1 秒)")
        logger.info(f"  API 端點: {self.api_url}/api/sensor/data")
        logger.info("  按 Ctrl+C 停止")
        logger.info("=" * 50)

    def stop(self):
        """
        停止數據推送

        優雅地停止推送線程並輸出統計資訊
        """
        if not self.running:
            logger.warning("數據推送器未在運行")
            return

        logger.info("正在停止數據推送...")
        self.running = False

        # 等待線程結束
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

        # 輸出統計資訊
        total_seconds = time.time() - self.stats['start_time']

        logger.info("=" * 50)
        logger.info("數據推送已停止")
        logger.info("統計摘要:")
        logger.info(f"  總推送批次: {self.stats['total_batches']}")
        logger.info(f"  總數據點數: {self.stats['total_points']}")
        logger.info(f"  運行時間: {total_seconds:.2f} 秒")
        logger.info(f"  平均速率: {self.stats['total_batches'] / total_seconds:.2f} 批次/秒")
        logger.info(f"  成功次數: {self.stats['success_count']}")
        logger.info(f"  錯誤次數: {self.stats['error_count']}")
        logger.info(f"  成功率: {self.stats['success_count'] / (self.stats['success_count'] + self.stats['error_count']) * 100:.1f}%")
        logger.info("=" * 50)

    def get_stats(self) -> dict:
        """
        獲取當前統計資訊

        Returns:
            統計資訊字典
        """
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            self.stats['elapsed_seconds'] = elapsed
            self.stats['average_rate'] = self.stats['total_batches'] / elapsed if elapsed > 0 else 0

        return self.stats.copy()


def check_server_health(api_url: str) -> bool:
    """
    檢查後端伺服器是否運行正常

    Args:
        api_url: API 基礎 URL

    Returns:
        True 如果伺服器正常，否則 False
    """
    try:
        response = requests.get(f"{api_url}/", timeout=5)
        is_healthy = response.status_code == 200

        if is_healthy:
            logger.info(f"✓ 後端伺服器運行正常: {api_url}")
        else:
            logger.error(f"✗ 後端伺服器回應異常: HTTP {response.status_code}")

        return is_healthy

    except requests.exceptions.RequestException as e:
        logger.error(f"✗ 無法連接到後端伺服器: {e}")
        return False


def main():
    """主程序入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="持續數據推送模擬機台 - 根據 RealTimeAnalysis.md 實作",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 使用預設配置啟動
  python scripts/continuous_machine_simulator.py

  # 指定感測器 ID
  python scripts/continuous_machine_simulator.py --sensor-id 2

  # 指定後端 URL
  python scripts/continuous_machine_simulator.py --url http://192.168.1.100:8081

  # 指定運行時長 (秒)
  python scripts/continuous_machine_simulator.py --duration 60
        """
    )

    parser.add_argument(
        "--sensor-id",
        type=int,
        default=1,
        help="感測器 ID (預設: 1)"
    )

    parser.add_argument(
        "--url",
        default="http://localhost:8081",
        help="後端 API 基礎 URL (預設: http://localhost:8081)"
    )

    parser.add_argument(
        "--duration",
        type=int,
        help="運行時長（秒），不指定則持續運行直到手動停止"
    )

    args = parser.parse_args()

    # 檢查伺服器健康狀態
    if not check_server_health(args.url):
        logger.error("後端伺服器未運行，請先啟動後端服務")
        sys.exit(1)

    # 創建並啟動推送器
    streamer = ContinuousDataStreamer(
        sensor_id=args.sensor_id,
        api_url=args.url
    )

    try:
        streamer.start()

        # 如果指定了運行時長，設置定時器
        if args.duration:
            logger.info(f"將在 {args.duration} 秒後自動停止")
            time.sleep(args.duration)
        else:
            # 持續運行直到用戶中斷
            while True:
                time.sleep(1)

                # 定期打印統計
                stats = streamer.get_stats()
                if stats['total_batches'] > 0 and stats['total_batches'] % 60 == 0:
                    logger.info(
                        f"運行中: {stats['total_batches']} 批次, "
                        f"{stats['total_points']} 點, "
                        f"速率: {stats['average_rate']:.2f} 批次/秒"
                    )

    except KeyboardInterrupt:
        logger.info("\n收到中斷信號")

    finally:
        streamer.stop()


if __name__ == "__main__":
    main()
