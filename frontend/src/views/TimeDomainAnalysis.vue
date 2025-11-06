<template>
  <div class="time-domain-page">
    <el-card>
      <template #header>
        <h2>時域特徵分析</h2>
      </template>

      <h3>原理說明</h3>
      <p>時域特徵直接從原始振動信號中提取統計特徵,用於整體健康評估。</p>

      <h4>主要特徵:</h4>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="Peak（峰值）">
          <code>Peak = max(|signal|)</code>
          <p>反映最大振動幅度,用於檢測衝擊</p>
        </el-descriptions-item>
        <el-descriptions-item label="RMS（均方根值）">
          <code>RMS = sqrt(mean(signal²))</code>
          <p>反映整體振動能量,最常用的健康指標</p>
        </el-descriptions-item>
        <el-descriptions-item label="Kurtosis（峰度）">
          <code>Kurt = E[(X-μ)⁴] / σ⁴</code>
          <p>反映信號尖銳程度,異常升高表示衝擊</p>
        </el-descriptions-item>
        <el-descriptions-item label="Crest Factor（波峰因數）">
          <code>CF = Peak / RMS</code>
          <p>反映峰值與平均值的比值</p>
        </el-descriptions-item>
      </el-descriptions>

      <h4 style="margin-top: 20px;">應用場景:</h4>
      <el-tag type="success" style="margin: 5px;">磨損程度監測</el-tag>
      <el-tag type="warning" style="margin: 5px;">異常檢測</el-tag>

      <el-alert
        title="診斷準則"
        type="info"
        style="margin-top: 15px;"
        :closable="false"
      >
        <ul style="margin: 5px 0; padding-left: 20px;">
          <li>RMS 緩慢上升 → 磨損加劇</li>
          <li>Kurtosis > 8 → 嚴重衝擊,可能存在缺陷</li>
        </ul>
      </el-alert>

      <!-- 即時計算區域 -->
      <el-divider>即時計算演示</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form label-width="120px">
            <el-form-item label="選擇軸承">
              <el-select v-model="timeDomainParams.bearingName" placeholder="請選擇軸承">
                <el-option label="Bearing1_1" value="Bearing1_1" />
                <el-option label="Bearing1_2" value="Bearing1_2" />
                <el-option label="Bearing2_1" value="Bearing2_1" />
                <el-option label="Bearing2_2" value="Bearing2_2" />
                <el-option label="Bearing3_1" value="Bearing3_1" />
                <el-option label="Bearing3_2" value="Bearing3_2" />
              </el-select>
            </el-form-item>
            <el-form-item label="檔案編號">
              <el-input-number v-model="timeDomainParams.fileNumber" :min="1" :max="100" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="calculateTimeDomain" :loading="timeDomainLoading">
                計算時域特徵
              </el-button>
              <el-button @click="calculateTimeDomainTrend" :loading="trendLoading">
                計算趨勢分析
              </el-button>
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="12" v-if="timeDomainResult">
          <el-card shadow="hover">
            <template #header>
              <h4>計算結果</h4>
            </template>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="資料點數">
                {{ timeDomainResult.data_points }}
              </el-descriptions-item>
              <el-descriptions-item label="軸承名稱">
                {{ timeDomainResult.bearing_name }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 Peak">
                {{ timeDomainResult.horizontal.peak.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 Peak">
                {{ timeDomainResult.vertical.peak.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 RMS">
                {{ timeDomainResult.horizontal.rms.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 RMS">
                {{ timeDomainResult.vertical.rms.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 Crest Factor">
                {{ timeDomainResult.horizontal.crest_factor.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 Crest Factor">
                {{ timeDomainResult.vertical.crest_factor.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平峰度">
                {{ timeDomainResult.horizontal.kurtosis.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直峰度">
                {{ timeDomainResult.vertical.kurtosis.toFixed(4) }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>

      <!-- 振動信號圖表 -->
      <div v-if="timeDomainResult" style="margin-top: 20px;">
        <el-card>
          <template #header>
            <h4>振動信號波形</h4>
          </template>
          <div ref="timeDomainSignalChart" style="width: 100%; height: 400px;"></div>
        </el-card>
      </div>

      <!-- 趨勢分析圖表 -->
      <div v-if="trendResult" style="margin-top: 20px;">
        <el-card>
          <template #header>
            <h4>時域特徵趨勢分析（共 {{ trendResult.file_count }} 個檔案）</h4>
          </template>
          <div ref="timeDomainTrendChart" style="width: 100%; height: 400px;"></div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import * as echarts from 'echarts'

// 時域計算參數
const timeDomainParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1
})

const timeDomainLoading = ref(false)
const trendLoading = ref(false)
const timeDomainResult = ref(null)
const trendResult = ref(null)

// Chart refs
const timeDomainSignalChart = ref(null)
const timeDomainTrendChart = ref(null)

// 計算時域特徵
const calculateTimeDomain = async () => {
  timeDomainLoading.value = true
  try {
    const response = await fetch(
      `http://localhost:8081/api/algorithms/time-domain/${timeDomainParams.value.bearingName}/${timeDomainParams.value.fileNumber}`
    )
    if (!response.ok) throw new Error('計算失敗')

    timeDomainResult.value = await response.json()

    // 繪製信號波形圖
    await nextTick()
    drawSignalChart()
  } catch (error) {
    console.error('計算時域特徵失敗:', error)
    alert('計算失敗: ' + error.message)
  } finally {
    timeDomainLoading.value = false
  }
}

// 計算趨勢分析
const calculateTimeDomainTrend = async () => {
  trendLoading.value = true
  try {
    const response = await fetch(
      `http://localhost:8081/api/algorithms/time-domain-trend/${timeDomainParams.value.bearingName}?max_files=50`
    )
    if (!response.ok) throw new Error('計算失敗')

    trendResult.value = await response.json()

    // 繪製趨勢圖
    await nextTick()
    drawTrendChart()
  } catch (error) {
    console.error('計算趨勢分析失敗:', error)
    alert('計算失敗: ' + error.message)
  } finally {
    trendLoading.value = false
  }
}

// 繪製信號波形圖
const drawSignalChart = () => {
  if (!timeDomainSignalChart.value || !timeDomainResult.value) return

  const chart = echarts.init(timeDomainSignalChart.value)

  const option = {
    title: {
      text: '振動加速度信號'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['水平方向', '垂直方向'],
      top: '5%',
      right: '5%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: timeDomainResult.value.signal_data.time,
      name: '樣本點'
    },
    yAxis: {
      type: 'value',
      name: '加速度 (g)'
    },
    series: [
      {
        name: '水平方向',
        type: 'line',
        data: timeDomainResult.value.signal_data.horizontal,
        showSymbol: false,
        lineStyle: { width: 1 }
      },
      {
        name: '垂直方向',
        type: 'line',
        data: timeDomainResult.value.signal_data.vertical,
        showSymbol: false,
        lineStyle: { width: 1 }
      }
    ]
  }

  chart.setOption(option)
}

// 繪製趨勢圖
const drawTrendChart = () => {
  if (!timeDomainTrendChart.value || !trendResult.value) return

  const chart = echarts.init(timeDomainTrendChart.value)

  const option = {
    title: {
      text: '時域特徵趨勢'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['水平 RMS', '垂直 RMS', '水平峰度', '垂直峰度'],
      top: '1%',
      right: '5%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: trendResult.value.file_numbers,
      name: '檔案編號'
    },
    yAxis: [
      {
        type: 'value',
        name: 'RMS',
        position: 'left'
      },
      {
        type: 'value',
        name: '峰度',
        position: 'right'
      }
    ],
    series: [
      {
        name: '水平 RMS',
        type: 'line',
        yAxisIndex: 0,
        data: trendResult.value.horizontal.rms,
        smooth: true
      },
      {
        name: '垂直 RMS',
        type: 'line',
        yAxisIndex: 0,
        data: trendResult.value.vertical.rms,
        smooth: true
      },
      {
        name: '水平峰度',
        type: 'line',
        yAxisIndex: 1,
        data: trendResult.value.horizontal.kurtosis,
        smooth: true
      },
      {
        name: '垂直峰度',
        type: 'line',
        yAxisIndex: 1,
        data: trendResult.value.vertical.kurtosis,
        smooth: true
      }
    ]
  }

  chart.setOption(option)
}
</script>

<style scoped>
.time-domain-page {
  padding: 20px;
}

h3 {
  margin-top: 0;
  color: #303133;
}

h4 {
  margin-top: 20px;
  color: #606266;
}

p {
  line-height: 1.6;
  color: #606266;
}

code {
  background-color: #f5f7fa;
  padding: 2px 8px;
  border-radius: 3px;
  color: #e6a23c;
  font-family: 'Consolas', 'Monaco', monospace;
}
</style>
