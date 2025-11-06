# 🔧 振動信號分析系統

現代化的 Web 應用程式，整合 Vue 3 前端與 FastAPI 後端，用於設備振動信號分析與故障診斷。

## ✨ 主要功能

### 1. 儀表板
- 實時健康狀態總覽
- 健康趨勢圖表
- 設備統計資訊
- 快速操作入口

### 2. 振動分析
- CSV 檔案上傳分析
- 完整的診斷報告
- 六大特徵分析：
  - 時域特徵（Peak, RMS, Kurtosis, CF）
  - 頻域特徵（FM0, BPF檢測）
  - 包絡分析（滾動體缺陷）
  - 高階統計（NA4, FM4, M6A, M8A）
  - 小波分析（STFT, CWT）
  - 狀態評估

### 3. 頻率計算器
- 理論故障頻率計算
- BPF（滾動體通過頻率）
- BSF（滾動體自轉頻率）
- Cage Frequency（保持鏈頻率）

### 4. 演算法展示
- 詳細的演算法原理說明
- 時域、頻域、小波、包絡分析
- 診斷準則與應用場景
- 故障類型對應表

### 5. 設備規格管理
- 新增/查看設備規格
- 負荷參數設定
- 狀態等級設定
- 密封與潤滑類型

### 6. 歷史記錄
- 分析結果查詢
- 健康趨勢追蹤
- 詳細報告檢視

## 🏗️ 技術架構

### 前端（Frontend）
- **框架**: Vue 3 (Composition API)
- **UI 組件**: Element Plus
- **路由**: Vue Router 4
- **狀態管理**: Pinia
- **圖表**: Chart.js + vue-chartjs
- **建構工具**: Vite

### 後端（Backend）
- **框架**: FastAPI
- **資料庫**: SQLite (輕量化部署)
- **ORM**: SQLAlchemy
- **數據處理**: NumPy, Pandas, SciPy
- **小波分析**: PyWavelets

### 核心演算法模組
整合原有的振動分析模組：
- `timedomain.py` - 時域特徵
- `frequencydomain.py` - 頻域特徵與 FFT
- `filterprocess.py` - 濾波與高階統計
- `waveletprocess.py` - STFT 與 CWT
- `hilbertransfer.py` - 希爾伯特轉換
- `harmonic_sildband_table.py` - 諧波與邊帶分析

## 📦 安裝與運行

### 前置需求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 1. 後端設置

```bash
cd backend

# 安裝依賴
pip install -r requirements.txt

# 啟動後端服務
python main.py
```

後端將運行於 `http://localhost:8000`

API 文檔: `http://localhost:8000/docs`

### 2. 前端設置

```bash
cd frontend

# 安裝依賴
npm install

# 啟動開發服務器
npm run dev
```

前端將運行於 `http://localhost:5173`

### 3. 生產環境建構

```bash
# 前端建構
cd frontend
npm run build

# 後端使用 Uvicorn 部署
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📊 資料庫結構

### EquipmentSpec (設備規格)
```sql
- id: Integer (主鍵)
- series: String (如 "Series A")
- type: String (如 "Type 1")
- load_rating: String (如 "Standard")
- C0: Float (基本靜負荷)
- C100: Float (基本動負荷)
- seal_type: String
- speed_max: Float
- lubrication: String
```

### AnalysisResult (分析結果)
```sql
- id: Integer (主鍵)
- equipment_spec_id: Integer (外鍵)
- timestamp: DateTime
- velocity: Float
- health_score: Float (0-100)
- time_features: JSON
- frequency_features: JSON
- envelope_features: JSON
- higher_order_features: JSON
- findings: JSON (診斷發現列表)
- recommendations: JSON (維護建議列表)
```

## 🔌 API 端點

### 設備規格
- `POST /api/equipment-specs` - 新增規格
- `GET /api/equipment-specs` - 獲取所有規格
- `GET /api/equipment-specs/{id}` - 獲取特定規格

### 分析
- `POST /api/calculate-frequencies` - 計算故障頻率
- `POST /api/analyze` - 執行振動分析
- `POST /api/upload-csv` - 上傳 CSV 檔案分析

### 結果
- `GET /api/results` - 獲取分析結果列表
- `GET /api/results/{id}` - 獲取特定結果
- `GET /api/health-trend/{equipment_spec_id}` - 獲取健康趨勢

## 📝 CSV 檔案格式

上傳的 CSV 檔案應包含以下欄位：
```
time, x, y, z, label, 12m, 60m
0.00002, 0.123, -0.456, 0.789, ...
0.00004, 0.124, -0.455, 0.788, ...
...
```

系統會自動提取 X 軸數據（第2欄）進行分析。

## 🎯 使用流程

### 1. 新增設備規格
進入「設備規格」頁面，新增您要監測的旋轉設備參數。

### 2. 計算理論頻率
使用「頻率計算」工具，根據設備參數和運行速度計算 BPF、BSF 等理論頻率。

### 3. 執行振動分析
1. 選擇設備規格
2. 設定採樣頻率（建議 25.6 kHz）
3. 輸入運行速度
4. 上傳 CSV 振動信號檔案
5. 查看完整診斷報告

### 4. 查看歷史記錄
在「歷史記錄」頁面追蹤設備健康趨勢，及早發現故障徵兆。

## 🔍 診斷準則

### 健康分數評級
- **90-100**: 健康（綠色）
- **75-90**: 輕微異常（黃色）
- **60-75**: 中等異常（橙色）
- **0-60**: 嚴重異常（紅色）

### 關鍵指標閾值
- **Kurtosis > 8**: 嚴重缺陷
- **NA4 > 3**: 早期故障
- **包絡譜 SNR > 3**: 顯著缺陷
- **RMS 持續上升**: 磨損加劇

## 🚀 進階功能

### 狀態評估
系統會根據設備參數自動評估狀態：
- RMS 過低 → 狀態異常（鬆動）
- Kurtosis 過高 → 狀態異常（缺陷）

### 多軸分析
目前實現 X 軸分析，可擴展至 Y、Z 軸同時分析。

### 趨勢預測
基於歷史數據預測剩餘使用壽命（開發中）。

## 🛠️ 開發指南

### 新增演算法
1. 在 `backend/analysis.py` 中新增分析方法
2. 更新 `_integrated_diagnosis` 整合新特徵
3. 在前端 `Algorithms.vue` 新增說明

### 自訂設備型號
在 `backend/analysis.py` 的 `_get_equipment_parameters` 方法中新增參數。

### 修改診斷邏輯
調整 `backend/analysis.py` 中的閾值和權重。

## 📚 參考文檔

詳細的技術文檔請參考：
- [CLAUDE.md](CLAUDE.md) - 開發指南

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

## 📄 授權

此專案採用 MIT 授權條款。

## 👤 作者

Lin Hung Chuan

---

**🎉 開始您的預測性維護之旅！**
