#!/usr/bin/env python3
"""
檢查 Sensor 資料是否寫入資料庫

使用方式:
    uv run python scripts/check_sensor_data.py --sensor-id 1
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database_async import db
from redis_client import redis_client


async def check_postgresql_sensor_data(sensor_id: int, limit: int = 10):
    """檢查 PostgreSQL 中的原始 sensor 資料"""
    print(f"\n{'='*60}")
    print(f"📊 檢查 PostgreSQL - sensor_data 表 (Sensor ID: {sensor_id})")
    print(f"{'='*60}")

    try:
        # 初始化資料庫連線
        await db.init_pool()

        # 查詢最新的資料
        query = """
            SELECT
                data_id,
                sensor_id,
                timestamp,
                horizontal_acceleration,
                vertical_acceleration
            FROM sensor_data
            WHERE sensor_id = $1
            ORDER BY timestamp DESC
            LIMIT $2
        """

        rows = await db.fetch(query, sensor_id, limit)

        if not rows:
            print("❌ 沒有找到資料")
            return False

        print(f"✅ 找到 {len(rows)} 筆資料:\n")

        for row in rows[:5]:  # 只顯示前 5 筆
            print(f"  📅 Data ID: {row['data_id']}")
            print(f"  🕐 Timestamp: {row['timestamp']}")
            print(f"  ↔️  H_Acc: {row['horizontal_acceleration']:.6f}")
            print(f"  ↕️  V_Acc: {row['vertical_acceleration']:.6f}")
            print()

        # 統計資料
        count_query = """
            SELECT
                COUNT(*) as total_count,
                MIN(timestamp) as earliest,
                MAX(timestamp) as latest
            FROM sensor_data
            WHERE sensor_id = $1
        """

        stats = await db.fetchone(count_query, sensor_id)

        print(f"📈 統計資訊:")
        print(f"  總筆數: {stats['total_count']}")
        print(f"  最早時間: {stats['earliest']}")
        print(f"  最新時間: {stats['latest']}")

        return True

    except Exception as e:
        print(f"❌ PostgreSQL 查詢錯誤: {e}")
        return False
    finally:
        await db.close_pool()


async def check_postgresql_features(sensor_id: int, limit: int = 10):
    """檢查 PostgreSQL 中的特徵資料"""
    print(f"\n{'='*60}")
    print(f"📊 檢查 PostgreSQL - realtime_features 表 (Sensor ID: {sensor_id})")
    print(f"{'='*60}")

    try:
        # 初始化資料庫連線
        if not db._is_connected:
            await db.init_pool()

        # 查詢最新的特徵
        query = """
            SELECT
                feature_id,
                sensor_id,
                window_start,
                window_end,
                rms_h,
                rms_v,
                kurtosis_h,
                kurtosis_v,
                peak_h,
                peak_v,
                crest_factor_h,
                crest_factor_v
            FROM realtime_features
            WHERE sensor_id = $1
            ORDER BY window_end DESC
            LIMIT $2
        """

        rows = await db.fetch(query, sensor_id, limit)

        if not rows:
            print("❌ 沒有找到特徵資料")
            return False

        print(f"✅ 找到 {len(rows)} 筆特徵資料:\n")

        for row in rows[:5]:
            print(f"  🆔 Feature ID: {row['feature_id']}")
            print(f"  ⏰ Window: {row['window_start']} ~ {row['window_end']}")
            print(f"  📊 RMS: H={row['rms_h']:.4f}, V={row['rms_v']:.4f}")
            print(f"  📈 Kurtosis: H={row['kurtosis_h']:.4f}, V={row['kurtosis_v']:.4f}")
            print(f"  🔺 Peak: H={row['peak_h']:.4f}, V={row['peak_v']:.4f}")
            print(f"  📐 Crest Factor: H={row['crest_factor_h']:.4f}, V={row['crest_factor_v']:.4f}")
            print()

        # 統計資料
        count_query = """
            SELECT
                COUNT(*) as total_count,
                MIN(window_start) as earliest,
                MAX(window_end) as latest
            FROM realtime_features
            WHERE sensor_id = $1
        """

        stats = await db.fetchone(count_query, sensor_id)

        print(f"📈 統計資訊:")
        print(f"  總筆數: {stats['total_count']}")
        print(f"  最早時間: {stats['earliest']}")
        print(f"  最新時間: {stats['latest']}")

        return True

    except Exception as e:
        print(f"❌ PostgreSQL 查詢錯誤: {e}")
        return False


async def check_redis_sensor_data(sensor_id: int):
    """檢查 Redis 中的 sensor 資料"""
    print(f"\n{'='*60}")
    print(f"📊 檢查 Redis Streams (Sensor ID: {sensor_id})")
    print(f"{'='*60}")

    try:
        # 初始化 Redis 連線
        await redis_client.connect()

        # 檢查 stream 是否存在
        # Redis key 格式: stream:sensor:{sensor_id} (參考 redis_client.py line 83)
        stream_key = f"stream:sensor:{sensor_id}"

        # 獲取 stream 資訊
        try:
            stream_info = await redis_client.redis.xinfo_stream(stream_key)
            print(f"✅ Stream 存在: {stream_key}")
            print(f"   長度: {stream_info.get('length', 0)}")
            print(f"   群組數: {stream_info.get('groups', 0)}")
            print(f"   第一筆 ID: {stream_info.get('first-entry', 'N/A')}")
            print(f"   最後一筆 ID: {stream_info.get('last-entry', 'N/A')}")

            # 讀取最新的幾筆資料
            entries = await redis_client.redis.xrevrange(
                stream_key,
                max='+',
                count=5
            )

            if entries:
                print(f"\n📝 最新 5 筆資料:")
                for entry_id, data in entries:
                    # entry_id 可能是字串或位元組,統一處理
                    if isinstance(entry_id, bytes):
                        entry_id = entry_id.decode()

                    print(f"\n  🆔 Entry ID: {entry_id}")
                    for key, value in data.items():
                        # 處理字串/位元組
                        key_str = key.decode() if isinstance(key, bytes) else key
                        value_str = value.decode() if isinstance(value, bytes) else value
                        print(f"     {key_str}: {value_str}")
            else:
                print("⚠️  Stream 存在但沒有資料")

            return True

        except Exception as e:
            if "no such key" in str(e):
                print(f"❌ Stream 不存在: {stream_key}")
                print("   可能原因:")
                print("   1. 尚未接收任何 sensor 資料")
                print("   2. 資料已過期 (Redis TTL: 24小時)")
                return False
            else:
                raise

    except Exception as e:
        print(f"❌ Redis 查詢錯誤: {e}")
        return False
    finally:
        await redis_client.close()


async def check_buffer_status(sensor_id: int):
    """檢查 Buffer Manager 狀態"""
    print(f"\n{'='*60}")
    print(f"📊 檢查 Buffer Manager 狀態 (Sensor ID: {sensor_id})")
    print(f"{'='*60}")

    try:
        from buffer_manager import buffer_manager

        # 獲取所有 buffer 統計
        stats = await buffer_manager.get_all_buffer_stats()

        sensor_found = False
        for stat in stats:
            if stat['sensor_id'] == sensor_id:
                sensor_found = True
                print(f"✅ Sensor {sensor_id} Buffer 狀態:")
                print(f"   Buffer Size: {stat['buffer_size']}")
                print(f"   Current Size: {stat['current_size']}")
                print(f"   Sample Count: {stat['sample_count']}")
                print(f"   Window Start: {stat['window_start']}")
                print(f"   Latest Timestamp: {stat['latest_timestamp']}")

                # 計算緩衝區使用率
                usage = (stat['current_size'] / stat['buffer_size'] * 100) if stat['buffer_size'] > 0 else 0
                print(f"   Buffer Usage: {usage:.1f}%")
                break

        if not sensor_found:
            print(f"❌ Sensor {sensor_id} 沒有 active buffer")
            print("   可能原因:")
            print("   1. 尚未接收到資料")
            print("   2. Buffer 已被清理")

        # 顯示所有 active sensors
        print(f"\n📋 所有 Active Buffers:")
        if stats:
            for stat in stats:
                print(f"   Sensor {stat['sensor_id']}: {stat['current_size']} samples")
        else:
            print("   沒有 active buffers")

        return sensor_found

    except Exception as e:
        print(f"❌ Buffer Manager 查詢錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(description='檢查 Sensor 資料是否寫入資料庫')
    parser.add_argument('--sensor-id', type=int, default=1, help='Sensor ID (預設: 1)')
    parser.add_argument('--all', action='store_true', help='檢查所有資料來源')
    parser.add_argument('--postgres', action='store_true', help='只檢查 PostgreSQL')
    parser.add_argument('--redis', action='store_true', help='只檢查 Redis')
    parser.add_argument('--buffer', action='store_true', help='只檢查 Buffer')

    args = parser.parse_args()

    sensor_id = args.sensor_id

    print(f"\n{'#'*60}")
    print(f"# 🔍 Sensor 資料檢查工具")
    print(f"# Sensor ID: {sensor_id}")
    print(f"# 檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")

    results = {}

    try:
        if args.all or not (args.postgres or args.redis or args.buffer):
            # 檢查所有
            print("\n🔍 檢查所有資料來源...")

            results['buffer'] = await check_buffer_status(sensor_id)
            results['redis'] = await check_redis_sensor_data(sensor_id)
            results['postgres_raw'] = await check_postgresql_sensor_data(sensor_id)
            results['postgres_features'] = await check_postgresql_features(sensor_id)

        else:
            # 檢查指定項目
            if args.buffer:
                results['buffer'] = await check_buffer_status(sensor_id)

            if args.redis:
                results['redis'] = await check_redis_sensor_data(sensor_id)

            if args.postgres:
                results['postgres_raw'] = await check_postgresql_sensor_data(sensor_id)
                results['postgres_features'] = await check_postgresql_features(sensor_id)

        # 總結
        print(f"\n{'='*60}")
        print("📋 檢查結果總結")
        print(f"{'='*60}")

        for name, result in results.items():
            status = "✅ 正常" if result else "❌ 無資料"
            print(f"  {name}: {status}")

        # 診斷建議
        print(f"\n💡 診斷建議:")

        if not results.get('buffer'):
            print("  ⚠️  Buffer Manager 沒有資料")
            print("     → 請確認機台是否正在推送資料")
            print("     → 請確認 WebSocket 連接是否正常")

        if not results.get('redis') and results.get('buffer'):
            print("  ⚠️  Buffer 有資料但 Redis 沒有")
            print("     → 請檢查 Redis 服務是否正常運行")
            print("     → 請檢查 redis_client.py 的連線設定")

        if not results.get('postgres_raw') and results.get('redis'):
            print("  ⚠️  Redis 有資料但 PostgreSQL 沒有")
            print("     → 這是正常的! 系統只會將特徵寫入 PostgreSQL")
            print("     → 原始資料存放在 Redis (24小時 TTL)")

        if not results.get('postgres_features') and results.get('buffer'):
            print("  ⚠️  Buffer 有資料但沒有產生特徵")
            print("     → 請確認 realtime_analyzer 是否正常運行")
            print("     → 請確認資料量是否達到分析門檻 (min_samples: 10000)")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
