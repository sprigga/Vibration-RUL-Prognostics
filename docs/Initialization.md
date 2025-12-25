# Initialization Parameters for PHM 2012 Dataset

## Overview

This document describes the initialization parameters in `backend/initialization.py` that have been adapted for the **PHM IEEE 2012 Data Challenge** dataset from the PRONOSTIA experimental platform.

## Dataset Characteristics

| Parameter | Value | Description |
|-----------|-------|-------------|
| Sampling Frequency | 25.6 kHz (25600 Hz) | Original sampling rate |
| File Duration | 0.1 seconds | Each CSV file |
| Data Points | 2560 points | Per file |
| Bearing Type | SKF NKRF 25/20 | PRONOSTIA platform |
| Rolling Elements (Nb) | 13 | Number of balls |
| Pitch Diameter (D) | 34 mm | Ball center circle diameter |
| Ball Diameter (d) | 6.7 mm | Single ball diameter |
| Contact Angle | 0° | Deep groove ball bearing |

## Working Conditions

The PHM 2012 dataset includes three operating conditions:

| Condition | RPM | Radial Load | Fr (Hz) | BPFO (Hz) | BPFI (Hz) |
|-----------|-----|-------------|---------|-----------|-----------|
| **Condition 1** | 1800 | 4000 N | 30.0 | 156.59 | 233.43 |
| **Condition 2** | 1650 | 4200 N | 27.5 | 143.54 | 213.98 |
| **Condition 3** | 1500 | 5000 N | 25.0 | 130.49 | 194.53 |

## Parameter Modifications

### 1. Sampling Parameters

| Parameter | Original (MFP) | New (PHM 2012) | Description |
|-----------|----------------|----------------|-------------|
| `fs` | 50000 Hz | **25600 Hz** | Original sampling frequency |
| `ts` | 1/50000 | **1/25600** | Sampling period (auto-calculated) |
| `tsa_fs` | 80 Hz | **180 Hz** | TSA resampling frequency |
| `tsa_ts` | 1/80 | **1/180** | TSA sampling period (auto-calculated) |

**Rationale for `tsa_fs = 180 Hz`:**
- For a shaft frequency of 30 Hz (Condition 1), 180 Hz provides 6 samples per revolution
- Original 80 Hz would only provide ~2.67 samples per revolution (insufficient for accurate TSA)

### 2. Bearing Characteristic Frequencies

| Parameter | Original (MFP) | New (PHM 2012) | Formula | Description |
|-----------|----------------|----------------|---------|-------------|
| `mortor_gear` | 99.873 Hz | **30.0 Hz** | Fr = RPM/60 | Shaft fundamental frequency |
| `belt_si` | 41.6 Hz | **156.59 Hz** | BPFO = (Nb/2)×(1-d/D)×Fr | Ball pass frequency outer |
| `mortor` | 1597.97 Hz | **233.43 Hz** | BPFI = (Nb/2)×(1+d/D)×Fr | Ball pass frequency inner |
| `high_hamonic` | 20673.84 Hz | **466.86 Hz** | BPFI×2 | Second harmonic |

**Calculation Details (Condition 1: 1800 RPM):**

```
Given:
- Nb = 13 (rolling elements)
- D = 34 mm (pitch diameter)
- d = 6.7 mm (ball diameter)
- Fr = 1800/60 = 30 Hz (shaft frequency)

BPFO = (13/2) × (1 - 6.7/34) × 30 = 6.5 × 0.803 × 30 = 156.59 Hz
BPFI = (13/2) × (1 + 6.7/34) × 30 = 6.5 × 1.197 × 30 = 233.43 Hz
FTF  = (1/2) × (1 - 6.7/34) × 30 = 0.5 × 0.803 × 30 = 12.05 Hz
BSF  = (34/(2×6.7)) × (1 - (6.7/34)²) × 30 = 2.537 × 0.961 × 30 = 73.16 Hz
```

### 3. Frequency Range Parameters

| Parameter | Original (MFP) | New (PHM 2012) | Description |
|-----------|----------------|----------------|-------------|
| `side_band_range` | 1.664 | **2.0** | Sideband tolerance (±2 Hz) |
| `harmonic_gmf_range` | 1.5 | **1.0** | Harmonic tolerance |
| `mortor_gear_range` | 2.5 | **2.0** | Shaft frequency range |
| `belt_si_range` | 2.5 | **2.0** | BPFO frequency range |
| `morotr_range` | 8.29 | **3.0** | BPFI frequency range |
| `high_hamonic_range` | 5 | **5.0** | High-order harmonic range |

### 4. STFT Parameters (Unchanged)

| Parameter | Value | Time Resolution | Frequency Resolution |
|-----------|-------|-----------------|----------------------|
| `stft_hann_nperseg` | 128 | 5 ms | 200 Hz |
| `stft_flattop_nperseg` | 256 | 10 ms | 100 Hz |
| `cwt_scale_max` | 64 | - | - |

These parameters are optimized for 2560 points per file at 25600 Hz sampling rate.

## Usage

### Basic Usage

```python
from backend.initialization import InitParameter

# Create instance with default Condition 1 (1800 RPM)
params = InitParameter()

print(f"Sampling rate: {params.fs} Hz")
print(f"Shaft frequency: {params.mortor_gear} Hz")
print(f"BPFO: {params.belt_si} Hz")
print(f"BPFI: {params.mortor} Hz")
```

### Switching Working Conditions

```python
# Switch to Condition 2 (1650 RPM)
info = params.set_working_condition(2)
print(info)
# Output: {'condition': 2, 'rpm': 1650, 'load_N': 4200, ...}

# Switch to Condition 3 (1500 RPM)
info = params.set_working_condition(3)
print(info)

# Get current condition info
current = params.get_current_condition_info()
print(current)
```

### Condition-Specific Reference Frequencies

```python
# Access pre-calculated frequencies for all conditions
print(f"Condition 1 BPFO: {params.bpfo_condition1} Hz")
print(f"Condition 2 BPFO: {params.bpfo_condition2} Hz")
print(f"Condition 3 BPFO: {params.bpfo_condition3} Hz")

# Additional frequencies (FTF, BSF)
print(f"Condition 1 FTF: {params.ftf_condition1} Hz")
print(f"Condition 1 BSF: {params.bsf_condition1} Hz")
```

## Bearing Fault Frequencies

| Fault Type | Frequency | Description |
|------------|-----------|-------------|
| **Inner Race** | BPFI | Fault on inner raceway |
| **Outer Race** | BPFO | Fault on outer raceway |
| **Ball/Roller** | BSF | Fault on rolling element |
| **Cage** | FTF | Fault on cage/retainer |

## Parameter Summary Table

| Category | Parameter | PHM 2012 Value | Original MFP Value |
|----------|-----------|----------------|-------------------|
| **Sampling** | `fs` | 25600 | 50000 |
| | `tsa_fs` | 180 | 80 |
| **Shaft** | `mortor_gear` | 30.0 | 99.873 |
| **Inner Race** | `mortor` | 233.43 | 1597.97 |
| **Outer Race** | `belt_si` | 156.59 | 41.6 |
| **Harmonic** | `high_hamonic` | 466.86 | 20673.84 |
| **Ranges** | `side_band_range` | 2.0 | 1.664 |
| | `harmonic_gmf_range` | 1.0 | 1.5 |
| | `mortor_gear_range` | 2.0 | 2.5 |
| | `belt_si_range` | 2.0 | 2.5 |
| | `morotr_range` | 3.0 | 8.29 |

## References

1. Nectoux, P., et al. (2012). PRONOSTIA: An experimental platform for bearings accelerated degradation tests. *IEEE International Conference on Prognostics and Health Management*, Denver.

2. PRONOSTIA Platform Specifications:
   - Bearing: SKF NKRF 25/20
   - Number of rolling elements: 13
   - Pitch diameter: 34 mm
   - Ball diameter: 6.7 mm

## Validation

To verify the parameters:

```python
from backend.initialization import InitParameter

# Test loading
p = InitParameter()
assert p.fs == 25600
assert p.mortor_gear == 30.0
assert p.belt_si == 156.59

# Test condition switching
info = p.set_working_condition(2)
assert p.mortor_gear == 27.5
assert p.belt_si == 143.54

print("All parameters validated successfully!")
```

## Notes

- All original MFP parameters are preserved as comments in the code
- Default initialization uses Condition 1 (1800 RPM, 4000 N)
- Use `set_working_condition()` to switch between conditions
- STFT parameters remain unchanged as they are well-suited for the data format
