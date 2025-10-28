<template>
  <div class="dashboard">

    <!-- IEEE PHM 2012 實驗摘要 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>🔬 IEEE PHM 2012 數據挑戰實驗摘要</span>
              <el-tag type="info">Remaining Useful Life 預測</el-tag>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card shadow="never" class="summary-card">
                <template #header>
                  <div class="summary-header">
                    <el-icon><Aim /></el-icon>
                    <span>實驗目的</span>
                  </div>
                </template>
                <div class="summary-content">
                  <p><strong>軸承剩餘使用壽命（RUL）預測</strong></p>
                  <p>專注於旋轉機械中軸承故障的預測，提高工業機械的可用性、安全性和成本效益。</p>
                  <el-divider />
                  <p><strong>失效標準：</strong>振動幅度超過 20g</p>
                  <p><strong>平台：</strong>PRONOSTIA 實驗平台</p>
                  <p><strong>地點：</strong>FEMTO-ST 研究所（法國）</p>
                </div>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card shadow="never" class="summary-card">
                <template #header>
                  <div class="summary-header">
                    <el-icon><Tools /></el-icon>
                    <span>測試方式</span>
                  </div>
                </template>
                <div class="summary-content">
                  <p><strong>軸承規格：</strong></p>
                  <ul>
                    <li>外徑：32mm，內徑：20mm，厚度：7mm</li>
                    <li>13 個滾珠，直徑 3.5mm</li>
                    <li>動態負載：4000N，靜態負載：2470N</li>
                  </ul>
                  <el-divider />
                  <p><strong>三種操作條件：</strong></p>
                  <el-tag size="small">1800 rpm, 4000 N</el-tag>
                  <el-tag size="small" style="margin: 2px;">1650 rpm, 4200 N</el-tag>
                  <el-tag size="small">1500 rpm, 5000 N</el-tag>
                </div>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card shadow="never" class="summary-card">
                <template #header>
                  <div class="summary-header">
                    <el-icon><Folder /></el-icon>
                    <span>資料集</span>
                  </div>
                </template>
                <div class="summary-content">
                  <p><strong>訓練資料：</strong>6 個完整的運行至失效實驗</p>
                  <p><strong>測試資料：</strong>11 個截斷的監測資料</p>
                  <el-divider />
                  <p><strong>數據採集：</strong></p>
                  <ul>
                    <li>振動：25.6 kHz 採樣頻率</li>
                    <li>溫度：0.1 Hz 採樣頻率</li>
                    <li>兩個加速度計（水平/垂直）</li>
                    <li>RTD 白金溫度感測器</li>
                  </ul>
                  <p><strong>實驗時長：</strong>1小時 - 7小時47分</p>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-row style="margin-top: 15px;">
            <el-col :span="24">
              <el-card shadow="never" class="summary-card">
                <template #header>
                  <div class="summary-header">
                    <el-icon><TrendCharts /></el-icon>
                    <span>挑戰特色與技術重點</span>
                  </div>
                </template>
                <div class="summary-content">
                  <el-row :gutter="15">
                    <el-col :span="6">
                      <div class="challenge-item">
                        <el-tag type="warning" size="small">小訓練集</el-tag>
                        <p>僅6個運行至失效實驗</p>
                      </div>
                    </el-col>
                    <el-col :span="6">
                      <div class="challenge-item">
                        <el-tag type="danger" size="small">高變異性</el-tag>
                        <p>軸承壽命差異極大</p>
                      </div>
                    </el-col>
                    <el-col :span="6">
                      <div class="challenge-item">
                        <el-tag type="info" size="small">多失效模式</el-tag>
                        <p>滾珠、內/外環、保持架</p>
                      </div>
                    </el-col>
                    <el-col :span="6">
                      <div class="challenge-item">
                        <el-tag type="success" size="small">真實劣化</el-tag>
                        <p>自然劣化無人工缺陷</p>
                      </div>
                    </el-col>
                  </el-row>
                  <el-divider />
                  <div class="scoring-info">
                    <strong>評分方法：</strong>非對稱評分函數，對早期和晚期預測採用不同懲罰機制
                    <br><strong>獲獎者：</strong>工業組 - A.L.D. Ltd. (以色列)，學術組 - CALCE, University of Maryland
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 時域特徵分析模組 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <h2>時域特徵分析</h2>
          </template>

          <h3>原理說明</h3>
          <p>時域特徵直接從原始振動信號中提取統計特徵，用於整體健康評估。</p>

          <h4>主要特徵:</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Peak（峰值）">
              <code>Peak = max(|signal|)</code>
              <p>反映最大振動幅度，用於檢測衝擊</p>
            </el-descriptions-item>
            <el-descriptions-item label="RMS（均方根值）">
              <code>RMS = sqrt(mean(signal²))</code>
              <p>反映整體振動能量，最常用的健康指標</p>
            </el-descriptions-item>
            <el-descriptions-item label="Kurtosis（峰度）">
              <code>Kurt = E[(X-μ)⁴] / σ⁴</code>
              <p>反映信號尖銳程度，異常升高表示衝擊</p>
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
              <li>Kurtosis > 8 → 嚴重衝擊，可能存在缺陷</li>
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
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Aim, Tools, Folder, TrendCharts } from '@element-plus/icons-vue'

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
.dashboard {
  padding: 20px;
}

.header-stats {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 15px;
}

.stat-info h3 {
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 5px;
  color: #303133;
}

.stat-info p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* IEEE PHM 2012 實驗摘要樣式 */
.summary-card {
  height: 100%;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
}

.summary-card :deep(.el-card__header) {
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  padding: 12px 16px;
}

.summary-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.summary-content {
  padding: 16px;
  font-size: 13px;
  line-height: 1.5;
}

.summary-content p {
  margin-bottom: 8px;
  color: #606266;
}

.summary-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.summary-content li {
  margin-bottom: 4px;
  color: #606266;
}

.summary-content strong {
  color: #303133;
}

.challenge-item {
  text-align: center;
  padding: 12px 8px;
  border-radius: 6px;
  background-color: #fafafa;
  height: 100%;
}

.challenge-item p {
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
}

.scoring-info {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}
</style>
