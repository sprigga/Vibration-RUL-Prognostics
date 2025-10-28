"""
測試 backend/timefrequency.py 的整合功能
"""
import numpy as np
from backend.timefrequency import TimeFrequency

# 生成測試信號
fs = 25600  # 採樣率
duration = 1.0  # 持續時間（秒）
t = np.linspace(0, duration, int(fs * duration))

# 模擬振動信號（包含多個頻率成分）
signal_1000 = np.sin(2 * np.pi * 1000 * t)  # 1000 Hz
signal_1500 = 0.5 * np.sin(2 * np.pi * 1500 * t)  # 1500 Hz
signal_2000 = 0.3 * np.sin(2 * np.pi * 2000 * t)  # 2000 Hz
noise = 0.1 * np.random.randn(len(t))

test_signal = signal_1000 + signal_1500 + signal_2000 + noise

print("=" * 70)
print("測試整合功能")
print("=" * 70)

# 測試 1: STFT 分析（帶頻率過濾）
print("\n1. 測試 STFT 分析（帶頻率過濾 800-2500 Hz）")
print("-" * 70)
stft_result = TimeFrequency.stft_analysis(
    test_signal, fs=fs, window='hann', nperseg=256,
    freq_range=(800, 2500)
)
print(f"NP4: {stft_result['np4']:.4f}")
print(f"最大頻率: {stft_result['max_freq']:.2f} Hz")
print(f"總能量: {stft_result['total_energy']:.2e}")
print(f"頻率範圍: {stft_result['freq_range']}")

# 測試 2: 雙窗口 STFT 分析
print("\n2. 測試雙窗口 STFT 分析")
print("-" * 70)
dual_result = TimeFrequency.dual_window_stft_analysis(
    test_signal, fs=fs, hann_nperseg=128, flattop_nperseg=256,
    freq_range=(800, 2500)
)
print(f"Hann NP4: {dual_result['hann_np4']:.4f}")
print(f"Flattop NP4: {dual_result['flattop_np4']:.4f}")
print(f"Hann 最大頻率: {dual_result['hann']['max_freq']:.2f} Hz")
print(f"Flattop 最大頻率: {dual_result['flattop']['max_freq']:.2f} Hz")

# 測試 3: CWT 分析（帶頻率過濾）
print("\n3. 測試 CWT 分析（帶頻率過濾 800-2500 Hz）")
print("-" * 70)
cwt_result = TimeFrequency.cwt_analysis(
    test_signal, fs=fs, wavelet='morl', scales=np.arange(1, 65),
    freq_range=(800, 2500)
)
print(f"NP4: {cwt_result['np4']:.4f}")
print(f"最大頻率: {cwt_result['max_freq']:.2f} Hz")
print(f"最大尺度: {cwt_result['max_scale']:.2f}")
print(f"總能量: {cwt_result['total_energy']:.2e}")

# 測試 4: 標準化能量分析
print("\n4. 測試標準化能量分析 (NE)")
print("-" * 70)
# 先取得 STFT 係數
f, t_axis, Zxx = TimeFrequency.stft_analysis(
    test_signal, fs=fs, window='hann', nperseg=256
)['frequencies'], \
TimeFrequency.stft_analysis(
    test_signal, fs=fs, window='hann', nperseg=256
)['time'], \
TimeFrequency.stft_analysis(
    test_signal, fs=fs, window='hann', nperseg=256
)['magnitude']

ne_result = TimeFrequency.normalized_energy_analysis(
    Zxx, f, t_axis, freq_range=(800, 2500), time_segment_duration=0.5
)
print(f"NE 結果數量: {len(ne_result)} 個時頻分段")
if len(ne_result) > 0:
    print("\n前 5 個分段的標準化能量:")
    print(ne_result.head())

# 測試 5: 比較有無頻率過濾的差異
print("\n5. 比較有無頻率過濾的差異")
print("-" * 70)
stft_no_filter = TimeFrequency.stft_analysis(
    test_signal, fs=fs, window='hann', nperseg=256
)
stft_with_filter = TimeFrequency.stft_analysis(
    test_signal, fs=fs, window='hann', nperseg=256,
    freq_range=(800, 2500)
)
print(f"無過濾 NP4: {stft_no_filter['np4']:.4f}")
print(f"有過濾 NP4: {stft_with_filter['np4']:.4f}")
print(f"NP4 差異: {abs(stft_with_filter['np4'] - stft_no_filter['np4']):.4f}")

print("\n" + "=" * 70)
print("所有測試完成！")
print("=" * 70)
