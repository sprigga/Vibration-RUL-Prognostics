<template>
  <div class="time-frequency-page">
    <el-card>
      <template #header>
        <h2>時頻分析（STFT & CWT）</h2>
      </template>

      <h3>原理說明</h3>
      <p>時頻分析提供時間和頻率的聯合分析，適合檢測瞬態衝擊和非穩態信號。</p>

      <h4>方法對比:</h4>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover">
            <h4>STFT（短時傅立葉轉換）</h4>
            <p>使用 Hann、Flattop、Hamming 窗</p>
            <p>窗長: 128 / 256 點</p>
            <p>重疊: 95%</p>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <h4>CWT（連續小波轉換）</h4>
            <p>小波基: Morlet、Ricker</p>
            <p>尺度: 1-64</p>
            <p>頻率範圍: 400-12800 Hz</p>
          </el-card>
        </el-col>
      </el-row>

      <h4 style="margin-top: 20px;">NP4 特徵:</h4>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="定義">
          <code>NP4 = N·Σ(Z-μ)⁴ / [Σ(Z-μ)²]²</code>
        </el-descriptions-item>
        <el-descriptions-item label="物理意義">
          類似峰度，反映時頻能量分佈的集中程度
        </el-descriptions-item>
        <el-descriptions-item label="應用">
          檢測瞬態衝擊、局部缺陷
        </el-descriptions-item>
      </el-descriptions>

      <!-- STFT 計算區域 -->
      <el-divider>STFT 即時計算演示</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form label-width="120px">
            <el-form-item label="選擇軸承">
              <el-select v-model="stftParams.bearingName" placeholder="請選擇軸承">
                <el-option label="Bearing1_1" value="Bearing1_1" />
                <el-option label="Bearing1_2" value="Bearing1_2" />
                <el-option label="Bearing2_1" value="Bearing2_1" />
                <el-option label="Bearing2_2" value="Bearing2_2" />
                <el-option label="Bearing3_1" value="Bearing3_1" />
              </el-select>
            </el-form-item>
            <el-form-item label="檔案編號">
              <el-input-number v-model="stftParams.fileNumber" :min="1" :max="100" />
            </el-form-item>
            <el-form-item label="窗函數">
              <el-select v-model="stftParams.window">
                <el-option label="Hann" value="hann" />
                <el-option label="Flattop" value="flattop" />
                <el-option label="Hamming" value="hamming" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="calculateSTFT" :loading="stftLoading">
                計算 STFT
              </el-button>
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="12" v-if="stftResult">
          <el-card shadow="hover">
            <template #header>
              <h4>STFT 計算結果</h4>
            </template>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="水平 NP4">
                {{ stftResult.horizontal.np4.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 NP4">
                {{ stftResult.vertical.np4.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平峰值頻率">
                {{ stftResult.horizontal.max_freq.toFixed(2) }} Hz
              </el-descriptions-item>
              <el-descriptions-item label="垂直峰值頻率">
                {{ stftResult.vertical.max_freq.toFixed(2) }} Hz
              </el-descriptions-item>
              <el-descriptions-item label="水平總能量">
                {{ stftResult.horizontal.total_energy.toFixed(2) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直總能量">
                {{ stftResult.vertical.total_energy.toFixed(2) }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>

      <!-- STFT 頻譜圖 -->
      <div v-if="stftResult" style="margin-top: 20px;">
        <el-card>
          <template #header>
            <h4>STFT 頻譜圖（時頻能量分布）</h4>
          </template>
          <div ref="stftChart" style="width: 100%; height: 400px;"></div>
        </el-card>
      </div>

      <!-- CWT 計算區域 -->
      <el-divider>CWT 即時計算演示</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form label-width="120px">
            <el-form-item label="選擇軸承">
              <el-select v-model="cwtParams.bearingName" placeholder="請選擇軸承">
                <el-option label="Bearing1_1" value="Bearing1_1" />
                <el-option label="Bearing1_2" value="Bearing1_2" />
                <el-option label="Bearing2_1" value="Bearing2_1" />
                <el-option label="Bearing2_2" value="Bearing2_2" />
                <el-option label="Bearing3_1" value="Bearing3_1" />
              </el-select>
            </el-form-item>
            <el-form-item label="檔案編號">
              <el-input-number v-model="cwtParams.fileNumber" :min="1" :max="100" />
            </el-form-item>
            <el-form-item label="小波基">
              <el-select v-model="cwtParams.wavelet">
                <el-option label="Morlet" value="morl" />
                <el-option label="Ricker" value="ricker" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="calculateCWT" :loading="cwtLoading">
                計算 CWT
              </el-button>
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="12" v-if="cwtResult">
          <el-card shadow="hover">
            <template #header>
              <h4>CWT 計算結果</h4>
            </template>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="水平 NP4">
                {{ cwtResult.horizontal.np4.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 NP4">
                {{ cwtResult.vertical.np4.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平峰值尺度">
                {{ cwtResult.horizontal.max_scale.toFixed(2) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直峰值尺度">
                {{ cwtResult.vertical.max_scale.toFixed(2) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平峰值頻率">
                {{ cwtResult.horizontal.max_freq.toFixed(2) }} Hz
              </el-descriptions-item>
              <el-descriptions-item label="垂直峰值頻率">
                {{ cwtResult.vertical.max_freq.toFixed(2) }} Hz
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>

      <!-- CWT 係數圖 -->
      <div v-if="cwtResult" style="margin-top: 20px;">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>
                <h4>CWT 小波係數圖（水平方向）</h4>
              </template>
              <div ref="cwtChartHoriz" style="width: 100%; height: 400px;"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header>
                <h4>各尺度能量分布</h4>
              </template>
              <div ref="cwtEnergyChart" style="width: 100%; height: 400px;"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Spectrogram 計算區域 -->
      <el-divider>Spectrogram 即時計算演示</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form label-width="120px">
            <el-form-item label="選擇軸承">
              <el-select v-model="spectrogramParams.bearingName" placeholder="請選擇軸承">
                <el-option label="Bearing1_1" value="Bearing1_1" />
                <el-option label="Bearing1_2" value="Bearing1_2" />
                <el-option label="Bearing2_1" value="Bearing2_1" />
                <el-option label="Bearing2_2" value="Bearing2_2" />
                <el-option label="Bearing3_1" value="Bearing3_1" />
              </el-select>
            </el-form-item>
            <el-form-item label="檔案編號">
              <el-input-number v-model="spectrogramParams.fileNumber" :min="1" :max="100" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="calculateSpectrogram" :loading="spectrogramLoading">
                計算 Spectrogram
              </el-button>
            </el-form-item>
          </el-form>
        </el-col>
        <el-col :span="12" v-if="spectrogramResult">
          <el-card shadow="hover">
            <template #header>
              <h4>Spectrogram 計算結果</h4>
            </template>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="水平平均功率">
                {{ spectrogramResult.horizontal.mean_power.toFixed(2) }} dB
              </el-descriptions-item>
              <el-descriptions-item label="垂直平均功率">
                {{ spectrogramResult.vertical.mean_power.toFixed(2) }} dB
              </el-descriptions-item>
              <el-descriptions-item label="水平最大功率">
                {{ spectrogramResult.horizontal.max_power.toFixed(2) }} dB
              </el-descriptions-item>
              <el-descriptions-item label="垂直最大功率">
                {{ spectrogramResult.vertical.max_power.toFixed(2) }} dB
              </el-descriptions-item>
              <el-descriptions-item label="水平峰值頻率">
                {{ spectrogramResult.horizontal.peak_freq.toFixed(2) }} Hz
              </el-descriptions-item>
              <el-descriptions-item label="垂直峰值頻率">
                {{ spectrogramResult.vertical.peak_freq.toFixed(2) }} Hz
              </el-descriptions-item>
              <el-descriptions-item label="水平峰值時間">
                {{ spectrogramResult.horizontal.peak_time.toFixed(4) }} s
              </el-descriptions-item>
              <el-descriptions-item label="垂直峰值時間">
                {{ spectrogramResult.vertical.peak_time.toFixed(4) }} s
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>

      <!-- Spectrogram 圖 -->
      <div v-if="spectrogramResult" style="margin-top: 20px;">
        <el-card>
          <template #header>
            <h4>頻譜圖（時頻功率分布）</h4>
          </template>
          <div ref="spectrogramChart" style="width: 100%; height: 400px;"></div>
        </el-card>
      </div>

      <h4 style="margin-top: 20px;">應用場景:</h4>
      <el-tag type="danger" style="margin: 5px;">瞬態衝擊檢測</el-tag>
      <el-tag type="warning" style="margin: 5px;">異物進入檢測</el-tag>
      <el-tag type="info" style="margin: 5px;">早期微裂紋</el-tag>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import * as echarts from 'echarts'

// STFT 參數
const stftParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1,
  window: 'hann'
})
const stftLoading = ref(false)
const stftResult = ref(null)

// CWT 參數
const cwtParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1,
  wavelet: 'morl'
})
const cwtLoading = ref(false)
const cwtResult = ref(null)

// Spectrogram 參數
const spectrogramParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1
})
const spectrogramLoading = ref(false)
const spectrogramResult = ref(null)

// Chart refs
const stftChart = ref(null)
const cwtChartHoriz = ref(null)
const cwtEnergyChart = ref(null)
const spectrogramChart = ref(null)

// 計算 STFT
const calculateSTFT = async () => {
  stftLoading.value = true
  try {
    const response = await fetch(
      `http://localhost:8081/api/algorithms/stft/${stftParams.value.bearingName}/${stftParams.value.fileNumber}?window=${stftParams.value.window}`
    )
    if (!response.ok) throw new Error('計算失敗')

    stftResult.value = await response.json()

    // 繪製 STFT 圖
    await nextTick()
    drawSTFTChart()
  } catch (error) {
    console.error('計算 STFT 失敗:', error)
    alert('計算失敗: ' + error.message)
  } finally {
    stftLoading.value = false
  }
}

// 計算 CWT
const calculateCWT = async () => {
  cwtLoading.value = true
  try {
    const response = await fetch(
      `http://localhost:8081/api/algorithms/cwt/${cwtParams.value.bearingName}/${cwtParams.value.fileNumber}?wavelet=${cwtParams.value.wavelet}`
    )
    if (!response.ok) throw new Error('計算失敗')

    cwtResult.value = await response.json()

    // 繪製 CWT 圖
    await nextTick()
    drawCWTChart()
  } catch (error) {
    console.error('計算 CWT 失敗:', error)
    alert('計算失敗: ' + error.message)
  } finally {
    cwtLoading.value = false
  }
}

// 計算頻譜圖
const calculateSpectrogram = async () => {
  spectrogramLoading.value = true
  try {
    const response = await fetch(
      `http://localhost:8081/api/algorithms/spectrogram/${spectrogramParams.value.bearingName}/${spectrogramParams.value.fileNumber}`
    )
    if (!response.ok) throw new Error('計算失敗')

    spectrogramResult.value = await response.json()

    // 繪製頻譜圖
    await nextTick()
    drawSpectrogramChart()
  } catch (error) {
    console.error('計算頻譜圖失敗:', error)
    alert('計算失敗: ' + error.message)
  } finally {
    spectrogramLoading.value = false
  }
}

// 繪製 STFT 圖
const drawSTFTChart = () => {
  if (!stftChart.value || !stftResult.value) return

  const chart = echarts.init(stftChart.value)

  const option = {
    title: {
      text: 'STFT 頻譜圖（水平方向）',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 繼承預設 */
      /* 第一次修改: 18 - 增大STFT圖標題 */
      /* 第二次修改: 20 - 進一步增大圖表標題 */
      textStyle: { color: '#ffffff', fontSize: 20, fontWeight: 600 }
    },
    tooltip: {
      position: 'top'
    },
    grid: {
      left: '3%',
      right: '10%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: stftResult.value.spectrogram_data.time.map(t => t.toFixed(2)),
      name: '時間 (s)',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 12 */
      /* 第一次修改: 13 - 增大軸刻度文字 */
      /* 第二次修改: 14 - 進一步增大軸刻度文字 */
      axisLabel: { color: '#ffffff', fontSize: 14 },
      /* 原始: 繼承預設 */
      /* 第一次修改: 14 - 增大軸標題文字 */
      /* 第二次修改: 15 - 進一步增大軸標題文字 */
      nameTextStyle: { color: '#ffffff', fontSize: 15 }
    },
    yAxis: {
      type: 'category',
      data: stftResult.value.spectrogram_data.frequencies.map(f => f.toFixed(0)),
      name: '頻率 (Hz)',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 12 */
      /* 第一次修改: 13 - 增大軸刻度文字 */
      /* 第二次修改: 14 - 進一步增大軸刻度文字 */
      axisLabel: { color: '#ffffff', fontSize: 14 },
      /* 原始: 繼承預設 */
      /* 第一次修改: 14 - 增大軸標題文字 */
      /* 第二次修改: 15 - 進一步增大軸標題文字 */
      nameTextStyle: { color: '#ffffff', fontSize: 15 }
    },
    visualMap: {
      min: 0,
      max: Math.max(...stftResult.value.spectrogram_data.horizontal_magnitude.flat()),
      calculable: true,
      orient: 'vertical',
      right: '0%',
      top: 'center',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      textStyle: { color: '#ffffff' }
    },
    series: [
      {
        name: 'STFT 能量',
        type: 'heatmap',
        data: stftResult.value.spectrogram_data.horizontal_magnitude.flatMap((row, i) =>
          row.map((val, j) => [j, i, val])
        ),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  chart.setOption(option)
}

// 繪製 CWT 圖
const drawCWTChart = () => {
  if (!cwtChartHoriz.value || !cwtResult.value) return

  const chart = echarts.init(cwtChartHoriz.value)

  const option = {
    title: {
      text: 'CWT 小波係數（水平方向）',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 繼承預設 */
      /* 第一次修改: 18 - 增大CWT圖標題 */
      /* 第二次修改: 20 - 進一步增大圖表標題 */
      textStyle: { color: '#ffffff', fontSize: 20, fontWeight: 600 }
    },
    tooltip: {
      position: 'top'
    },
    grid: {
      left: '3%',
      right: '10%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: Array.from({ length: cwtResult.value.cwt_data.horizontal_magnitude[0].length }, (_, i) => i),
      name: '時間樣本',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 12 */
      /* 第一次修改: 13 - 增大軸刻度文字 */
      /* 第二次修改: 14 - 進一步增大軸刻度文字 */
      axisLabel: { color: '#ffffff', fontSize: 14 },
      /* 原始: 繼承預設 */
      /* 第一次修改: 14 - 增大軸標題文字 */
      /* 第二次修改: 15 - 進一步增大軸標題文字 */
      nameTextStyle: { color: '#ffffff', fontSize: 15 }
    },
    yAxis: {
      type: 'category',
      data: cwtResult.value.cwt_data.frequencies.map(f => f.toFixed(0)),
      name: '頻率 (Hz)',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 12 */
      /* 第一次修改: 13 - 增大軸刻度文字 */
      /* 第二次修改: 14 - 進一步增大軸刻度文字 */
      axisLabel: { color: '#ffffff', fontSize: 14 },
      /* 原始: 繼承預設 */
      /* 第一次修改: 14 - 增大軸標題文字 */
      /* 第二次修改: 15 - 進一步增大軸標題文字 */
      nameTextStyle: { color: '#ffffff', fontSize: 15 }
    },
    visualMap: {
      min: 0,
      max: Math.max(...cwtResult.value.cwt_data.horizontal_magnitude.flat()),
      calculable: true,
      orient: 'vertical',
      right: '0%',
      top: 'center',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 繼承預設 */
      /* 修改: 增大至 14 提升 visualMap 文字可讀性 */
      /* 原始: 繼承預設 */
      /* 第一次修改: 14 - 增大visualMap文字 */
      /* 第二次修改: 15 - 進一步增大visualMap文字 */
      textStyle: { color: '#ffffff', fontSize: 15 }
    },
    series: [
      {
        name: 'CWT 係數',
        type: 'heatmap',
        data: cwtResult.value.cwt_data.horizontal_magnitude.flatMap((row, i) =>
          row.map((val, j) => [j, i, val])
        ),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  chart.setOption(option)

  // 繪製能量分布圖
  if (cwtEnergyChart.value) {
    const energyChart = echarts.init(cwtEnergyChart.value)

    const energyOption = {
      title: {
        text: '各尺度能量分布',
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        /* 原始: 繼承預設 */
        /* 第一次修改: 18 - 增大能量圖標題 */
        /* 第二次修改: 20 - 進一步增大圖表標題 */
        textStyle: { color: '#ffffff', fontSize: 20, fontWeight: 600 }
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['水平方向', '垂直方向'],
        top: '5%',
        right: '5%',
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        /* 原始: 繼承預設 */
        /* 第一次修改: 14 - 增大圖例文字 */
        /* 第二次修改: 15 - 進一步增大圖例文字 */
        textStyle: { color: '#ffffff', fontSize: 15 }
      },
      xAxis: {
        type: 'category',
        data: cwtResult.value.cwt_data.scales,
        name: '尺度',
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        /* 原始: 12 */
        /* 第一次修改: 13 - 增大軸刻度文字 */
        /* 第二次修改: 14 - 進一步增大軸刻度文字 */
        axisLabel: { color: '#ffffff', fontSize: 14 },
        /* 原始: 繼承預設 */
        /* 第一次修改: 14 - 增大軸標題文字 */
        /* 第二次修改: 15 - 進一步增大軸標題文字 */
        nameTextStyle: { color: '#ffffff', fontSize: 15 }
      },
      yAxis: {
        type: 'value',
        name: '能量',
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        /* 原始: 12 */
        /* 第一次修改: 13 - 增大軸刻度文字 */
        /* 第二次修改: 14 - 進一步增大軸刻度文字 */
        axisLabel: { color: '#ffffff', fontSize: 14 },
        /* 原始: 繼承預設 */
        /* 第一次修改: 14 - 增大軸標題文字 */
        /* 第二次修改: 15 - 進一步增大軸標題文字 */
        nameTextStyle: { color: '#ffffff', fontSize: 15 },
        splitLine: {
          // 原始：繼承預設顏色
          // 修改：深色主題淺色網格
          lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
        }
      },
      series: [
        {
          name: '水平方向',
          type: 'line',
          data: cwtResult.value.horizontal.energy_per_scale,
          smooth: true
        },
        {
          name: '垂直方向',
          type: 'line',
          data: cwtResult.value.vertical.energy_per_scale,
          smooth: true
        }
      ]
    }

    energyChart.setOption(energyOption)
  }
}

// 繪製頻譜圖
const drawSpectrogramChart = () => {
  if (!spectrogramChart.value || !spectrogramResult.value) return

  const chart = echarts.init(spectrogramChart.value)

  const { frequencies, time, horizontal_power_db, vertical_power_db } = spectrogramResult.value.spectrogram_data

  const option = {
    title: {
      text: '頻譜圖（水平方向）',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 繼承預設 */
      /* 第一次修改: 18 - 增大頻譜圖標題 */
      /* 第二次修改: 20 - 進一步增大圖表標題 */
      textStyle: { color: '#ffffff', fontSize: 20, fontWeight: 600 }
    },
    tooltip: {
      position: 'top'
    },
    grid: {
      left: '3%',
      right: '10%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: time.map(t => t.toFixed(2)),
      name: '時間 (s)',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 12 */
      /* 第一次修改: 13 - 增大軸刻度文字 */
      /* 第二次修改: 14 - 進一步增大軸刻度文字 */
      axisLabel: { color: '#ffffff', fontSize: 14 },
      /* 原始: 繼承預設 */
      /* 第一次修改: 14 - 增大軸標題文字 */
      /* 第二次修改: 15 - 進一步增大軸標題文字 */
      nameTextStyle: { color: '#ffffff', fontSize: 15 }
    },
    yAxis: {
      type: 'category',
      data: frequencies.map(f => f.toFixed(0)),
      name: '頻率 (Hz)',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 12 */
      /* 第一次修改: 13 - 增大軸刻度文字 */
      /* 第二次修改: 14 - 進一步增大軸刻度文字 */
      axisLabel: { color: '#ffffff', fontSize: 14 },
      /* 原始: 繼承預設 */
      /* 第一次修改: 14 - 增大軸標題文字 */
      /* 第二次修改: 15 - 進一步增大軸標題文字 */
      nameTextStyle: { color: '#ffffff', fontSize: 15 }
    },
    visualMap: {
      min: Math.min(...horizontal_power_db.flat()),
      max: Math.max(...horizontal_power_db.flat()),
      calculable: true,
      orient: 'vertical',
      right: '0%',
      top: 'center',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 繼承預設 */
      /* 修改: 增大至 14 提升 visualMap 文字可讀性 */
      /* 原始: 繼承預設 */
      /* 第一次修改: 14 - 增大visualMap文字 */
      /* 第二次修改: 15 - 進一步增大visualMap文字 */
      textStyle: { color: '#ffffff', fontSize: 15 }
    },
    series: [
      {
        name: '功率 (dB)',
        type: 'heatmap',
        data: horizontal_power_db.flatMap((row, i) =>
          row.map((val, j) => [j, i, val])
        ),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  chart.setOption(option)
}
</script>

<style scoped>
/* ===== 原始：淺色主題 ===== */
/* ===== 修改為：Apple Keynote 深色漸層主題 ===== */

/* ===== 字體設定 - 與 FONT.md 規範對齊 ===== */
/* 原始設定: h1=3.2em, h2=1.5em, h3=1.25em, h4=1.1em, h5=1em, p=16px */
/* 修改: 增大標題與內容文字,提供更舒適的閱讀體驗 */
.time-frequency-page h1 {
  font-size: 3.2em;
  line-height: 1.1;
  font-weight: bold;
  color: var(--text-primary);
}
.time-frequency-page h2 {
  /* 原始: 1.5em (≈24px) */
  /* 第一次修改: 1.75em (≈28px) - 增大主要區塊標題 */
  /* 第二次修改: 1.85em (≈29.6px) - 進一步增大標題以提升可讀性 */
  font-size: 1.85em;
  line-height: 1.3;
  font-weight: bold;
  color: var(--text-primary);
}
.time-frequency-page h3 {
  /* 原始: 1.25em (≈20px) */
  /* 第一次修改: 1.4em (≈22.4px) - 增大小區塊標題 */
  /* 第二次修改: 1.5em (≈24px) - 進一步增大小區塊標題 */
  font-size: 1.5em;
  line-height: 1.4;
  font-weight: bold;
  color: var(--text-primary);
}
.time-frequency-page h4 {
  /* 原始: 1.1em (≈17.6px) */
  /* 第一次修改: 1.2em (≈19.2px) - 增大小標題 */
  /* 第二次修改: 1.25em (≈20px) - 進一步增大小標題 */
  font-size: 1.25em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--accent-primary);
}
.time-frequency-page h5 {
  /* 原始: 1em (16px) */
  /* 修改: 1.1em (≈17.6px) - 增大次級標題 */
  font-size: 1.1em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--text-primary);
}
.time-frequency-page p {
  /* 原始: 16px */
  /* 第一次修改: 17px - 略微增大內容文字 */
  /* 第二次修改: 18px - 進一步增大內容文字以提升閱讀舒適度 */
  font-size: 18px;
  line-height: 1.6;
  color: var(--text-secondary);
}
.time-frequency-page a {
  font-weight: 500;
  color: var(--accent-primary);
}

.time-frequency-page {
  padding: 20px;
  min-height: 100%;
}

/* ===== 表單區域樣式 ===== */
.time-frequency-page :deep(.el-form) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題表單樣式 */
  color: var(--text-primary);
}

.time-frequency-page :deep(.el-form-item__label) {
  /* 表單標籤文字顏色 */
  color: var(--text-primary) !important;
  font-weight: 500;
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大表單標籤文字 */
  /* 第二次修改: 16px - 進一步增大表單標籤文字 */
  font-size: 16px;
}

/* ===== 輸入框樣式 ===== */
.time-frequency-page :deep(.el-input__wrapper) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.time-frequency-page :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.time-frequency-page :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.time-frequency-page :deep(.el-input__inner) {
  /* 輸入框內部樣式 */
  background-color: transparent;
  color: var(--text-primary);
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大輸入框文字 */
  /* 第二次修改: 16px - 進一步增大輸入框文字 */
  font-size: 16px;
}

/* ===== 下拉選擇框樣式 ===== */
.time-frequency-page :deep(.el-select) {
  /* 確保下拉框繼承正確的顏色 */
  color: var(--text-primary);
}

.time-frequency-page :deep(.el-select .el-input__wrapper) {
  /* 下拉選擇框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.time-frequency-page :deep(.el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.time-frequency-page :deep(.el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.time-frequency-page :deep(.el-select .el-input__inner) {
  /* 下拉選擇框文字 */
  color: var(--text-primary);
}

.time-frequency-page :deep(.el-select__placeholder) {
  /* 下拉選擇框佔位符 */
  color: var(--text-secondary);
}

.time-frequency-page :deep(.el-select__caret) {
  /* 下拉選擇框箭頭圖標 */
  color: var(--text-secondary);
}

/* ===== 下拉選單選項樣式 ===== */
/* 注意:Element Plus 下拉選單通過 Teleport 渲染到 body 層級 */
/* 下拉選單樣式已移至全局樣式文件: src/styles/select-dropdown-dark.css */
/* 該文件在 main.js 中導入,確保樣式正確應用 */

/* ===== 數字輸入框樣式 ===== */
.time-frequency-page :deep(.el-input-number) {
  /* 數字輸入框整體 */
  color: var(--text-primary);
}

.time-frequency-page :deep(.el-input-number .el-input__wrapper) {
  /* 數字輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.time-frequency-page :deep(.el-input-number .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.time-frequency-page :deep(.el-input-number .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.time-frequency-page :deep(.el-input-number__decrease),
.time-frequency-page :deep(.el-input-number__increase) {
  /* 數字輸入框 +/- 按鈕 */
  background-color: var(--bg-secondary);
  border: none;
  color: var(--text-primary);
}

.time-frequency-page :deep(.el-input-number__decrease:hover),
.time-frequency-page :deep(.el-input-number__increase:hover) {
  /* 按鈕懸停效果 */
  color: var(--accent-primary);
  background-color: var(--bg-tertiary);
}

.time-frequency-page :deep(.el-input-number__decrease.is-disabled),
.time-frequency-page :deep(.el-input-number__increase.is-disabled) {
  /* 禁用狀態按鈕 */
  color: var(--text-disabled);
  background-color: var(--bg-secondary);
}

/* ===== 按鈕樣式 ===== */
.time-frequency-page :deep(.el-button) {
  /* 按鈕整體樣式 */
  color: var(--text-primary);
  border-color: var(--border-color);
  /* 原始: 繼承預設 (≈14px) */
  /* 修改: 15px - 增大按鈕文字 */
  font-size: 15px;
}

.time-frequency-page :deep(.el-button--primary) {
  /* 主要按鈕 */
  background-color: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #ffffff;
}

.time-frequency-page :deep(.el-button--primary:hover) {
  /* 主要按鈕懸停 */
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.time-frequency-page :deep(.el-button--default) {
  /* 預設按鈕 */
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.time-frequency-page :deep(.el-button--default:hover) {
  /* 預設按鈕懸停 */
  background-color: var(--bg-tertiary);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* ===== 分隔線樣式 ===== */
.time-frequency-page :deep(.el-divider) {
  /* 分隔線整體樣式 */
  border-top-color: var(--border-color);
}

.time-frequency-page :deep(.el-divider__text) {
  /* 分隔線文字樣式 */
  background-color: var(--bg-card);
  color: var(--accent-primary);
  font-weight: 600;
  /* 原始: 16px */
  /* 第一次修改: 17px - 略微增大分隔線文字 */
  /* 第二次修改: 18px - 進一步增大分隔線文字 */
  font-size: 18px;
  padding: 0 20px;
}

.time-frequency-page :deep(.el-divider--horizontal) {
  /* 水平分隔線 */
  display: flex;
  align-items: center;
  margin: 24px 0;
}

/* ===== 標題樣式 ===== */
/* [已註解] h3, h4, p 樣式已移至文件開頭的全局字體定義區域,與 FONT.md 規範對齊 */
/* 以下為補充的特定樣式調整 */
.time-frequency-page h3 {
  margin-top: 0;
}

.time-frequency-page h4 {
  margin-top: 20px;
  /* 確保標題在深色背景下可讀 */
  background: var(--bg-secondary);
  padding: 10px 15px;
  border-radius: 6px;
  border-left: 4px solid var(--accent-primary);
}

code {
  /* 原始：linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)) */
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
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大代碼文字 */
  /* 第二次修改: 16px - 進一步增大代碼文字 */
  font-size: 16px;
}

/* ===== 表格樣式修正 ===== */
/* 針對 el-descriptions 表格組件的樣式優化 */
.time-frequency-page :deep(.el-descriptions) {
  /* 確保表格在深色背景下可讀 */
  background-color: transparent;
}

.time-frequency-page :deep(.el-descriptions__label) {
  /* 表格標籤列樣式 */
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  font-weight: 500;
  padding: 12px 16px !important;
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大表格標籤文字 */
  /* 第二次修改: 16px - 進一步增大表格標籤文字 */
  font-size: 16px;
}

.time-frequency-page :deep(.el-descriptions__content) {
  /* 表格內容列樣式 */
  color: var(--text-primary) !important;
  padding: 12px 16px !important;
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大表格內容文字 */
  /* 第二次修改: 16px - 進一步增大表格內容文字 */
  font-size: 16px;
}

.time-frequency-page :deep(.el-descriptions__cell) {
  /* 表格單元格邊框 */
  border-color: var(--border-color) !important;
}

.time-frequency-page :deep(.el-descriptions--bordered .el-descriptions__cell) {
  /* 邊框表格的單元格樣式 */
  border: 1px solid var(--border-color);
}

/* 表格標題優化 */
.time-frequency-page :deep(.el-card__header) {
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.time-frequency-page :deep(.el-card__body) {
  background-color: var(--bg-primary);
}

/* 數字值的特殊樣式 */
.time-frequency-page :deep(.el-descriptions__content) {
  font-family: 'Consolas', 'Monaco', monospace;
  font-weight: 600;
  color: var(--accent-primary) !important;
}

/* ===== 卡片樣式 ===== */
.time-frequency-page :deep(.el-card) {
  /* 卡片整體 */
  background-color: var(--bg-card);
  border-color: var(--border-color);
}

.time-frequency-page :deep(.el-card__header) {
  /* 卡片標題 */
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.time-frequency-page :deep(.el-card__body) {
  /* 卡片內容 */
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

/* ===== Tag 樣式 ===== */
.time-frequency-page :deep(.el-tag) {
  border-color: var(--border-color);
}

.time-frequency-page :deep(.el-tag--info) {
  background-color: var(--accent-info-bg);
  border-color: var(--accent-info);
  color: var(--accent-info);
}

.time-frequency-page :deep(.el-tag--success) {
  background-color: var(--accent-success-bg);
  border-color: var(--accent-success);
  color: var(--accent-success);
}

.time-frequency-page :deep(.el-tag--warning) {
  background-color: var(--accent-warning-bg);
  border-color: var(--accent-warning);
  color: var(--accent-warning);
}

.time-frequency-page :deep(.el-tag--danger) {
  background-color: var(--accent-danger-bg);
  border-color: var(--accent-danger);
  color: var(--accent-danger);
}
</style>
