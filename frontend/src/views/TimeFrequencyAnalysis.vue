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
      text: 'STFT 頻譜圖（水平方向）'
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
      name: '時間 (s)'
    },
    yAxis: {
      type: 'category',
      data: stftResult.value.spectrogram_data.frequencies.map(f => f.toFixed(0)),
      name: '頻率 (Hz)'
    },
    visualMap: {
      min: 0,
      max: Math.max(...stftResult.value.spectrogram_data.horizontal_magnitude.flat()),
      calculable: true,
      orient: 'vertical',
      right: '0%',
      top: 'center'
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
      text: 'CWT 小波係數（水平方向）'
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
      name: '時間樣本'
    },
    yAxis: {
      type: 'category',
      data: cwtResult.value.cwt_data.frequencies.map(f => f.toFixed(0)),
      name: '頻率 (Hz)'
    },
    visualMap: {
      min: 0,
      max: Math.max(...cwtResult.value.cwt_data.horizontal_magnitude.flat()),
      calculable: true,
      orient: 'vertical',
      right: '0%',
      top: 'center'
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
        text: '各尺度能量分布'
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['水平方向', '垂直方向'],
        top: '5%',
        right: '5%'
      },
      xAxis: {
        type: 'category',
        data: cwtResult.value.cwt_data.scales,
        name: '尺度'
      },
      yAxis: {
        type: 'value',
        name: '能量'
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
      text: '頻譜圖（水平方向）'
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
      name: '時間 (s)'
    },
    yAxis: {
      type: 'category',
      data: frequencies.map(f => f.toFixed(0)),
      name: '頻率 (Hz)'
    },
    visualMap: {
      min: Math.min(...horizontal_power_db.flat()),
      max: Math.max(...horizontal_power_db.flat()),
      calculable: true,
      orient: 'vertical',
      right: '0%',
      top: 'center'
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
/* ===== 參照 FONT.md 和 common-styles.css 統一樣式 ===== */
/* 基礎樣式(h3, h4, p, code)已由 common-styles.css 統一管理 */

.time-frequency-page {
  padding: 20px;
}

/* 組件特定樣式保留 */
</style>
