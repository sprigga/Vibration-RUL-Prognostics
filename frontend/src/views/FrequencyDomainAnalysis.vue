<template>
  <div class="frequency-domain-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>頻域特徵分析</h2>
          <el-tag type="info">Frequency Domain Analysis</el-tag>
        </div>
      </template>

      <!-- 原理說明 -->
      <el-card shadow="never" style="margin-bottom: 20px;">
        <template #header>
          <h3>原理說明</h3>
        </template>
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
      </el-card>

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
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import * as echarts from 'echarts'

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
      text: title
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
      name: '頻率 (Hz)',
      boundaryGap: false,
      data: freqData.map(f => f.toFixed(1))
    },
    yAxis: {
      type: 'value',
      name: '幅值'
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
</script>

<style scoped>
.frequency-domain-page {
  padding: 20px;
  min-height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
}

h3 {
  margin: 0 0 15px;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

h4 {
  margin: 15px 0 10px;
  font-size: 16px;
  color: #667eea;
  font-weight: 600;
}

p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 15px;
}

code {
  display: block;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  padding: 8px 12px;
  margin: 8px 0;
  border-radius: 8px;
  font-family: 'Courier New', monospace;
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
}
</style>
