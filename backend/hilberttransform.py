"""
Hilbert Transform Analysis Module
Based on hilbertransfer.py, adapted for PHM database integration
"""
import pandas as pd
import numpy as np
from scipy.signal import hilbert


class HilbertTransform:
    """Hilbert Transform analysis for vibration signals"""

    def __init__(self):
        pass

    def calculate_nb4(self, envelope_data, segment_count=10):
        """
        計算 NB4 (Normalized Bispectrum 4th order) 數值

        Args:
            envelope_data: numpy array of envelope amplitude
            segment_count: 資料分割段數 (default: 10)

        Returns:
            nb4: NB4 特徵值
        """
        n = len(envelope_data)

        if n == 0:
            return 0.0

        # 計算整體平均值
        amp_mean = np.mean(envelope_data)

        # 分段計算
        segment_size = n // segment_count
        total_sum_segment = 0.0

        for i in range(segment_count):
            start_idx = i * segment_size
            end_idx = (i + 1) * segment_size if i < segment_count - 1 else n

            segment_data = envelope_data[start_idx:end_idx]

            if len(segment_data) == 0:
                continue

            segment_mean = np.mean(segment_data)
            sum_segment = np.sum((segment_data - segment_mean) ** 2) / len(segment_data)
            total_sum_segment += sum_segment

        # 計算 NB4
        if total_sum_segment == 0:
            return 0.0

        division_total_sum_segment = (total_sum_segment / segment_count) ** 2
        total_sum_all = np.sum((envelope_data - amp_mean) ** 4) / n

        nb4 = total_sum_all / division_total_sum_segment

        return float(nb4)

    def hilbert_transform(self, signal):
        """
        計算希爾伯特轉換及包絡線

        Args:
            signal: numpy array of input signal

        Returns:
            dict containing:
                - analytic_signal: complex analytic signal
                - envelope: amplitude envelope
                - instantaneous_phase: instantaneous phase
                - instantaneous_frequency: instantaneous frequency
        """
        # 計算希爾伯特轉換
        analytic_signal = hilbert(signal)

        # 提取包絡線（振幅）
        envelope = np.abs(analytic_signal)

        # 瞬時相位
        instantaneous_phase = np.angle(analytic_signal)

        # 瞬時頻率（相位對時間的導數）
        instantaneous_frequency = np.diff(np.unwrap(instantaneous_phase)) / (2.0 * np.pi)

        return {
            'analytic_signal': analytic_signal,
            'envelope': envelope,
            'instantaneous_phase': instantaneous_phase,
            'instantaneous_frequency': instantaneous_frequency
        }

    def analyze_signal(self, signal, segment_count=10):
        """
        完整的希爾伯特轉換分析

        Args:
            signal: numpy array of input signal
            segment_count: NB4 計算的分段數

        Returns:
            dict containing analysis results
        """
        # 執行希爾伯特轉換
        ht_result = self.hilbert_transform(signal)

        # 計算 NB4
        nb4 = self.calculate_nb4(ht_result['envelope'], segment_count)

        # 計算包絡線統計特徵
        envelope = ht_result['envelope']
        envelope_stats = {
            'mean': float(np.mean(envelope)),
            'std': float(np.std(envelope)),
            'max': float(np.max(envelope)),
            'min': float(np.min(envelope)),
            'rms': float(np.sqrt(np.mean(envelope ** 2))),
            'peak_to_peak': float(np.max(envelope) - np.min(envelope))
        }

        return {
            'nb4': nb4,
            'envelope': ht_result['envelope'],
            'envelope_stats': envelope_stats,
            'instantaneous_phase': ht_result['instantaneous_phase'],
            'instantaneous_frequency': ht_result['instantaneous_frequency'],
            'analytic_real': ht_result['analytic_signal'].real,
            'analytic_imag': ht_result['analytic_signal'].imag
        }

    def analyze_dual_channel(self, horizontal_signal, vertical_signal, segment_count=10):
        """
        分析水平和垂直雙通道信號

        Args:
            horizontal_signal: numpy array of horizontal channel
            vertical_signal: numpy array of vertical channel
            segment_count: NB4 計算的分段數

        Returns:
            dict containing results for both channels
        """
        horiz_result = self.analyze_signal(horizontal_signal, segment_count)
        vert_result = self.analyze_signal(vertical_signal, segment_count)

        return {
            'horizontal': horiz_result,
            'vertical': vert_result
        }
