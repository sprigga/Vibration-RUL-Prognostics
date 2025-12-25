import pandas as pd
import numpy as np
try:
    from backend.initialization import InitParameter as ip
    from backend.timedomain import TimeDomain as td
    from backend.harmonic_sildband_table import HarmonicSildband as hs
except ModuleNotFoundError:
    from initialization import InitParameter as ip
    from timedomain import TimeDomain as td
    from harmonic_sildband_table import HarmonicSildband as hs

ip=ip()

class FrequencyDomain():

#    計算傅立葉轉換
    @staticmethod
    def fft_process(amp, fs):
        fft_value=np.fft.fft(amp) #原始的FFT,是複數
        abs_fft = np.abs(fft_value) #原始的取絕對值的FFT
        abs_fft_n = (np.abs(fft_value/fft_value.size))*2 # 計算用
        abs_fft_segment1 = np.abs(fft_value/fft_value.size)*2 #畫圖用
        if (len(fft_value) % 2 ==0): 
            abs_fft_segment2 = abs_fft_segment1[0:int(fft_value.size/2)]
        else:
            abs_fft_segment2 = abs_fft_segment1[0:int(fft_value.size/2+1)]
        abs_fft_segment2[1:-1] = 2 * abs_fft_segment2[1:-1]
        freqs_number_segment = fs*np.arange(0,(fft_value.size/2))/fft_value.size
        freqs = np.fft.fftfreq(fft_value.size,1./fs) #all freqs
        return fft_value,abs_fft,freqs,abs_fft_n,abs_fft_segment2,freqs_number_segment
    
#    計算逆傅立葉轉換
    @staticmethod
    def ifft_process(fft_value):
        
        # 逆FFT的計算
        ifft_value=np.fft.ifft(fft_value)
        time_value = np.arange(0,np.size(ifft_value)) * (360/ifft_value.size)
        ifft_tsa = pd.DataFrame({'Degree':time_value,'Acc':ifft_value.real})
        return ifft_tsa,time_value

    #計算低頻的FM0數值
    def fft_fm0_si(self, amp, fs):

        fft_value,abs_fft,freqs,abs_fft_n,_,_ = FrequencyDomain.fft_process(amp,fs)
        fftoutput=pd.DataFrame({'freqs':np.round(freqs,3),
                                'freqs1':np.round(freqs,5),
                                'abs_fft':abs_fft,
                                'abs_fft_n': abs_fft_n,
                                'fft':fft_value})

#        先計算mortor gear的主要頻率
        mask1 = fftoutput['freqs']>=ip.mortor_gear-ip.side_band_range
        mask2 = fftoutput['freqs']<=ip.mortor_gear+ip.side_band_range
        max_mortor_gear=fftoutput[mask1 & mask2]

        # Safety check for empty DataFrame
        if max_mortor_gear.empty:
            max_mortor_gear = fftoutput.iloc[0:1]  # Use first row as fallback
        else:
            max_mortor_gear = fftoutput[fftoutput['abs_fft']==np.max(max_mortor_gear['abs_fft'])]
        max_mortor_gear1=max_mortor_gear.iloc[0:1]


#        先計算培林的主要頻率
        mask3 = fftoutput['freqs']>=ip.belt_si - ip.side_band_range
        mask4 = fftoutput['freqs']<=ip.belt_si + ip.side_band_range
        max_belt_si=fftoutput[mask3 & mask4]

        # Safety check for empty DataFrame
        if max_belt_si.empty:
            max_belt_si = fftoutput.iloc[0:1]  # Use first row as fallback
        else:
            max_belt_si = fftoutput[fftoutput['abs_fft']==np.max(max_belt_si['abs_fft'])]
        max_belt_si1=max_belt_si.iloc[0:1]


#        用mortor gear的主要頻率來找出周圍的頻率
        mask7 = fftoutput['freqs']>=float(max_mortor_gear1['freqs'].values[0]) - ip.harmonic_gmf_range
        mask8 = fftoutput['freqs']<float(max_mortor_gear1['freqs'].values[0])
        mask9 = fftoutput['freqs']>float(max_mortor_gear1['freqs'].values[0])
        mask10 = fftoutput['freqs']<=float(max_mortor_gear1['freqs'].values[0]) + ip.harmonic_gmf_range

#        用培林的主要頻率來找出周圍的頻率
        mask11 = fftoutput['freqs']>=float(max_belt_si1['freqs'].values[0]) - ip.harmonic_gmf_range
        mask12 = fftoutput['freqs']<float(max_belt_si1['freqs'].values[0])
        mask13 = fftoutput['freqs']>float(max_belt_si1['freqs'].values[0])
        mask14 = fftoutput['freqs']<=float(max_belt_si1['freqs'].values[0]) + ip.harmonic_gmf_range

       #呼叫計算harmonic sildband table的方法
        low_filter_sum,_ = hs.Harmonic(fftoutput)

        # Safety check: if harmonic sum is 0, use peak value to avoid division by zero
        if low_filter_sum == 0:
            low_filter_sum = 1.0  # Default value to avoid division by zero

#        篩選motor gear和培林的數值
        fft_mgs1=fftoutput[mask7 & mask8]
        fft_mgs2=fftoutput[mask9 & mask10]

        fft_bi1=fftoutput[mask11 & mask12]
        fft_bi2=fftoutput[mask13 & mask14]

#        計算低頻的FM0的數值
        low_fm0=td.peak(amp)/low_filter_sum

#        計算出motor gear si和belt si的數值
        len_mgs = len(fft_mgs1) + len(fft_mgs2)
        len_bi = len(fft_bi1) + len(fft_bi2)

        total_fft_mgs = (np.sum(fft_mgs1['abs_fft_n']) + np.sum(fft_mgs2['abs_fft_n'])) / len_mgs if len_mgs > 0 else 0.0
        total_fft_bi = (np.sum(fft_bi1['abs_fft_n']) + np.sum(fft_bi2['abs_fft_n'])) / len_bi if len_bi > 0 else 0.0

        return fftoutput,total_fft_mgs,total_fft_bi,low_fm0
    
#   計算實時同步訊號(TSA)的高頻FM0
    def tsa_fft_fm0_slf(self, amp, fs, fft):

        tsa_fft_value,tsa_abs_fft,tsa_freqs,tsa_abs_fft_n,_,_ = FrequencyDomain.fft_process(amp,fs)
        tsa_fftoutput=pd.DataFrame({'tsa_freqs':np.round(tsa_freqs,3),
                                    'tsa_freqs1':np.round(tsa_freqs,5),
                                    'tsa_abs_fft':tsa_abs_fft,
                                    'tsa_abs_fft_n': tsa_abs_fft_n,
                                    'tsa_fft':tsa_fft_value})

        fftoutput=fft


#        計算TSA FFT和原始FFT頻率的倍率
        max1=fftoutput[fftoutput['abs_fft']==np.max(fftoutput['abs_fft'])]
        max2=tsa_fftoutput[tsa_fftoutput['tsa_abs_fft']==np.max(tsa_fftoutput['tsa_abs_fft'])]

        max3=max1.iloc[0:1]
        max4=max2.iloc[0:1]

        # Safety check for division by zero
        max4_freq = float(max4['tsa_freqs1'].values[0])
        if max4_freq == 0:
            max_freqs = 1.0
        else:
            max_freqs = float(max3['freqs1'].values[0]) / max4_freq

        tsa_fftoutput=pd.DataFrame({'tsa_freqs':np.round(tsa_freqs,3),
                                    'tsa_freqs1':np.round(tsa_freqs,5),
                                    'multiply_freqs':np.round(tsa_freqs*max_freqs,5),
                                    'tsa_abs_fft':tsa_abs_fft,
                                    'tsa_abs_fft_n': tsa_abs_fft_n,
                                    'tsa_fft':tsa_fft_value})

#        先計算mortor gear的主要頻率
        mask1 = tsa_fftoutput['multiply_freqs']>=ip.mortor_gear-ip.side_band_range
        mask2 = tsa_fftoutput['multiply_freqs']<=ip.mortor_gear+ip.side_band_range
        max_mortor_gear=tsa_fftoutput[mask1 & mask2]

        # Safety check for empty DataFrame
        if max_mortor_gear.empty:
            max_mortor_gear = tsa_fftoutput.iloc[0:1]
        else:
            max_mortor_gear = tsa_fftoutput[tsa_fftoutput['tsa_abs_fft']==np.max(max_mortor_gear['tsa_abs_fft'])]
        max_mortor_gear1=max_mortor_gear.iloc[0:1]

#        先計算培林的主要頻率
        mask3 = tsa_fftoutput['multiply_freqs']>=ip.belt_si - ip.side_band_range
        mask4 = tsa_fftoutput['multiply_freqs']<=ip.belt_si + ip.side_band_range
        max_belt_si=tsa_fftoutput[mask3 & mask4]

        # Safety check for empty DataFrame
        if max_belt_si.empty:
            max_belt_si = tsa_fftoutput.iloc[0:1]
        else:
            max_belt_si = tsa_fftoutput[tsa_fftoutput['tsa_abs_fft']==np.max(max_belt_si['tsa_abs_fft'])]
        max_belt_si1=max_belt_si.iloc[0:1]

#         用mortor gear的主要頻率來找出周圍的頻率
        mask7 = tsa_fftoutput['multiply_freqs']>=float(max_mortor_gear1['multiply_freqs'].values[0]) - ip.mortor_gear_range
        mask8 = tsa_fftoutput['multiply_freqs']<float(max_mortor_gear1['multiply_freqs'].values[0])
        mask9 = tsa_fftoutput['multiply_freqs']>float(max_mortor_gear1['multiply_freqs'].values[0])
        mask10 = tsa_fftoutput['multiply_freqs']<=float(max_mortor_gear1['multiply_freqs'].values[0]) + ip.mortor_gear_range

#        用培林的主要頻率來找出周圍的頻率
        mask11 = tsa_fftoutput['multiply_freqs']>=float(max_belt_si1['multiply_freqs'].values[0]) - ip.belt_si_range
        mask12 = tsa_fftoutput['multiply_freqs']<float(max_belt_si1['multiply_freqs'].values[0])
        mask13 = tsa_fftoutput['multiply_freqs']>float(max_belt_si1['multiply_freqs'].values[0])
        mask14 = tsa_fftoutput['multiply_freqs']<=float(max_belt_si1['multiply_freqs'].values[0]) + ip.belt_si_range

         #---high freqency fm0---
        high_filter_sum,_ = hs.Sildband(tsa_fftoutput)

        # Safety check: if sideband sum is 0, use default value to avoid division by zero
        if high_filter_sum == 0:
            high_filter_sum = 1.0


#        篩選motor gear和培林的數值
        tsa_fft_mgs1=tsa_fftoutput[mask7 & mask8]
        tsa_fft_mgs2=tsa_fftoutput[mask9 & mask10]
#
        tsa_fft_bi1=tsa_fftoutput[mask11 & mask12]
        tsa_fft_bi2=tsa_fftoutput[mask13 & mask14]

#        計算高頻的FM0的數值
        high_fm0 = td.peak(amp)/ high_filter_sum

#        計算出motor gear si和belt si的數值
        rms_val = td.rms(amp)
        if rms_val == 0:
            rms_val = 1.0  # Avoid division by zero

        total_tsa_fft_mgs = (np.sum(tsa_fft_mgs1['tsa_abs_fft_n']) + np.sum(tsa_fft_mgs2['tsa_abs_fft_n'])) / rms_val
        total_tsa_fft_bi = (np.sum(tsa_fft_bi1['tsa_abs_fft_n']) + np.sum(tsa_fft_bi2['tsa_abs_fft_n'])) / rms_val

        return tsa_fftoutput,total_tsa_fft_mgs,total_tsa_fft_bi,high_fm0

    #==================================================================
    # 計算頻域特徵趨勢（所有檔案）
    #==================================================================
    def calculate_frequency_domain_trend(
        self,
        bearing_name: str,
        sampling_rate: int = 25600,
        progress_callback=None
    ):
        """
        計算頻域特徵趨勢（所有檔案）

        計算所有檔案的頻域特徵,包括低頻和高頻 FM0、
        Motor Gear Sideband Index (MGS)、Belt/Bearing Index (BI)

        Args:
            bearing_name: 軸承名稱 (例如: "Bearing1_1")
            sampling_rate: 採樣頻率 (默認 25600 Hz)
            progress_callback: 進度回調函數 callback(current, total, file_number)

        Returns:
            包含所有檔案頻域特徵的字典,格式適合圖表和表格顯示
        """
        import sqlite3
        import time
        try:
            from backend.config import PHM_DATABASE_PATH
        except ModuleNotFoundError:
            from config import PHM_DATABASE_PATH

        start_time = time.time()

        # 連接資料庫
        conn = sqlite3.connect(PHM_DATABASE_PATH)
        cursor = conn.cursor()

        # 獲取所有檔案（不使用 LIMIT）
        cursor.execute("""
            SELECT mf.file_number, mf.file_id
            FROM measurement_files mf
            JOIN bearings b ON mf.bearing_id = b.bearing_id
            WHERE b.bearing_name = ?
            ORDER BY mf.file_number
        """, (bearing_name,))

        files = cursor.fetchall()

        if not files:
            conn.close()
            raise ValueError(f"No files found for {bearing_name}")

        total_files = len(files)

        # 初始化結果結構
        feature_keys = ["low_fm0", "high_fm0", "mgs_low", "bi_low", "mgs_high", "bi_high"]

        trend_data = {
            "bearing_name": bearing_name,
            "file_count": total_files,
            "horizontal": {key: [] for key in feature_keys},
            "vertical": {key: [] for key in feature_keys},
            "file_numbers": [],
            "table_data": []
        }

        # 處理每個檔案
        for idx, (file_num, file_id) in enumerate(files):
            try:
                # 更新進度
                if progress_callback:
                    progress_callback(idx + 1, total_files, file_num)

                # 查詢資料
                query = f"""
                    SELECT horizontal_acceleration, vertical_acceleration
                    FROM measurements
                    WHERE file_id = {file_id}
                """
                df = pd.read_sql_query(query, conn)

                if df.empty:
                    print(f"Warning: File {file_num} has no data, skipping")
                    # 插入 NaN 值
                    for key in feature_keys:
                        trend_data["horizontal"][key].append(float('nan'))
                        trend_data["vertical"][key].append(float('nan'))
                    trend_data["file_numbers"].append(file_num)
                    continue

                # 提取資料
                horiz = df['horizontal_acceleration'].values
                vert = df['vertical_acceleration'].values

                # 計算低頻特徵
                horiz_fftoutput, horiz_mgs_low, horiz_bi_low, horiz_low_fm0 = \
                    self.fft_fm0_si(horiz, sampling_rate)
                vert_fftoutput, vert_mgs_low, vert_bi_low, vert_low_fm0 = \
                    self.fft_fm0_si(vert, sampling_rate)

                # 計算高頻特徵
                horiz_tsa_fftoutput, horiz_mgs_high, horiz_bi_high, horiz_high_fm0 = \
                    self.tsa_fft_fm0_slf(horiz, sampling_rate, horiz_fftoutput)
                vert_tsa_fftoutput, vert_mgs_high, vert_bi_high, vert_high_fm0 = \
                    self.tsa_fft_fm0_slf(vert, sampling_rate, vert_fftoutput)

                # 儲存結果
                trend_data["horizontal"]["low_fm0"].append(float(horiz_low_fm0))
                trend_data["horizontal"]["high_fm0"].append(float(horiz_high_fm0))
                trend_data["horizontal"]["mgs_low"].append(float(horiz_mgs_low))
                trend_data["horizontal"]["bi_low"].append(float(horiz_bi_low))
                trend_data["horizontal"]["mgs_high"].append(float(horiz_mgs_high))
                trend_data["horizontal"]["bi_high"].append(float(horiz_bi_high))

                trend_data["vertical"]["low_fm0"].append(float(vert_low_fm0))
                trend_data["vertical"]["high_fm0"].append(float(vert_high_fm0))
                trend_data["vertical"]["mgs_low"].append(float(vert_mgs_low))
                trend_data["vertical"]["bi_low"].append(float(vert_bi_low))
                trend_data["vertical"]["mgs_high"].append(float(vert_mgs_high))
                trend_data["vertical"]["bi_high"].append(float(vert_bi_high))

                trend_data["file_numbers"].append(file_num)

                # 添加到表格資料
                trend_data["table_data"].append({
                    "file_number": file_num,
                    "h_low_fm0": float(horiz_low_fm0),
                    "h_high_fm0": float(horiz_high_fm0),
                    "h_mgs_low": float(horiz_mgs_low),
                    "h_bi_low": float(horiz_bi_low),
                    "h_mgs_high": float(horiz_mgs_high),
                    "h_bi_high": float(horiz_bi_high),
                    "v_low_fm0": float(vert_low_fm0),
                    "v_high_fm0": float(vert_high_fm0),
                    "v_mgs_low": float(vert_mgs_low),
                    "v_bi_low": float(vert_bi_low),
                    "v_mgs_high": float(vert_mgs_high),
                    "v_bi_high": float(vert_bi_high)
                })

            except Exception as e:
                print(f"Error processing file {file_num}: {str(e)}")
                # 插入 NaN 值
                for key in feature_keys:
                    trend_data["horizontal"][key].append(float('nan'))
                    trend_data["vertical"][key].append(float('nan'))
                trend_data["file_numbers"].append(file_num)
                continue

        conn.close()

        # 計算處理時間
        trend_data["processing_time"] = time.time() - start_time

        return trend_data
