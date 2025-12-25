<template>
  <div class="phm-database">
    <div class="header">
      <h1>PHM 資料庫查詢</h1>
      <p class="subtitle">查詢 PHM IEEE 2012 訓練資料集</p>
    </div>

    <!-- Bearings List -->
    <div class="section">
      <h2>軸承列表</h2>
      <div v-if="loading" class="loading">載入中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="bearings-grid">
        <div
          v-for="bearing in bearings"
          :key="bearing.bearing_id"
          class="bearing-card"
          :class="{ active: selectedBearing === bearing.bearing_name }"
          @click="selectBearing(bearing.bearing_name)"
        >
          <h3>{{ bearing.bearing_name }}</h3>
          <div class="stats">
            <div class="stat">
              <span class="label">檔案數:</span>
              <span class="value">{{ bearing.file_count?.toLocaleString() }}</span>
            </div>
            <div class="stat">
              <span class="label">測量記錄:</span>
              <span class="value">{{ bearing.measurement_count?.toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bearing Details -->
    <div v-if="selectedBearing" class="section">
      <h2>{{ selectedBearing }} 詳細資訊</h2>

      <!-- Tabs -->
      <div class="tabs">
        <button
          :class="{ active: activeTab === 'info' }"
          @click="activeTab = 'info'"
        >
          基本資訊
        </button>
        <button
          :class="{ active: activeTab === 'files' }"
          @click="activeTab = 'files'"
        >
          檔案列表
        </button>
        <button
          :class="{ active: activeTab === 'measurements' }"
          @click="activeTab = 'measurements'"
        >
          測量資料
        </button>
        <button
          :class="{ active: activeTab === 'anomalies' }"
          @click="activeTab = 'anomalies'"
        >
          異常檢測
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Info Tab -->
        <div v-if="activeTab === 'info'" class="info-tab">
          <div v-if="bearingInfo" class="info-grid">
            <div class="info-card">
              <h3>統計摘要</h3>
              <div class="info-item">
                <span class="label">軸承 ID:</span>
                <span class="value">{{ bearingInfo.bearing_id }}</span>
              </div>
              <div class="info-item">
                <span class="label">檔案數量:</span>
                <span class="value">{{ bearingInfo.file_count?.toLocaleString() }}</span>
              </div>
              <div class="info-item">
                <span class="label">測量記錄:</span>
                <span class="value">{{ bearingInfo.measurement_count?.toLocaleString() }}</span>
              </div>
            </div>

            <div class="info-card">
              <h3>水平加速度統計</h3>
              <div class="info-item">
                <span class="label">平均值:</span>
                <span class="value">{{ bearingInfo.acceleration_stats?.avg_h_acc?.toFixed(3) }}</span>
              </div>
              <div class="info-item">
                <span class="label">最小值:</span>
                <span class="value">{{ bearingInfo.acceleration_stats?.min_h_acc?.toFixed(3) }}</span>
              </div>
              <div class="info-item">
                <span class="label">最大值:</span>
                <span class="value">{{ bearingInfo.acceleration_stats?.max_h_acc?.toFixed(3) }}</span>
              </div>
              <div class="info-item">
                <span class="label">平均絕對值:</span>
                <span class="value">{{ bearingInfo.acceleration_stats?.avg_abs_h_acc?.toFixed(3) }}</span>
              </div>
            </div>

            <div class="info-card">
              <h3>垂直加速度統計</h3>
              <div class="info-item">
                <span class="label">平均值:</span>
                <span class="value">{{ bearingInfo.acceleration_stats?.avg_v_acc?.toFixed(3) }}</span>
              </div>
              <div class="info-item">
                <span class="label">最小值:</span>
                <span class="value">{{ bearingInfo.acceleration_stats?.min_v_acc?.toFixed(3) }}</span>
              </div>
              <div class="info-item">
                <span class="label">最大值:</span>
                <span class="value">{{ bearingInfo.acceleration_stats?.max_v_acc?.toFixed(3) }}</span>
              </div>
              <div class="info-item">
                <span class="label">平均絕對值:</span>
                <span class="value">{{ bearingInfo.acceleration_stats?.avg_abs_v_acc?.toFixed(3) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Files Tab -->
        <div v-if="activeTab === 'files'" class="files-tab">
          <div class="controls">
            <button @click="loadFiles(0)" :disabled="filesLoading">
              重新載入
            </button>
            <span class="page-info">
              顯示 {{ filesOffset + 1 }} - {{ Math.min(filesOffset + filesLimit, filesTotalCount) }}
              / 共 {{ filesTotalCount }} 筆
            </span>
          </div>

          <div v-if="filesLoading" class="loading">載入中...</div>
          <div v-else-if="files.length === 0" class="empty">無檔案資料</div>
          <div v-else class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>檔案編號</th>
                  <th>檔案名稱</th>
                  <th>記錄數</th>
                  <th>平均水平加速度</th>
                  <th>平均垂直加速度</th>
                  <th>最大絕對值(H)</th>
                  <th>最大絕對值(V)</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="file in files" :key="file.file_id">
                  <td>{{ file.file_number }}</td>
                  <td>{{ file.file_name }}</td>
                  <td>{{ file.record_count?.toLocaleString() }}</td>
                  <td>{{ file.avg_h_acc?.toFixed(3) }}</td>
                  <td>{{ file.avg_v_acc?.toFixed(3) }}</td>
                  <td>{{ file.max_abs_h_acc?.toFixed(3) }}</td>
                  <td>{{ file.max_abs_v_acc?.toFixed(3) }}</td>
                  <td>
                    <button
                      class="btn-small"
                      @click="loadFileData(file.file_number)"
                    >
                      查看資料
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div class="pagination">
            <button
              @click="loadFiles(Math.max(0, filesOffset - filesLimit))"
              :disabled="filesOffset === 0 || filesLoading"
            >
              上一頁
            </button>
            <button
              @click="loadFiles(filesOffset + filesLimit)"
              :disabled="filesOffset + filesLimit >= filesTotalCount || filesLoading"
            >
              下一頁
            </button>
          </div>
        </div>

        <!-- Measurements Tab -->
        <div v-if="activeTab === 'measurements'" class="measurements-tab">
          <div class="controls">
            <label>
              檔案編號 (選填):
              <input
                v-model.number="fileNumberFilter"
                type="number"
                placeholder="輸入檔案編號"
              />
            </label>
            <button @click="loadMeasurements(0)" :disabled="measurementsLoading">
              查詢
            </button>
            <span class="page-info">
              顯示 {{ measurementsOffset + 1 }} -
              {{ Math.min(measurementsOffset + measurementsLimit, measurementsTotalCount) }}
              / 共 {{ measurementsTotalCount?.toLocaleString() }} 筆
            </span>
          </div>

          <div v-if="measurementsLoading" class="loading">載入中...</div>
          <div v-else-if="measurements.length === 0" class="empty">無測量資料</div>
          <div v-else class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>檔案編號</th>
                  <th>時:分:秒.微秒</th>
                  <th>水平加速度</th>
                  <th>垂直加速度</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="m in measurements" :key="m.measurement_id">
                  <td>{{ m.file_number }}</td>
                  <td>{{ m.hour }}:{{ m.minute }}:{{ m.second }}.{{ m.microsecond }}</td>
                  <td>{{ m.horizontal_acceleration?.toFixed(3) }}</td>
                  <td>{{ m.vertical_acceleration?.toFixed(3) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div class="pagination">
            <button
              @click="loadMeasurements(Math.max(0, measurementsOffset - measurementsLimit))"
              :disabled="measurementsOffset === 0 || measurementsLoading"
            >
              上一頁
            </button>
            <button
              @click="loadMeasurements(measurementsOffset + measurementsLimit)"
              :disabled="measurementsOffset + measurementsLimit >= measurementsTotalCount || measurementsLoading"
            >
              下一頁
            </button>
          </div>
        </div>

        <!-- Anomalies Tab -->
        <div v-if="activeTab === 'anomalies'" class="anomalies-tab">
          <div class="controls">
            <label>
              水平閾值:
              <input
                v-model.number="thresholdH"
                type="number"
                step="0.1"
              />
            </label>
            <label>
              垂直閾值:
              <input
                v-model.number="thresholdV"
                type="number"
                step="0.1"
              />
            </label>
            <button @click="searchAnomalies" :disabled="anomaliesLoading">
              搜尋異常
            </button>
          </div>

          <div v-if="anomaliesLoading" class="loading">載入中...</div>
          <div v-else-if="anomalies.length === 0" class="empty">
            無異常資料 (閾值: H={{ thresholdH }}, V={{ thresholdV }})
          </div>
          <div v-else>
            <p class="anomaly-count">找到 {{ anomalies.length }} 筆異常資料</p>
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>檔案編號</th>
                    <th>檔案名稱</th>
                    <th>時間</th>
                    <th>水平加速度</th>
                    <th>垂直加速度</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="a in anomalies"
                    :key="a.measurement_id"
                    :class="{
                      'anomaly-h': Math.abs(a.horizontal_acceleration) > thresholdH,
                      'anomaly-v': Math.abs(a.vertical_acceleration) > thresholdV
                    }"
                  >
                    <td>{{ a.file_number }}</td>
                    <td>{{ a.file_name }}</td>
                    <td>{{ a.hour }}:{{ a.minute }}:{{ a.second }}.{{ a.microsecond }}</td>
                    <td :class="{ highlight: Math.abs(a.horizontal_acceleration) > thresholdH }">
                      {{ a.horizontal_acceleration?.toFixed(3) }}
                    </td>
                    <td :class="{ highlight: Math.abs(a.vertical_acceleration) > thresholdV }">
                      {{ a.vertical_acceleration?.toFixed(3) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { getApiUrl } from '@/config/api'

// 使用環境變數配置 API_BASE URL，避免硬編碼
// 原始配置: const API_BASE = 'http://localhost:8000'
// 修改: 統一 Backend 伺服器運行在 port 8081
// 現在: 使用環境變數 VITE_API_BASE_URL 從 .env 檔案讀取
const API_BASE = getApiUrl('api')

// State
const loading = ref(false)
const error = ref(null)
const bearings = ref([])
const selectedBearing = ref(null)
const bearingInfo = ref(null)
const activeTab = ref('info')

// Files
const files = ref([])
const filesLoading = ref(false)
const filesOffset = ref(0)
const filesLimit = ref(20)
const filesTotalCount = ref(0)

// Measurements
const measurements = ref([])
const measurementsLoading = ref(false)
const measurementsOffset = ref(0)
const measurementsLimit = ref(100)
const measurementsTotalCount = ref(0)
const fileNumberFilter = ref(null)

// Anomalies
const anomalies = ref([])
const anomaliesLoading = ref(false)
const thresholdH = ref(10.0)
const thresholdV = ref(10.0)

// Load bearings list
const loadBearings = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get(`${API_BASE}/api/phm/database/bearings`)
    bearings.value = response.data.bearings
  } catch (err) {
    error.value = err.response?.data?.detail || err.message
  } finally {
    loading.value = false
  }
}

// Select bearing
const selectBearing = async (bearingName) => {
  selectedBearing.value = bearingName
  activeTab.value = 'info'
  await loadBearingInfo(bearingName)
}

// Load bearing info
const loadBearingInfo = async (bearingName) => {
  try {
    const response = await axios.get(
      `${API_BASE}/api/phm/database/bearing/${bearingName}`
    )
    bearingInfo.value = response.data
  } catch (err) {
    console.error('Error loading bearing info:', err)
  }
}

// Load files
const loadFiles = async (offset) => {
  if (!selectedBearing.value) return

  filesLoading.value = true
  filesOffset.value = offset
  try {
    const response = await axios.get(
      `${API_BASE}/api/phm/database/bearing/${selectedBearing.value}/files`,
      { params: { offset, limit: filesLimit.value } }
    )
    files.value = response.data.files
    filesTotalCount.value = response.data.total_count
  } catch (err) {
    console.error('Error loading files:', err)
  } finally {
    filesLoading.value = false
  }
}

// Load measurements
const loadMeasurements = async (offset) => {
  if (!selectedBearing.value) return

  measurementsLoading.value = true
  measurementsOffset.value = offset
  try {
    const params = { offset, limit: measurementsLimit.value }
    if (fileNumberFilter.value) {
      params.file_number = fileNumberFilter.value
    }

    const response = await axios.get(
      `${API_BASE}/api/phm/database/bearing/${selectedBearing.value}/measurements`,
      { params }
    )
    measurements.value = response.data.measurements
    measurementsTotalCount.value = response.data.total_count
  } catch (err) {
    console.error('Error loading measurements:', err)
  } finally {
    measurementsLoading.value = false
  }
}

// Load file data
const loadFileData = async (fileNumber) => {
  activeTab.value = 'measurements'
  fileNumberFilter.value = fileNumber
  await loadMeasurements(0)
}

// Search anomalies
const searchAnomalies = async () => {
  if (!selectedBearing.value) return

  anomaliesLoading.value = true
  try {
    const response = await axios.get(
      `${API_BASE}/api/phm/database/bearing/${selectedBearing.value}/anomalies`,
      {
        params: {
          threshold_h: thresholdH.value,
          threshold_v: thresholdV.value,
          limit: 100
        }
      }
    )
    anomalies.value = response.data.anomalies
  } catch (err) {
    console.error('Error searching anomalies:', err)
  } finally {
    anomaliesLoading.value = false
  }
}

// Initialize
onMounted(() => {
  loadBearings()
})
</script>

<style scoped>
/* ===== 原始：淺色主題 ===== */
/* ===== 修改為：Apple Keynote 深色漸層主題 ===== */
/* ===== 參照 FONT.md 和 common-styles.css 統一樣式 ===== */
/* 基礎樣式(h1, h2, h3, p, code)已由 common-styles.css 統一管理 */

/* ===== CSS 變數定義 ===== */
:root {
  --text-primary: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-disabled: rgba(255, 255, 255, 0.3);
  --bg-primary: rgba(30, 30, 30, 0.8);
  --bg-secondary: rgba(50, 50, 50, 0.6);
  --bg-tertiary: rgba(70, 70, 70, 0.5);
  --bg-card: rgba(40, 40, 40, 0.7);
  --border-color: rgba(255, 255, 255, 0.15);
  --border-color-light: rgba(255, 255, 255, 0.08);
  --accent-primary: #667eea;
  --accent-hover: #5568d3;
  --accent-success: #48bb78;
  --accent-warning: #ed8936;
  --accent-danger: #f56565;
  --accent-info: #4299e1;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
}

.phm-database {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.section {
  background: var(--bg-card);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px var(--shadow-sm);
}

.section h2 {
  color: var(--text-primary);
  margin-bottom: 1rem;
  border-bottom: 2px solid var(--accent-primary);
  padding-bottom: 0.5rem;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.error {
  color: var(--accent-danger);
}

/* Bearings Grid */
.bearings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.bearing-card {
  border: 2px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  background: var(--bg-card);
}

.bearing-card:hover {
  border-color: var(--accent-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px var(--shadow-md);
}

.bearing-card.active {
  border-color: var(--accent-success);
  background: var(--bg-secondary);
}

.bearing-card h3 {
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.stat .label {
  color: var(--text-secondary);
}

.stat .value {
  font-weight: bold;
  color: var(--text-primary);
}

/* Tabs */
.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid var(--border-color);
}

/* 原始：繼承預設顏色 */
/* 修改：深色主題按鈕樣式 */
.tabs button {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 1rem;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tabs button:hover {
  color: var(--accent-primary);
}

.tabs button.active {
  color: var(--accent-primary);
  border-bottom-color: var(--accent-primary);
}

.tab-content {
  padding: 1rem 0;
}

/* Info Tab */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.info-card {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  background: var(--bg-card);
}

.info-card h3 {
  color: var(--accent-primary);
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-color-light);
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: var(--text-secondary);
}

.info-item .value {
  font-weight: bold;
  color: var(--text-primary);
}

/* Controls */
.controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.controls label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-primary);
}

/* 原始：繼承預設顏色 */
/* 修改：深色主題輸入框樣式 */
.controls input {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  width: 150px;
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.controls input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

/* 原始：繼承預設顏色 */
/* 修改：深色主題按鈕樣式 */
.controls button {
  padding: 0.5rem 1rem;
  background: var(--accent-info);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.controls button:hover:not(:disabled) {
  background: var(--accent-primary);
}

.controls button:disabled {
  background: var(--text-disabled);
  cursor: not-allowed;
  opacity: 0.5;
}

.page-info {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* Table */
.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.data-table th,
.data-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-weight: bold;
}

.data-table tr:hover {
  background: var(--bg-secondary);
}

/* 原始：繼承預設顏色 */
/* 修改：深色主題按鈕樣式 */
.btn-small {
  padding: 0.25rem 0.75rem;
  background: var(--accent-info);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-small:hover {
  background: var(--accent-primary);
}

/* Pagination */
.pagination {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1rem;
}

/* 原始：繼承預設顏色 */
/* 修改：深色主題按鈕樣式 */
.pagination button {
  padding: 0.5rem 1rem;
  background: var(--accent-info);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.pagination button:hover:not(:disabled) {
  background: var(--accent-primary);
}

.pagination button:disabled {
  background: var(--text-disabled);
  cursor: not-allowed;
  opacity: 0.5;
}

/* Anomalies */
.anomaly-count {
  margin-bottom: 1rem;
  font-weight: bold;
  color: var(--accent-danger);
}

.data-table tr.anomaly-h,
.data-table tr.anomaly-v {
  background: var(--bg-secondary);
}

.data-table td.highlight {
  color: var(--accent-danger);
  font-weight: bold;
}
</style>
