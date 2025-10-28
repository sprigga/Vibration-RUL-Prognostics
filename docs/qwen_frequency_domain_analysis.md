# 頻域特徵分析 (Frequency Domain Analysis) - 振動信號處理

## 原理說明 (Principles of Analysis)

頻域特徵分析是通過快速傅立葉轉換（FFT）將時域振動信號轉換為頻域表示，以識別機械系統中的故障特徵頻率。這種方法能夠將複雜的時域信號分解為不同頻率組成的分量，從而更容易識別特定的機械故障模式。

### 傅立葉轉換原理
- **FFT（快速傅立葉轉換）**: 將時域信號 x(t) 轉換為頻域表示 X(f)
  ```
  X(f) = ∫ x(t)e^(-j2πft) dt
  ```

- **頻域表示**: 顯示信號在不同頻率下的幅值和相位分布
- **故障診斷**: 不同機械故障會在特定頻率產生特徵峰值

## 關鍵概念 (Key Concepts)

### 1. FFT（快速傅立葉轉換）
- 將原始振動信號轉換為頻率域
- 計算複雜度為 O(N log N)
- 生成複數型態的頻域表示

### 2. FM0（正規化峰值）
- **定義**: FM0 = Peak / ΣE_harmonics (峰值與諧波能量比值)
- 用於評估信號中峰值成分與整體諧波能量的關係
- 異常升高表示可能存在局部缺陷

### 3. TSA（時間同步平均）
- **定義**: 實時同步訊號分析，用於高頻分析
- 將信號與旋轉速度同步，減少非同步噪聲
- 提升故障特徵的信噪比

### 4. 諧波與邊帶分析
- **諧波**: 基頻的整數倍頻率分量
- **邊帶**: 围繞主要頻率的對稱頻率分量
- 用於檢測調製現象和機械缺陷

## 故障頻率基準 (Fault Frequency References)

根據系統參數，機械故障會在特定頻率產生特徵信號：

### 軸承故障頻率
- **BPF（Ball Pass Frequency）**: 滾動體通過頻率及諧波
- **BSF（Ball Spin Frequency）**: 滾動體自轉頻率
- **FTF（Fundamental Train Frequency）**: 保持鏈旋轉頻率

### 齒輪故障頻率
- **GMF（Gear Mesh Frequency）**: 齒輪嚙合頻率
- **邊帶頻率**: GMF ± n×rpm（n為諧波次數）

### 系統參數
根據 `initialization.py` 中的設定：
- **主電機頻率 (mortor_gear)**: 99.873 Hz
- **皮帶系統頻率 (belt_si)**: 41.6 Hz
- **高頻範圍 (mortor)**: 1597.97039 Hz
- **邊帶範圍**: ±1.664 Hz
- **諧波範圍**: ±1.5 Hz

## 應用場景 (Application Scenarios)

### 1. 滾動體缺陷檢測
- 檢測滾動體表面的點蝕、裂紋或異物
- 在BPF及其諧波頻率處觀察到能量集中
- 適用於滾軸軸承健康監測

### 2. 軌道損傷檢測
- 檢測軌道表面損傷或不均勻磨損
- 在邊帶頻率處觀察到調製現象
- 適用於軌道健康監測

### 3. 安裝問題診斷
- 檢測平行度不良、不平衡或軸彎曲
- 在倍頻和邊帶頻率處觀察到異常
- 適用於機械安裝精度評估

### 4. 早期故障檢測
- 通過諧波和邊帶分析檢測微小缺陷
- 在高頻段觀察到能量變化
- 適用於預測性維護

## 低頻FFT和高頻TSA計算差異

### 低頻FFT分析 (`fft_fm0_si`)

#### 計算流程：
1. **FFT轉換**:
   - 使用 `fft_process` 計算原始FFT
   - 生成複數FFT值和幅值譜
   - 計算頻率陣列

2. **特徵頻率識別**:
   - 尋找主電機齒輪頻率範圍 (±1.664 Hz around 99.873 Hz)
   - 尋找皮帶系統頻率範圍 (±1.664 Hz around 41.6 Hz)
   - 識別主要峰值頻率

3. **諧波計算**:
   - 使用 `HarmonicSildband.Harmonic` 計算諧波能量
   - 頻率範圍從0.25倍到2.75倍，以0.25為步長
   - 計算諧波總能量

4. **FM0計算**:
   - `low_fm0 = Peak / low_filter_sum`
   - 其中 Peak 由時域計算獲取 (max - min)

5. **MGS & BI 計算**:
   - **MGS (Motor Gear SI)**: 計算電機齒輪邊帶能量
     ```
     total_fft_mgs = (sum(fft_mgs1['abs_fft_n']) + sum(fft_mgs2['abs_fft_n'])) / (len(fft_mgs1) + len(fft_mgs2))
     ```
   - **BI (Bearing Index)**: 計算軸承能量指標
     ```
     total_fft_bi = (sum(fft_bi1['abs_fft_n']) + sum(fft_bi2['abs_fft_n'])) / (len(fft_bi1) + len(fft_bi2))
     ```

### 高頻TSA分析 (`tsa_fft_fm0_slf`)

#### 計算流程：
1. **TSA-FFT轉換**:
   - 對TSA信號進行FFT轉換
   - 生成高頻頻域表示

2. **頻率倍率計算**:
   - 計算原始FFT與TSA-FFT的頻率關係
   - `max_freqs = original_max_freq / tsa_max_freq`

3. **頻率映射**:
   - 將TSA頻率乘以倍率因子進行映射
   - `multiply_freqs = tsa_freqs * max_freqs`

4. **特徵識別**:
   - 在映射後的頻率域中尋找特徵頻率
   - 範圍擴大到±2.5 Hz around特徵頻率

5. **邊帶計算**:
   - 使用 `HarmonicSildband.Sildband` 計算高頻邊帶能量
   - 計算範圍從2.75倍到14.25倍，以0.25為步長
   - 包括11.71倍的例外頻率計算

6. **高頻FM0計算**:
   - `high_fm0 = Peak / high_filter_sum`

7. **高頻MGS & BI計算**:
   - **TSA-MGS**: 使用RMS正規化
     ```
     total_tsa_fft_mgs = (sum(tsa_fft_mgs1['tsa_abs_fft_n']) + sum(tsa_fft_mgs2['tsa_abs_fft_n'])) / RMS(amp)
     ```
   - **TSA-BI**: 使用RMS正規化
     ```
     total_tsa_fft_bi = (sum(tsa_fft_bi1['tsa_abs_fft_n']) + sum(tsa_fft_bi2['tsa_abs_fft_n'])) / RMS(amp)
     ```

## 計算公式詳細說明

### FFT運算（`fft_process`）
```python
def fft_process(amp, fs):
    fft_value = np.fft.fft(amp)  # 原始的FFT，複數型態
    abs_fft = np.abs(fft_value)  # 原始取絕對值的FFT
    abs_fft_n = (np.abs(fft_value/fft_value.size))*2  # 計算用
    abs_fft_segment1 = np.abs(fft_value/fft_value.size)*2  # 畫圖用
    if (len(fft_value) % 2 == 0): 
        abs_fft_segment2 = abs_fft_segment1[0:int(fft_value.size/2)]
    else:
        abs_fft_segment2 = abs_fft_segment1[0:int(fft_value.size/2+1)]
    abs_fft_segment2[1:-1] = 2 * abs_fft_segment2[1:-1]
    freqs_number_segment = fs*np.arange(0,(fft_value.size/2))/fft_value.size
    freqs = np.fft.fftfreq(fft_value.size, 1./fs)  # 全部頻率
    return fft_value, abs_fft, freqs, abs_fft_n, abs_fft_segment2, freqs_number_segment
```

### 低頻FM0計算（`fft_fm0_si`）
- **目的**: 計算低頻範圍內的正規化峰值指標
- **主要計算**:
  1. 識別主要頻率（電機齒輪和皮帶系統）
  2. 計算相關諧波能量總和
  3. 計算FM0 = Peak / 諧波總能量

### 高頻TSA-FM0計算（`tsa_fft_fm0_slf`）
- **目的**: 計算高頻範圍內的正規化峰值指標，使用TSA技術
- **主要計算**:
  1. 時間同步平均處理
  2. 高頻FFT轉換
  3. 頻率倍率映射
  4. 計算高頻邊帶能量
  5. 計算FM0 = Peak / 邊帶總能量

## 參數設定

### 頻率範圍參數
- **邊帶範圍**: ±1.664 Hz
- **諧波GMF範圍**: ±1.5 Hz
- **電機齒輪範圍**: ±2.5 Hz
- **皮帶系統範圍**: ±2.5 Hz
- **高諧波範圍**: ±5 Hz

### 採樣參數
- **低頻採樣率**: 50000 Hz
- **高頻TSA採樣率**: 80 Hz
- **頻率解析度**: 依信號長度而定

## 診斷準則

### 低頻分析準則
- **FM0升高**: 表示諧波能量異常，可能存在機械缺陷
- **MGS異常**: 電機齒輪系統問題
- **BI增加**: 軸承或其他旋轉部件異常

### 高頻分析準則
- **高頻FM0異常**: 高頻範圍內的能量異常
- **邊帶能量集中**: 機械調製問題
- **TSA指標異常**: 同步問題或高頻缺陷

## 實際應用範例

### 計算流程
1. **數據預處理**: 準備振動信號數據
2. **FFT計算**: 執行快速傅立葉轉換
3. **特徵識別**: 在頻譜中尋找特徵頻率
4. **指標計算**: 計算FM0, MGS, BI等指標
5. **結果分析**: 評估機械健康狀態

### 振動信號處理
- **水平和垂直方向**: 同時分析兩個方向的振動
- **多參數計算**: 同時計算多種頻域特徵
- **實時監測**: 支援連續監測和趨勢分析

## 程式碼結構

### 主要類別：FrequencyDomain
- `fft_process`: FFT轉換函數
- `ifft_process`: 逆FFT轉換函數
- `fft_fm0_si`: 低頻FM0計算
- `tsa_fft_fm0_slf`: 高頻TSA-FM0計算

### 輔助類別：HarmonicSildband
- `Harmonic`: 計算諧波能量
- `Sildband`: 計算邊帶能量
- `Tsa_Harmonic`: 計算TSA諧波能量

此頻域分析方法提供了全面的機械故障檢測能力，結合低頻和高頻分析可以更準確地診斷不同類型的機械缺陷。