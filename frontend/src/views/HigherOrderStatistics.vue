<template>
  <div class="higher-order-stats-page">
    <el-card>
      <template #header>
        <h2>高階統計特徵分析</h2>
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
      },
      // 原始：繼承預設顏色
      // 修改：深色主題 tooltip
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      borderColor: 'var(--border-color)',
      textStyle: { color: '#ffffff' }
    },
    legend: {
      data: ['水平方向', '垂直方向'],
      top: '5%',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 繼承預設 */
      /* 第一次修改: 增大至 14 提升圖例可讀性 */
      /* 第二次修改: 增大至 15 進一步提升圖例可讀性 */
      textStyle: { color: '#ffffff', fontSize: 15 }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['水平', '垂直'],
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      axisLabel: { color: '#ffffff', fontSize: 12 },
      axisLine: { lineStyle: { color: 'var(--border-color)' } }
    },
    yAxis: {
      type: 'value',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      axisLabel: { color: '#ffffff', fontSize: 12 },
      axisLine: { lineStyle: { color: 'var(--border-color)' } },
      splitLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
      }
    }
  }

  // NA4 圖表
  if (filterChartNA4.value) {
    const chartNA4 = echarts.init(filterChartNA4.value)
    chartNA4.setOption({
      ...commonOption,
      title: {
        text: 'NA4（分段正規化四次矩）',
        left: 'center',
        /* 原始: 繼承預設 */
        /* 第一次修改: 增大至 18 提升圖表標題可讀性 */
        /* 第二次修改: 增大至 20 進一步提升圖表標題 */
        textStyle: { color: '#ffffff', fontSize: 20, fontWeight: 600 }
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
        left: 'center',
        /* 原始: 繼承預設 */
        /* 第一次修改: 增大至 18 提升圖表標題可讀性 */
        /* 第二次修改: 增大至 20 進一步提升圖表標題 */
        textStyle: { color: '#ffffff', fontSize: 20, fontWeight: 600 }
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
        left: 'center',
        /* 原始: 繼承預設 */
        /* 第一次修改: 增大至 18 提升圖表標題可讀性 */
        /* 第二次修改: 增大至 20 進一步提升圖表標題 */
        textStyle: { color: '#ffffff', fontSize: 20, fontWeight: 600 }
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
        left: 'center',
        /* 原始: 繼承預設 */
        /* 第一次修改: 增大至 18 提升圖表標題可讀性 */
        /* 第二次修改: 增大至 20 進一步提升圖表標題 */
        textStyle: { color: '#ffffff', fontSize: 20, fontWeight: 600 }
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
        left: 'center',
        /* 原始: 繼承預設 */
        /* 第一次修改: 增大至 18 提升圖表標題可讀性 */
        /* 第二次修改: 增大至 20 進一步提升圖表標題 */
        textStyle: { color: '#ffffff', fontSize: 20, fontWeight: 600 }
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
      text: '進階濾波特徵趨勢',
      // 原始：繼承預設顏色
      // 修改：深色主題白色標題
      /* 原始: 16 */
      /* 第一次修改: 18 - 增大趨勢圖標題 */
      /* 第二次修改: 20 - 進一步增大趨勢圖標題 */
      textStyle: { color: '#ffffff', fontSize: 20, fontWeight: 600 }
    },
    tooltip: {
      trigger: 'axis',
      // 原始：繼承預設顏色
      // 修改：深色主題 tooltip
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      borderColor: 'var(--border-color)',
      textStyle: { color: '#ffffff' }
    },
    legend: {
      data: ['水平 NA4', '垂直 NA4', '水平 FM4', '垂直 FM4'],
      top: '5%',
      right: '5%',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      /* 原始: 繼承預設 */
      /* 第一次修改: 增大至 14 提升圖例可讀性 */
      /* 第二次修改: 增大至 15 進一步提升圖例可讀性 */
      textStyle: { color: '#ffffff', fontSize: 15 }
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
      name: '檔案編號',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      nameTextStyle: { color: '#ffffff', fontSize: 14 },
      axisLabel: { color: '#ffffff', fontSize: 12 },
      axisLine: { lineStyle: { color: 'var(--border-color)' } },
      splitLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
      }
    },
    yAxis: {
      type: 'value',
      name: '特徵值',
      // 原始：繼承預設顏色
      // 修改：深色主題白色文字
      nameTextStyle: { color: '#ffffff', fontSize: 14 },
      axisLabel: { color: '#ffffff', fontSize: 12 },
      axisLine: { lineStyle: { color: 'var(--border-color)' } },
      splitLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
      }
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
/* ===== 原始：淺色主題 ===== */
/* ===== 修改為：Apple Keynote 深色漸層主題 ===== */

/* ===== 字體設定 - 與 FONT.md 規範對齊 ===== */
/* 原始設定: h1=3.2em, h2=1.5em, h3=1.25em, h4=1.1em, h5=1em, p=16px */
/* 修改: 增大標題與內容文字,提供更舒適的閱讀體驗 */
.higher-order-stats-page h1 {
  font-size: 3.2em;
  line-height: 1.1;
  font-weight: bold;
  color: var(--text-primary);
}
.higher-order-stats-page h2 {
  /* 原始: 1.5em (≈24px) */
  /* 第一次修改: 1.75em (≈28px) - 增大主要區塊標題 */
  /* 第二次修改: 1.85em (≈29.6px) - 進一步增大標題以提升可讀性 */
  font-size: 1.85em;
  line-height: 1.3;
  font-weight: bold;
  color: var(--text-primary);
}
.higher-order-stats-page h3 {
  /* 原始: 1.25em (≈20px) */
  /* 第一次修改: 1.4em (≈22.4px) - 增大小區塊標題 */
  /* 第二次修改: 1.5em (≈24px) - 進一步增大小區塊標題 */
  font-size: 1.5em;
  line-height: 1.4;
  font-weight: bold;
  color: var(--text-primary);
}
.higher-order-stats-page h4 {
  /* 原始: 1.1em (≈17.6px) */
  /* 第一次修改: 1.2em (≈19.2px) - 增大小標題 */
  /* 第二次修改: 1.25em (≈20px) - 進一步增大小標題 */
  font-size: 1.25em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--accent-primary);
}
.higher-order-stats-page h5 {
  /* 原始: 1em (16px) */
  /* 修改: 1.1em (≈17.6px) - 增大次級標題 */
  font-size: 1.1em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--text-primary);
}
.higher-order-stats-page p {
  /* 原始: 16px */
  /* 第一次修改: 17px - 略微增大內容文字 */
  /* 第二次修改: 18px - 進一步增大內容文字以提升閱讀舒適度 */
  font-size: 18px;
  line-height: 1.6;
  color: var(--text-secondary);
}
.higher-order-stats-page a {
  font-weight: 500;
  color: var(--accent-primary);
}

.higher-order-stats-page {
  padding: 20px;
  min-height: 100%;
}

/* ===== 表單區域樣式 ===== */
.higher-order-stats-page :deep(.el-form) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題表單樣式 */
  color: var(--text-primary);
}

.higher-order-stats-page :deep(.el-form-item__label) {
  /* 表單標籤文字顏色 */
  color: var(--text-primary) !important;
  font-weight: 500;
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大表單標籤文字 */
  /* 第二次修改: 16px - 進一步增大表單標籤文字 */
  font-size: 16px;
}

/* ===== 輸入框樣式 ===== */
.higher-order-stats-page :deep(.el-input__wrapper) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.higher-order-stats-page :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.higher-order-stats-page :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.higher-order-stats-page :deep(.el-input__inner) {
  /* 輸入框內部樣式 */
  background-color: transparent;
  color: var(--text-primary);
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大輸入框文字 */
  /* 第二次修改: 16px - 進一步增大輸入框文字 */
  font-size: 16px;
}

/* ===== 下拉選擇框樣式 ===== */
.higher-order-stats-page :deep(.el-select) {
  /* 確保下拉框繼承正確的顏色 */
  color: var(--text-primary);
}

.higher-order-stats-page :deep(.el-select .el-input__wrapper) {
  /* 下拉選擇框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.higher-order-stats-page :deep(.el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.higher-order-stats-page :deep(.el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.higher-order-stats-page :deep(.el-select .el-input__inner) {
  /* 下拉選擇框文字 */
  color: var(--text-primary);
}

.higher-order-stats-page :deep(.el-select__placeholder) {
  /* 下拉選擇框佔位符 */
  color: var(--text-secondary);
}

.higher-order-stats-page :deep(.el-select__caret) {
  /* 下拉選擇框箭頭圖標 */
  color: var(--text-secondary);
}

/* ===== 下拉選單選項樣式 ===== */
.higher-order-stats-page :deep(.el-select-dropdown) {
  /* 下拉選單背景 */
  background-color: var(--bg-card);
  border-color: var(--border-color);
}

.higher-order-stats-page :deep(.el-select-dropdown__item) {
  /* 下拉選單選項 */
  color: var(--text-primary);
  background-color: transparent;
}

.higher-order-stats-page :deep(.el-select-dropdown__item:hover) {
  /* 下拉選單選項懸停 */
  background-color: var(--bg-secondary);
  color: var(--accent-primary);
}

.higher-order-stats-page :deep(.el-select-dropdown__item.is-selected) {
  /* 下拉選單選項已選中 */
  background-color: var(--bg-tertiary);
  color: var(--accent-primary);
  font-weight: 500;
}

/* ===== 數字輸入框樣式 ===== */
.higher-order-stats-page :deep(.el-input-number) {
  /* 數字輸入框整體 */
  color: var(--text-primary);
}

.higher-order-stats-page :deep(.el-input-number .el-input__wrapper) {
  /* 數字輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.higher-order-stats-page :deep(.el-input-number .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.higher-order-stats-page :deep(.el-input-number .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.higher-order-stats-page :deep(.el-input-number__decrease),
.higher-order-stats-page :deep(.el-input-number__increase) {
  /* 數字輸入框 +/- 按鈕 */
  background-color: var(--bg-secondary);
  border: none;
  color: var(--text-primary);
}

.higher-order-stats-page :deep(.el-input-number__decrease:hover),
.higher-order-stats-page :deep(.el-input-number__increase:hover) {
  /* 按鈕懸停效果 */
  color: var(--accent-primary);
  background-color: var(--bg-tertiary);
}

.higher-order-stats-page :deep(.el-input-number__decrease.is-disabled),
.higher-order-stats-page :deep(.el-input-number__increase.is-disabled) {
  /* 禁用狀態按鈕 */
  color: var(--text-disabled);
  background-color: var(--bg-secondary);
}

/* ===== 按鈕樣式 ===== */
.higher-order-stats-page :deep(.el-button) {
  /* 按鈕整體樣式 */
  color: var(--text-primary);
  border-color: var(--border-color);
  /* 原始: 繼承預設 (≈14px) */
  /* 修改: 15px - 增大按鈕文字 */
  font-size: 15px;
}

.higher-order-stats-page :deep(.el-button--primary) {
  /* 主要按鈕 */
  background-color: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #ffffff;
}

.higher-order-stats-page :deep(.el-button--primary:hover) {
  /* 主要按鈕懸停 */
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.higher-order-stats-page :deep(.el-button--default) {
  /* 預設按鈕 */
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.higher-order-stats-page :deep(.el-button--default:hover) {
  /* 預設按鈕懸停 */
  background-color: var(--bg-tertiary);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* ===== 分隔線樣式 ===== */
.higher-order-stats-page :deep(.el-divider) {
  /* 分隔線整體樣式 */
  border-top-color: var(--border-color);
}

.higher-order-stats-page :deep(.el-divider__text) {
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

.higher-order-stats-page :deep(.el-divider--horizontal) {
  /* 水平分隔線 */
  display: flex;
  align-items: center;
  margin: 24px 0;
}

/* ===== 標題樣式 ===== */
/* [已註解] h3, h4, p 樣式已移至文件開頭的全局字體定義區域,與 FONT.md 規範對齊 */
/* 以下為補充的特定樣式調整 */
.higher-order-stats-page h3 {
  margin-top: 0;
}

.higher-order-stats-page h4 {
  margin-top: 20px;
  /* 確保標題在深色背景下可讀 */
  background: var(--bg-secondary);
  padding: 10px 15px;
  border-radius: 6px;
  border-left: 4px solid var(--accent-primary);
}

.higher-order-stats-page code {
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
.higher-order-stats-page :deep(.el-descriptions) {
  /* 確保表格在深色背景下可讀 */
  background-color: transparent;
}

.higher-order-stats-page :deep(.el-descriptions__label) {
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

.higher-order-stats-page :deep(.el-descriptions__content) {
  /* 表格內容列樣式 */
  color: var(--text-primary) !important;
  padding: 12px 16px !important;
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大表格內容文字 */
  /* 第二次修改: 16px - 進一步增大表格內容文字 */
  font-size: 16px;
}

/* 針對 size="small" 的 descriptions 表格增大文字以提升可讀性 */
.higher-order-stats-page :deep(.el-descriptions.el-descriptions--small) {
  /* 覆蓋 small size 的預設字體大小 */
}
.higher-order-stats-page :deep(.el-descriptions.el-descriptions--small .el-descriptions__label) {
  /* 原始: 16px */
  /* 第一次修改: 18px - 增大 small size 表格標籤文字以方便閱讀 */
  /* 第二次修改: 17.1px (18px * 0.95) - 縮小5%並防止文字換行 */
  font-size: 17.1px;
  padding: 14px 18px !important;
  white-space: nowrap;
}
.higher-order-stats-page :deep(.el-descriptions.el-descriptions--small .el-descriptions__content) {
  /* 原始: 16px */
  /* 第一次修改: 18px - 增大 small size 表格內容文字以方便閱讀 */
  /* 第二次修改: 17.1px (18px * 0.95) - 縮小5%並防止文字換行 */
  font-size: 17.1px;
  padding: 14px 18px !important;
  white-space: nowrap;
}
.higher-order-stats-page :deep(.el-descriptions.el-descriptions--small .el-tag) {
  /* el-tag 內的文字大小調整 */
  font-size: 17.1px !important;
}

.higher-order-stats-page :deep(.el-descriptions__cell) {
  /* 表格單元格邊框 */
  border-color: var(--border-color) !important;
}

.higher-order-stats-page :deep(.el-descriptions--bordered .el-descriptions__cell) {
  /* 邊框表格的單元格樣式 */
  border: 1px solid var(--border-color);
}

/* 表格標題優化 */
.higher-order-stats-page :deep(.el-card__header) {
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.higher-order-stats-page :deep(.el-card__body) {
  background-color: var(--bg-primary);
}

/* ===== Alert 樣式 ===== */
.higher-order-stats-page :deep(.el-alert--success) {
  background: var(--bg-secondary);
  border-color: var(--accent-success);
}

/* ===== Tag 樣式 ===== */
.higher-order-stats-page :deep(.el-tag) {
  color: var(--text-primary);
  border-color: var(--border-color);
}

/* 原始：組件特定樣式保留 .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-primary);
}

.card-header h2 {
  // 深色主題漸層文字效果
  background: linear-gradient(135deg, #ffffff, var(--text-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
} */
</style>
