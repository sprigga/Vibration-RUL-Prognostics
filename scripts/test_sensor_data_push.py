#!/usr/bin/env python3
"""
機台數據推送測試腳本

模擬機台將振動數據推送到後端 Buffer Manager
支援單次推送和持續推送兩種模式
"""

import requests
import time
import random
import numpy as np
from datetime import datetime, timedelta
import argparse
import sys
from typing import Optional

class MachineDataSimulator:
    """模擬機台數據的生成器"""

    def __init__(self, sensor_id: int = 1, sampling_rate: int = 25600):
        self.sensor_id = sensor_id
        self.sampling_rate = sampling_rate
        self.base_h_acc = 0.0
        self.base_v_acc = 0.0
        self.phase = 0.0

    def generate_single_point(self, noise_level: float = 0.1) -> dict:
        """生成單個數據點"""
        self.phase += 0.01

        # 模擬振動訊號 (正弦波 + 噪音)
        h_acc = self.base_h_acc + 0.05 * np.sin(self.phase) + random.gauss(0, noise_level)
        v_acc = self.base_v_acc + 0.04 * np.cos(self.phase) + random.gauss(0, noise_level)

        return {
            "timestamp": datetime.now(),
            "h_acc": round(h_acc, 6),
            "v_acc": round(v_acc, 6)
        }

    def generate_batch(self, num_samples: int, noise_level: float = 0.1) -> list:
        """生成批量數據"""
        data_points = []
        start_time = datetime.now()

        for i in range(num_samples):
            timestamp = start_time + timedelta(microseconds=i * (1000000 / self.sampling_rate))
            point = self.generate_single_point(noise_level)
            point["timestamp"] = timestamp
            data_points.append(point)

        return data_points

    def generate_arrays(self, num_samples: int, noise_level: float = 0.1) -> tuple:
        """生成陣列形式數據（用於流式 API）"""
        h_acc = []
        v_acc = []

        for _ in range(num_samples):
            point = self.generate_single_point(noise_level)
            h_acc.append(point["h_acc"])
            v_acc.append(point["v_acc"])

        return h_acc, v_acc


class DataPusher:
    """數據推送客戶端"""

    def __init__(self, base_url: str = "http://localhost:8081", sensor_id: int = 1):
        self.base_url = base_url
        self.sensor_id = sensor_id
        self.simulator = MachineDataSimulator(sensor_id)

    def push_single_batch(self, num_samples: int = 100) -> dict:
        """
        推送單次批量數據

        Args:
            num_samples: 樣本數量

        Returns:
            響應結果
        """
        url = f"{self.base_url}/api/sensor/data"

        # 生成數據
        data_points = self.simulator.generate_batch(num_samples)

        # 準備請求
        payload = {
            "sensor_id": self.sensor_id,
            "data": [
                {
                    "timestamp": point["timestamp"].isoformat(),
                    "h_acc": point["h_acc"],
                    "v_acc": point["v_acc"]
                }
                for point in data_points
            ]
        }

        print(f"推送 {num_samples} 個數據點到感測器 {self.sensor_id}...")

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            print(f"✓ 成功: {result['message']}")
            return result
        except requests.exceptions.RequestException as e:
            print(f"✗ 失敗: {e}")
            return {"status": "error", "error": str(e)}

    def push_stream(self, num_samples: int = 25600, sampling_rate: float = 25600.0) -> dict:
        """
        推送流式數據（陣列形式）

        Args:
            num_samples: 樣本數量
            sampling_rate: 採樣率 Hz

        Returns:
            響應結果
        """
        url = f"{self.base_url}/api/sensor/data/stream"

        # 生成陣列數據
        h_acc, v_acc = self.simulator.generate_arrays(num_samples)
        timestamp_start = datetime.now()

        # 準備請求參數
        params = {
            "sensor_id": self.sensor_id,
            "h_acc": h_acc,
            "v_acc": v_acc,
            "timestamp_start": timestamp_start.isoformat(),
            "sampling_rate": sampling_rate
        }

        print(f"推送 {num_samples} 個流式數據點 (採樣率: {sampling_rate} Hz)...")

        try:
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            print(f"✓ 成功: 處理了 {result['processed']} 個點")
            return result
        except requests.exceptions.RequestException as e:
            print(f"✗ 失敗: {e}")
            return {"status": "error", "error": str(e)}

    def continuous_push(
        self,
        batch_size: int = 25600,
        duration_seconds: Optional[int] = None,
        interval_seconds: float = 1.0
    ):
        """
        持續推送數據

        Args:
            batch_size: 每次推送的樣本數
            duration_seconds: 持續時間（秒），None 表示無限
            interval_seconds: 推送間隔（秒）
        """
        url = f"{self.base_url}/api/sensor/data"

        print(f"開始持續推送模式...")
        print(f"  - 感測器 ID: {self.sensor_id}")
        print(f"  - 批次大小: {batch_size}")
        print(f"  - 推送間隔: {interval_seconds} 秒")
        if duration_seconds:
            print(f"  - 持續時間: {duration_seconds} 秒")
        print(f"  - 按 Ctrl+C 停止")
        print("-" * 50)

        counter = 0
        start_time = time.time()

        try:
            while True:
                # 檢查是否達到持續時間
                if duration_seconds:
                    elapsed = time.time() - start_time
                    if elapsed >= duration_seconds:
                        print(f"\n已達到指定持續時間 ({duration_seconds} 秒)")
                        break

                # 生成並推送數據
                data_points = self.simulator.generate_batch(batch_size)

                payload = {
                    "sensor_id": self.sensor_id,
                    "data": [
                        {
                            "timestamp": point["timestamp"].isoformat(),
                            "h_acc": point["h_acc"],
                            "v_acc": point["v_acc"]
                        }
                        for point in data_points
                    ]
                }

                try:
                    response = requests.post(url, json=payload, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        counter += 1
                        if counter % 5 == 0:
                            elapsed = time.time() - start_time
                            rate = counter / elapsed if elapsed > 0 else 0
                            print(f"已推送 {counter} 批次 ({counter * batch_size} 點) - "
                                  f"平均速率: {rate:.2f} 批次/秒")
                    else:
                        print(f"批次 {counter + 1} 失敗: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    print(f"批次 {counter + 1} 失敗: {e}")

                # 等待下一次推送
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print(f"\n\n用戶中斷")

        total_seconds = time.time() - start_time
        print("-" * 50)
        print(f"總計:")
        print(f"  - 推送批次: {counter}")
        print(f"  - 數據點數: {counter * batch_size}")
        print(f"  - 運行時間: {total_seconds:.2f} 秒")
        print(f"  - 平均速率: {counter / total_seconds:.2f} 批次/秒")


def check_server_health(base_url: str) -> bool:
    """檢查伺服器是否運行"""
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="機台數據推送測試工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 推送單次小批量
  python scripts/test_sensor_data_push.py --mode single --samples 100

  # 推送大批量流式數據
  python scripts/test_sensor_data_push.py --mode stream --samples 25600

  # 持續推送 1 分鐘
  python scripts/test_sensor_data_push.py --mode continuous --duration 60

  # 持續推送無限時間
  python scripts/test_sensor_data_push.py --mode continuous
        """
    )

    parser.add_argument(
        "--url",
        default="http://localhost:8081",
        help="後端 API 基礎 URL (預設: http://localhost:8081)"
    )

    parser.add_argument(
        "--sensor-id",
        type=int,
        default=1,
        help="感測器 ID (預設: 1)"
    )

    parser.add_argument(
        "--mode",
        choices=["single", "stream", "continuous"],
        default="single",
        help="推送模式 (預設: single)"
    )

    parser.add_argument(
        "--samples",
        type=int,
        default=100,
        help="樣本數量 (預設: 100)"
    )

    parser.add_argument(
        "--duration",
        type=int,
        help="持續推送時間（秒）"
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="推送間隔（秒，僅 continuous 模式，預設: 1.0)"
    )

    parser.add_argument(
        "--sampling-rate",
        type=float,
        default=25600.0,
        help="採樣率 Hz (預設: 25600.0)"
    )

    args = parser.parse_args()

    # 檢查伺服器
    print(f"檢查伺服器: {args.url}")
    if not check_server_health(args.url):
        print(f"✗ 無法連接到伺服器。請確保後端正在運行。")
        sys.exit(1)
    print("✓ 伺服器運行正常\n")

    # 創建推送器
    pusher = DataPusher(args.url, args.sensor_id)

    # 根據模式執行
    if args.mode == "single":
        pusher.push_single_batch(args.samples)

    elif args.mode == "stream":
        pusher.push_stream(args.samples, args.sampling_rate)

    elif args.mode == "continuous":
        batch_size = args.samples if args.samples > 0 else 25600
        pusher.continuous_push(
            batch_size=batch_size,
            duration_seconds=args.duration,
            interval_seconds=args.interval
        )


if __name__ == "__main__":
    main()
