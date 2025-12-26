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
          <code>Peak = max(signal) - min(signal)</code>
          <p>反映最大振動幅度,用於檢測衝擊</p>
        </el-descriptions-item>
        <el-descriptions-item label="Average（平均值）">
          <code>Avg = mean(signal)</code>
          <p>信號的平均值,反映直流分量偏移</p>
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
        <el-descriptions-item label="Energy Operator（能量運算元）">
          <code>EO = (n²Σδ⁴) / (Σδ²)²</code>
          <p>反映信號能量變化率,用於檢測非線性特徵</p>
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
        <ul class="diagnostic-criteria-list">
          <li>RMS 緩慢上升 → 磨損加劇</li>
          <li>Kurtosis > 8 → 嚴重衝擊,可能存在缺陷</li>
          <li>EO 值顯著變化 → 能量分佈異常,檢測非線性故障</li>
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
              <el-descriptions-item label="水平 Peak（峰值）">
                {{ timeDomainResult.horizontal.peak.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 Peak（峰值）">
                {{ timeDomainResult.vertical.peak.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 Average（平均值）">
                {{ timeDomainResult.horizontal.avg.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 Average（平均值）">
                {{ timeDomainResult.vertical.avg.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 RMS（均方根）">
                {{ timeDomainResult.horizontal.rms.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 RMS（均方根）">
                {{ timeDomainResult.vertical.rms.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 Crest Factor（波峰因數）">
                {{ timeDomainResult.horizontal.crest_factor.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 Crest Factor（波峰因數）">
                {{ timeDomainResult.vertical.crest_factor.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 Kurtosis（峰度）">
                {{ timeDomainResult.horizontal.kurtosis.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 Kurtosis（峰度）">
                {{ timeDomainResult.vertical.kurtosis.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="水平 EO（能量運算元）">
                {{ timeDomainResult.horizontal.eo.toFixed(4) }}
              </el-descriptions-item>
              <el-descriptions-item label="垂直 EO（能量運算元）">
                {{ timeDomainResult.vertical.eo.toFixed(4) }}
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
      text: '振動加速度信號',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      textStyle: {
        color: '#ffffff',
        // 原始: 繼承預設 (≈18px)
        // 第一次修改: 18px - 確保圖表標題清晰可讀
        // 第二次修改: 20px - 進一步增大圖表標題
        fontSize: 20
      }
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
      textStyle: {
        color: '#ffffff',
        // 原始: 12
        // 第一次修改: 14 - 增大圖例文字
        // 第二次修改: 15 - 進一步增大圖例文字
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
      data: timeDomainResult.value.signal_data.time,
      name: '樣本點',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      axisLabel: {
        color: '#ffffff',
        // 原始: 12
        // 第一次修改: 13 - 增大軸刻度文字
        // 第二次修改: 14 - 進一步增大軸刻度文字
        fontSize: 14
      },
      nameTextStyle: {
        color: '#ffffff',
        // 原始: 繼承預設
        // 第一次修改: 14 - 增大軸標題文字
        // 第二次修改: 15 - 進一步增大軸標題文字
        fontSize: 15
      }
    },
    yAxis: {
      type: 'value',
      name: '加速度 (g)',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      axisLabel: {
        color: '#ffffff',
        // 原始: 12
        // 第一次修改: 13 - 增大軸刻度文字
        // 第二次修改: 14 - 進一步增大軸刻度文字
        fontSize: 14
      },
      nameTextStyle: {
        color: '#ffffff',
        // 原始: 繼承預設
        // 第一次修改: 14 - 增大軸標題文字
        // 第二次修改: 15 - 進一步增大軸標題文字
        fontSize: 15
      },
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
      text: '時域特徵趨勢',
      left: 'center',
      top: '1%',
      textStyle: {
        // 原始: 16 */
        /* 第一次修改: 18 - 增大趨勢圖標題 */
        /* 第二次修改: 20 - 進一步增大趨勢圖標題 */
        fontSize: 20,
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        color: '#ffffff'
      }
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['水平 Peak', '垂直 Peak', '水平 Avg', '垂直 Avg', '水平 RMS', '垂直 RMS', '水平 Kurtosis', '垂直 Kurtosis', '水平 CF', '垂直 CF', '水平 EO', '垂直 EO'],
      top: '8%',
      right: '2%',
      type: 'scroll',
      textStyle: {
        // 原始: 11 */
        /* 第一次修改: 12 - 增大圖例文字,避免過大影響版面 */
        /* 第二次修改: 13 - 進一步增大圖例文字 */
        fontSize: 13,
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        color: '#ffffff'
      },
      itemGap: 8,
      itemWidth: 20,
      itemHeight: 12
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '8%',
      top: '25%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: trendResult.value.file_numbers,
      name: '檔案編號',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      axisLabel: {
        color: '#ffffff',
        // 原始: 12 */
        /* 第一次修改: 13 - 增大軸刻度文字 */
        /* 第二次修改: 14 - 進一步增大軸刻度文字 */
        fontSize: 14
      },
      nameTextStyle: {
        color: '#ffffff',
        // 原始: 繼承預設 */
        /* 第一次修改: 14 - 增大軸標題文字 */
        /* 第二次修改: 15 - 進一步增大軸標題文字 */
        fontSize: 15
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '振幅值',
        position: 'left',
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        axisLabel: {
          color: '#ffffff',
          // 原始: 12 */
          /* 第一次修改: 13 - 增大軸刻度文字 */
          /* 第二次修改: 14 - 進一步增大軸刻度文字 */
          fontSize: 14
        },
        nameTextStyle: {
          color: '#ffffff',
          // 原始: 繼承預設 */
          /* 第一次修改: 14 - 增大軸標題文字 */
          /* 第二次修改: 15 - 進一步增大軸標題文字 */
          fontSize: 15
        },
        splitLine: {
          // 原始：繼承預設顏色
          // 修改：深色主題淺色網格
          lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
        }
      },
      {
        type: 'value',
        name: '峰度/波峰因數',
        position: 'right',
        // 原始：繼承預設顏色
        // 修改：深色主題白色文字
        axisLabel: {
          color: '#ffffff',
          // 原始: 12 */
          /* 第一次修改: 13 - 增大軸刻度文字 */
          /* 第二次修改: 14 - 進一步增大軸刻度文字 */
          fontSize: 14
        },
        nameTextStyle: {
          color: '#ffffff',
          // 原始: 繼承預設 */
          /* 第一次修改: 14 - 增大軸標題文字 */
          /* 第二次修改: 15 - 進一步增大軸標題文字 */
          fontSize: 15
        },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '水平 Peak',
        type: 'line',
        yAxisIndex: 0,
        data: trendResult.value.horizontal.peak,
        smooth: true
      },
      {
        name: '垂直 Peak',
        type: 'line',
        yAxisIndex: 0,
        data: trendResult.value.vertical.peak,
        smooth: true
      },
      {
        name: '水平 Avg',
        type: 'line',
        yAxisIndex: 0,
        data: trendResult.value.horizontal.avg,
        smooth: true
      },
      {
        name: '垂直 Avg',
        type: 'line',
        yAxisIndex: 0,
        data: trendResult.value.vertical.avg,
        smooth: true
      },
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
        name: '水平 Kurtosis',
        type: 'line',
        yAxisIndex: 1,
        data: trendResult.value.horizontal.kurtosis,
        smooth: true
      },
      {
        name: '垂直 Kurtosis',
        type: 'line',
        yAxisIndex: 1,
        data: trendResult.value.vertical.kurtosis,
        smooth: true
      },
      {
        name: '水平 CF',
        type: 'line',
        yAxisIndex: 1,
        data: trendResult.value.horizontal.crest_factor,
        smooth: true
      },
      {
        name: '垂直 CF',
        type: 'line',
        yAxisIndex: 1,
        data: trendResult.value.vertical.crest_factor,
        smooth: true
      },
      {
        name: '水平 EO',
        type: 'line',
        yAxisIndex: 0,
        data: trendResult.value.horizontal.eo,
        smooth: true
      },
      {
        name: '垂直 EO',
        type: 'line',
        yAxisIndex: 0,
        data: trendResult.value.vertical.eo,
        smooth: true
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
.time-domain-page h1 {
  font-size: 3.2em;
  line-height: 1.1;
  font-weight: bold;
  color: var(--text-primary);
}
.time-domain-page h2 {
  /* 原始: 1.5em (≈24px) */
  /* 第一次修改: 1.75em (≈28px) - 增大主要區塊標題 */
  /* 第二次修改: 1.85em (≈29.6px) - 進一步增大標題以提升可讀性 */
  font-size: 1.85em;
  line-height: 1.3;
  font-weight: bold;
  color: var(--text-primary);
}
.time-domain-page h3 {
  /* 原始: 1.25em (≈20px) */
  /* 第一次修改: 1.4em (≈22.4px) - 增大小區塊標題 */
  /* 第二次修改: 1.5em (≈24px) - 進一步增大小區塊標題 */
  font-size: 1.5em;
  line-height: 1.4;
  font-weight: bold;
  color: var(--text-primary);
}
.time-domain-page h4 {
  /* 原始: 1.1em (≈17.6px) */
  /* 第一次修改: 1.2em (≈19.2px) - 增大小標題 */
  /* 第二次修改: 1.25em (≈20px) - 進一步增大小標題 */
  font-size: 1.25em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--accent-primary);
}
.time-domain-page h5 {
  /* 原始: 1em (16px) */
  /* 修改: 1.1em (≈17.6px) - 增大次級標題 */
  font-size: 1.1em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--text-primary);
}
.time-domain-page p {
  /* 原始: 16px */
  /* 第一次修改: 17px - 略微增大內容文字 */
  /* 第二次修改: 18px - 進一步增大內容文字以提升閱讀舒適度 */
  font-size: 18px;
  line-height: 1.6;
  color: var(--text-secondary);
}
.time-domain-page a {
  font-weight: 500;
  color: var(--accent-primary);
}

.time-domain-page {
  padding: 20px;
  min-height: 100%;
}

/* ===== 表單區域樣式 ===== */
.time-domain-page :deep(.el-form) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題表單樣式 */
  color: var(--text-primary);
}

.time-domain-page :deep(.el-form-item__label) {
  /* 表單標籤文字顏色 */
  color: var(--text-primary) !important;
  font-weight: 500;
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大表單標籤文字 */
  /* 第二次修改: 16px - 進一步增大表單標籤文字 */
  font-size: 16px;
}

/* ===== 輸入框樣式 ===== */
.time-domain-page :deep(.el-input__wrapper) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.time-domain-page :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.time-domain-page :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.time-domain-page :deep(.el-input__inner) {
  /* 輸入框內部樣式 */
  background-color: transparent;
  color: var(--text-primary);
}

/* ===== 下拉選擇框樣式 ===== */
.time-domain-page :deep(.el-select) {
  /* 確保下拉框繼承正確的顏色 */
  color: var(--text-primary);
}

.time-domain-page :deep(.el-select .el-input__wrapper) {
  /* 下拉選擇框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.time-domain-page :deep(.el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.time-domain-page :deep(.el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.time-domain-page :deep(.el-select .el-input__inner) {
  /* 下拉選擇框文字 */
  color: var(--text-primary);
}

.time-domain-page :deep(.el-select__placeholder) {
  /* 下拉選擇框佔位符 */
  color: var(--text-secondary);
}

.time-domain-page :deep(.el-select__caret) {
  /* 下拉選擇框箭頭圖標 */
  color: var(--text-secondary);
}

/* ===== 下拉選單選項樣式 ===== */
/* 注意:Element Plus 下拉選單通過 Teleport 渲染到 body 層級 */
/* 下拉選單樣式已移至全局樣式文件: src/styles/select-dropdown-dark.css */
/* 該文件在 main.js 中導入,確保樣式正確應用 */

/* ===== 數字輸入框樣式 ===== */
.time-domain-page :deep(.el-input-number) {
  /* 數字輸入框整體 */
  color: var(--text-primary);
}

.time-domain-page :deep(.el-input-number .el-input__wrapper) {
  /* 數字輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.time-domain-page :deep(.el-input-number .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.time-domain-page :deep(.el-input-number .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.time-domain-page :deep(.el-input-number__decrease),
.time-domain-page :deep(.el-input-number__increase) {
  /* 數字輸入框 +/- 按鈕 */
  background-color: var(--bg-secondary);
  border: none;
  color: var(--text-primary);
}

.time-domain-page :deep(.el-input-number__decrease:hover),
.time-domain-page :deep(.el-input-number__increase:hover) {
  /* 按鈕懸停效果 */
  color: var(--accent-primary);
  background-color: var(--bg-tertiary);
}

.time-domain-page :deep(.el-input-number__decrease.is-disabled),
.time-domain-page :deep(.el-input-number__increase.is-disabled) {
  /* 禁用狀態按鈕 */
  color: var(--text-disabled);
  background-color: var(--bg-secondary);
}

/* ===== 按鈕樣式 ===== */
.time-domain-page :deep(.el-button) {
  /* 按鈕整體樣式 */
  color: var(--text-primary);
  border-color: var(--border-color);
  /* 原始: 繼承預設 (≈14px) */
  /* 修改: 15px - 增大按鈕文字 */
  font-size: 15px;
}

.time-domain-page :deep(.el-button--primary) {
  /* 主要按鈕 */
  background-color: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #ffffff;
}

.time-domain-page :deep(.el-button--primary:hover) {
  /* 主要按鈕懸停 */
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.time-domain-page :deep(.el-button--default) {
  /* 預設按鈕 */
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.time-domain-page :deep(.el-button--default:hover) {
  /* 預設按鈕懸停 */
  background-color: var(--bg-tertiary);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* ===== 分隔線樣式 ===== */
.time-domain-page :deep(.el-divider) {
  /* 分隔線整體樣式 */
  border-top-color: var(--border-color);
}

.time-domain-page :deep(.el-divider__text) {
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

.time-domain-page :deep(.el-divider--horizontal) {
  /* 水平分隔線 */
  display: flex;
  align-items: center;
  margin: 24px 0;
}

/* ===== 標題樣式 ===== */
/* [已註解] h3, h4, p 樣式已移至文件開頭的全局字體定義區域,與 FONT.md 規範對齊 */
/* 以下為補充的特定樣式調整 */
.time-domain-page h3 {
  margin-top: 0;
}

.time-domain-page h4 {
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
.time-domain-page :deep(.el-descriptions) {
  /* 確保表格在深色背景下可讀 */
  background-color: transparent;
}

.time-domain-page :deep(.el-descriptions__label) {
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

.time-domain-page :deep(.el-descriptions__content) {
  /* 表格內容列樣式 */
  color: var(--text-primary) !important;
  padding: 12px 16px !important;
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大表格內容文字 */
  /* 第二次修改: 16px - 進一步增大表格內容文字 */
  font-size: 16px;
}

/* 針對 size="small" 的 descriptions 表格增大文字以提升可讀性 */
.time-domain-page :deep(.el-descriptions.el-descriptions--small) {
  /* 覆蓋 small size 的預設字體大小 */
}
.time-domain-page :deep(.el-descriptions.el-descriptions--small .el-descriptions__label) {
  /* 原始: 16px */
  /* 第一次修改: 18px - 增大 small size 表格標籤文字以方便閱讀 */
  /* 第二次修改: 17.1px (18px * 0.95) - 縮小5%並防止文字換行 */
  font-size: 17.1px;
  padding: 14px 18px !important;
  white-space: nowrap;
}
.time-domain-page :deep(.el-descriptions.el-descriptions--small .el-descriptions__content) {
  /* 原始: 16px */
  /* 第一次修改: 18px - 增大 small size 表格內容文字以方便閱讀 */
  /* 第二次修改: 17.1px (18px * 0.95) - 縮小5%並防止文字換行 */
  font-size: 17.1px;
  padding: 14px 18px !important;
  white-space: nowrap;
}

.time-domain-page :deep(.el-descriptions__cell) {
  /* 表格單元格邊框 */
  border-color: var(--border-color) !important;
}

.time-domain-page :deep(.el-descriptions--bordered .el-descriptions__cell) {
  /* 邊框表格的單元格樣式 */
  border: 1px solid var(--border-color);
}

/* 表格標題優化 */
.time-domain-page :deep(.el-card__header) {
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.time-domain-page :deep(.el-card__body) {
  background-color: var(--bg-primary);
}

/* 數字值的特殊樣式 */
.time-domain-page :deep(.el-descriptions__content strong) {
  font-family: 'Consolas', 'Monaco', monospace;
  font-weight: 600;
  color: var(--accent-primary) !important;
}

/* ===== 診斷準則列表樣式 ===== */
.time-domain-page .diagnostic-criteria-list {
  margin: 8px 0;
  padding-left: 0;
  list-style-position: inside;
}

.time-domain-page .diagnostic-criteria-list li {
  margin: 8px 0;
  line-height: 1.6;
  /* 原始：繼承預設顼色 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
  padding-left: 8px;
  /* 原始: 繼承預設 */
  /* 第一次修改: 16px - 增大診斷準則列表文字 */
  /* 第二次修改: 17px - 進一步增大列表文字 */
  font-size: 17px;
}

/* ===== 引用區塊樣式 ===== */
.time-domain-page :deep(.el-alert__content) {
  background: transparent;
}

.time-domain-page :deep(.el-alert__title) {
  /* 原始: 繼承預設 */
  /* 第一次修改: 16px - 增大 alert 標題文字 */
  /* 第二次修改: 17px - 進一步增大 alert 標題 */
  font-size: 17px;
}

.time-domain-page :deep(.el-alert--info) {
  background: var(--bg-secondary);
  border-color: var(--accent-info);
}
</style>
