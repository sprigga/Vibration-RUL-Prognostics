"""
Filter Process Module for Advanced Signal Analysis

This module provides advanced filtering and statistical analysis methods
for vibration signal processing, including:
- NA4: Normalized 4th moment with segmentation
- FM4: Fourth moment feature
- M6A: 6th moment feature
- M8A: 8th moment feature
- ER: Energy ratio (sideband to total)
"""

import pandas as pd
import numpy as np
from typing import Tuple, Any

try:
    from backend.timedomain import TimeDomain as td
    from backend.frequencydomain import FrequencyDomain as fd
except ModuleNotFoundError:
    from timedomain import TimeDomain as td
    from frequencydomain import FrequencyDomain as fd


class FilterProcess:
    """Advanced signal processing and filtering methods"""

    @staticmethod
    def NA4(signal: np.ndarray, m: int = 10) -> Tuple[float, float, float]:
        """
        Calculate Normalized 4th moment with segmentation (NA4)

        NA4 is sensitive to early fault detection and measures the
        concentration of signal energy.

        Args:
            signal: Input signal array
            m: Number of segments (default: 10)

        Returns:
            Tuple of (na4, total_sum_all, division_total_sum_segment)
        """
        n = len(signal)
        segment_size = n // m
        signal_mean = np.mean(signal)

        # Calculate segmented variance
        total_sum_segment = 0
        for i in range(m):
            start_idx = i * segment_size
            end_idx = (i + 1) * segment_size if i < m - 1 else n
            segment = signal[start_idx:end_idx]
            segment_mean = np.mean(segment)
            sum_segment = np.sum((segment - segment_mean) ** 2)
            total_sum_segment += sum_segment

        division_total_sum_segment = (total_sum_segment / m) ** 2

        # Calculate total 4th moment
        total_sum_all = np.sum((signal - signal_mean) ** 4) * n

        # Calculate NA4
        na4 = total_sum_all / division_total_sum_segment if division_total_sum_segment != 0 else np.nan

        return na4, total_sum_all, division_total_sum_segment

    @staticmethod
    def FM4(signal: np.ndarray) -> float:
        """
        Calculate Fourth Moment Feature (FM4)

        FM4 is useful for detecting sideband energy anomalies.

        Formula: FM4 = N·Σ(x-μ)⁴ / [Σ(x-μ)²]²

        Args:
            signal: Input signal array

        Returns:
            FM4 value
        """
        n = len(signal)
        signal_mean = np.mean(signal)
        difference = signal - signal_mean

        denominator = np.sum(difference ** 2) ** 2
        fm4 = (n * np.sum(difference ** 4)) / denominator if denominator != 0 else np.nan

        return float(fm4)

    @staticmethod
    def M6A(signal: np.ndarray) -> float:
        """
        Calculate 6th Moment Feature (M6A)

        M6A is sensitive to very early stage faults.

        Formula: M6A = N²·Σ(x-μ)⁶ / [Σ(x-μ)²]³

        Args:
            signal: Input signal array

        Returns:
            M6A value
        """
        n = len(signal)
        signal_mean = np.mean(signal)
        difference = signal - signal_mean

        denominator = np.sum(difference ** 2) ** 3
        m6a = ((n ** 2) * np.sum(difference ** 6)) / denominator if denominator != 0 else np.nan

        return float(m6a)

    @staticmethod
    def M8A(signal: np.ndarray) -> float:
        """
        Calculate 8th Moment Feature (M8A)

        M8A is highly sensitive to lubrication issues and extreme early faults.

        Formula: M8A = N³·Σ(x-μ)⁸ / [Σ(x-μ)²]⁴

        Args:
            signal: Input signal array

        Returns:
            M8A value
        """
        n = len(signal)
        signal_mean = np.mean(signal)
        difference = signal - signal_mean

        denominator = np.sum(difference ** 2) ** 4
        m8a = ((n ** 3) * np.sum(difference ** 8)) / denominator if denominator != 0 else np.nan

        return float(m8a)

    @staticmethod
    def ER_simple(signal: np.ndarray, fs: int, low_freq: float = 1000, high_freq: float = 5000) -> float:
        """
        Calculate simplified Energy Ratio (ER)

        ER measures the ratio of energy in a specific frequency band to total energy.
        This is a simplified version that uses a bandpass frequency range.

        Args:
            signal: Input signal array
            fs: Sampling frequency
            low_freq: Lower frequency bound for energy calculation (Hz)
            high_freq: Upper frequency bound for energy calculation (Hz)

        Returns:
            ER value (ratio)
        """
        # Calculate FFT
        fft_values = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/fs)

        # Only use positive frequencies
        positive_freq_indices = freqs > 0
        freqs = freqs[positive_freq_indices]
        fft_magnitude = np.abs(fft_values[positive_freq_indices])

        # Calculate total RMS
        total_rms = td.rms(signal)

        # Calculate band RMS (energy in specified frequency range)
        band_mask = (freqs >= low_freq) & (freqs <= high_freq)
        if np.sum(band_mask) > 0:
            band_energy = np.sum(fft_magnitude[band_mask] ** 2)
            total_energy = np.sum(fft_magnitude ** 2)
            er = np.sqrt(band_energy / total_energy) if total_energy > 0 else 0.0
        else:
            er = 0.0

        return float(er)

    @staticmethod
    def calculate_all_features(signal: np.ndarray, fs: int = 25600, segment_count: int = 10) -> dict:
        """
        Calculate all filter process features for a signal

        Args:
            signal: Input signal array
            fs: Sampling frequency (default: 25600 Hz for PHM dataset)
            segment_count: Number of segments for NA4 calculation

        Returns:
            Dictionary containing all calculated features
        """
        # Calculate all features
        na4, total_sum_all, div_total_sum = FilterProcess.NA4(signal, segment_count)
        fm4 = FilterProcess.FM4(signal)
        m6a = FilterProcess.M6A(signal)
        m8a = FilterProcess.M8A(signal)
        er = FilterProcess.ER_simple(signal, fs)

        # Also calculate basic time domain features for reference
        peak = td.peak(signal)
        rms = td.rms(signal)
        kurtosis = td.kurt(signal)

        return {
            'na4': float(na4),
            'fm4': float(fm4),
            'm6a': float(m6a),
            'm8a': float(m8a),
            'er': float(er),
            'kurtosis': float(kurtosis),
            'peak': float(peak),
            'rms': float(rms),
            'segment_count': segment_count
        }
