<template>
  <div class="realtime-analysis">
    <!-- Header Card with Controls -->
    <el-card class="header-card">
      <div class="header-content">
        <h2>📡 即時分析監控</h2>
        <div class="controls">
          <el-input-number
            v-model="sensorId"
            :min="1"
            :max="100"
            placeholder="Sensor ID"
            :disabled="isStreaming"
            style="width: 150px; margin-right: 10px"
          />
          <el-button
            v-if="!isStreaming"
            type="primary"
            @click="startStreaming"
            :loading="connecting"
          >
            開始監控
          </el-button>
          <el-button
            v-else
            type="danger"
            @click="stopStreaming"
          >
            停止監控
          </el-button>
          <el-tag
            :type="connectionStatusType"
            style="margin-left: 10px"
          >
            {{ connectionStatusText }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- Alert Panel -->
    <el-card v-if="hasAlerts" class="alerts-card">
      <template #header>
        <div class="alert-header">
          <span style="color: var(--accent-danger)">⚠️ 警報訊息</span>
          <el-badge :value="alertHistory.length" class="alert-badge" />
        </div>
      </template>
      <div
        v-for="alert in alertHistory.slice(0, 5)"
        :key="alert.alert_id || alert.received_at"
        class="alert-item"
      >
        <el-tag :type="getAlertType(alert.severity)">
          {{ alert.severity ? alert.severity.toUpperCase() : 'WARNING' }}
        </el-tag>
        <span class="alert-message">{{ alert.message }}</span>
        <span class="alert-time">{{ formatTime(alert.created_at || alert.received_at) }}</span>
      </div>
    </el-card>

    <!-- Real-time Features Display -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="feature in featureCards" :key="feature.key">
        <el-card class="feature-card">
          <div class="feature-value">
            {{ formatFeatureValue(feature.key) }}
          </div>
          <div class="feature-label">{{ feature.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Real-time Charts -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>RMS 趨勢</span>
              <el-tag size="small" type="info">{{ featureCount }} 點</el-tag>
            </div>
          </template>
          <div ref="rmsChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>Kurtosis 趨勢</span>
              <el-tag size="small" type="info">{{ featureCount }} 點</el-tag>
            </div>
          </template>
          <div ref="kurtosisChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Additional Charts -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>Peak 趨勢</span>
              <el-tag size="small" type="info">{{ featureCount }} 點</el-tag>
            </div>
          </template>
          <div ref="peakChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>Crest Factor 趨勢</span>
              <el-tag size="small" type="info">{{ featureCount }} 點</el-tag>
            </div>
          </template>
          <div ref="crestChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRealtimeStore } from '@/stores/realtime'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// Store
const realtimeStore = useRealtimeStore()
const {
  isConnected,
  isStreaming,
  latestFeatures,
  alertHistory,
  connectionStatus,
  featureBuffer,
  hasAlerts,
  featureCount,
  currentWindow
} = storeToRefs(realtimeStore)

// Refs
const sensorId = ref(1)
const connecting = ref(false)
const rmsChartRef = ref(null)
const kurtosisChartRef = ref(null)
const peakChartRef = ref(null)
const crestChartRef = ref(null)

// Chart instances
let rmsChart = null
let kurtosisChart = null
let peakChart = null
let crestChart = null

// Feature cards configuration
const featureCards = [
  { key: 'rms_h', label: 'RMS (水平)' },
  { key: 'rms_v', label: 'RMS (垂直)' },
  { key: 'kurtosis_h', label: 'Kurtosis (水平)' },
  { key: 'kurtosis_v', label: 'Kurtosis (垂直)' },
  { key: 'peak_h', label: 'Peak (水平)' },
  { key: 'peak_v', label: 'Peak (垂直)' },
  { key: 'crest_factor_h', label: 'Crest Factor (水平)' },
  { key: 'crest_factor_v', label: 'Crest Factor (垂直)' }
]

// Computed
const connectionStatusType = computed(() => {
  const status = connectionStatus.value
  if (status === 'connected') return 'success'
  if (status === 'connecting') return 'warning'
  if (status === 'error') return 'danger'
  return 'info'
})

const connectionStatusText = computed(() => {
  const status = connectionStatus.value
  const statusMap = {
    'disconnected': '未連接',
    'connecting': '連接中',
    'connected': '已連接',
    'error': '連接錯誤'
  }
  return statusMap[status] || '未知'
})

// Methods
async function startStreaming() {
  connecting.value = true
  try {
    // 清空舊的緩衝區資料
    realtimeStore.clearBuffers()

    // 重新初始化圖表,清空舊資料
    if (rmsChart) {
      rmsChart.setOption({ xAxis: { data: [] }, series: [{ data: [] }, { data: [] }] })
    }
    if (kurtosisChart) {
      kurtosisChart.setOption({ xAxis: { data: [] }, series: [{ data: [] }, { data: [] }] })
    }
    if (peakChart) {
      peakChart.setOption({ xAxis: { data: [] }, series: [{ data: [] }, { data: [] }] })
    }
    if (crestChart) {
      crestChart.setOption({ xAxis: { data: [] }, series: [{ data: [] }, { data: [] }] })
    }

    realtimeStore.connect(sensorId.value)
    ElMessage.success('開始即時監控')
  } catch (error) {
    ElMessage.error('連接失敗')
    console.error('Connection error:', error)
  } finally {
    connecting.value = false
  }
}

function stopStreaming() {
  realtimeStore.disconnect()
  ElMessage.info('停止監控')
}

function formatFeatureValue(key) {
  const value = latestFeatures.value[key]
  return value !== undefined ? value.toFixed(4) : '--'
}

function formatTime(timestamp) {
  if (!timestamp) return '--'
  return new Date(timestamp).toLocaleTimeString('zh-TW')
}

function getAlertType(severity) {
  const types = {
    'critical': 'danger',
    'warning': 'warning',
    'info': 'info'
  }
  return types[severity] || 'info'
}

function initCharts() {
  // Common chart options - 深色主題
  const commonOption = {
    animation: false,
    backgroundColor: 'transparent',
    grid: {
      top: 30,
      right: 20,
      bottom: 50,  // 原始: 30, 修改: 50 - 增加底部空間以容納旋轉的標籤
      left: 60,
      // 原始：繼承預設
      // 修改：深色網格線
      borderColor: 'rgba(255, 255, 255, 0.1)'
    },
    xAxis: {
      type: 'category',
      data: [],
      axisLabel: {
        // 原始：rotate: 45
        // 修改：不自動旋轉，讓 ECharts 自動間隔顯示
        rotate: 0,
        // 原始：未設定
        // 修改：自動計算間隔，避免標籤重疊 (0 表示不自動)
        interval: 'auto',
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        color: '#ffffff',
        // 原始: 12
        // 修改: 13 - 增大軸標籤文字
        fontSize: 13,
        // 原始：未設定
        // 修改：標籤格式化，只顯示 時:分:秒
        formatter: function(value) {
          if (!value) return ''
          // value 已經是格式化後的時間字串
          return value
        }
      },
      // 原始：繼承預設顏色
      // 修改：深色軸線
      axisLine: { lineStyle: { color: '#ffffff' } },
      axisTick: { lineStyle: { color: '#ffffff' } },
      // 原始：繼承預設
      // 修改：深色網格線
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
    },
    yAxis: { 
      type: 'value',
      axisLabel: {
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        color: '#ffffff',
        // 原始: 12
        // 修改: 14 - 增大軸標籤文字
        fontSize: 14
      },
      // 原始：繼承預設顏色
      // 修改：深色軸線
      axisLine: { lineStyle: { color: '#ffffff' } },
      axisTick: { lineStyle: { color: '#ffffff' } },
      // 原始：繼承預設
      // 修改：深色網格線
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
    },
    tooltip: { 
      trigger: 'axis',
      // 原始：繼承預設
      // 修改：深色主題提示框
      backgroundColor: 'rgba(30, 30, 30, 0.9)',
      borderColor: 'var(--accent-primary)',
      textStyle: {
        color: '#ffffff'
      }
    },
    legend: { 
      data: [],
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      textStyle: {
        color: '#ffffff',
        // 原始: 12
        // 修改: 15 - 增大圖例文字
        fontSize: 15
      }
    }
  }

  // RMS Chart
  rmsChart = echarts.init(rmsChartRef.value)
  rmsChart.setOption({
    ...commonOption,
    legend: { data: ['水平', '垂直'] },
    series: [
      { 
        name: '水平', 
        type: 'line', 
        data: [], 
        smooth: true, 
        lineStyle: { width: 2 },
        // 原始：繼承預設顏色
        // 修改：使用強調色
        itemStyle: { color: 'rgb(54, 162, 235)' }
      },
      { 
        name: '垂直', 
        type: 'line', 
        data: [], 
        smooth: true, 
        lineStyle: { width: 2 },
        // 原始：繼承預設顏色
        // 修改：使用對比色
        itemStyle: { color: 'rgb(75, 192, 192)' }
      }
    ]
  })

  // Kurtosis Chart
  kurtosisChart = echarts.init(kurtosisChartRef.value)
  kurtosisChart.setOption({
    ...commonOption,
    legend: { data: ['水平', '垂直'] },
    series: [
      { 
        name: '水平', 
        type: 'line', 
        data: [], 
        smooth: true, 
        lineStyle: { width: 2 },
        // 原始：繼承預設顏色
        // 修改：使用強調色
        itemStyle: { color: 'rgb(255, 99, 132)' }
      },
      { 
        name: '垂直', 
        type: 'line', 
        data: [], 
        smooth: true, 
        lineStyle: { width: 2 },
        // 原始：繼承預設顏色
        // 修改：使用對比色
        itemStyle: { color: 'rgb(153, 102, 255)' }
      }
    ]
  })

  // Peak Chart
  peakChart = echarts.init(peakChartRef.value)
  peakChart.setOption({
    ...commonOption,
    legend: { data: ['水平', '垂直'] },
    series: [
      { 
        name: '水平', 
        type: 'line', 
        data: [], 
        smooth: true, 
        lineStyle: { width: 2 },
        // 原始：繼承預設顏色
        // 修改：使用強調色
        itemStyle: { color: 'rgb(255, 159, 64)' }
      },
      { 
        name: '垂直', 
        type: 'line', 
        data: [], 
        smooth: true, 
        lineStyle: { width: 2 },
        // 原始：繼承預設顏色
        // 修改：使用對比色
        itemStyle: { color: 'rgb(54, 162, 235)' }
      }
    ]
  })

  // Crest Factor Chart
  crestChart = echarts.init(crestChartRef.value)
  crestChart.setOption({
    ...commonOption,
    legend: { data: ['水平', '垂直'] },
    series: [
      { 
        name: '水平', 
        type: 'line', 
        data: [], 
        smooth: true, 
        lineStyle: { width: 2 },
        // 原始：繼承預設顏色
        // 修改：使用強調色
        itemStyle: { color: 'rgb(75, 192, 192)' }
      },
      { 
        name: '垂直', 
        type: 'line', 
        data: [], 
        smooth: true, 
        lineStyle: { width: 2 },
        // 原始：繼承預設顏色
        // 修改：使用對比色
        itemStyle: { color: 'rgb(255, 205, 86)' }
      }
    ]
  })
}

function updateCharts() {
  // 原始：手動過濾時間標籤，每 300 點顯示一次
  // 修改：提供所有時間戳，讓 ECharts 的 interval: 'auto' 自動處理間隔
  // 優點：ECharts 會根據可用空間自動調整標籤密度，避免擁擠

  const timestamps = currentWindow.value.timestamps.map(t => {
    const date = new Date(t)
    // 簡化時間格式，只顯示 時:分:秒
    return date.toLocaleTimeString('zh-TW', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  })

  // 只有當有資料時才更新圖表
  if (timestamps.length === 0) {
    return
  }

  // Update RMS Chart
  if (currentWindow.value.rms_h.length > 0 && currentWindow.value.rms_v.length > 0) {
    rmsChart.setOption({
      xAxis: { data: timestamps },
      series: [
        { data: currentWindow.value.rms_h },
        { data: currentWindow.value.rms_v }
      ]
    })
  }

  // Update Kurtosis Chart
  if (currentWindow.value.kurtosis_h.length > 0 && currentWindow.value.kurtosis_v.length > 0) {
    kurtosisChart.setOption({
      xAxis: { data: timestamps },
      series: [
        { data: currentWindow.value.kurtosis_h },
        { data: currentWindow.value.kurtosis_v }
      ]
    })
  }

  // Update Peak Chart
  if (currentWindow.value.peak_h.length > 0 && currentWindow.value.peak_v.length > 0) {
    peakChart.setOption({
      xAxis: { data: timestamps },
      series: [
        { data: currentWindow.value.peak_h },
        { data: currentWindow.value.peak_v }
      ]
    })
  }

  // Update Crest Factor Chart
  const crestH = currentWindow.value.crest_factor_h || []
  const crestV = currentWindow.value.crest_factor_v || []
  if (crestH.length > 0 && crestV.length > 0) {
    crestChart.setOption({
      xAxis: { data: timestamps },
      series: [
        { data: crestH },
        { data: crestV }
      ]
    })
  }
}

// Watch for feature updates - 監聽 featureCount 變化以確保圖表更新
watch(featureCount, (newCount) => {
  if (newCount > 0) {
    updateCharts()
  }
})

// Lifecycle
onMounted(() => {
  initCharts()

  // Handle window resize
  window.addEventListener('resize', () => {
    if (rmsChart) rmsChart.resize()
    if (kurtosisChart) kurtosisChart.resize()
    if (peakChart) peakChart.resize()
    if (crestChart) crestChart.resize()
  })
})

onUnmounted(() => {
  // Cleanup charts
  if (rmsChart) rmsChart.dispose()
  if (kurtosisChart) kurtosisChart.dispose()
  if (peakChart) peakChart.dispose()
  if (crestChart) crestChart.dispose()

  // Disconnect WebSocket
  realtimeStore.disconnect()
})
</script>

<style scoped>
/* 原始：淺色主題 */
/* 修改為：Apple Keynote 深色漸層主題 (與 Dashboard.vue 一致) */

/* ===== 字體設定 - 與 FONT.md 規範對齊 ===== */
/* 全局字體族設定（繼承自 style.css） */
/* font-family: system-ui, Avenir, Helvetica, Arial, sans-serif; */

/* ===== 標題層級字體大小設定（與 Dashboard.vue 一致）===== */
.realtime-analysis h2 {
  /* 原始: 24px */
  /* 修改: 與 FONT.md h2 規範對齊 (1.85em ≈ 29.6px) */
  font-size: 1.85em;
  line-height: 1.3;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0;
}

.realtime-analysis {
  padding: 20px;
  /* 原始：#f5f7fa */
  /* 修改：深色主題背景 */
  background: var(--bg-primary);
  min-height: 100vh;
}

/* ===== 卡片樣式 - 深色主題 ===== */
.realtime-analysis :deep(.el-card) {
  /* 卡片整體樣式 */
  background-color: var(--bg-card);
  border-color: var(--border-color);
}

.realtime-analysis :deep(.el-card__header) {
  /* 卡片標題區域 */
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.realtime-analysis :deep(.el-card__body) {
  /* 卡片內容區域 */
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.header-card {
  margin-bottom: 20px;
  border: none;
  /* 原始：box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1) */
  /* 修改：深色發光陰影 */
  box-shadow: 0 2px 12px var(--shadow-glow);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* ===== 警報卡片樣式 - 深色主題 ===== */
.alerts-card {
  margin-bottom: 20px;
  /* 原始：1px solid #F56C6C */
  /* 修改：使用危險色邊框 */
  border: 1px solid var(--accent-danger);
  /* 原始：box-shadow: 0 2px 12px 0 rgba(245, 108, 108, 0.2) */
  /* 修改：深色發光陰影 */
  box-shadow: 0 2px 12px rgba(245, 108, 108, 0.3);
}

.alerts-card :deep(.el-card__header) {
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--accent-danger);
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  /* 原始：1px solid #eee */
  /* 修改：深色淺邊框 */
  border-bottom: 1px solid var(--border-color-light);
  transition: background-color 0.3s;
}

.alert-item:hover {
  /* 原始：#fef0f0 */
  /* 修改：深色次要背景 */
  background-color: var(--bg-secondary);
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-message {
  flex: 1;
  /* 原始：#606266 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
}

.alert-time {
  margin-left: auto;
  color: var(--text-secondary);
  /* 原始：12px */
  /* 第一次修改: 14px - 增大時間文字 */
  /* 第二次修改: 15px - 進一步增大時間文字 */
  font-size: 15px;
}

/* ===== 特徵卡片樣式 - 深色主題 ===== */
.feature-card {
  text-align: center;
  padding: 15px;
  border: none;
  /* 原始：box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1) */
  /* 修改：深色發光陰影 */
  box-shadow: 0 2px 12px var(--shadow-glow);
  transition: transform 0.3s, box-shadow 0.3s;
  /* 原始：繼承白色背景 */
  /* 修改：深色卡片背景 */
  background: var(--bg-card);
}

.feature-card:hover {
  transform: translateY(-2px);
  /* 原始：box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15) */
  /* 修改：使用已有深色發光陰影，增強效果 */
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

.feature-value {
  /* 原始：28px */
  /* 第一次修改: 32px - 增大數值顯示 */
  /* 第二次修改: 35px - 進一步增大數值顯示 */
  font-size: 35px;
  font-weight: bold;
  /* 原始：#409EFF */
  /* 修改：使用強調色 */
  color: var(--accent-primary);
  margin-bottom: 8px;
}

.feature-label {
  /* 原始：14px */
  /* 第一次修改: 16px - 增大標籤文字 */
  /* 第二次修改: 17px - 進一步增大標籤文字 */
  font-size: 17px;
  /* 原始：#606266 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
  font-weight: 500;
}

/* ===== 圖表標題樣式 - 深色主題 ===== */
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: var(--text-primary);
  /* 原始：繼承預設 */
  /* 修改：與 FONT.md h4 規範對齊 (1.1em ≈ 17.6px) */
  font-size: 1.1em;
}

/* ===== el-tag 樣式 - 深色主題 ===== */
.realtime-analysis :deep(.el-tag) {
  /* 標籤樣式 */
  color: var(--text-primary);
  border-color: var(--border-color);
}

.realtime-analysis :deep(.el-tag--info) {
  /* Info 類型標籤 */
  background-color: var(--bg-secondary);
  border-color: var(--accent-info);
  color: var(--accent-info);
}

/* ===== el-button 按鈕樣式 - 深色主題 ===== */
.realtime-analysis :deep(.el-button) {
  /* 按鈕整體樣式 */
  color: var(--text-primary);
  border-color: var(--border-color);
}

.realtime-analysis :deep(.el-button--primary) {
  /* 主要按鈕 */
  background-color: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #ffffff;
}

.realtime-analysis :deep(.el-button--primary:hover) {
  /* 主要按鈕懸停 */
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.realtime-analysis :deep(.el-button--danger) {
  /* 危險按鈕 */
  background-color: var(--accent-danger);
  border-color: var(--accent-danger);
  color: #ffffff;
}

.realtime-analysis :deep(.el-button--danger:hover) {
  /* 危險按鈕懸停 */
  background-color: rgba(245, 108, 108, 0.8);
  border-color: var(--accent-danger);
}

.realtime-analysis :deep(.el-button--default) {
  /* 預設按鈕 */
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.realtime-analysis :deep(.el-button--default:hover) {
  /* 預設按鈕懸停 */
  background-color: var(--bg-tertiary);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.realtime-analysis :deep(.el-button--small) {
  /* 小按鈕 */
  padding: 5px 12px;
  /* 原始: 繼承 */
  /* 修改: 15px - 略微增大小按鈕文字,避免過大影響版面 */
  font-size: 15px;
}

/* ===== el-input-number 數字輸入框樣式 - 深色主題 ===== */
.realtime-analysis :deep(.el-input-number) {
  /* 數字輸入框整體 */
  color: var(--text-primary);
}

.realtime-analysis :deep(.el-input-number .el-input__wrapper) {
  /* 數字輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.realtime-analysis :deep(.el-input-number .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.realtime-analysis :deep(.el-input-number .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.realtime-analysis :deep(.el-input-number .el-input__inner) {
  /* 輸入框內部樣式 */
  background-color: transparent;
  color: var(--text-primary);
}

.realtime-analysis :deep(.el-input-number__decrease),
.realtime-analysis :deep(.el-input-number__increase) {
  /* 數字輸入框 +/- 按鈕 */
  background-color: var(--bg-secondary);
  border: none;
  color: var(--text-primary);
}

.realtime-analysis :deep(.el-input-number__decrease:hover),
.realtime-analysis :deep(.el-input-number__increase:hover) {
  /* 按鈕懸停效果 */
  color: var(--accent-primary);
  background-color: var(--bg-tertiary);
}

.realtime-analysis :deep(.el-input-number__decrease.is-disabled),
.realtime-analysis :deep(.el-input-number__increase.is-disabled) {
  /* 禁用狀態按鈕 */
  color: var(--text-disabled);
  background-color: var(--bg-secondary);
}
</style>
