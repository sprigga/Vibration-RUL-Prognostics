<template>
  <div class="higher-order-stats-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>高階統計特徵分析</h2>
          <el-tag type="primary">NA4, FM4, M6A, M8A, ER</el-tag>
        </div>
      </template>

      <h3>原理說明</h3>
      <p>進階濾波特徵基於高階統計矩和能量分析，對早期故障特別敏感。</p>

      <h4>關鍵特徵:</h4>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="NA4（分段正規化四次矩）">
          <code>NA4 = N·Σ(x-μ)⁴ / [Σ(x-μ_segment)²/M]²</code>
          <p>通過分段計算檢測諧波能量異常，對早期微裂紋敏感</p>
        </el-descriptions-item>
        <el-descriptions-item label="FM4（四次矩特徵）">
          <code>FM4 = N·Σ(x-μ)⁴ / [Σ(x-μ)²]²</code>
          <p>檢測邊帶能量異常，判斷是否存在調製現象</p>
        </el-descriptions-item>
        <el-descriptions-item label="M6A（六次矩特徵）">
          <code>M6A = N²·Σ(x-μ)⁶ / [Σ(x-μ)²]³</code>
          <p>對極早期故障敏感</p>
        </el-descriptions-item>
        <el-descriptions-item label="M8A（八次矩特徵）">
          <code>M8A = N³·Σ(x-μ)⁸ / [Σ(x-μ)²]⁴</code>
          <p>對潤滑不良和極早期故障高度敏感</p>
        </el-descriptions-item>
        <el-descriptions-item label="ER（能量比）">
          <code>ER = E_band / E_total</code>
          <p>特定頻帶能量占總能量的比例</p>
        </el-descriptions-item>
      </el-descriptions>

      <h4 style="margin-top: 20px;">應用場景:</h4>
      <el-tag type="danger" style="margin: 5px;">早期微裂紋檢測</el-tag>
      <el-tag type="warning" style="margin: 5px;">潤滑狀態監測</el-tag>
      <el-tag type="info" style="margin: 5px;">調製信號分析</el-tag>

      <el-alert
        title="診斷準則"
        type="success"
        style="margin-top: 15px;"
        :closable="false"
      >
        <ul style="margin: 5px 0; padding-left: 20px;">
          <li>NA4 > 3 → 存在早期微裂紋</li>
          <li>FM4 異常 → 邊帶能量增加，可能有調製現象</li>
          <li>M6A / M8A 上升 → 潤滑不良或極早期故障</li>
          <li>ER 增大 → 特定頻帶能量集中</li>
        </ul>
      </el-alert>

      <!-- 計算區域 -->
      <el-divider>即時計算演示</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form label-width="120px">
            <el-form-item label="選擇軸承">
              <el-select v-model="filterParams.bearingName" placeholder="請選擇軸承">
                <el-option label="Bearing1_1" value="Bearing1_1" />
                <el-option label="Bearing1_2" value="Bearing1_2" />
                <el-option label="Bearing2_1" value="Bearing2_1" />
                <el-option label="Bearing2_2" value="Bearing2_2" />
                <el-option label="Bearing3_1" value="Bearing3_1" />
              </el-select>
            </el-form-item>
            <el-form-item label="檔案編號">
              <el-input-number v-model="filterParams.fileNumber" :min="1" :max="100" />
            </el-form-item>
            <el-form-item label="分段數量">
              <el-input-number v-model="filterParams.segmentCount" :min="5" :max="20" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="calculateFilterFeatures" :loading="filterLoading">
                計算濾波特徵
              </el-button>
              <el-button @click="calculateFilterTrend" :loading="filterTrendLoading">
                計算趨勢分析
              </el-button>
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="12" v-if="filterResult">
          <el-card shadow="hover">
            <template #header>
              <h4>計算結果</h4>
            </template>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="水平 NA4">
                <el-tag :type="filterResult.horizontal.na4 > 3 ? 'danger' : 'success'">
                  {{ filterResult.horizontal.na4.toFixed(4) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="垂直 NA4">
                <el-tag :type="filterResult.vertical.na4 > 3 ? 'danger' : 'success'">
                  {{ filterResult.vertical.na4.toFixed(4) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="水平 FM4">
                {{ filterResult.horizontal.fm4.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 FM4">
                {{ filterResult.vertical.fm4.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 M6A">
                {{ filterResult.horizontal.m6a.toFixed(6) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 M6A">
                {{ filterResult.vertical.m6a.toFixed(6) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 M8A">
                {{ filterResult.horizontal.m8a.toFixed(8) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 M8A">
                {{ filterResult.vertical.m8a.toFixed(8) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 ER">
                {{ filterResult.horizontal.er.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 ER">
                {{ filterResult.vertical.er.toFixed(4) }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>

      <!-- 比較圖 -->
      <div v-if="filterResult" style="margin-top: 20px;">
        <el-card>
          <template #header>
            <h4>進階濾波特徵比較</h4>
          </template>
          <el-row :gutter="20">
            <el-col :span="12">
              <div ref="filterChartNA4" style="width: 100%; height: 300px;"></div>
            </el-col>
            <el-col :span="12">
              <div ref="filterChartFM4" style="width: 100%; height: 300px;"></div>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="8">
              <div ref="filterChartM6A" style="width: 100%; height: 300px;"></div>
            </el-col>
            <el-col :span="8">
              <div ref="filterChartM8A" style="width: 100%; height: 300px;"></div>
            </el-col>
            <el-col :span="8">
              <div ref="filterChartER" style="width: 100%; height: 300px;"></div>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- 趨勢分析圖 -->
      <div v-if="filterTrendResult" style="margin-top: 20px;">
        <el-card>
          <template #header>
            <h4>進階濾波特徵趨勢分析（共 {{ filterTrendResult.file_count }} 個檔案）</h4>
          </template>
          <div ref="filterTrendChart" style="width: 100%; height: 400px;"></div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import * as echarts from 'echarts'

// Filter Features 參數
const filterParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1,
  segmentCount: 10
})
const filterLoading = ref(false)
const filterTrendLoading = ref(false)
const filterResult = ref(null)
const filterTrendResult = ref(null)

// Chart refs
const filterChartNA4 = ref(null)
const filterChartFM4 = ref(null)
const filterChartM6A = ref(null)
const filterChartM8A = ref(null)
const filterChartER = ref(null)
const filterTrendChart = ref(null)

// 計算進階濾波特徵
const calculateFilterFeatures = async () => {
  filterLoading.value = true
  try {
    const response = await fetch(
      `http://localhost:8081/api/algorithms/filter-features/${filterParams.value.bearingName}/${filterParams.value.fileNumber}?segment_count=${filterParams.value.segmentCount}`
    )
    if (!response.ok) throw new Error('計算失敗')

    filterResult.value = await response.json()

    // 繪製比較圖
    await nextTick()
    drawFilterChart()
  } catch (error) {
    console.error('計算進階濾波特徵失敗:', error)
    alert('計算失敗: ' + error.message)
  } finally {
    filterLoading.value = false
  }
}

// 計算進階濾波特徵趨勢
const calculateFilterTrend = async () => {
  filterTrendLoading.value = true
  try {
    const response = await fetch(
      `http://localhost:8081/api/algorithms/filter-trend/${filterParams.value.bearingName}?max_files=50`
    )
    if (!response.ok) throw new Error('計算失敗')

    filterTrendResult.value = await response.json()

    // 繪製趨勢圖
    await nextTick()
    drawFilterTrendChart()
  } catch (error) {
    console.error('計算進階濾波特徵趨勢失敗:', error)
    alert('計算失敗: ' + error.message)
  } finally {
    filterTrendLoading.value = false
  }
}

// 繪製進階濾波特徵比較圖
const drawFilterChart = () => {
  if (!filterResult.value) return

  const commonOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['水平方向', '垂直方向'],
      top: '5%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['水平', '垂直']
    },
    yAxis: {
      type: 'value'
    }
  }

  // NA4 圖表
  if (filterChartNA4.value) {
    const chartNA4 = echarts.init(filterChartNA4.value)
    chartNA4.setOption({
      ...commonOption,
      title: {
        text: 'NA4（分段正規化四次矩）',
        left: 'center'
      },
      series: [{
        name: 'NA4',
        type: 'bar',
        data: [
          filterResult.value.horizontal.na4,
          filterResult.value.vertical.na4
        ],
        itemStyle: {
          color: (params) => params.dataIndex === 0 ? '#5470c6' : '#91cc75'
        }
      }]
    })
  }

  // FM4 圖表
  if (filterChartFM4.value) {
    const chartFM4 = echarts.init(filterChartFM4.value)
    chartFM4.setOption({
      ...commonOption,
      title: {
        text: 'FM4（四次矩特徵）',
        left: 'center'
      },
      series: [{
        name: 'FM4',
        type: 'bar',
        data: [
          filterResult.value.horizontal.fm4,
          filterResult.value.vertical.fm4
        ],
        itemStyle: {
          color: (params) => params.dataIndex === 0 ? '#5470c6' : '#91cc75'
        }
      }]
    })
  }

  // M6A 圖表
  if (filterChartM6A.value) {
    const chartM6A = echarts.init(filterChartM6A.value)
    chartM6A.setOption({
      ...commonOption,
      title: {
        text: 'M6A（六次矩特徵）',
        left: 'center'
      },
      series: [{
        name: 'M6A',
        type: 'bar',
        data: [
          filterResult.value.horizontal.m6a,
          filterResult.value.vertical.m6a
        ],
        itemStyle: {
          color: (params) => params.dataIndex === 0 ? '#5470c6' : '#91cc75'
        }
      }]
    })
  }

  // M8A 圖表
  if (filterChartM8A.value) {
    const chartM8A = echarts.init(filterChartM8A.value)
    chartM8A.setOption({
      ...commonOption,
      title: {
        text: 'M8A（八次矩特徵）',
        left: 'center'
      },
      series: [{
        name: 'M8A',
        type: 'bar',
        data: [
          filterResult.value.horizontal.m8a,
          filterResult.value.vertical.m8a
        ],
        itemStyle: {
          color: (params) => params.dataIndex === 0 ? '#5470c6' : '#91cc75'
        }
      }]
    })
  }

  // ER 圖表
  if (filterChartER.value) {
    const chartER = echarts.init(filterChartER.value)
    chartER.setOption({
      ...commonOption,
      title: {
        text: 'ER（能量比）',
        left: 'center'
      },
      series: [{
        name: 'ER',
        type: 'bar',
        data: [
          filterResult.value.horizontal.er,
          filterResult.value.vertical.er
        ],
        itemStyle: {
          color: (params) => params.dataIndex === 0 ? '#5470c6' : '#91cc75'
        }
      }]
    })
  }
}

// 繪製進階濾波特徵趨勢圖
const drawFilterTrendChart = () => {
  if (!filterTrendChart.value || !filterTrendResult.value) return

  const chart = echarts.init(filterTrendChart.value)

  const option = {
    title: {
      text: '進階濾波特徵趨勢'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['水平 NA4', '垂直 NA4', '水平 FM4', '垂直 FM4'],
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
      data: filterTrendResult.value.file_numbers,
      name: '檔案編號'
    },
    yAxis: {
      type: 'value',
      name: '特徵值'
    },
    series: [
      {
        name: '水平 NA4',
        type: 'line',
        data: filterTrendResult.value.horizontal.na4,
        smooth: true
      },
      {
        name: '垂直 NA4',
        type: 'line',
        data: filterTrendResult.value.vertical.na4,
        smooth: true
      },
      {
        name: '水平 FM4',
        type: 'line',
        data: filterTrendResult.value.horizontal.fm4,
        smooth: true
      },
      {
        name: '垂直 FM4',
        type: 'line',
        data: filterTrendResult.value.vertical.fm4,
        smooth: true
      }
    ]
  }

  chart.setOption(option)
}
</script>

<style scoped>
.higher-order-stats-page {
  padding: 20px;
  min-height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
}

h3 {
  color: #303133;
  margin-top: 15px;
  margin-bottom: 10px;
  font-weight: 600;
}

h4 {
  color: #667eea;
  margin-top: 15px;
  margin-bottom: 10px;
  font-weight: 600;
}

code {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  padding: 2px 8px;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

p {
  color: #606266;
  line-height: 1.6;
  margin: 8px 0;
}
</style>
