"""
Time-Frequency Analysis Module
提供各種時頻域分析算法，包括 STFT、CWT、包絡分析等
"""
import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from scipy.stats import kurtosis


class TimeFrequency:
    """時頻域分析類"""

    @staticmethod
    def stft_analysis(x, fs=25600, window='hann', nperseg=256,
                      noverlap=None, freq_range=None):
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
        freq_range : tuple, optional
            頻率過濾範圍 (low_freq, high_freq)，例如 (800, 2500)

        Returns:
        --------
        dict : 包含頻率、時間、STFT 結果和特徵
        """
        if noverlap is None:
            noverlap = int(nperseg * 0.95)

        f, t, Zxx = signal.stft(
            x, fs=fs, window=window, nperseg=nperseg, noverlap=noverlap
        )
        magnitude = np.abs(Zxx)

        # 頻率過濾（如果指定範圍）
        if freq_range is not None:
            low_freq, high_freq = freq_range
            freq_mask = (f > low_freq) & (f <= high_freq)
            f_filtered = f[freq_mask]
            magnitude_filtered = magnitude[freq_mask, :]

            # 使用過濾後的數據計算 NP4
            np4 = TimeFrequency._calculate_np4(magnitude_filtered)

            # 找出能量最大的時間-頻率點（在過濾範圍內）
            max_idx = np.unravel_index(np.argmax(magnitude_filtered),
                                        magnitude_filtered.shape)
            max_freq = f_filtered[max_idx[0]]
            max_time = t[max_idx[1]]
            max_magnitude = magnitude_filtered[max_idx]
            total_energy = float(np.sum(magnitude_filtered**2))
        else:
            # 計算 NP4 特徵
            np4 = TimeFrequency._calculate_np4(magnitude)

            # 找出能量最大的時間-頻率點
            max_idx = np.unravel_index(np.argmax(magnitude), magnitude.shape)
            max_freq = f[max_idx[0]]
            max_time = t[max_idx[1]]
            max_magnitude = magnitude[max_idx]
            total_energy = float(np.sum(magnitude**2))

        return {
            'frequencies': f,
            'time': t,
            'magnitude': magnitude,
            'np4': float(np4),
            'max_freq': float(max_freq),
            'max_time': float(max_time),
            'max_magnitude': float(max_magnitude),
            'total_energy': total_energy,
            'freq_range': freq_range
        }

    @staticmethod
    def cwt_analysis(x, fs=25600, wavelet='morl', scales=None,
                     freq_range=None):
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
        freq_range : tuple, optional
            頻率過濾範圍 (low_freq, high_freq)，例如 (800, 2500)

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

        # 頻率過濾（如果指定範圍）
        if freq_range is not None:
            low_freq, high_freq = freq_range
            freq_mask = (frequencies > low_freq) & (frequencies <= high_freq)
            frequencies_filtered = frequencies[freq_mask]
            magnitude_filtered = magnitude[freq_mask, :]

            # 使用過濾後的數據計算 NP4
            np4 = TimeFrequency._calculate_np4(magnitude_filtered)

            # 找出最大能量的尺度（在過濾範圍內）
            energy_per_scale = np.sum(magnitude_filtered**2, axis=1)
            if len(energy_per_scale) > 0:
                max_scale_idx = np.argmax(energy_per_scale)
                max_freq = frequencies_filtered[max_scale_idx]
                max_scale = scales[freq_mask][max_scale_idx]
                total_energy = float(np.sum(magnitude_filtered**2))
            else:
                max_scale = 0.0
                max_freq = 0.0
                total_energy = 0.0
        else:
            # 計算 NP4
            np4 = TimeFrequency._calculate_np4(magnitude)

            # 找出最大能量的尺度
            energy_per_scale = np.sum(magnitude**2, axis=1)
            max_scale_idx = np.argmax(energy_per_scale)
            max_scale = scales[max_scale_idx]
            max_freq = frequencies[max_scale_idx]
            total_energy = float(np.sum(magnitude**2))

        return {
            'scales': scales,
            'frequencies': frequencies,
            'magnitude': magnitude,
            'np4': float(np4),
            'max_scale': float(max_scale),
            'max_freq': float(max_freq),
            'energy_per_scale': energy_per_scale,
            'total_energy': total_energy,
            'freq_range': freq_range
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
        peak_freqs = [float(freq[i]) for i in peaks_idx
                      if freq[i] > 0]
        peak_mags = [float(envelope_magnitude[i]) for i in peaks_idx
                     if freq[i] > 0]

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
    def higher_order_statistics(x, fs=25600, M=10):
        """
        高階統計分析 (已整合至 FilterProcess)

        此方法已棄用，請使用 FilterProcess.calculate_all_features() 代替
        為了向後兼容性保留此方法，內部委託給 FilterProcess

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
        dict : 包含 NA4, FM4, M6A, M8A, ER, Kurtosis 等特徵
        """
        # 導入 FilterProcess 以使用統一的實現
        try:
            from backend.filterprocess import FilterProcess
        except ModuleNotFoundError:
            from filterprocess import FilterProcess

        # 使用 FilterProcess 的統一實現（更精確的計算）
        return FilterProcess.calculate_all_features(x, fs, M)

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
        f, t, Sxx = signal.spectrogram(x, fs=fs, window=window,
                                        nperseg=nperseg)

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
        instantaneous_frequency = (np.diff(instantaneous_phase) /
                                   (2.0 * np.pi) * fs)

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

    @staticmethod
    def dual_window_stft_analysis(x, fs=25600, hann_nperseg=128,
                                   flattop_nperseg=256,
                                   freq_range=(800, 2500)):
        """
        雙窗口 STFT 分析 (Hann + Flattop)
        模擬 waveletprocess.py 的 StftProcess 方法

        Parameters:
        -----------
        x : array_like
            輸入信號
        fs : int
            採樣率
        hann_nperseg : int
            Hann 窗口的段長度
        flattop_nperseg : int
            Flattop 窗口的段長度
        freq_range : tuple
            頻率過濾範圍 (low_freq, high_freq)

        Returns:
        --------
        dict : 包含兩種窗口的分析結果
        """
        # Hann 窗口分析
        hann_result = TimeFrequency.stft_analysis(
            x, fs=fs, window='hann',
            nperseg=hann_nperseg,
            noverlap=int(hann_nperseg * 0.95),
            freq_range=freq_range
        )

        # Flattop 窗口分析
        flattop_result = TimeFrequency.stft_analysis(
            x, fs=fs, window='flattop',
            nperseg=flattop_nperseg,
            noverlap=int(flattop_nperseg * 0.95),
            freq_range=freq_range
        )

        return {
            'hann': hann_result,
            'flattop': flattop_result,
            'hann_np4': hann_result['np4'],
            'flattop_np4': flattop_result['np4']
        }

    @staticmethod
    def normalized_energy_analysis(coefficients, frequencies, time,
                                    freq_range=(800, 2500),
                                    time_segment_duration=0.5):
        """
        標準化能量分析 (NE)
        模擬 waveletprocess.py 的 NE 方法

        Parameters:
        -----------
        coefficients : 2D array
            時頻係數矩陣（頻率 x 時間）
        frequencies : array_like
            頻率數組
        time : array_like
            時間數組
        freq_range : tuple
            頻率範圍 (low_freq, high_freq)
        time_segment_duration : float
            時間分段長度（秒）

        Returns:
        --------
        pd.DataFrame : 每個時頻分段的標準化能量
        """
        import pandas as pd

        magnitude = np.abs(coefficients)

        # 計算時間分段
        time_mask = time <= time_segment_duration
        if np.any(time_mask):
            segment_size = np.sum(time_mask)
            n_time_segments = len(time) // segment_size
        else:
            segment_size = len(time)
            n_time_segments = 1

        # 定義頻率分段（從高到低）
        low_freq, high_freq = freq_range
        freq_segments = np.arange(high_freq, low_freq - 200, -200)
        if freq_segments[-1] != low_freq:
            freq_segments = np.append(freq_segments, low_freq)

        ne_results = []

        # 對每個頻率段計算
        for i in range(len(freq_segments) - 1):
            freq_high = freq_segments[i]
            freq_low = freq_segments[i + 1]

            # 找出頻率範圍內的索引
            freq_mask = (frequencies > freq_low) & (frequencies <= freq_high)
            if not np.any(freq_mask):
                continue

            # 該頻率段的總能量
            freq_segment_energy = np.sum(magnitude[freq_mask, :])

            if freq_segment_energy == 0:
                continue

            # 對每個時間段計算標準化能量
            for j in range(n_time_segments):
                time_start = j * segment_size
                time_end = min((j + 1) * segment_size, len(time))

                # 該時頻區域的能量
                time_freq_energy = np.sum(
                    magnitude[freq_mask, time_start:time_end]
                )

                # 標準化能量
                ne = time_freq_energy / freq_segment_energy

                ne_results.append({
                    'freq_segment': f'{freq_low}-{freq_high}',
                    'time_segment': j,
                    'normalized_energy': ne,
                    'freq_low': freq_low,
                    'freq_high': freq_high
                })

        return pd.DataFrame(ne_results)
