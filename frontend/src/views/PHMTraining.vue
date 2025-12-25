<template>
  <div class="phm-training">
    <el-card class="header-card">
      <h2>📊 PHM 2012 訓練數據視覺化</h2>
      <p>IEEE PHM Data Challenge - Learning Set Analysis</p>
    </el-card>

    <!-- 載入狀態 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>載入訓練數據中...</p>
    </div>

    <!-- 數據摘要表格 -->
    <el-card v-if="!loading && trainingData" class="summary-card">
      <template #header>
        <div class="card-header">
          <span>訓練集摘要</span>
          <el-tag type="info">共 {{ trainingData.total_bearings }} 個軸承</el-tag>
        </div>
      </template>

      <el-table :data="trainingData.bearings" stripe style="width: 100%">
        <el-table-column prop="name" label="軸承編號" width="120" />
        <el-table-column label="操作條件" width="120">
          <template #default="scope">
            <el-tag :type="getConditionType(scope.row.condition)">
              Condition {{ scope.row.condition }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="load_N" label="負載 (N)" width="100" />
        <el-table-column prop="speed_rpm" label="轉速 (RPM)" width="120" />
        <el-table-column prop="actual_RUL_min" label="實際 RUL (分鐘)" width="150">
          <template #default="scope">
            <strong>{{ scope.row.actual_RUL_min }}</strong>
          </template>
        </el-table-column>
        <el-table-column prop="num_files" label="數據文件數" width="120" />
        <el-table-column prop="total_duration_min" label="總時長 (分鐘)" width="130" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="viewBearingDetails(scope.row)"
            >
              查看詳情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 統計圖表 -->
    <el-row :gutter="20" v-if="!loading && statisticsData.length > 0">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>振動趨勢分析</span>
              <el-select
                v-model="selectedBearing"
                placeholder="選擇軸承"
                style="width: 200px"
              >
                <el-option
                  v-for="bearing in bearingOptions"
                  :key="bearing"
                  :label="bearing"
                  :value="bearing"
                />
              </el-select>
            </div>
          </template>

          <canvas ref="chartContainer" style="width: 100%; height: 400px"></canvas>
        </el-card>
      </el-col>
    </el-row>

    <!-- 峰度趨勢圖 -->
    <el-row :gutter="20" v-if="!loading && statisticsData.length > 0">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <span>峰度趨勢分析（故障指標）</span>
          </template>

          <canvas ref="kurtosisChartContainer" style="width: 100%; height: 400px"></canvas>
        </el-card>
      </el-col>
    </el-row>

    <!-- 數據分析說明 -->
    <el-card class="info-card">
      <template #header>
        <span>📖 數據說明</span>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="數據集">PHM IEEE 2012 Challenge - Learning Set</el-descriptions-item>
        <el-descriptions-item label="採樣率">25,600 Hz</el-descriptions-item>
        <el-descriptions-item label="操作條件">3 種不同負載-轉速組合</el-descriptions-item>
        <el-descriptions-item label="數據類型">水平 + 垂直振動</el-descriptions-item>
        <el-descriptions-item label="峰度正常值">≈ 3</el-descriptions-item>
        <el-descriptions-item label="峰度異常值">> 5-10 表示故障</el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <h4>關鍵發現：</h4>
      <ul>
        <li>✅ <strong>峰度是最可靠的早期故障指標</strong>，在多數案例中提供 1000-3000 分鐘預警</li>
        <li>✅ <strong>垂直振動通常比水平振動更早顯示退化跡象</strong></li>
        <li>⚠️ Bearing3_1 (高負載 5000N) 具有最短壽命 (5730 分鐘) 和最突發的故障模式</li>
        <li>⭐ Bearing1_1 擁有最豐富數據 (2803 files) 和最長壽命 (28020 分鐘)</li>
      </ul>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/stores/api'
import { Chart } from 'chart.js/auto'

const loading = ref(true)
const trainingData = ref(null)
const statisticsData = ref([])
const selectedBearing = ref('Bearing1_1')
const bearingOptions = ref([])
const chartContainer = ref(null)
const kurtosisChartContainer = ref(null)
let vibrationChart = null
let kurtosisChart = null

const getConditionType = (condition) => {
  const types = { 1: 'primary', 2: 'warning', 3: 'success' }
  return types[condition] || 'info'
}

const loadTrainingData = async () => {
  try {
    loading.value = true

    // 載入摘要數據
    const summaryData = await api.getPHMTrainingSummary()
    trainingData.value = summaryData
    console.log('Training summary loaded:', summaryData)

    // 載入統計數據
    const analysisData = await api.getPHMAnalysisData()
    const stats = analysisData.statistics

    statisticsData.value = stats
    bearingOptions.value = [...new Set(stats.map(s => s.bearing_name))]
    console.log('Statistics data loaded:', stats.length, 'records')
    console.log('Bearing options:', bearingOptions.value)

    loading.value = false

    // 等待 DOM 更新後再渲染圖表
    await nextTick()
    renderCharts()
  } catch (error) {
    console.error('Failed to load training data:', error)
    ElMessage.error('載入訓練數據失敗: ' + (error.response?.data?.detail || error.message))
    loading.value = false
  }
}

const renderCharts = () => {
  renderVibrationChart()
  renderKurtosisChart()
}

const renderVibrationChart = () => {
  if (!chartContainer.value) {
    console.error('Chart container not found')
    return
  }

  const bearingData = statisticsData.value.filter(
    d => d.bearing_name === selectedBearing.value
  )

  console.log('Rendering vibration chart for:', selectedBearing.value)
  console.log('Bearing data points:', bearingData.length)

  if (bearingData.length === 0) {
    console.warn('No data for bearing:', selectedBearing.value)
    return
  }

  if (vibrationChart) {
    vibrationChart.destroy()
  }

  const ctx = chartContainer.value.getContext('2d')
  vibrationChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: bearingData.map(d => d.time_min),
      datasets: [
        {
          label: '水平振動 RMS',
          data: bearingData.map(d => d.horiz_rms),
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          tension: 0.1,
          pointRadius: 1,
          borderWidth: 2
        },
        {
          label: '垂直振動 RMS',
          data: bearingData.map(d => d.vert_rms),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.1)',
          tension: 0.1,
          pointRadius: 1,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: `${selectedBearing.value} - 振動 RMS 趨勢`
        },
        legend: {
          position: 'top'
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: '時間 (分鐘)'
          }
        },
        y: {
          title: {
            display: true,
            text: 'RMS 值'
          },
          beginAtZero: false
        }
      }
    }
  })
  console.log('Vibration chart rendered successfully')
}

const renderKurtosisChart = () => {
  if (!kurtosisChartContainer.value) {
    console.error('Kurtosis chart container not found')
    return
  }

  const bearingData = statisticsData.value.filter(
    d => d.bearing_name === selectedBearing.value
  )

  console.log('Rendering kurtosis chart for:', selectedBearing.value)
  console.log('Bearing data points:', bearingData.length)

  if (bearingData.length === 0) {
    console.warn('No data for bearing:', selectedBearing.value)
    return
  }

  if (kurtosisChart) {
    kurtosisChart.destroy()
  }

  const ctx = kurtosisChartContainer.value.getContext('2d')
  kurtosisChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: bearingData.map(d => d.time_min),
      datasets: [
        {
          label: '水平振動峰度',
          data: bearingData.map(d => d.horiz_kurtosis),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          tension: 0.1,
          pointRadius: 1,
          borderWidth: 2
        },
        {
          label: '垂直振動峰度',
          data: bearingData.map(d => d.vert_kurtosis),
          borderColor: 'rgb(153, 102, 255)',
          backgroundColor: 'rgba(153, 102, 255, 0.1)',
          tension: 0.1,
          pointRadius: 1,
          borderWidth: 2
        },
        {
          label: '正常閾值 (≈3)',
          data: Array(bearingData.length).fill(3),
          borderColor: 'rgb(255, 206, 86)',
          borderDash: [5, 5],
          borderWidth: 2,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: `${selectedBearing.value} - 峰度趨勢（故障指標）`
        },
        legend: {
          position: 'top'
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: '時間 (分鐘)'
          }
        },
        y: {
          title: {
            display: true,
            text: '峰度值'
          },
          beginAtZero: false
        }
      }
    }
  })
  console.log('Kurtosis chart rendered successfully')
}

const viewBearingDetails = (bearing) => {
  selectedBearing.value = bearing.name
  renderVibrationChart()
  renderKurtosisChart()

  // 滾動到圖表區域
  const chartCard = document.querySelector('.chart-card')
  if (chartCard) {
    chartCard.scrollIntoView({ behavior: 'smooth' })
  }
}

watch(selectedBearing, () => {
  renderVibrationChart()
  renderKurtosisChart()
})

onMounted(() => {
  loadTrainingData()
})
</script>

<style scoped>
/* ===== 參照 FONT.md 和 common-styles.css 統一樣式 ===== */
/* 基礎樣式(h2, h4, p, code)已由 common-styles.css 統一管理 */

.phm-training {
  max-width: 1400px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 20px;
  /* 深色主題漸層背景 */
  background: linear-gradient(135deg, var(--theme-mid), var(--theme-lower-mid));
  color: white;
}

.header-card h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.header-card p {
  margin: 0;
  opacity: 0.9;
}

.loading-container {
  text-align: center;
  padding: 60px;
}

.loading-container .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.summary-card,
.chart-card,
.info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-primary);
}

.info-card h4 {
  margin: 16px 0 8px 0;
  color: var(--accent-info);
}

.info-card ul {
  margin: 8px 0;
  padding-left: 24px;
}

.info-card li {
  margin: 8px 0;
  line-height: 1.6;
  color: var(--text-secondary);
}
</style>
