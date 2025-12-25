# FrequencyDomain 頻域分析模組

## 概述

`FrequencyDomain` 類別提供振動訊號的頻域分析功能，主要用於齒輪箱和軸承的故障診斷。該模組包含傅立葉轉換(FFT)、逆傅立葉轉換(IFFT)、低頻 FM0 計算以及高頻 FM0 計算等核心算法。

## 依賴模組

```python
- pandas: 資料處理
- numpy: 數值運算
- initialization.InitParameter: 初始化參數
- timedomain.TimeDomain: 時域分析
- harmonic_sildband_table.HarmonicSildband: 諧波與邊帶計算
```

## 類別初始化

```python
ip = ip()  # 全局初始化參數實例
```

## 核心方法

### 1. fft_process(amp, fs) - 傅立葉轉換

**功能**: 將時域振幅訊號轉換為頻域訊號

**輸入參數**:
- `amp`: 振幅數組 (時域訊號)
- `fs`: 取樣頻率 (Hz)

**輸出**:
- `fft_value`: 原始 FFT 複數值
- `abs_fft`: FFT 絕對值
- `freqs`: 所有頻率數組
- `abs_fft_n`: 標準化 FFT 絕對值 (用於計算)
- `abs_fft_segment2`: 單邊頻譜 FFT 值 (用於畫圖)
- `freqs_number_segment`: 單邊頻率數組

**算法原理**:

1. **FFT 計算**:
```python
fft_value = np.fft.fft(amp)  # 原始 FFT (複數)
```

2. **絕對值計算**:
```python
abs_fft = np.abs(fft_value)  # 取絕對值
```

3. **標準化**:
```python
abs_fft_n = (np.abs(fft_value / fft_value.size)) * 2
```

4. **單邊頻譜處理**:
   - 根據 FFT 長度奇偶性截取前半部分
   - 修正直流分量和奈奎斯特頻率之外的振幅 (×2)

### 2. ifft_process(fft_value) - 逆傅立葉轉換

**功能**: 將頻域訊號轉換回時域訊號

**輸入參數**:
- `fft_value`: FFT 複數值

**輸出**:
- `ifft_tsa`: DataFrame 包含 Degree 和 Acc 欄位
- `time_value`: 時間/角度數組

**算法原理**:

```python
ifft_value = np.fft.ifft(fft_value)  # 逆 FFT
time_value = np.arange(0, np.size(ifft_value)) * (360 / ifft_value.size)  # 轉換為角度
```

### 3. fft_fm0_si(amp, fs) - 低頻 FM0 與指標計算

**功能**: 計算低頻 FM0 值以及馬達齒輪和皮帶的同步指標

**輸入參數**:
- `amp`: 振幅數組
- `fs`: 取樣頻率

**輸出**:
- `fftoutput`: 完整 FFT 輸出 DataFrame
- `total_fft_mgs`: 馬達齒輪同步指標
- `total_fft_bi`: 皮帶同步指標
- `low_fm0`: 低頻 FM0 值

**算法流程**:

#### 步驟 1: FFT 處理
```python
fft_value, abs_fft, freqs, abs_fft_n, _, _ = FrequencyDomain.fft_process(amp, fs)
```

#### 步驟 2: 建立 FFT 輸出表
```python
fftoutput = pd.DataFrame({
    'freqs': np.round(freqs, 3),      # 頻率 (3位小數)
    'freqs1': np.round(freqs, 5),     # 頻率 (5位小數)
    'abs_fft': abs_fft,               # FFT 絕對值
    'abs_fft_n': abs_fft_n,           # 標準化 FFT
    'fft': fft_value                  # 原始 FFT 複數值
})
```

#### 步驟 3: 計算馬達齒輦主要頻率
```python
# 範圍: [mortor_gear - side_band_range, mortor_gear + side_band_range]
mask1 = fftoutput['freqs'] >= ip.mortor_gear - ip.side_band_range
mask2 = fftoutput['freqs'] <= ip.mortor_gear + ip.side_band_range
max_mortor_gear = fftoutput[mask1 & mask2]

# 取該範圍內振幅最大的頻率
max_mortor_gear = fftoutput[fftoutput['abs_fft'] == np.max(max_mortor_gear['abs_fft'])]
```

#### 步驟 4: 計算皮帶主要頻率
```python
# 範圍: [belt_si - side_band_range, belt_si + side_band_range]
mask3 = fftoutput['freqs'] >= ip.belt_si - ip.side_band_range
mask4 = fftoutput['freqs'] <= ip.belt_si + ip.side_band_range
max_belt_si = fftoutput[mask3 & mask4]

# 取該範圍內振幅最大的頻率
max_belt_si = fftoutput[fftoutput['abs_fft'] == np.max(max_belt_si['abs_fft'])]
```

#### 步驟 5: 計算諧波邊帶和
```python
low_filter_sum, _ = hs.Harmonic(fftoutput)
# 安全檢查: 若和為 0, 則設為 1.0 避免除以零
```

**詳細說明**:
`hs.Harmonic()` 方法執行低頻諧波分析:
- **目的**: 提取齒輪故障特徵
- **頻率範圍**: 1× - 10× BPFI (10個諧波,整數步長)
- **公差範圍**: ±1.0 Hz (使用 `ip.harmonic_gmf_range`)
- **算法詳解**: 詳見 [諧波與邊帶分析](#諧波與邊帶分析) 章節
- **物理意義**: 諧波振幅累加和代表齒輪故障能量

#### 步驟 6: 計算 FM0 值
```python
low_fm0 = td.peak(amp) / low_filter_sum
```

**FM0 物理意義**:
- **分子**: 時域峰峰值 = 振動總能量
- **分母**: 諧波能量和 = 齒輪故障特徵能量
- **比值**: 總能量相對於齒輪故障能量的比例
- **診斷**: FM0 越低表示齒輪故障越嚴重

**詳細說明**: 請參考 [FM0 指標詳解](#fm0-指標詳解) 章節

#### 步驟 7: 計算同步指標

**馬達齒輦同步指標 (MGS)**:
```python
# 左側範圍: [主頻 - harmonic_gmf_range, 主頻)
# 右側範圍: (主頻, 主頻 + harmonic_gmf_range]
fft_mgs1 = fftoutput[mask7 & mask8]  # 左側
fft_mgs2 = fftoutput[mask9 & mask10]  # 右側

# 平均值計算
len_mgs = len(fft_mgs1) + len(fft_mgs2)
total_fft_mgs = (np.sum(fft_mgs1['abs_fft_n']) + np.sum(fft_mgs2['abs_fft_n'])) / len_mgs
```

**皮帶同步指標 (BI)**:
```python
fft_bi1 = fftoutput[mask11 & mask12]  # 左側
fft_bi2 = fftoutput[mask13 & mask14]  # 右側

len_bi = len(fft_bi1) + len(fft_bi2)
total_fft_bi = (np.sum(fft_bi1['abs_fft_n']) + np.sum(fft_bi2['abs_fft_n'])) / len_bi
```

### 4. tsa_fft_fm0_slf(amp, fs, fft) - 高頻 FM0 與 TSA 分析

**功能**: 計算時域同步平均(TSA)後的高頻 FM0 值及邊帶指標

**輸入參數**:
- `amp`: TSA 後的振幅數組
- `fs`: 取樣頻率
- `fft`: 原始 FFT 輸出 (用於頻率校正)

**輸出**:
- `tsa_fftoutput`: TSA FFT 輸出 DataFrame
- `total_tsa_fft_mgs`: TSA 馬達齒輦邊帶指標
- `total_tsa_fft_bi`: TSA 皮帶邊帶指標
- `high_fm0`: 高頻 FM0 值

**算法流程**:

#### 步驟 1: TSA FFT 處理
```python
tsa_fft_value, tsa_abs_fft, tsa_freqs, tsa_abs_fft_n, _, _ = FrequencyDomain.fft_process(amp, fs)
```

#### 步驟 2: 頻率倍率校正

**原理**: 由於 TSA 重採樣會改變頻率刻度,需要計算校正倍率

```python
# 原始 FFT 最大值頻率
max1 = fftoutput[fftoutput['abs_fft'] == np.max(fftoutput['abs_fft'])]

# TSA FFT 最大值頻率
max2 = tsa_fftoutput[tsa_fftoutput['tsa_abs_fft'] == np.max(tsa_fftoutput['tsa_abs_fft'])]

# 計算頻率倍率
max_freqs = float(max3['freqs1'].values[0]) / float(max4['tsa_freqs1'].values[0])

# 應用倍率校正
tsa_fftoutput['multiply_freqs'] = np.round(tsa_freqs * max_freqs, 5)
```

#### 步驟 3: 馬達齒輦主要頻率 (使用校正後頻率)
```python
mask1 = tsa_fftoutput['multiply_freqs'] >= ip.mortor_gear - ip.side_band_range
mask2 = tsa_fftoutput['multiply_freqs'] <= ip.mortor_gear + ip.side_band_range
max_mortor_gear = tsa_fftoutput[mask1 & mask2]
```

#### 步驟 4: 皮帶主要頻率
```python
mask3 = tsa_fftoutput['multiply_freqs'] >= ip.belt_si - ip.side_band_range
mask4 = tsa_fftoutput['multiply_freqs'] <= ip.belt_si + ip.side_band_range
max_belt_si = tsa_fftoutput[mask3 & mask4]
```

#### 步驟 5: 計算邊帶和
```python
high_filter_sum, _ = hs.Sildband(tsa_fftoutput)
```

**詳細說明**:
`hs.Sildband()` 方法執行高頻邊帶分析:
- **目的**: 提取軸承故障特徵
- **頻率範圍**: 2× - 16× BPFI (15個邊帶,整數步長)
- **特殊邊帶**: 11.71× (特定調製效應)
- **公差範圍**: ±5.0 Hz (使用 `ip.high_hamonic_range`)
- **算法詳解**: 詳見 [諧波與邊帶分析](#諧波與邊帶分析) 章節
- **物理意義**: 邊帶振幅累加和代表軸承故障能量

#### 步驟 6: 計算高頻 FM0
```python
high_fm0 = td.peak(amp) / high_filter_sum
```

**FM0 物理意義**:
- **分子**: 時域峰峰值 = 振動總能量
- **分母**: 邊帶能量和 = 軸承故障特徵能量
- **比值**: 總能量相對於軸承故障能量的比例
- **診斷**: FM0 越低表示軸承故障越嚴重

**詳細說明**: 請參考 [FM0 指標詳解](#fm0-指標詳解) 章節

#### 步驟 7: 計算邊帶指標 (使用 RMS 標準化)

**馬達齒輦邊帶**:
```python
# 使用 mortor_gear_range 定義範圍
tsa_fft_mgs1 = tsa_fftoutput[mask7 & mask8]  # 左側
tsa_fft_mgs2 = tsa_fftoutput[mask9 & mask10]  # 右側

# RMS 標準化
rms_val = td.rms(amp)
total_tsa_fft_mgs = (np.sum(tsa_fft_mgs1['tsa_abs_fft_n']) + np.sum(tsa_fft_mgs2['tsa_abs_fft_n'])) / rms_val
```

**皮帶邊帶**:
```python
# 使用 belt_si_range 定義範圍
tsa_fft_bi1 = tsa_fftoutput[mask11 & mask12]  # 左側
tsa_fft_bi2 = tsa_fftoutput[mask13 & mask14]  # 右側

total_tsa_fft_bi = (np.sum(tsa_fft_bi1['tsa_abs_fft_n']) + np.sum(tsa_fft_bi2['tsa_abs_fft_n'])) / rms_val
```

## 諧波與邊帶分析

本節詳細說明 `harmonic_sildband_table.py` 模組中的兩個核心方法: `Harmonic()` 和 `Sildband()`。這兩個方法是頻域分析中提取故障特徵的關鍵算法。

### Harmonic() 方法 - 低頻諧波分析

**功能**:
計算常規 FFT 數據中馬達頻率 (BPFI) 周圍的諧波能量和,用於檢測齒輪故障特徵。

**參數**:
- `fft`: DataFrame,包含 FFT 分析結果
  - `freqs`: 頻率值 (3位小數)
  - `freqs1`: 頻率值 (5位小數)
  - `abs_fft`: FFT 絕對值
  - `abs_fft_n`: 標準化 FFT 絕對值
  - `fft`: 原始 FFT 複數值

**返回值**:
- `harmonic_sum`: 諧波能量總和 (float)
- `max_harmonic_freq_combine`: 每個諧波的頻率和振幅資訊 (DataFrame)

**算法詳解**:

1. **定位基礎頻率**:
```python
# 在 BPFI ± 2.0 Hz 範圍內搜索最大振幅
# BPFI = 233.43 Hz (工作條件 1)
# 搜索範圍: [231.43, 235.43] Hz
```

2. **計算諧波倍數** (10個諧波,整數步長):
```
倍數 | 頻率 (Hz)    | 搜索範圍 (±1.0 Hz)
-----|-------------|-------------------
1x   | 233.43     | [232.43, 234.43]
2x   | 466.86     | [465.86, 467.86]
3x   | 700.29     | [699.29, 701.29]
4x   | 933.72     | [932.72, 934.72]
5x   | 1167.15    | [1166.15, 1168.15]
6x   | 1400.58    | [1399.58, 1401.58]
7x   | 1634.01    | [1633.01, 1635.01]
8x   | 1867.44    | [1866.44, 1868.44]
9x   | 2100.87    | [2099.87, 2101.87]
10x  | 2334.30    | [2333.30, 2335.30]
```

3. **峰值檢測**:
對每個諧波倍數,在 ±1.0 Hz 公差範圍內搜索該頻帶的最大振幅值。

4. **能量累加**:
```python
harmonic_sum = Σ(各諧波的最大振幅)
```

**應用場景**:
- 齒輪故障診斷 (齒面磨損、點蝕)
- 低頻段故障特徵提取
- 與 `fft_fm0_si()` 方法配合使用

### Sildband() 方法 - 高頻邊帶分析

**功能**:
計算 TSA FFT 數據中馬達頻率周圍的邊帶能量和,用於檢測軸承故障特徵。邊帶是調製效應產生的頻率成分,通常出現在載波頻率周圍。

**參數**:
- `tsa_fft`: DataFrame,包含 TSA FFT 分析結果
  - `tsa_freqs`: TSA 頻率值 (3位小數)
  - `tsa_freqs1`: TSA 頻率值 (5位小數)
  - `multiply_freqs`: 頻率校正後的乘積頻率
  - `tsa_abs_fft`: TSA FFT 絕對值
  - `tsa_abs_fft_n`: 標準化 TSA FFT 絕對值
  - `tsa_fft`: 原始 TSA FFT 複數值

**返回值**:
- `filter_sum`: 邊帶能量總和 (float)
- `max_filter_freq_combine`: 每個邊帶的頻率和振幅資訊 (DataFrame)

**算法詳解**:

1. **定位基礎頻率**:
```python
# 在 BPFI ± 2.0 Hz 範圍內搜索最大振幅
# BPFI = 233.43 Hz (工作條件 1)
# 搜索範圍: [231.43, 235.43] Hz
```

2. **計算邊帶倍數** (15個邊帶,整數步長 + 1個特殊邊帶):
```
倍數範圍 | 起始頻率 (Hz) | 結束頻率 (Hz) | 公差
---------|--------------|--------------|--------
2x - 16x | 466.86 | 3734.88 | ±5.0 Hz
步長: 1 | 特殊: 11.71x
```

部分邊帶示例:
```
倍數 | 頻率 (Hz)    | 搜索範圍 (±5.0 Hz)
-----|-------------|--------------------
2x   | 466.86     | [461.86, 471.86]
3x   | 700.29     | [695.29, 705.29]
4x   | 933.72     | [928.72, 938.72]
...
11x  | 2567.73    | [2562.73, 2572.73]
11.71x | 2733.45   | [2728.45, 2738.45] (特殊邊帶)
12x  | 2801.16    | [2796.16, 2806.16]
...
16x  | 3734.88    | [3729.88, 3739.88]
```

3. **峰值檢測**:
對每個邊帶倍數,在 ±5.0 Hz 公差範圍內搜索該頻帶的最大振幅值。

4. **能量累加**:
```python
filter_sum = Σ(各邊帶的最大振幅)
```

**為什麼包含 11.71x 邊帶**:
這是一個特殊的邊帶頻率,對應特定的調製效應,可能與軸承的幾何結構或故障模式相關。

**應用場景**:
- 軸承故障診斷 (內圈、外圈、滾珠故障)
- 高頻段故障特徵提取
- 與 `tsa_fft_fm0_slf()` 方法配合使用

### Harmonic() vs Sildband() 對比

| 特性 | Harmonic() | Sildband() |
|------|-----------|-----------|
| **輸入數據** | 常規 FFT | TSA FFT |
| **頻率範圍** | 1× - 10× BPFI | 2× - 16× BPFI |
| **倍數數量** | 10 個 (整數步長) | 15+1 個 (整數步長+特殊) |
| **公差範圍** | ±1.0 Hz | ±5.0 Hz |
| **檢測目標** | 齒輪故障特徵 | 軸承故障特徵 |
| **能量特徵** | 諧波能量 | 邊帶能量 |
| **物理意義** | 齒輪嚙合頻率的倍頻 | 調製產生的邊頻成分 |

### 諧波與邊帶的物理解釋

**諧波 (Harmonics)**:
- 定義: 基礎頻率的整數倍或分數倍
- 產生原因: 齒輪嚙合的非線性、齒面故障、幾何偏差
- 特徵: 能量集中在特定頻率倍數點
- 故障指示: 諧波振幅增加表示齒輪故障惡化

**邊帶 (Sidebands)**:
- 定義: 出現在載波頻率兩側的頻率成分
- 產生原因: 振幅調製 (AM) 或頻率調製 (FM)
- 特徵: 對稱或非對稱分布在主頻兩側
- 故障指示: 邊帶數量和振幅增加表示軸承或調製故障

**在 PHM 2012 數據集中的應用**:
- 低頻諧波 (Harmonic) 反映齒輪箱健康狀態 (1×-10× BPFI = 233-2334 Hz)
- 高頻邊帶 (Sildband) 反映軸承損傷程度 (2×-16× BPFI = 467-3735 Hz)
- 兩者結合提供完整的機械系統故障診斷

## FM0 指標詳解

FM0 (Fault Metric 0) 是本頻域分析模組的核心指標,用於量化齒輪和軸承的故障嚴重程度。

### FM0 定義

```python
# 低頻 FM0 (使用諧波能量)
low_fm0 = peak(amp) / harmonic_sum

# 高頻 FM0 (使用邊帶能量)
high_fm0 = peak(amp) / sideband_sum
```

其中:
- `peak(amp)`: 時域訊號的峰峰值 = max(amp) - min(amp)
- `harmonic_sum`: Harmonic() 方法返回的諧波能量和
- `sideband_sum`: Sildband() 方法返回的邊帶能量和

### 物理意義

FM0 是一個比值指標,其物理含義如下:

**分子 - 時域總能量**:
- 代表振動訊號的整體強度
- 反映所有振動源(齒輪、軸承、結構等)的總和
- 對故障敏感但無法區分故障類型

**分母 - 特定故障頻率能量**:
- 低頻: 諧波能量 (反映齒輪故障特徵)
- 高頻: 邊帶能量 (反映軸承故障特徵)
- 代表特定故障模式的能量集中度

**比值 - 故障特徵強度**:
- FM0 越低: 故障特徵能量相對總能量的比例越高
- FM0 越高: 故障特徵能量相對分散或總能量過高

### 故障診斷意義

#### FM0 下降 (故障指標)

**原因分析**:
1. **早期局部故障**:
   - 故障特徵頻率能量明顯
   - 總能量尚未顯著上升
   - FM0 下降是早期預警信號

2. **特定故障惡化**:
   - 單一故障模式主導
   - 能量集中在特定頻率帶
   - 齒輪或軸承故障明顯

3. **典型表現**:
   - 低頻 FM0 下降 → 齒輪故障
   - 高頻 FM0 下降 → 軸承故障

**診斷準則**:
```
正常狀態: FM0 ≈ 基準值 (需根據設備建立)
早期故障: FM0 下降 10-20%
嚴重故障: FM0 下降 >30%
危急狀態: FM0 下降 >50%
```

#### FM0 上升 (需警惕)

**原因分析**:
1. **故障擴散**:
   - 從局部故障擴展到全域
   - 多個部件同時故障
   - 特徵頻率能量分散

2. **能量背景上升**:
   - 總振動能量急劇增加
   - 故障特徵相對比例下降
   - 可能伴隨結構共振

3. **診斷挑戰**:
   - FM0 上升不代表故障好轉
   - 需配合其他指標 (如 RMS) 判斷
   - 可能表示故障惡化到晚期

### FM0 與其他指標的聯合應用

#### FM0 + RMS (均方根值)

```
場景 1: RMS 上升 + FM0 下降
→ 嚴重局部故障
→ 特徵: 總能量高,故障能量集中
→ 例子: 齒輪斷齒、軸承剝落

場景 2: RMS 上升 + FM0 上升
→ 多故障或全域故障
→ 特徵: 總能量高,能量分散
→ 例子: 多部件磨損、結構鬆動

場景 3: RMS 正常 + FM0 下降
→ 早期局部故障
→ 特徵: 總能量正常,故障能量集中
→ 例子: 早期齒面點蝕、輕微軸承損傷
```

#### FM0 + 峰值因數 (Crest Factor, CF)

```
場景 1: CF 上升 + FM0 下降
→ 衝擊性故障
→ 特徵: 尖銳衝擊,能量集中
→ 例子: 軸承滾珠通過、齒輪崩裂

場景 2: CF 正常 + FM0 下降
→ 磨損性故障
→ 特徵: 平穩磨損,能量集中
→ 例子: 齒面均勻磨損、軸承磨損
```

#### 低頻 FM0 vs 高頻 FM0

```
場景 1: 低頻 FM0 下降, 高頻 FM0 正常
→ 齒輪故障,軸承正常
→ 重點檢查: 齒輪嚙合、齒面狀況

場景 2: 高頻 FM0 下降, 低頻 FM0 正常
→ 軸承故障,齒輪正常
→ 重點檢查: 軸承內外圈、滾珠

場景 3: 兩者 FM0 都下降
→ 齒輪和軸承都有問題
→ 重點檢查: 全面檢修

場景 4: 兩者 FM0 都正常
→ 可能是其他部件故障
→ 重點檢查: 聯軸器、基座、對中
```

### FM0 的優勢與局限

**優勢**:
1. **綜合指標**: 結合時域和頻域特徵
2. **敏感度高**: 對早期故障相對敏感
3. **指向性明確**: 低頻/高頻分別對應齒輪/軸承
4. **計算簡單**: 易於實時監測

**局限**:
1. **相對值**: 需要建立基準線
2. **非絕對**: 不同設備無法直接比較
3. **依賴參數**: 對頻率參數設定敏感
4. **需要配合**: 單獨使用可能誤判

### 實際應用建議

1. **建立基準**:
   - 在設備正常狀態下測量 FM0
   - 記錄不同工況下的基準值
   - 定期更新基準以反映設備老化

2. **設定閾值**:
   - 預警閾值: 基準值的 80-90%
   - 報警閾值: 基準值的 70%
   - 危急閥值: 基準值的 50%

3. **趨勢分析**:
   - 追蹤 FM0 隨時間的變化
   - 注意突然下降或持續下降趨勢
   - 結合維護記錄分析

4. **多維度診斷**:
   - 永遠配合其他指標使用
   - 考慮設備運行歷史
   - 結合現場檢查驗證

## 特徵計算完整實例

本節通過一個完整的計算範例,演示如何使用 `FrequencyDomain` 模組進行頻域特徵提取和故障診斷。

### 實例場景

假設我們要分析一個齒輪箱的振動訊號,該齒輪箱在**工作條件 1 (1800 RPM)** 下運行,懷疑可能存在齒輪磨損或軸承損傷。

### 步驟 1: 初始化參數

```python
# 從 initialization.py 獲取參數
# 工作條件 1 (1800 RPM)

# 採樣參數
fs = 25600              # 原始取樣頻率 (Hz)
tsa_fs = 180            # TSA 重採樣頻率 (Hz)

# 軸承特徵頻率
mortor_gear = 30.0      # 軸頻率 Fr (Hz) = 1800 RPM / 60
belt_si = 156.59        # BPFO 外圈滾珠通過頻率 (Hz)
mortor = 233.43         # BPFI 內圈滾珠通過頻率 (Hz)
high_hamonic = 466.86   # BPFI × 2 (Hz)

# 頻率搜索範圍
side_band_range = 2.0           # 主頻搜索公差 (Hz)
harmonic_gmf_range = 1.0        # 諧波公差 (Hz)
mortor_gear_range = 2.0         # 馬達齒輪範圍 (Hz)
belt_si_range = 2.0             # 皮帶範圍 (Hz)
high_hamonic_range = 5.0        # 邊帶公差 (Hz)
```

### 步驟 2: FFT 處理

```python
# 假設已載入原始振動訊號
import numpy as np
from backend.frequencydomain import FrequencyDomain

# 原始訊號
amp = np.array([振動數據...])  # 假設長度 25600 點 (1秒數據)

# 計算 FFT
fft_value, abs_fft, freqs, abs_fft_n, _, _ = FrequencyDomain.fft_process(amp, fs)

# FFT 結果示例:
# fft_value: 複數數組,頻域表示
# abs_fft: 振幅譜
# freqs: 頻率數組 (0 - 12800 Hz)
# abs_fft_n: 標準化振幅譜 (用於計算)
```

### 步驟 3: 低頻諧波分析 (Harmonic() 方法)

```python
from backend.harmonic_sildband_table import HarmonicSildband as hs

# 建立 FFT 輸出表
import pandas as pd
fftoutput = pd.DataFrame({
    'freqs': np.round(freqs, 3),
    'freqs1': np.round(freqs, 5),
    'abs_fft': abs_fft,
    'abs_fft_n': abs_fft_n,
    'fft': fft_value
})

# 執行諧波分析
low_filter_sum, harmonic_details = hs.Harmonic(fftoutput)

# Harmonic() 方法內部執行過程:
#
# 1. 找到 BPFI 主頻 (233.43 Hz)
#    搜索範圍: [231.43, 235.43] Hz (使用 ip.side_band_range = 2.0 Hz)
#    假設找到峰值: 233.42 Hz, 振幅 = 12.5 m/s²
#
# 2. 計算並搜索 10 個諧波倍數 (整數步長):
#
#    倍數  |  目標頻率  |  搜索範圍 (±1.0 Hz)  |  找到頻率  |  最大振幅
#   -------|-----------|---------------------|-----------|-----------
#    1x    |  233.43   |  [232.43, 234.43]   |  233.42   |  12.5
#    2x    |  466.86   |  [465.86, 467.86]   |  466.85   |   8.3
#    3x    |  700.29   |  [699.29, 701.29]   |  700.28   |   6.7
#    4x    |  933.72   |  [932.72, 934.72]   |  933.71   |   5.1
#    5x    | 1167.15   |  [1166.15, 1168.15]  | 1167.16   |   4.2
#    6x    | 1400.58   |  [1399.58, 1401.58]  | 1400.57   |   3.5
#    7x    | 1634.01   |  [1633.01, 1635.01]  | 1634.02   |   2.9
#    8x    | 1867.44   |  [1866.44, 1868.44]  | 1867.43   |   2.4
#    9x    | 2100.87   |  [2099.87, 2101.87]  | 2100.88   |   2.0
#    10x   | 2334.30   |  [2333.30, 2335.30]  | 2334.31   |   1.7
#
# 3. 累加所有諧波振幅:
low_filter_sum = 12.5 + 8.3 + 6.7 + 5.1 + 4.2 + 3.5 + 2.9 + 2.4 + 2.0 + 1.7
                = 49.3 (m/s²)

# 結果:
print(f"諧波能量和: {low_filter_sum:.2f} m/s²")
```

### 步驟 4: 計算低頻 FM0

```python
from backend.timedomain import TimeDomain as td

# 計算時域峰值
peak_value = td.peak(amp)  # = max(amp) - min(amp)
# 假設: peak_value = 25.8 m/s²

# 計算低頻 FM0
low_fm0 = peak_value / low_filter_sum
       = 25.8 / 49.3
       = 0.523

print(f"時域峰值: {peak_value:.2f} m/s²")
print(f"低頻 FM0: {low_fm0:.3f}")
```

### 步驟 5: 計算同步指標

```python
# 馬達齒輦同步指標 (MGS)
# 主頻: 30.0 Hz
# 搜索範圍: [28.0, 30.0) 和 (30.0, 32.0]
#    (使用 mortor_gear_range = 2.0 Hz)

mask7 = fftoutput['freqs'] >= 30.0 - 2.0  # >= 28.0
mask8 = fftoutput['freqs'] < 30.0         # < 30.0
mask9 = fftoutput['freqs'] > 30.0         # > 30.0
mask10 = fftoutput['freqs'] <= 30.0 + 2.0 # <= 32.0

fft_mgs1 = fftoutput[mask7 & mask8]  # 左側: [28.0, 30.0)
fft_mgs2 = fftoutput[mask9 & mask10] # 右側: (30.0, 32.0]

# 假設找到:
# fft_mgs1: 3 個頻率點, 總能量 = 6.8 m/s²
# fft_mgs2: 3 個頻率點, 總能量 = 7.3 m/s²

len_mgs = len(fft_mgs1) + len(fft_mgs2)  # = 6
total_fft_mgs = (6.8 + 7.3) / 6
              = 2.35 m/s²

# 皮帶同步指標 (BI)
# 主頻: 156.59 Hz
# 搜索範圍: [154.59, 156.59) 和 (156.59, 158.59]
#    (使用 belt_si_range = 2.0 Hz)

mask11 = fftoutput['freqs'] >= 156.59 - 2.0  # >= 154.59
mask12 = fftoutput['freqs'] < 156.59         # < 156.59
mask13 = fftoutput['freqs'] > 156.59         # > 156.59
mask14 = fftoutput['freqs'] <= 156.59 + 2.0  # <= 158.59

fft_bi1 = fftoutput[mask11 & mask12]  # 左側
fft_bi2 = fftoutput[mask13 & mask14]  # 右側

# 假設找到:
# fft_bi1: 4 個頻率點, 總能量 = 6.2 m/s²
# fft_bi2: 4 個頻率點, 總能量 = 6.8 m/s²

len_bi = len(fft_bi1) + len(fft_bi2)  # = 8
total_fft_bi = (6.2 + 6.8) / 8
             = 1.62 m/s²

print(f"馬達齒輦同步指標 (MGS): {total_fft_mgs:.2f} m/s²")
print(f"皮帶同步指標 (BI): {total_fft_bi:.2f} m/s²")
```

### 步驟 6: TSA 處理後的高頻分析

```python
# 假設已完成 TSA 重採樣
# tsa_amp = TSA 處理後的振幅數組 (重採樣到 180 Hz)

# 1. TSA FFT 處理
tsa_fft_value, tsa_abs_fft, tsa_freqs, tsa_abs_fft_n, _, _ = \
    FrequencyDomain.fft_process(tsa_amp, tsa_fs)

# 2. 頻率校正 (重要!)
# TSA 重採樣改變了頻率刻度,需要計算校正倍率

# 原始 FFT 最大值頻率
max1 = fftoutput[fftoutput['abs_fft'] == np.max(fftoutput['abs_fft'])]
# 假設: max1_freq = 233.42 Hz

# TSA FFT 最大值頻率
max2 = tsa_fftoutput[tsa_fftoutput['tsa_abs_fft'] == np.max(tsa_fftoutput['tsa_abs_fft'])]
# 假設: max2_freq = 1.64 Hz

# 計算頻率倍率
max_freqs = 233.42 / 1.64  # = 142.3

# 應用倍率校正
tsa_fftoutput['multiply_freqs'] = tsa_freqs * max_freqs

# 3. 執行邊帶分析 (Sildband() 方法)
high_filter_sum, sideband_details = hs.Sildband(tsa_fftoutput)

# Sildband() 方法內部執行過程:
#
# 1. 找到 BPFI 主頻 (校正後)
#    搜索範圍: [231.43, 235.43] Hz (使用 ip.side_band_range = 2.0 Hz)
#    假設找到: 233.45 Hz, 振幅 = 10.2 m/s²
#
# 2. 計算並搜索 15+1 個邊帶倍數 (整數步長 + 1個特殊):
#
#    倍數   |  目標頻率  |  搜索範圍 (±5.0 Hz)  |  找到頻率  |  最大振幅
#   --------|-----------|---------------------|-----------|-----------
#    2x     |  466.86   |  [461.86, 471.86]   |  466.88   |   3.8
#    3x     |  700.29   |  [695.29, 705.29]   |  700.27   |   3.2
#    4x     |  933.72   |  [928.72, 938.72]   |  933.70   |   2.7
#    5x     | 1167.15   |  [1162.15, 1172.15]  | 1167.18   |   2.3
#    6x     | 1400.58   |  [1395.58, 1405.58]  | 1400.55   |   2.0
#    7x     | 1634.01   |  [1629.01, 1639.01]  | 1634.03   |   1.7
#    8x     | 1867.44   |  [1862.44, 1872.44]  | 1867.42   |   1.5
#    9x     | 2100.87   |  [2095.87, 2105.87]  | 2100.89   |   1.3
#    10x    | 2334.30   |  [2329.30, 2339.30]  | 2334.28   |   1.1
#    11x    | 2567.73   |  [2562.73, 2572.73]  | 2567.75   |   1.0
#    11.71x | 2733.45   |  [2728.45, 2738.45]  | 2733.50   |   0.8 (特殊)
#    12x    | 2801.16   |  [2796.16, 2806.16]  | 2801.14   |   0.9
#    13x    | 3034.59   |  [3029.59, 3039.59]  | 3034.61   |   0.7
#    14x    | 3268.02   |  [3263.02, 3273.02]  | 3268.00   |   0.6
#    15x    | 3501.45   |  [3496.45, 3506.45]  | 3501.47   |   0.5
#    16x    | 3734.88   |  [3729.88, 3739.88]  | 3734.90   |   0.4
#
# 3. 累加所有邊帶振幅:
high_filter_sum = 3.8 + 3.2 + 2.7 + 2.3 + 2.0 + 1.7 + 1.5 + 1.3 + 1.1 + 1.0 + 0.8 + 0.9 + 0.7 + 0.6 + 0.5 + 0.4
                 = 24.5 m/s²

# 4. 計算高頻 FM0
high_fm0 = td.peak(tsa_amp) / high_filter_sum
         = 25.8 / 24.5
         = 1.053

print(f"邊帶能量和: {high_filter_sum:.2f} m/s²")
print(f"高頻 FM0: {high_fm0:.3f}")
```

### 步驟 7: 完整結果匯總與解讀

```python
# 所有特徵匯總
results = {
    '時域峰值': 25.8,           # m/s²
    '低頻 FM0': 0.523,          # 諧波 FM0
    '高頻 FM0': 1.053,          # 邊帶 FM0
    'MGS': 2.35,               # 馬達齒輦同步指標 (m/s²)
    'BI': 1.62                 # 皮帶同步指標 (m/s²)
}

print("=== 診斷結果 ===")
print(f"1. 低頻 FM0 = {results['低頻 FM0']:.3f}")
print(f"   解讀: 低頻 FM0 中等,諧波能量中等")
print(f"   → 齒輪可能存在輕微故障")
print()
print(f"2. 高頻 FM0 = {results['高頻 FM0']:.3f}")
print(f"   解讀: 高頻 FM0 較高,邊帶能量較低")
print(f"   → 軸承狀況相對良好")
print()
print(f"3. 馬達齒輦同步指標 (MGS) = {results['MGS']:.2f} m/s²")
print(f"   解讀: 指標正常範圍")
print(f"   → 馬達齒輦嚙合狀況良好")
print()
print(f"4. 皮帶同步指標 (BI) = {results['BI']:.2f} m/s²")
print(f"   解讀: 指標正常範圍")
print(f"   → 皮帶/軸承外圈狀況良好")
print()
print("=== 總體診斷 ===")
print("主要發現: 齒輪可能存在輕微局部故障,軸承狀況良好")
print("建議行動:")
print("  1. 監測齒輪齒面狀況變化趨勢")
print("  2. 繼續監測軸承狀態")
print("  3. 按照正常維護計劃檢查")
```

### 對比不同故障情況的 FM0

| 故障類型 | 低頻 FM0 | 高頻 FM0 | 診斷結論 |
|---------|---------|---------|---------|
| **正常狀態** | 0.50-0.60 | 0.35-0.45 | 無明顯故障 |
| **齒輪早期故障** | 0.40-0.49 | 0.35-0.45 | 齒面輕微磨損/點蝕 |
| **齒輪嚴重故障** | < 0.40 | 0.35-0.45 | 齒面嚴重磨損/斷齒 |
| **軸承早期故障** | 0.50-0.60 | 0.25-0.34 | 滾珠/內圈輕微損傷 |
| **軸承嚴重故障** | 0.50-0.60 | < 0.25 | 滾珠/內圈嚴重損傷 |
| **齒輪+軸承故障** | < 0.40 | < 0.25 | 多部件故障,需全面檢修 |
| **能量分散故障** | > 0.60 | > 0.45 | 可能結構鬆動/對中不良 |

*註: 實際閾值需根據具體設備和工況建立*

### 實例總結

本實例展示了完整的頻域分析流程:

1. **參數初始化**: 根據工作條件設定頻率參數
2. **FFT 處理**: 將時域訊號轉換為頻域
3. **諧波分析**: 使用 Harmonic() 方法提取低頻特徵
4. **邊帶分析**: 使用 Sildband() 方法提取高頻特徵
5. **FM0 計算**: 結合時域和頻域特徵計算故障指標
6. **綜合診斷**: 根據多個指標評估設備健康狀態

通過這個流程,我們可以有效地診斷齒輪箱和軸承的故障狀態,為預測性維護提供科學依據。

## 關鍵參數

本節列出 `FrequencyDomain` 模組使用的所有關鍵參數,包括實際數值和使用場景。這些參數來自 `initialization.py` 模組的 `InitParameter` 類別。

### 完整參數表格

#### 採樣參數

| 參數名稱 | 實際數值 | 單位 | 說明 | 使用場景 |
|---------|---------|------|------|---------|
| `fs` | 25600 | Hz | 原始取樣頻率 | FFT 計算、頻譜分析 |
| `tsa_fs` | 180 | Hz | TSA 重採樣頻率 | 時域同步平均處理 |
| `ts` | 3.91e-5 | s | 原始取樣週期 (1/fs) | 時域計算、時間軸生成 |
| `tsa_ts` | 0.00556 | s | TSA 取樣週期 (1/tsa_fs) | TSA 時域分析 |

**說明**:
- 原始訊號以 25.6 kHz 高頻取樣,捕捉完整的振動訊號
- TSA 重採樣到 180 Hz,用於同步平均和邊帶分析
- TSA 重採樣會改變頻率刻度,需要頻率校正(見 `tsa_fft_fm0_slf()` 方法)

#### 軸承特徵頻率 (工作條件 1 - 1800 RPM)

| 參數名稱 | 實際數值 | 單位 | 說明 | 使用場景 |
|---------|---------|------|------|---------|
| `mortor_gear` | 30.0 | Hz | 軸頻率 (Fr = RPM/60) | 低頻/高頻分析的主頻檢測 |
| `belt_si` | 156.59 | Hz | BPFO - 外圈滾珠通過頻率 | 皮帶/軸承外圈故障檢測 |
| `mortor` | 233.43 | Hz | BPFI - 內圈滾珠通過頻率 | 諧波/邊帶計算的基礎頻率 |
| `high_hamonic` | 466.86 | Hz | BPFI × 2 (二次諧波) | 高頻分析、諧波檢測 |

**頻率計算公式**:
```
軸頻率 (Fr) = 轉速 (RPM) / 60

BPFO (外圈) = (n/2) × Fr × [1 - (d/D) × cos(α)]
BPFI (內圈) = (n/2) × Fr × [1 + (d/D) × cos(α)]

其中:
n = 滾珠數量
d = 滾珠直徑
D = 軸承節徑
α = 接觸角
```

**PHM 2012 數據集軸承參數** (條件 1):
- 轉速: 1800 RPM
- 滾珠數量: 8 個
- 軸承幾何: 特定設計參數

#### 頻率搜索範圍 (公差)

| 參數名稱 | 實際數值 | 單位 | 說明 | 使用場景 |
|---------|---------|------|------|---------|
| `side_band_range` | 2.0 | Hz | 主頻搜索公差 | 定位 BPFI 主頻峰值 |
| `harmonic_gmf_range` | 1.0 | Hz | 低頻諧波公差 | Harmonic() 方法諧波檢測 |
| `mortor_gear_range` | 2.0 | Hz | 馬達齒輦頻率範圍 | TSA MGS 指標計算 |
| `belt_si_range` | 2.0 | Hz | 皮帶頻率範圍 | TSA BI 指標計算 |
| `morotr_range` | 3.0 | Hz | BPFI 頻率範圍 | (備用,當前未使用) |
| `high_hamonic_range` | 5.0 | Hz | 高頻邊帶公差 | Sildband() 方法邊帶檢測 |

**公差設計原理**:
- **低頻諧波 (±1.0 Hz)**: 精確檢測,因諧波頻率間隔較小
- **高頻邊帶 (±5.0 Hz)**: 寬鬆檢測,因高頻頻率漂移較大
- **主頻搜索 (±2.0 Hz)**: 平衡精度和穩定性

#### STFT 參數 (短時傅立葉轉換)

| 參數名稱 | 實際數值 | 單位 | 說明 | 使用場景 |
|---------|---------|------|------|---------|
| `stft_hann_nperseg` | 128 | - | Hann 窗段長度 | 時頻分析、Hann 窗 |
| `stft_flattop_nperseg` | 256 | - | Flat-top 窗段長度 | 時頻分析、Flat-top 窗 |

**說明**:
- Hann 窗: 適合一般時頻分析,頻率洩漏小
- Flat-top 窗: 適合精確振幅測量,頻率解析度較高
- 段長決定時頻解析度的平衡

### 頻率倍數範圍表

| 分析類型 | 使用方法 | 倍數範圍 | 步長 | 公差 | 檢測目標 | 應用場景 |
|---------|---------|---------|------|------|---------|---------|
| **低頻諧波** | Harmonic() | 1× - 10× BPFI | 1 (整數) | ±1.0 Hz | 齒輪故障特徵 | 齒面磨損、點蝕檢測 |
| **高頻邊帶** | Sildband() | 2× - 16× BPFI | 1 (整數) | ±5.0 Hz | 軸承故障特徵 | 內圈、外圈、滾珠故障 |
| **特殊邊帶** | Sildband() | 11.71× | - | ±5.0 Hz | 特定調製效應 | 特殊故障模式檢測 |

**諧波/邊帶選擇依據**:
1. **1× 開始**: 從基頻開始捕捉主要諧波成分
2. **整數步長**: 簡化計算,提高效率 (與原 MFP 的 0.25 步長不同)
3. **2× 分界**: 區分低頻諧波和高頻邊帶
4. **16× 結束**: 覆蓋主要邊帶範圍至 3735 Hz,避免高頻噪聲
5. **11.71× 特殊邊帶**: 捕捉特定調製效應 (可能與軸承幾何相關)

### 工作條件參數表

PHM 2012 數據集包含三個工作條件,對應不同轉速:

| 條件 | 轉速 (RPM) | 軸頻率 (Hz) | BPFO (Hz) | BPFI (Hz) | 應用場景 |
|------|-----------|------------|-----------|-----------|---------|
| **條件 1** | 1800 | 30.0 | 156.59 | 233.43 | 額定運行、主要分析 |
| **條件 2** | 1650 | 27.5 | 143.54 | 213.98 | 降速運行 |
| **條件 3** | 1500 | 25.0 | 130.49 | 194.53 | 低速運行 |

**頻率轉換公式**:
```
軸頻率 = 轉速 / 60
BPFO_條件X = BPFO_條件1 × (轉速X / 轉速1)
BPFI_條件X = BPFI_條件1 × (轉速X / 轉速1)
```

**切換工作條件**:
```python
from backend.initialization import InitParameter as ip

ip_instance = ip()
ip_instance.set_working_condition(1)  # 切換到條件 1 (1800 RPM)
```

### 參數使用示例

#### 示例 1: 低頻諧波分析

```python
# 在 fft_fm0_si() 方法中使用

# 1. 定位 BPFI 主頻 (233.43 Hz ± 2.0 Hz)
mask = (fftoutput['freqs'] >= 233.43 - 2.0) & \
       (fftoutput['freqs'] <= 233.43 + 2.0)

# 2. 計算諧波倍數 (整數倍,例如 3x)
target_freq = 233.43 × 3 = 700.29 Hz
search_range = ±1.0 Hz  # 使用 harmonic_gmf_range
```

#### 示例 2: 高頻邊帶分析

```python
# 在 tsa_fft_fm0_slf() 方法中使用

# 1. TSA 頻率校正後定位 BPFI 主頻
max_freqs = 原始主頻 / TSA主頻  # 計算倍率
corrected_freq = tsa_freq × max_freqs

# 2. 計算邊帶倍數 (整數倍,例如 5x)
target_freq = 233.43 × 5 = 1167.15 Hz
search_range = ±5.0 Hz  # 使用 high_hamonic_range

# 特殊邊帶 11.71x
target_freq_special = 233.43 × 11.71 = 2733.45 Hz
```

#### 示例 3: 同步指標計算

```python
# 馬達齒輦同步指標 (MGS)
mortor_gear = 30.0 Hz
mortor_gear_range = 2.0 Hz

# 左側範圍: [28.0, 30.0) Hz
# 右側範圍: (30.0, 32.0] Hz
# 計算該範圍內的平均能量
```

### 參數敏感性分析

| 參數 | 靈敏度 | 過小影響 | 過大影響 | 建議調整策略 |
|------|-------|---------|---------|-------------|
| `side_band_range` | 中 | 錯過主頻 | 混淆相近頻率 | 保持 2.0 Hz |
| `harmonic_gmf_range` | 高 | 漏掉諧波 | 包含噪音 | 根據信噪比調整 |
| `high_hamonic_range` | 低 | 漏掉邊帶 | 過度平滑 | 保持 5.0 Hz |
| `mortor_gear_range` | 低 | 範圍不足 | 包含其他頻率 | 根據轉速穩定性調整 |
| `belt_si_range` | 低 | 範圍不足 | 包含其他頻率 | 根據轉速穩定性調整 |

### 參數優化建議

1. **根據設備特性調整**:
   - 不同軸承型號: 調整 BPFO/BPFI 計算
   - 不同轉速範圍: 按比例調整頻率參數
   - 不同取樣頻率: 調整頻率解析度相關參數

2. **根據訊號品質調整**:
   - 高信噪比: 可縮小搜索公差
   - 低信噪比: 需增大搜索公差
   - 頻率漂移嚴重: 增大公差範圍

3. **驗證參數有效性**:
   - 使用已知故障數據測試
   - 比較不同參數下的 FM0 變化
   - 確保 FM0 對故障敏感且穩定

### 參數文件位置

所有參數定義在:
```
/home/ubuntu/Viberation-RUL-Prognostics/backend/initialization.py
```

參數文檔在:
```
/home/ubuntu/Viberation-RUL-Prognostics/docs/Initialization.md
```

## 應用場景

1. **齒輦故障診斷**:
   - FM0 值上升指示齒輦磨損
   - 馬達齒輦同步指標異常指示齒輦故障

2. **皮帶/軸承故障診斷**:
   - 皮帶同步指標異常指示皮帶滑動或張力問題
   - 邊帶能量增加指示軸承損傷

3. **頻譜分析**:
   - 識識主要故障頻率成分
   - 追蹤諧波和邊帶變化

## 安全措施

程式中實作了多個安全檢查:

1. **空 DataFrame 檢查**: 當頻率篩選結果為空時,使用第一列作為備選
2. **除以零保護**:
   - `low_filter_sum = 0` 時設為 1.0
   - `high_filter_sum = 0` 時設為 1.0
   - `rms_val = 0` 時設為 1.0
   - 頻率倍率計算時檢查除數是否為 0

## 與其他模組的關係

```
FrequencyDomain
    ├─→ TimeDomain (使用 peak(), rms() 方法)
    ├─→ HarmonicSildband (使用 Harmonic(), Sildband() 方法)
    └─→ InitParameter (使用頻率參數)
```
