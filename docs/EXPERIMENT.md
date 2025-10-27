# IEEE PHM 2012 Data Challenge - Experimental Setup and Conditions

## Overview
The IEEE PHM 2012 Data Challenge was organized by the IEEE Reliability Society and FEMTO-ST Institute to focus on the **estimation of the Remaining Useful Life (RUL) of bearings**. This challenge addressed a critical industrial problem since most failures of rotating machines are related to bearings, strongly affecting availability, security, and cost-effectiveness of mechanical systems in industries such as power and transportation.

## PRONOSTIA Experimental Platform

### Platform Description
The experiments were conducted on the PRONOSTIA platform at FEMTO-ST Institute (Besançon, France), an experimental platform dedicated to test and validate bearings fault detection, diagnostic, and prognostic approaches. The platform enables accelerated degradation of bearings under constant and/or variable operating conditions while gathering online health monitoring data.

### Key Platform Components

#### 1. Rotating Part
- **Motor**: Asynchronous motor with 250W power
- **Gearbox**: Allows motor to reach rated speed of 2830 rpm while maintaining secondary shaft speed less than 2000 rpm
- **Shaft Support**: Made of one piece, held by two pillow blocks with large bearings
- **Human Machine Interface**: Allows operators to set speed, rotation direction, and monitoring parameters

#### 2. Loading Part  
- **Pneumatic Jack**: Generates radial force up to bearing's maximum dynamic load (4000 N)
- **Force Amplification**: Uses lever arm to amplify force from pneumatic jack
- **Force Application**: Radial force applied indirectly on external ring of test bearing through clamping ring
- **Digital Control**: Force controlled by digital electro-pneumatic regulator

#### 3. Measurement Part
- **Operating Conditions Monitoring**: Radial force, rotation speed, and torque measured at 100 Hz
- **Vibration Sensors**: Two miniature accelerometers (DYTRAN 3035B) positioned at 90° to each other
- **Temperature Sensor**: RTD platinum PT100 probe placed near external bearing ring
- **Data Acquisition**: Acceleration sampled at 25.6 kHz, temperature at 0.1 Hz

## Experimental Conditions

### Test Bearings Specifications
- **Type**: Ball bearings with synthetic rubber seals
- **Dimensions**: 
  - Outside Race Diameter: 32 mm
  - Inside Diameter: 20 mm  
  - Thickness: 7 mm
- **Load Ratings**:
  - Static: 2470 N
  - Dynamic: 4000 N
- **Maximum Speed**: 13000 rpm
- **Rolling Elements**: 13 balls, 3.5 mm diameter

### Operating Conditions
Three different load conditions were tested:
1. **Condition 1**: 1800 rpm and 4000 N
2. **Condition 2**: 1650 rpm and 4200 N  
3. **Condition 3**: 1500 rpm and 5000 N

### Failure Criteria
- Experiments stopped when vibration amplitude exceeded 20g
- RUL defined as time to accelerometer exceeding 20g
- Tests stopped for security reasons to avoid damage propagation to test bed

## Dataset Organization

### Learning Dataset (Training Data)
The learning set consisted of 6 complete run-to-failure experiments:

| Operating Condition | Condition 1 (1800 rpm, 4000 N) | Condition 2 (1650 rpm, 4200 N) | Condition 3 (1500 rpm, 5000 N) |
|-------------------|--------------------------------|--------------------------------|--------------------------------|
| **Learning Set** | Bearing1_1, Bearing1_2 | Bearing2_1, Bearing2_2 | Bearing3_1, Bearing3_2 |

**Learning Dataset Characteristics:**
- **Bearing1_1**: 7h47m duration, 3269 files (vibration + temperature)
- **Bearing1_2**: 2h25m duration, 1015 files (vibration + temperature)
- **Bearing2_1**: 2h31m duration, 1062 files (vibration + temperature)
- **Bearing2_2**: 2h12m duration, 797 files (vibration only)
- **Bearing3_1**: 1h25m duration, 604 files (vibration + temperature)
- **Bearing3_2**: 4h32m duration, 1637 files (vibration only)

### Test Dataset (Prediction Target)
The test set included 11 bearings with truncated monitoring data:

| Bearing | Operating Condition | Duration | Files | Actual RUL | Signals |
|---------|-------------------|----------|-------|------------|---------|
| Bearing1_3 | 1800 rpm, 4000 N | 5h00m | 1802 | 5730 s | Vibration |
| Bearing1_4 | 1800 rpm, 4000 N | 3h09m | 1327 | 339 s | Vibration + Temperature |
| Bearing1_5 | 1800 rpm, 4000 N | 6h23m | 2685 | 1610 s | Vibration + Temperature |
| Bearing1_6 | 1800 rpm, 4000 N | 6h23m | 2685 | 1460 s | Vibration + Temperature |
| Bearing1_7 | 1800 rpm, 4000 N | 4h10m | 1752 | 7570 s | Vibration + Temperature |
| Bearing2_3 | 1650 rpm, 4200 N | 3h20m | 1202 | 7530 s | Vibration |
| Bearing2_4 | 1650 rpm, 4200 N | 1h41m | 713 | 1390 s | Vibration + Temperature |
| Bearing2_5 | 1650 rpm, 4200 N | 5h33m | 2337 | 3090 s | Vibration + Temperature |
| Bearing2_6 | 1650 rpm, 4200 N | 1h35m | 572 | 1290 s | Vibration |
| Bearing2_7 | 1650 rpm, 4200 N | 0h28m | 200 | 580 s | Vibration |
| Bearing3_3 | 1500 rpm, 5000 N | 0h58m | 410 | 820 s | Vibration + Temperature |

## Data Acquisition Specifications

### Vibration Data
- **Sampling Frequency**: 25.6 kHz
- **Recording Pattern**: 2560 samples (1/10 second) recorded every 10 seconds
- **Sensors**: Two DYTRAN 3035B accelerometers (±50g range, 100 mV/g)
- **Positioning**: 90° apart - one horizontal, one vertical
- **File Format**: ASCII files named "acc_xxxxx.csv"
- **Data Columns**: Hour, Minute, Second, Microsecond, Horizontal Acceleration, Vertical Acceleration

### Temperature Data  
- **Sampling Frequency**: 10 Hz
- **Recording Pattern**: 600 samples recorded every minute
- **Sensor**: RTD platinum PT100 (Class 1/3 DIN, -200°C to +600°C range)
- **File Format**: ASCII files named "temp_xxxxx.csv" 
- **Data Columns**: Hour, Minute, Second, 0.x second, RTD sensor reading

### Accelerometer Specifications (DYTRAN 3035B)
- **Range**: ±50g
- **Sensitivity**: 100 mV/g
- **Frequency Response**: 0.5 Hz to 10 kHz (±5%)
- **Resonant Frequency**: 45 kHz
- **Weight**: 2.5 grams
- **Temperature Range**: -60°F to +225°F

## Challenge Design and Scoring

### Scoring Methodology
Teams were evaluated using an asymmetric scoring function that penalized early and late predictions differently:

**Error Calculation:**
```
%Eri = 100 × (ActRULi - RUL_esti) / ActRULi
```

**Scoring Function:**
- **Early Predictions** (Eri ≤ 0): Ai = exp(-ln(0.5) × (Eri/5))
- **Late Predictions** (Eri > 0): Ai = exp(-ln(0.5) × (Eri/20))

**Final Score:** Average of all 11 experiment scores

### Key Challenge Characteristics
1. **Small Training Set**: Only 6 run-to-failure experiments for model development
2. **High Variability**: Bearing life varied dramatically (1h to 7h duration)  
3. **Multi-failure Modes**: Bearings exhibited various defect types (balls, inner/outer races, cage)
4. **Realistic Degradation**: Natural degradation without artificially induced defects
5. **Theoretical Model Limitations**: Standard bearing theory (L10, BPFI, BPFE) did not match experimental observations
6. **Cross-condition Robustness**: Algorithms needed to work across different operating conditions

## Challenge Winners

### Industrial Category
- **Winner**: A.L.D. Ltd. (Israel) - Sergey Porotsky
- **Runner-up**: GE Global Research (NY) - Tianyi Wang

### Academic Category  
- **Winner**: CALCE, University of Maryland - Arvind Sai Sarathi Vasan
- **Runner-up**: Jožef Stefan Institute (Slovenia) - Matej Gasperin

## Technical Notes
- Degradation patterns showed very different behaviors across bearings
- Frequency signature-based detection was difficult due to simultaneous multiple component degradation
- Platform designed for both constant and variable operating conditions (challenge used constant conditions)
- Data compression provided in 7z format
- FEMTO-ST team members excluded from competition for fairness