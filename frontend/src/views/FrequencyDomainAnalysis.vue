<template>
  <div class="frequency-domain-page">
    <el-card>
      <template #header>
        <h2>頻域特徵分析</h2>
      </template>

      <!-- [修改] 移除嵌套 el-card，與 TimeDomainAnalysis.vue 保持一致 -->
      <!-- [原始] 使用嵌套 el-card shadow="never" 包裝原理說明區域 -->
      <!-- [修改後] 直接在主卡片內部顯示，結構與 TimeDomainAnalysis.vue 一致 -->
      <h3>原理說明</h3>
      <p>透過快速傅立葉轉換（FFT）將時域信號轉換為頻域，識別故障特徵頻率。</p>

      <h4 style="margin-top: 20px;">關鍵概念:</h4>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover">
            <h4>FFT（快速傅立葉轉換）</h4>
            <code>X(f) = ∫ x(t)e^(-j2πft) dt</code>
            <p>將時域信號轉為頻域</p>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <h4>FM0（正規化峰值）</h4>
            <code>FM0 = Peak / ΣE_harmonics</code>
            <p>峰值與諧波能量比值</p>
          </el-card>
        </el-col>
      </el-row>

      <h4 style="margin-top: 20px;">故障頻率:</h4>
      <el-table :data="faultFrequencies" border>
        <el-table-column prop="type" label="故障類型" />
        <el-table-column prop="frequency" label="特徵頻率" />
        <el-table-column prop="description" label="說明" />
      </el-table>

      <h4 style="margin-top: 20px;">應用場景:</h4>
      <el-tag type="danger" style="margin: 5px;">滾動體缺陷檢測</el-tag>
      <el-tag type="warning" style="margin: 5px;">軌道損傷檢測</el-tag>
      <el-tag type="info" style="margin: 5px;">安裝問題診斷</el-tag>

      <h4 style="margin-top: 20px;">IEEE PHM 2012 軸承故障頻率 (SKF 6205):</h4>
      <el-table :data="bearingFaultFrequencies" border>
        <el-table-column prop="bearing" label="軸承名稱" width="120" />
        <el-table-column prop="rpm" label="轉速(RPM)" width="100" />
        <el-table-column prop="shaft_freq" label="軸頻率(Hz)" width="100" />
        <el-table-column prop="bpfo" label="BPFO(Hz)" width="100">
          <template #default="scope">
            <el-tag type="danger">{{ scope.row.bpfo }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="bpfi" label="BPFI(Hz)" width="100">
          <template #default="scope">
            <el-tag type="warning">{{ scope.row.bpfi }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="bsf" label="BSF(Hz)" width="100" />
        <el-table-column prop="ftf" label="FTF(Hz)" width="100" />
        <el-table-column prop="description" label="說明" />
      </el-table>

      <!-- 頻域計算區域 -->
      <el-divider>即時計算演示</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form label-width="120px">
            <el-form-item label="選擇軸承">
              <el-select v-model="frequencyDomainParams.bearingName" placeholder="請選擇軸承">
                <el-option label="Bearing1_1" value="Bearing1_1" />
                <el-option label="Bearing1_2" value="Bearing1_2" />
                <el-option label="Bearing2_1" value="Bearing2_1" />
                <el-option label="Bearing2_2" value="Bearing2_2" />
                <el-option label="Bearing3_1" value="Bearing3_1" />
              </el-select>
            </el-form-item>
            <el-form-item label="檔案編號">
              <el-input-number v-model="frequencyDomainParams.fileNumber" :min="1" :max="100" />
            </el-form-item>
            <el-form-item label="方法選擇">
              <el-radio-group v-model="frequencyMethod">
                <el-radio label="fft">低頻FFT (FM0)</el-radio>
                <el-radio label="tsa">高頻TSA (FM0)</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="calculateFrequencyDomain" :loading="frequencyDomainLoading">
                計算頻域特徵
              </el-button>
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="12" v-if="frequencyDomainResult">
          <el-card shadow="hover">
            <template #header>
              <h4>計算結果</h4>
            </template>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="資料點數">
                {{ frequencyDomainResult.data_points || frequencyDomainResult.sampling_rate }}
              </el-descriptions-item>
              <el-descriptions-item label="軸承名稱">
                {{ frequencyDomainResult.bearing_name }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 Low FM0" v-if="frequencyMethod === 'fft'">
                {{ frequencyDomainResult.horizontal?.low_fm0?.toFixed(6) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 High FM0" v-if="frequencyMethod === 'tsa'">
                {{ frequencyDomainResult.horizontal?.high_fm0?.toFixed(6) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 Low FM0" v-if="frequencyMethod === 'fft'">
                {{ frequencyDomainResult.vertical?.low_fm0?.toFixed(6) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 High FM0" v-if="frequencyMethod === 'tsa'">
                {{ frequencyDomainResult.vertical?.high_fm0?.toFixed(6) }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>

      <!-- 頻譜圖 -->
      <div v-if="frequencyDomainResult" style="margin-top: 20px;">
        <el-card>
          <template #header>
            <h4>頻域頻譜圖</h4>
          </template>
          <div ref="frequencyDomainChart" style="width: 100%; height: 400px;"></div>
        </el-card>
      </div>

      <!-- ==================== 完整頻域特徵趨勢分析 ==================== -->
      <el-divider>完整頻域特徵趨勢分析</el-divider>

      <el-card shadow="never" style="margin-bottom: 20px;">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form label-width="120px">
              <el-form-item label="選擇軸承">
                <el-select v-model="trendParams.bearingName" placeholder="請選擇軸承">
                  <el-option label="Bearing1_1" value="Bearing1_1" />
                  <el-option label="Bearing1_2" value="Bearing1_2" />
                  <el-option label="Bearing2_1" value="Bearing2_1" />
                  <el-option label="Bearing2_2" value="Bearing2_2" />
                  <el-option label="Bearing3_1" value="Bearing3_1" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="success" @click="calculateTrend" :loading="trendLoading" :disabled="trendLoading">
                  <el-icon v-if="trendLoading"><Loading /></el-icon>
                  計算完整頻域特徵
                </el-button>
              </el-form-item>
            </el-form>
          </el-col>
          <el-col :span="16" v-if="trendResult">
            <el-card shadow="hover">
              <template #header>
                <h4>處理摘要</h4>
              </template>
              <el-descriptions :column="3" border size="small">
                <el-descriptions-item label="軸承名稱">
                  {{ trendResult.bearing_name }}
                </el-descriptions-item>
                <el-descriptions-item label="檔案數量">
                  {{ trendResult.file_count }}
                </el-descriptions-item>
                <el-descriptions-item label="處理時間">
                  {{ trendResult.processing_time?.toFixed(2) }} 秒
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
        </el-row>

        <!-- 進度提示 -->
        <el-alert
          v-if="trendLoading"
          title="正在計算所有檔案的頻域特徵，請稍候..."
          type="info"
          :closable="false"
          show-icon
          style="margin-top: 15px;"
        >
          此過程可能需要較長時間，取決於檔案數量。
        </el-alert>
      </el-card>

      <!-- 趨勢圖表區域 -->
      <!-- [原代碼] 使用 :span="12" 雙列布局 -->
      <!-- [修改] 改為 :span="24" 單列布局，圖表垂直排列 -->
      <div v-if="trendResult" style="margin-top: 20px;">
        <el-row :gutter="20">
          <el-col :span="24" v-for="feature in featureConfig" :key="feature.key">
            <el-card style="margin-bottom: 20px;">
              <template #header>
                <h4>{{ feature.title }}</h4>
              </template>
              <div :ref="el => setTrendChartRef(feature.key, el)" style="width: 100%; height: 350px;"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- [已移除] 表格資料 - 完整資料表格區域已刪除 -->
    </el-card>
  </div>
</template>

<script setup>
// [原代碼] import { ref, nextTick, computed } from 'vue'
// [修改] 移除 computed (表格分頁已移除)
import { ref, nextTick } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== 原有頻域計算 ====================
// 頻域計算參數
const frequencyDomainParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1
})
const frequencyMethod = ref('fft')
const frequencyDomainLoading = ref(false)
const frequencyDomainResult = ref(null)

// Chart refs
const frequencyDomainChart = ref(null)

// ==================== 新增趨勢分析 ====================
// 趨勢計算參數
const trendParams = ref({
  bearingName: 'Bearing1_1'
})
const trendLoading = ref(false)
const trendResult = ref(null)

// 趨勢圖表 refs
const trendChartRefs = ref({})

// 特徵配置
// [原代碼] 包含 6 個特徵：low_fm0, high_fm0, mgs_low, bi_low, mgs_high, bi_high
// [修改] 移除 Motor Gear Sideband (mgs_low, mgs_high) 和 Belt Index (bi_low, bi_high) 相關特徵
const featureConfig = [
  { key: 'low_fm0', title: '低頻 FM0 趨勢' },
  { key: 'high_fm0', title: '高頻 FM0 趨勢' }
  // { key: 'mgs_low', title: 'Motor Gear Sideband (低頻) 趨勢' },  // [已移除]
  // { key: 'bi_low', title: 'Belt Index (低頻) 趨勢' },  // [已移除]
  // { key: 'mgs_high', title: 'Motor Gear Sideband (高頻) 趨勢' },  // [已移除]
  // { key: 'bi_high', title: 'Belt Index (高頻) 趨勢' }  // [已移除]
]

// [已移除] 表格分頁相關程式碼 - paginatedTableData, tablePagination

// 設置趨勢圖表 ref
const setTrendChartRef = (key, el) => {
  if (el) {
    trendChartRefs.value[key] = el
  }
}

// 故障頻率表格數據
const faultFrequencies = [
  { type: 'BPFO', frequency: '外圈故障頻率', description: '滾珠通過外環缺陷頻率 = N·(1-d/D)·f_r/2' },
  { type: 'BPFI', frequency: '內圈故障頻率', description: '滾珠通過內環缺陷頻率 = N·(1+d/D)·f_r/2' },
  { type: 'BSF', frequency: '滾珠故障頻率', description: '滾珠自轉頻率 = D·[1-(d/D)²]·f_r/(2d)' },
  { type: 'FTF', frequency: '保持架頻率', description: '保持架旋轉頻率 = (1-d/D)·f_r/2' }
]

// 軸承故障頻率數據（基於 IEEE PHM 2012 Challenge EXPERIMENT.md 的官方操作條件）
// 條件 1: 1800 rpm, 4000 N → Bearing1_1, Bearing1_2
// 條件 2: 1650 rpm, 4200 N → Bearing2_1, Bearing2_2
// 條件 3: 1500 rpm, 5000 N → Bearing3_1, Bearing3_2
const bearingFaultFrequencies = [
  { bearing: 'Bearing1_1', rpm: 1800, shaft_freq: 30.0, bpfo: 107.91, bpfi: 172.09, bsf: 70.89, ftf: 11.85, description: '條件1: 1800 rpm, 4000 N' },
  { bearing: 'Bearing1_2', rpm: 1800, shaft_freq: 30.0, bpfo: 107.91, bpfi: 172.09, bsf: 70.89, ftf: 11.85, description: '條件1: 1800 rpm, 4000 N' },
  { bearing: 'Bearing2_1', rpm: 1650, shaft_freq: 27.5, bpfo: 98.92, bpfi: 157.58, bsf: 65.02, ftf: 10.86, description: '條件2: 1650 rpm, 4200 N' },
  { bearing: 'Bearing2_2', rpm: 1650, shaft_freq: 27.5, bpfo: 98.92, bpfi: 157.58, bsf: 65.02, ftf: 10.86, description: '條件2: 1650 rpm, 4200 N' },
  { bearing: 'Bearing3_1', rpm: 1500, shaft_freq: 25.0, bpfo: 89.93, bpfi: 143.32, bsf: 59.11, ftf: 9.87, description: '條件3: 1500 rpm, 5000 N' },
  { bearing: 'Bearing3_2', rpm: 1500, shaft_freq: 25.0, bpfo: 89.93, bpfi: 143.32, bsf: 59.11, ftf: 9.87, description: '條件3: 1500 rpm, 5000 N' }
]

// 計算頻域特徵
const calculateFrequencyDomain = async () => {
  frequencyDomainLoading.value = true
  try {
    let url
    if (frequencyMethod.value === 'fft') {
      url = `http://localhost:8081/api/algorithms/frequency-fft/${frequencyDomainParams.value.bearingName}/${frequencyDomainParams.value.fileNumber}`
    } else {
      url = `http://localhost:8081/api/algorithms/frequency-tsa/${frequencyDomainParams.value.bearingName}/${frequencyDomainParams.value.fileNumber}`
    }

    const response = await fetch(url)
    if (!response.ok) throw new Error('計算失敗')

    frequencyDomainResult.value = await response.json()

    // 繪製頻譜圖
    await nextTick()
    drawFrequencyDomainChart()
  } catch (error) {
    console.error('計算頻域特徵失敗:', error)
    alert('計算失敗: ' + error.message)
  } finally {
    frequencyDomainLoading.value = false
  }
}

// 繪製頻域圖
const drawFrequencyDomainChart = () => {
  if (!frequencyDomainChart.value || !frequencyDomainResult.value) return

  const chart = echarts.init(frequencyDomainChart.value)

  let frequencies, horizMagnitude, vertMagnitude, title

  if (frequencyMethod.value === 'fft') {
    frequencies = frequencyDomainResult.value.fft_spectrum?.frequencies || []
    horizMagnitude = frequencyDomainResult.value.fft_spectrum?.horizontal_magnitude || []
    vertMagnitude = frequencyDomainResult.value.fft_spectrum?.vertical_magnitude || []
    title = '低頻FFT頻譜圖'
  } else {
    frequencies = frequencyDomainResult.value.tsa_spectrum?.frequencies || []
    horizMagnitude = frequencyDomainResult.value.tsa_spectrum?.horizontal_magnitude || []
    vertMagnitude = frequencyDomainResult.value.tsa_spectrum?.vertical_magnitude || []
    title = '高頻TSA頻譜圖'
  }

  // 只取前1000個點以避免性能問題
  const limit = Math.min(1000, frequencies.length)
  const freqData = frequencies.slice(0, limit)
  const horizData = horizMagnitude.slice(0, limit)
  const vertData = vertMagnitude.slice(0, limit)

  const option = {
    title: {
      text: title,
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      textStyle: {
        color: '#ffffff',
        /* 原始: 繼承預設 */
        /* 第一次修改: fontSize: 18 */
        /* 第二次修改: fontSize: 20 - 增大圖表標題 */
        fontSize: 20,
        fontWeight: 600
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const index = params[0].dataIndex
        return `頻率: ${freqData[index].toFixed(2)} Hz<br/>` +
               `${params[0].seriesName}: ${params[0].value.toFixed(4)}<br/>` +
               `${params[1].seriesName}: ${params[1].value.toFixed(4)}`
      }
    },
    legend: {
      data: ['水平方向', '垂直方向'],
      top: '5%',
      right: '5%',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      textStyle: {
        color: '#ffffff',
        /* 原始: 繼承預設 */
        /* 第一次修改: fontSize: 14 */
        /* 第二次修改: fontSize: 15 - 增大圖例文字 */
        fontSize: 15
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      name: '頻率 (Hz)',
      boundaryGap: false,
      data: freqData.map(f => f.toFixed(1)),
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      axisLabel: {
        color: '#ffffff',
        /* 原始: 繼承預設 */
        /* 第一次修改: fontSize: 12 */
        /* 第二次修改: fontSize: 14 - 增大X軸刻度文字 */
        fontSize: 14
      },
      nameTextStyle: {
        color: '#ffffff',
        /* 原始: 繼承預設 */
        /* 第一次修改: fontSize: 14 */
        /* 第二次修改: fontSize: 15 - 增大X軸名稱文字 */
        fontSize: 15
      }
    },
    yAxis: {
      type: 'value',
      name: '幅值',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      axisLabel: {
        color: '#ffffff',
        /* 原始: 繼承預設 */
        /* 第一次修改: fontSize: 12 */
        /* 第二次修改: fontSize: 14 - 增大Y軸刻度文字 */
        fontSize: 14
      },
      nameTextStyle: {
        color: '#ffffff',
        /* 原始: 繼承預設 */
        /* 第一次修改: fontSize: 14 */
        /* 第二次修改: fontSize: 15 - 增大Y軸名稱文字 */
        fontSize: 15
      },
      splitLine: {
        // 原始：繼承預設顏色
        // 修改：深色主題淺色網格
        lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
      }
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        start: 0,
        end: 20 // 默認顯示前20%
      }
    ],
    series: [
      {
        name: '水平方向',
        type: 'line',
        data: horizData,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 1 }
      },
      {
        name: '垂直方向',
        type: 'line',
        data: vertData,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 1 }
      }
    ]
  }

  chart.setOption(option)
}

// ==================== 趨勢計算方法 ====================

// 計算完整頻域特徵趨勢
const calculateTrend = async () => {
  trendLoading.value = true
  try {
    const url = `http://localhost:8081/api/algorithms/frequency-domain-trend/${trendParams.value.bearingName}`
    const response = await fetch(url)
    if (!response.ok) throw new Error('計算失敗')

    trendResult.value = await response.json()

    // [已移除] 重置分頁 - tablePagination 已移除

    // 繪製趨勢圖
    await nextTick()
    drawAllTrendCharts()
  } catch (error) {
    console.error('計算趨勢失敗:', error)
    alert('計算失敗: ' + error.message)
  } finally {
    trendLoading.value = false
  }
}

// 繪製所有趨勢圖
const drawAllTrendCharts = () => {
  if (!trendResult.value) return

  featureConfig.forEach(feature => {
    drawTrendChart(feature.key, feature.title)
  })
}

// 繪製單個趨勢圖
const drawTrendChart = (feature, title) => {
  const chartEl = trendChartRefs.value[feature]
  if (!chartEl || !trendResult.value) return

  // 銷毀舊圖表實例（如果存在）
  const existingChart = echarts.getInstanceByDom(chartEl)
  if (existingChart) {
    existingChart.dispose()
  }

  const chart = echarts.init(chartEl)

  const fileNumbers = trendResult.value.file_numbers || []
  const horizontalData = trendResult.value.horizontal?.[feature] || []
  const verticalData = trendResult.value.vertical?.[feature] || []

  const option = {
    title: {
      text: title,
      left: 'center',
      textStyle: {
        /* 原始: fontSize: 14 */
        /* 第一次修改: 增大至 16 提升趨勢圖標題可讀性 */
        /* 第二次修改: 增大至 18 提升趨勢圖標題可讀性 */
        fontSize: 18,
        fontWeight: 'normal',
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        color: '#ffffff'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const index = params[0].dataIndex
        let result = `檔案編號: ${fileNumbers[index]}<br/>`
        params.forEach(param => {
          result += `${param.seriesName}: ${param.value?.toFixed(6) || 'N/A'}<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['水平方向', '垂直方向'],
      top: '8%',
      right: '5%',
      textStyle: {
        /* 原始: fontSize: 11 */
        /* 第一次修改: 增大至 13 提升趨勢圖圖例可讀性 */
        /* 第二次修改: 增大至 14 提升趨勢圖圖例可讀性 */
        fontSize: 14,
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        color: '#ffffff'
      }
    },
    grid: {
      left: '8%',
      right: '4%',
      bottom: '12%',
      top: '25%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      name: '檔案編號',
      nameTextStyle: {
        /* 原始: fontSize: 11 */
        /* 第一次修改: 增大至 13 提升X軸名稱可讀性 */
        /* 第二次修改: 增大至 15 提升X軸名稱可讀性 */
        fontSize: 15,
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        color: '#ffffff'
      },
      data: fileNumbers,
      axisLabel: {
        /* 原始: fontSize: 10 */
        /* 第一次修改: 增大至 11 提升X軸標籤可讀性 */
        /* 第二次修改: 增大至 12 提升X軸標籤可讀性 */
        fontSize: 12,
        rotate: fileNumbers.length > 50 ? 45 : 0,
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        color: '#ffffff'
      }
    },
    yAxis: {
      type: 'value',
      name: '特徵值',
      nameTextStyle: {
        /* 原始: fontSize: 11 */
        /* 第一次修改: 增大至 13 提升Y軸名稱可讀性 */
        /* 第二次修改: 增大至 15 提升Y軸名稱可讀性 */
        fontSize: 15,
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        color: '#ffffff'
      },
      axisLabel: {
        /* 原始: fontSize: 10 */
        /* 第一次修改: 增大至 11 提升Y軸標籤可讀性 */
        /* 第二次修改: 增大至 12 提升Y軸標籤可讀性 */
        fontSize: 12,
        formatter: function(value) {
          return value.toFixed(2)
        },
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        color: '#ffffff'
      },
      splitLine: {
        // 原始：繼承預設顏色
        // 修改：深色主題淺色網格
        lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        show: fileNumbers.length > 20,
        xAxisIndex: [0],
        start: 0,
        end: 100,
        height: 20,
        bottom: '5%'
      }
    ],
    series: [
      {
        name: '水平方向',
        type: 'line',
        data: horizontalData,
        smooth: true,
        showSymbol: fileNumbers.length <= 50,
        symbolSize: 4,
        lineStyle: {
          width: 2,
          color: '#409EFF'
        },
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '垂直方向',
        type: 'line',
        data: verticalData,
        smooth: true,
        showSymbol: fileNumbers.length <= 50,
        symbolSize: 4,
        lineStyle: {
          width: 2,
          color: '#67C23A'
        },
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }

  chart.setOption(option)

  // 響應式調整
  window.addEventListener('resize', () => {
    chart.resize()
  })
}
</script>

<style scoped>
/* ===== 原始：淺色主題 ===== */
/* ===== 修改為：Apple Keynote 深色漸層主題 ===== */

/* ===== 字體設定 - 與 FONT.md 規範對齊 ===== */
.frequency-domain-page h1 {
  font-size: 3.2em;
  line-height: 1.1;
  font-weight: bold;
  color: var(--text-primary);
}
.frequency-domain-page h2 {
  /* 原始: 1.5em (≈24px) */
  /* 修改: 1.85em (≈29.6px) - 增大主要區塊標題,與 TimeDomainAnalysis 保持一致 */
  font-size: 1.85em;
  line-height: 1.3;
  font-weight: bold;
  color: var(--text-primary);
}
.frequency-domain-page h3 {
  /* 原始: 1.25em (≈20px) */
  /* 修改: 1.5em (≈24px) - 增大小區塊標題,與 TimeDomainAnalysis 保持一致 */
  font-size: 1.5em;
  line-height: 1.4;
  font-weight: bold;
  color: var(--text-primary);
}
.frequency-domain-page h4 {
  /* 原始: 1.1em (≈17.6px) */
  /* 修改: 1.25em (≈20px) - 增大小標題,與 TimeDomainAnalysis 保持一致 */
  font-size: 1.25em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--accent-primary);
}
.frequency-domain-page h5 {
  font-size: 1em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--text-primary);
}
.frequency-domain-page p {
  /* 原始: 16px */
  /* 修改: 增大至 18px 提升閱讀舒適度 */
  font-size: 18px;
  line-height: 1.6;
  color: var(--text-secondary);
}
.frequency-domain-page a {
  font-weight: 500;
  color: var(--accent-primary);
}

.frequency-domain-page {
  padding: 20px;
  min-height: 100%;
}

/* ===== 表單區域樣式 ===== */
.frequency-domain-page :deep(.el-form) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題表單樣式 */
  color: var(--text-primary);
}

.frequency-domain-page :deep(.el-form-item__label) {
  /* 表單標籤文字顏色 */
  color: var(--text-primary) !important;
  font-weight: 500;
  /* 原始: 繼承預設 */
  /* 第一次修改: 增大至 15px 提升標籤可讀性 */
  /* 第二次修改: 增大至 16px 與 TimeDomainAnalysis 保持一致 */
  font-size: 16px;
}

/* ===== 輸入框樣式 ===== */
.frequency-domain-page :deep(.el-input__wrapper) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.frequency-domain-page :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.frequency-domain-page :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.frequency-domain-page :deep(.el-input__inner) {
  /* 輸入框內部樣式 */
  background-color: transparent;
  color: var(--text-primary);
  /* 原始: 繼承預設 */
  /* 修改: 增大至 15px 提升輸入框文字可讀性 */
  font-size: 15px;
}

/* ===== 下拉選擇框樣式 ===== */
.frequency-domain-page :deep(.el-select) {
  /* 確保下拉框繼承正確的顏色 */
  color: var(--text-primary);
}

.frequency-domain-page :deep(.el-select .el-input__wrapper) {
  /* 下拉選擇框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.frequency-domain-page :deep(.el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.frequency-domain-page :deep(.el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.frequency-domain-page :deep(.el-select .el-input__inner) {
  /* 下拉選擇框文字 */
  color: var(--text-primary);
}

.frequency-domain-page :deep(.el-select__placeholder) {
  /* 下拉選擇框佔位符 */
  color: var(--text-secondary);
}

.frequency-domain-page :deep(.el-select__caret) {
  /* 下拉選擇框箭頭圖標 */
  color: var(--text-secondary);
}

/* ===== 下拉選單選項樣式 ===== */
/* 注意:Element Plus 下拉選單通過 Teleport 渲染到 body 層級 */
/* 下拉選單樣式已移至全局樣式文件: src/styles/select-dropdown-dark.css */
/* 該文件在 main.js 中導入,確保樣式正確應用 */

/* ===== 數字輸入框樣式 ===== */
.frequency-domain-page :deep(.el-input-number) {
  /* 數字輸入框整體 */
  color: var(--text-primary);
}

.frequency-domain-page :deep(.el-input-number .el-input__wrapper) {
  /* 數字輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.frequency-domain-page :deep(.el-input-number .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.frequency-domain-page :deep(.el-input-number .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.frequency-domain-page :deep(.el-input-number__decrease),
.frequency-domain-page :deep(.el-input-number__increase) {
  /* 數字輸入框 +/- 按鈕 */
  background-color: var(--bg-secondary);
  border: none;
  color: var(--text-primary);
}

.frequency-domain-page :deep(.el-input-number__decrease:hover),
.frequency-domain-page :deep(.el-input-number__increase:hover) {
  /* 按鈕懸停效果 */
  color: var(--accent-primary);
  background-color: var(--bg-tertiary);
}

.frequency-domain-page :deep(.el-input-number__decrease.is-disabled),
.frequency-domain-page :deep(.el-input-number__increase.is-disabled) {
  /* 禁用狀態按鈕 */
  color: var(--text-disabled);
  background-color: var(--bg-secondary);
}

/* ===== 按鈕樣式 ===== */
.frequency-domain-page :deep(.el-button) {
  /* 按鈕整體樣式 */
  color: var(--text-primary);
  border-color: var(--border-color);
  /* 原始: 繼承預設 (≈14px) */
  /* 第一次修改: 增大至 15px 提升按鈕文字可讀性 */
  /* 第二次修改: 增大至 16px 與 TimeDomainAnalysis 保持一致 */
  font-size: 16px;
}

.frequency-domain-page :deep(.el-button--primary) {
  /* 主要按鈕 */
  background-color: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #ffffff;
}

.frequency-domain-page :deep(.el-button--primary:hover) {
  /* 主要按鈕懸停 */
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.frequency-domain-page :deep(.el-button--default) {
  /* 預設按鈕 */
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.frequency-domain-page :deep(.el-button--default:hover) {
  /* 預設按鈕懸停 */
  background-color: var(--bg-tertiary);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.frequency-domain-page :deep(.el-button--success) {
  /* 成功按鈕 */
  background-color: var(--accent-success);
  border-color: var(--accent-success);
  color: #ffffff;
}

.frequency-domain-page :deep(.el-button--success:hover) {
  /* 成功按鈕懸停 */
  background-color: var(--accent-success-hover);
  border-color: var(--accent-success-hover);
}

/* ===== 分隔線樣式 ===== */
.frequency-domain-page :deep(.el-divider) {
  /* 分隔線整體樣式 */
  border-top-color: var(--border-color);
}

.frequency-domain-page :deep(.el-divider__text) {
  /* 分隔線文字樣式 */
  background-color: var(--bg-card);
  color: var(--accent-primary);
  font-weight: 600;
  /* 原始: 16px */
  /* 第一次修改: 增大至 17px 提升分隔線文字可讀性 */
  /* 第二次修改: 增大至 18px 與 TimeDomainAnalysis 保持一致 */
  font-size: 18px;
  padding: 0 20px;
}

.frequency-domain-page :deep(.el-divider--horizontal) {
  /* 水平分隔線 */
  display: flex;
  align-items: center;
  margin: 24px 0;
}

/* ===== 表格樣式修正 ===== */
.frequency-domain-page :deep(.el-table) {
  /* 表格整體樣式 */
  background-color: var(--bg-card);
  color: var(--text-primary);
}

.frequency-domain-page :deep(.el-table__header-wrapper) {
  /* 表頭樣式 */
  background-color: var(--bg-secondary);
}

.frequency-domain-page :deep(.el-table th) {
  /* 表頭單元格 */
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  font-weight: 600;
  border-color: var(--border-color) !important;
  /* 原始: 繼承預設 */
  /* 第一次修改: 增大至 14px 提升表頭可讀性 */
  /* 第二次修改: 增大至 15px 提升表頭可讀性 */
  font-size: 15px;
}

.frequency-domain-page :deep(.el-table td) {
  /* 表格單元格 */
  border-color: var(--border-color) !important;
  color: var(--text-primary);
  /* 原始: 繼承預設 */
  /* 第一次修改: 增大至 14px 提升表格內容可讀性 */
  /* 第二次修改: 增大至 15px 提升表格內容可讀性 */
  font-size: 15px;
}

.frequency-domain-page :deep(.el-table__row) {
  /* 表格行 */
  background-color: var(--bg-card);
}

.frequency-domain-page :deep(.el-table__row:hover > td) {
  /* 表格行懸停 */
  background-color: var(--bg-secondary) !important;
}

.frequency-domain-page :deep(.el-table--border) {
  /* 邊框表格 */
  border: 1px solid var(--border-color);
}

.frequency-domain-page :deep(.el-table--border::after) {
  /* 表格外邊框 */
  background-color: var(--border-color);
}

.frequency-domain-page :deep(.el-table--border td, .el-table--border th) {
  /* 表格單元格邊框 */
  border-right: 1px solid var(--border-color);
}

/* ===== 卡片樣式 ===== */
.frequency-domain-page :deep(.el-card) {
  /* 卡片整體 */
  background-color: var(--bg-card);
  border-color: var(--border-color);
}

.frequency-domain-page :deep(.el-card__header) {
  /* 卡片標題 */
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.frequency-domain-page :deep(.el-card__body) {
  /* 卡片內容 */
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

/* ===== 描述列表樣式 ===== */
.frequency-domain-page :deep(.el-descriptions) {
  /* 確保表格在深色背景下可讀 */
  background-color: transparent;
}

.frequency-domain-page :deep(.el-descriptions__label) {
  /* 表格標籤列樣式 */
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  font-weight: 500;
  padding: 12px 16px !important;
  /* 原始: 繼承預設 */
  /* 第一次修改: 增大至 14px 提升描述列表標籤可讀性 */
  /* 第二次修改: 增大至 16px 與 TimeDomainAnalysis 保持一致 */
  font-size: 16px;
}

.frequency-domain-page :deep(.el-descriptions__content) {
  /* 表格內容列樣式 */
  color: var(--text-primary) !important;
  padding: 12px 16px !important;
  /* 原始: 繼承預設 */
  /* 第一次修改: 增大至 14px 提升描述列表內容可讀性 */
  /* 第二次修改: 增大至 16px 與 TimeDomainAnalysis 保持一致 */
  font-size: 16px;
}

.frequency-domain-page :deep(.el-descriptions__cell) {
  /* 表格單元格邊框 */
  border-color: var(--border-color) !important;
}

.frequency-domain-page :deep(.el-descriptions--bordered .el-descriptions__cell) {
  /* 邊框表格的單元格樣式 */
  border: 1px solid var(--border-color);
}

/* 數字值的特殊樣式 */
.frequency-domain-page :deep(.el-descriptions__content) {
  font-family: 'Consolas', 'Monaco', monospace;
  font-weight: 600;
  color: var(--accent-primary) !important;
}

/* ===== 標題樣式 ===== */
/* [已註解] h3, h4, p 樣式已移至文件開頭的全局字體定義區域,與 FONT.md 規範對齊 */
/* 以下為補充的特定樣式調整 */
.frequency-domain-page h3 {
  margin-top: 0;
}

.frequency-domain-page h4 {
  margin-top: 20px;
  /* 確保標題在深色背景下可讀 */
  background: var(--bg-secondary);
  padding: 10px 15px;
  border-radius: 6px;
  border-left: 4px solid var(--accent-primary);
}

/* ===== code 樣式 ===== */
code {
  /* 原始：繼承預設 */
  /* 修改：深色主題代碼背景 */
  background: var(--bg-tertiary);
  padding: 2px 8px;
  border-radius: 6px;
  /* 原始：#667eea */
  /* 修改：使用強調色 */
  color: var(--accent-primary);
  /* 原始：rgba(102, 126, 234, 0.2) */
  /* 修改：深色邊框 */
  border: 1px solid var(--border-color);
  font-family: 'Consolas', 'Monaco', monospace;
  display: block;
  padding: 8px 12px;
  margin: 8px 0;
  /* 原始: 繼承預設 */
  /* 第一次修改: 增大至 15px 提升代碼可讀性 */
  /* 第二次修改: 增大至 16px 與 TimeDomainAnalysis 保持一致 */
  font-size: 16px;
}

/* ===== 組件特定樣式 ===== */
/* [已移除] .card-header 樣式 - 統一使用簡單的 h2 標題，與 TimeDomainAnalysis.vue 保持一致 */

/* ===== 單選框組樣式 ===== */
.frequency-domain-page :deep(.el-radio-group) {
  color: var(--text-primary);
}

.frequency-domain-page :deep(.el-radio) {
  color: var(--text-primary);
  margin-right: 20px;
}

.frequency-domain-page :deep(.el-radio__label) {
  color: var(--text-primary);
}

.frequency-domain-page :deep(.el-radio__input.is-checked .el-radio__inner) {
  background-color: var(--accent-primary);
  border-color: var(--accent-primary);
}

.frequency-domain-page :deep(.el-radio__input.is-checked + .el-radio__label) {
  color: var(--accent-primary);
}

/* ===== Alert 樣式 ===== */
.frequency-domain-page :deep(.el-alert) {
  background-color: var(--bg-secondary);
  border-color: var(--accent-info);
}

.frequency-domain-page :deep(.el-alert__content) {
  color: var(--text-primary);
}

.frequency-domain-page :deep(.el-alert__title) {
  color: var(--text-primary);
}

/* ===== Tag 樣式 ===== */
.frequency-domain-page :deep(.el-tag) {
  border-color: var(--border-color);
}

.frequency-domain-page :deep(.el-tag--info) {
  background-color: var(--accent-info-bg);
  border-color: var(--accent-info);
  color: var(--accent-info);
}

.frequency-domain-page :deep(.el-tag--success) {
  background-color: var(--accent-success-bg);
  border-color: var(--accent-success);
  color: var(--accent-success);
}

.frequency-domain-page :deep(.el-tag--warning) {
  background-color: var(--accent-warning-bg);
  border-color: var(--accent-warning);
  color: var(--accent-warning);
}

.frequency-domain-page :deep(.el-tag--danger) {
  background-color: var(--accent-danger-bg);
  border-color: var(--accent-danger);
  color: var(--accent-danger);
}
</style>
