import pandas as pd

# ===================================================================
# PHM 2012 數據集初始化參數配置
# ===================================================================
# 數據集特徵:
#   - 採樣頻率: 25.6 kHz (25600 Hz)
#   - 每個文件: 2560 數據點 (0.1秒)
#   - 軸承: SKF NKRF 25/20 (PRONOSTIA 平台)
#   - 滾動體數量 (Nb): 13
#   - 節圓直徑 (D): 34 mm
#   - 滾動體直徑 (d): 6.7 mm
#   - 接觸角: 0 度
# ===================================================================

class InitParameter():

    def __init__(self):

        # -----------------------------------------------------------------
        # 採樣參數
        # -----------------------------------------------------------------
        # [原 MFP 參數: tsa_fs = 80 Hz]
        self.tsa_fs = 180          # [PHM 2012] TSA 重採樣頻率
                                   # 提高至 180 Hz 以獲得每圈 6 個採樣點 (對於 30 Hz 轉軸頻率)

        # [原 MFP 參數: fs = 50000 Hz]
        self.fs = 25600            # [PHM 2012] 原始採樣頻率
                                   # 來源: PHM 2012 數據集規格

        self.tsa_ts = 1./self.tsa_fs  # TSA 採樣週期 (秒)
                                     # = 1/180 ≈ 0.00556 秒

        self.ts = 1./self.fs       # 採樣週期 (秒)
                                   # = 1/25600 ≈ 3.90625e-5 秒

        # -----------------------------------------------------------------
        # 軸承特徵頻率
        # 基於條件1 (1800 RPM, 4000 N) 的計算
        # 轉軸頻率 Fr = 1800/60 = 30 Hz
        # -----------------------------------------------------------------

        # [原 MFP 參數: mortor_gear = 99.873 Hz - MFP 齒輪箱馬達齒輪頻率]
        self.mortor_gear = 30.0    # [PHM 2012] 轉軸基頻 Fr
                                   # 公式: Fr = RPM / 60
                                   # 條件1: 1800 RPM → 30 Hz
                                   # 用途: 邊帶分析的基準頻率

        # [原 MFP 參數: belt_si = 41.6 Hz - MFP 皮帶頻率]
        self.belt_si = 156.59      # [PHM 2012] BPFO (Ball Pass Frequency Outer)
                                   # 外圈通過頻率
                                   # 公式: BPFO = (Nb/2) * (1 - d/D) * Fr
                                   # 計算: 6.5 * (1 - 6.7/34) * 30 = 156.59 Hz
                                   # 用途: 外圈故障檢測基準頻率

        # [原 MFP 參數: mortor = 1597.97039 Hz - MFP 馬達高頻]
        self.mortor = 233.43       # [PHM 2012] BPFI (Ball Pass Frequency Inner)
                                   # 內圈通過頻率
                                   # 公式: BPFI = (Nb/2) * (1 + d/D) * Fr
                                   # 計算: 6.5 * (1 + 6.7/34) * 30 = 233.43 Hz
                                   # 用途: 內圈故障檢測基準頻率

        # [原 MFP 參數: high_hamonic = 20673.84 Hz - MFP 高階諧波]
        self.high_hamonic = 466.86 # [PHM 2012] BPFI × 2 (二倍諧波)
                                   # 計算: 233.43 * 2 = 466.86 Hz
                                   # 用途: 高階邊帶分析的基準

        # -----------------------------------------------------------------
        # 頻率搜索範圍參數 (用於 FFT 峰值檢測的容差範圍)
        # -----------------------------------------------------------------

        # [原 MFP 參數: side_band_range = 1.664]
        self.side_band_range = 2.0  # [調整] 邊帶容差範圍
                                   # 說明: 容許 ±2 Hz 的頻率偏差
                                   # 用途: 在基準頻率周圍搜索邊帶能量

        # [原 MFP 參數: harmonic_gmf_range = 1.5]
        self.harmonic_gmf_range = 1.0  # [調整] 諧波容差範圍
                                       # 說明: 用於低頻諧波分析的帶寬

        # [原 MFP 參數: mortor_gear_range = 2.5]
        self.mortor_gear_range = 2.0  # [調整] 轉軸頻率範圍
                                     # 用途: mortor_gear 周圍的分析範圍

        # [原 MFP 參數: belt_si_range = 2.5]
        self.belt_si_range = 2.0    # [調整] BPFO 頻率範圍
                                   # 用途: belt_si (BPFO) 周圍的分析範圍

        # [原 MFP 參數: morotr_range = 8.29]
        self.morotr_range = 3.0     # [調整] BPFI 頻率範圍
                                   # 說明: 縮小範圍以適配較低的軸承頻率
                                   # 用途: mortor (BPFI) 周圍的分析範圍

        # [原 MFP 參數: high_hamonic_range = 5]
        self.high_hamonic_range = 5.0  # [保持] 高階諧波範圍
                                      # 用途: 高階邊帶分析的帶寬

        # -----------------------------------------------------------------
        # 其他參數
        # -----------------------------------------------------------------
        self.indexlist1 = []
        self.indexlist2 = []

        self.cwt_scale_max = 64    # [保持] CWT 最大尺度

        # -----------------------------------------------------------------
        # STFT 參數 (短時傅立葉轉換)
        # -----------------------------------------------------------------
        # 針對 2560 點/文件，25600 Hz 採樣率優化

        # Hann 窗口: 適合頻率解析，時間解析較低
        self.stft_hann_nperseg = 128
        # [保持] Hann 窗口段長度
        # 說明:
        #   - 時間分辨率: 128/25600 = 0.005 秒
        #   - 頻率分辨率: 25600/128 = 200 Hz
        #   - 適合捕捉低頻軸承故障特徵

        # Flattop 窗口: 適合幅值精度
        self.stft_flattop_nperseg = 256
        # [保持] Flattop 窗口段長度
        # 說明:
        #   - 時間分辨率: 256/25600 = 0.01 秒
        #   - 頻率分辨率: 25600/256 = 100 Hz
        #   - 更好的幅值精度，適合諧波分析

        # -----------------------------------------------------------------
        # PHM 2012 特定的軸承故障頻率 (參考用)
        # -----------------------------------------------------------------
        # 條件1 (1800 RPM) - 當前使用
        self.fr_condition1 = 30.0
        self.bpfo_condition1 = 156.59
        self.bpfi_condition1 = 233.43
        self.ftf_condition1 = 12.05   # FTF (Fundamental Train Frequency) - 保持架頻率
        self.bsf_condition1 = 73.16   # BSF (Ball Spin Frequency) - 滾動體自旋頻率

        # 條件2 (1650 RPM)
        self.fr_condition2 = 27.5
        self.bpfo_condition2 = 143.54
        self.bpfi_condition2 = 213.98
        self.ftf_condition2 = 11.05
        self.bsf_condition2 = 66.91

        # 條件3 (1500 RPM)
        self.fr_condition3 = 25.0
        self.bpfo_condition3 = 130.49
        self.bpfi_condition3 = 194.53
        self.ftf_condition3 = 10.04
        self.bsf_condition3 = 60.83


        #---測試用的資料---
        # Note: These test data files are only loaded if they exist
        # This allows the module to work in environments without test data (e.g., Docker containers)
        #    inputdir = r'C:\Users\jasonchien\.spyder-py3\20181121_tsa_good.csv'  #檔案路徑，可修改。
        #    inputdir2 = r'C:\Users\jasonchien\.spyder-py3\MFP45_600C_NOL_L1_M354B_accelerometer_1.csv'  #good
        inputdir = r'C:\Users\jasonchien\.spyder-py3\20181121_tsa_defect.csv'  #檔案路徑，可修改。
        inputdir2 = r'C:\Users\jasonchien\.spyder-py3\MFP45_600C_59T_L1_M354B_accelerometer_1.csv'  #defect
        inputdir3 = r'C:\Users\jasonchien\.spyder-py3\Harmonic Sideband Filter for Polo_1.csv'  #檔案路徑，可修改。
        inputdir5 = r'D:\MFPDataset5\20190117_104625_ML_GAP0.1_MFP45_600C_C1_NOISE\MFP45_600C_ML_GAP0.1_M354B_accelerometer_signal_010.csv'
        inputdir6 = r'D:\MFPDataset5\20190117_104625_ML_GAP0.1_MFP45_600C_C1_NOISE\MFP45_600C_ML_GAP0.1_M354B_accelerometer_TSA_60T_010.csv'

        # Initialize test data attributes as None (will be loaded only if files exist)
        self.pdata = None
        self.pdata2 = None
        self.pdata3 = None
        self.pdata4 = None
        self.pdata5 = None
        self.pdata6 = None

        # Try to load test data files if they exist (for legacy batch processing)
        import os
        try:
            if os.path.exists(inputdir):
                dataSet = pd.read_csv(inputdir,names=['Degree','Acc'])
                self.pdata = pd.DataFrame(dataSet,columns=['Degree','Acc'])
            if os.path.exists(inputdir2):
                dataSet2 = pd.read_csv(inputdir2,names=['time','x','y','z','label','12m','60m'])
                self.pdata2 = pd.DataFrame(dataSet2,columns=['time','x','y','z','label','12m','60m'])
            if os.path.exists(inputdir3):
                dataSet3 = pd.read_csv(inputdir3,header=None)
                self.pdata3 = pd.DataFrame(dataSet3)
                self.pdata4 = self.pdata3[0]*-1
            if os.path.exists(inputdir5):
                dataSet5 = pd.read_csv(inputdir5,names=['time','x','y','z','label','12m','60m'])
                self.pdata5 = pd.DataFrame(dataSet5,columns=['time','x','y','z','label','12m','60m'])
            if os.path.exists(inputdir6):
                dataSet6 = pd.read_csv(inputdir6,names=['Degree','x','y','z'])
                self.pdata6 = pd.DataFrame(dataSet6,columns=['Degree','x','y','z'])
        except Exception as e:
            # Silently skip test data loading if files are not accessible
            # This allows the module to work in Docker containers and web environments
            pass
        #----------------

    # ===================================================================
    # 工作條件切換方法
    # ===================================================================
    def set_working_condition(self, condition: int):
        """根據工作條件設置軸承特徵頻率

        PHM 2012 數據集有三種工作條件:
        - 條件1: 1800 RPM, 4000 N 徑向載荷
        - 條件2: 1650 RPM, 4200 N 徑向載荷
        - 條件3: 1500 RPM, 5000 N 徑向載荷

        Args:
            condition: 工作條件編號 (1, 2, 或 3)

        Raises:
            ValueError: 當條件編號無效時
        """
        condition_params = {
            1: {
                'rpm': 1800,
                'load': 4000,
                'fr': 30.0,
                'bpfo': 156.59,
                'bpfi': 233.43,
                'ftf': 12.05,
                'bsf': 73.16
            },
            2: {
                'rpm': 1650,
                'load': 4200,
                'fr': 27.5,
                'bpfo': 143.54,
                'bpfi': 213.98,
                'ftf': 11.05,
                'bsf': 66.91
            },
            3: {
                'rpm': 1500,
                'load': 5000,
                'fr': 25.0,
                'bpfo': 130.49,
                'bpfi': 194.53,
                'ftf': 10.04,
                'bsf': 60.83
            }
        }

        if condition not in condition_params:
            raise ValueError(f"條件必須為 1, 2, 或 3，獲得: {condition}")

        params = condition_params[condition]

        # 更新主要特徵頻率參數
        self.mortor_gear = params['fr']
        self.belt_si = params['bpfo']
        self.mortor = params['bpfi']
        self.high_hamonic = params['bpfi'] * 2

        # 更新當前條件的參考頻率
        self.current_condition = condition
        self.current_rpm = params['rpm']
        self.current_load = params['load']

        return {
            'condition': condition,
            'rpm': params['rpm'],
            'load_N': params['load'],
            'fr_hz': params['fr'],
            'bpfo_hz': params['bpfo'],
            'bpfi_hz': params['bpfi']
        }

    def get_current_condition_info(self):
        """獲取當前工作條件信息

        Returns:
            dict: 包含當前條件的詳細信息
        """
        if hasattr(self, 'current_condition'):
            return {
                'condition': self.current_condition,
                'rpm': self.current_rpm,
                'load_N': self.current_load,
                'fr': self.mortor_gear,
                'bpfo': self.belt_si,
                'bpfi': self.mortor
            }
        else:
            # 默認條件1
            return {
                'condition': 1,
                'rpm': 1800,
                'load_N': 4000,
                'fr': self.mortor_gear,
                'bpfo': self.belt_si,
                'bpfi': self.mortor
            }
