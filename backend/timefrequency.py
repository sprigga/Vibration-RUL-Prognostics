"""
Time-Frequency Analysis Module
提供各種時頻域分析算法，包括 STFT、CWT、包絡分析等
"""
import pandas as pd
import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from scipy.stats import kurtosis
from math import sqrt


class TimeFrequency:
    """時頻域分析類"""

    @staticmethod
    def stft_analysis(x, fs=25600, window='hann', nperseg=256, noverlap=None):
        """
        短時傅立葉轉換 (STFT)

        Parameters:
        -----------
        x : array_like
            輸入信號
        fs : int
            採樣率
        window : str or tuple
            窗函數類型 ('hann', 'flattop', etc.)
        nperseg : int
            每段的長度
        noverlap : int
            重疊的樣本數（默認為 95%）

        Returns:
        --------
        dict : 包含頻率、時間、STFT 結果和特徵
        """
        if noverlap is None:
            noverlap = int(nperseg * 0.95)

        f, t, Zxx = signal.stft(x, fs=fs, window=window, nperseg=nperseg, noverlap=noverlap)
        magnitude = np.abs(Zxx)

        # 計算 NP4 特徵
        np4 = TimeFrequency._calculate_np4(magnitude)

        # 找出能量最大的時間-頻率點
        max_idx = np.unravel_index(np.argmax(magnitude), magnitude.shape)
        max_freq = f[max_idx[0]]
        max_time = t[max_idx[1]]
        max_magnitude = magnitude[max_idx]

        return {
            'frequencies': f,
            'time': t,
            'magnitude': magnitude,
            'np4': float(np4),
            'max_freq': float(max_freq),
            'max_time': float(max_time),
            'max_magnitude': float(max_magnitude),
            'total_energy': float(np.sum(magnitude**2))
        }

    @staticmethod
    def cwt_analysis(x, fs=25600, wavelet='morl', scales=None):
        """
        連續小波轉換 (CWT)

        Parameters:
        -----------
        x : array_like
            輸入信號
        fs : int
            採樣率
        wavelet : str
            小波基函數 ('morl' for Morlet, 'gaus' for Gaussian, etc.)
        scales : array_like
            尺度數組（默認為 1-64）

        Returns:
        --------
        dict : 包含尺度、CWT 係數和特徵
        """
        if scales is None:
            scales = np.arange(1, 65)

        # 使用 scipy.signal.cwt
        if wavelet == 'morl':
            wavelet_func = signal.morlet2
        else:
            wavelet_func = signal.ricker

        coefficients = signal.cwt(x, wavelet_func, scales)
        magnitude = np.abs(coefficients)

        # 計算頻率（近似）
        frequencies = fs / (2 * scales)

        # 計算 NP4
        np4 = TimeFrequency._calculate_np4(magnitude)

        # 找出最大能量的尺度
        energy_per_scale = np.sum(magnitude**2, axis=1)
        max_scale_idx = np.argmax(energy_per_scale)
        max_scale = scales[max_scale_idx]
        max_freq = frequencies[max_scale_idx]

        return {
            'scales': scales,
            'frequencies': frequencies,
            'magnitude': magnitude,
            'np4': float(np4),
            'max_scale': float(max_scale),
            'max_freq': float(max_freq),
            'energy_per_scale': energy_per_scale,
            'total_energy': float(np.sum(magnitude**2))
        }

    @staticmethod
    def envelope_analysis(x, fs=25600, lowcut=4000, highcut=10000):
        """
        包絡分析（希爾伯特轉換）

        Parameters:
        -----------
        x : array_like
            輸入信號
        fs : int
            採樣率
        lowcut : float
            帶通濾波器低截止頻率
        highcut : float
            帶通濾波器高截止頻率

        Returns:
        --------
        dict : 包含包絡信號、包絡頻譜和特徵
        """
        # 設計帶通濾波器
        nyquist = fs / 2
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = signal.butter(4, [low, high], btype='band')

        # 帶通濾波
        x_filtered = signal.filtfilt(b, a, x)

        # 希爾伯特轉換提取包絡
        analytic_signal = signal.hilbert(x_filtered)
        envelope = np.abs(analytic_signal)

        # 對包絡做 FFT
        n = len(envelope)
        freq = fftfreq(n, 1/fs)[:n//2]
        envelope_fft = fft(envelope)
        envelope_magnitude = 2.0/n * np.abs(envelope_fft[:n//2])

        # 找出峰值頻率
        peaks_idx = np.argsort(envelope_magnitude)[-10:][::-1]
        peak_freqs = [float(freq[i]) for i in peaks_idx if freq[i] > 0]
        peak_mags = [float(envelope_magnitude[i]) for i in peaks_idx if freq[i] > 0]

        # 計算 RMS
        envelope_rms = float(np.sqrt(np.mean(envelope**2)))

        return {
            'envelope': envelope,
            'frequencies': freq,
            'magnitude': envelope_magnitude,
            'peak_frequencies': peak_freqs,
            'peak_magnitudes': peak_mags,
            'envelope_rms': envelope_rms,
            'total_power': float(np.sum(envelope_magnitude**2))
        }

    @staticmethod
    def higher_order_statistics(x, fs=25600, M=8):
        """
        高階統計分析

        Parameters:
        -----------
        x : array_like
            輸入信號
        fs : int
            採樣率
        M : int
            分段數量

        Returns:
        --------
        dict : 包含 NA4, FM4, M6A, M8A, ER 等特徵
        """
        n = len(x)
        mean_x = np.mean(x)

        # 計算中心矩
        centered = x - mean_x
        moment2 = np.sum(centered**2)
        moment4 = np.sum(centered**4)
        moment6 = np.sum(centered**6)
        moment8 = np.sum(centered**8)

        # NA4: 正規化四次矩（帶分段）
        segment_length = n // M
        na4_values = []
        for i in range(M):
            start = i * segment_length
            end = (i + 1) * segment_length if i < M - 1 else n
            segment = x[start:end]
            seg_centered = segment - np.mean(segment)
            seg_m2 = np.sum(seg_centered**2) / len(segment)
            seg_m4 = np.sum(seg_centered**4)
            if seg_m2 > 0:
                na4_values.append(len(segment) * seg_m4 / (seg_m2**2))

        na4 = float(np.mean(na4_values)) if na4_values else 0.0

        # FM4: 四次矩比值
        fm4 = float(n * moment4 / (moment2**2)) if moment2 > 0 else 0.0

        # M6A: 六次矩
        m6a = float(moment6 / n) if n > 0 else 0.0

        # M8A: 八次矩
        m8a = float(moment8 / n) if n > 0 else 0.0

        # ER: 能量比（需要頻譜分析）
        # 簡化版本：使用 RMS 作為總能量
        rms_total = np.sqrt(np.mean(x**2))

        # 使用濾波後的 RMS 作為邊帶能量
        # 帶通濾波 (1000-5000 Hz 作為示例)
        nyquist = fs / 2
        b, a = signal.butter(4, [1000/nyquist, 5000/nyquist], btype='band')
        x_sideband = signal.filtfilt(b, a, x)
        rms_sideband = np.sqrt(np.mean(x_sideband**2))

        er = float(rms_sideband / rms_total) if rms_total > 0 else 0.0

        # Kurtosis
        kurt = float(kurtosis(x, fisher=False, bias=False))

        return {
            'na4': na4,
            'fm4': fm4,
            'm6a': m6a,
            'm8a': m8a,
            'er': er,
            'kurtosis': kurt,
            'rms': float(rms_total)
        }

    @staticmethod
    def _calculate_np4(magnitude_matrix):
        """
        計算 NP4 特徵（用於時頻分析）

        NP4 = N * Σ(Z - μ)⁴ / [Σ(Z - μ)²]²

        Parameters:
        -----------
        magnitude_matrix : 2D array
            時頻域能量矩陣

        Returns:
        --------
        float : NP4 值
        """
        Z = magnitude_matrix.flatten()
        N = len(Z)
        mean_Z = np.mean(Z)

        centered = Z - mean_Z
        sum_2 = np.sum(centered**2)
        sum_4 = np.sum(centered**4)

        if sum_2 > 0:
            np4 = N * sum_4 / (sum_2**2)
        else:
            np4 = 0.0

        return np4

    @staticmethod
    def spectrogram_features(x, fs=25600, window='hann', nperseg=256):
        """
        計算頻譜圖及其統計特徵

        Parameters:
        -----------
        x : array_like
            輸入信號
        fs : int
            採樣率
        window : str
            窗函數
        nperseg : int
            每段長度

        Returns:
        --------
        dict : 頻譜圖數據和統計特徵
        """
        f, t, Sxx = signal.spectrogram(x, fs=fs, window=window, nperseg=nperseg)

        # 轉換為 dB
        Sxx_db = 10 * np.log10(Sxx + 1e-10)

        # 計算統計特徵
        mean_power = float(np.mean(Sxx_db))
        max_power = float(np.max(Sxx_db))
        std_power = float(np.std(Sxx_db))

        # 找出峰值
        max_idx = np.unravel_index(np.argmax(Sxx), Sxx.shape)
        peak_freq = float(f[max_idx[0]])
        peak_time = float(t[max_idx[1]])

        return {
            'frequencies': f,
            'time': t,
            'power_db': Sxx_db,
            'mean_power': mean_power,
            'max_power': max_power,
            'std_power': std_power,
            'peak_freq': peak_freq,
            'peak_time': peak_time
        }

    @staticmethod
    def instantaneous_frequency(x, fs=25600):
        """
        計算瞬時頻率

        Parameters:
        -----------
        x : array_like
            輸入信號
        fs : int
            採樣率

        Returns:
        --------
        dict : 瞬時頻率和相關特徵
        """
        # 希爾伯特轉換
        analytic_signal = signal.hilbert(x)

        # 瞬時相位
        instantaneous_phase = np.unwrap(np.angle(analytic_signal))

        # 瞬時頻率
        instantaneous_frequency = np.diff(instantaneous_phase) / (2.0 * np.pi) * fs

        # 統計特徵
        mean_freq = float(np.mean(instantaneous_frequency))
        std_freq = float(np.std(instantaneous_frequency))
        max_freq = float(np.max(instantaneous_frequency))
        min_freq = float(np.min(instantaneous_frequency))

        return {
            'instantaneous_frequency': instantaneous_frequency,
            'mean_freq': mean_freq,
            'std_freq': std_freq,
            'max_freq': max_freq,
            'min_freq': min_freq
        }
