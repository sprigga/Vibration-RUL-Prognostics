<template>
  <div class="algorithms-page">
    <el-card>
      <template #header>
        <h2>演算法原理與應用展示</h2>
      </template>

      <el-collapse v-model="activeAlgorithms" accordion>
        <!-- Time Domain -->
        <el-collapse-item title="時域特徵分析" name="time-domain">
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
        </el-collapse-item>

        <!-- Envelope Analysis & Hilbert Transform (Merged) -->
        <el-collapse-item title="包絡分析與希爾伯特轉換（Envelope Analysis & Hilbert Transform）" name="envelope-hilbert">
          <h3>原理說明</h3>
          <p>希爾伯特轉換是信號處理中的重要工具，用於提取信號的瞬時特徵。包絡分析結合帶通濾波與希爾伯特轉換，特別適合檢測軸承故障的週期性衝擊特徵。</p>

          <h4>核心概念:</h4>
          <el-descriptions :column="1" border style="margin-bottom: 20px;">
            <el-descriptions-item label="解析信號">
              <code>z(t) = x(t) + jH[x(t)]</code>
              <p>將實數信號轉換為複數解析信號，其中 H[·] 為希爾伯特轉換</p>
            </el-descriptions-item>
            <el-descriptions-item label="包絡線（振幅）">
              <code>A(t) = |z(t)| = √(x²(t) + H[x(t)]²)</code>
              <p>信號的瞬時振幅，反映調變信號的能量變化</p>
            </el-descriptions-item>
            <el-descriptions-item label="瞬時相位">
              <code>φ(t) = arctan(H[x(t)] / x(t))</code>
              <p>信號的瞬時相位角</p>
            </el-descriptions-item>
            <el-descriptions-item label="瞬時頻率">
              <code>f(t) = (1/2π) · dφ/dt</code>
              <p>相位對時間的導數，反映頻率的時間變化</p>
            </el-descriptions-item>
            <el-descriptions-item label="NB4 特徵">
              <code>NB4 = N·Σ(A-μ)⁴ / [Σ(A-μ_segment)²/M]²</code>
              <p>正規化四次矩（分段計算），檢測包絡線的尖峰特性，> 3 表示存在顯著衝擊</p>
            </el-descriptions-item>
          </el-descriptions>

          <h4>包絡頻譜分析流程:</h4>
          <el-steps direction="vertical" :active="5">
            <el-step title="帶通濾波" description="選擇共振頻帶（如 4-10 kHz），濾除低頻干擾" />
            <el-step title="希爾伯特轉換" description="計算解析信號 z(t) = x(t) + jH[x(t)]" />
            <el-step title="提取包絡" description="取振幅包絡 A(t) = |z(t)|" />
            <el-step title="FFT 分析" description="對包絡信號做頻譜分析" />
            <el-step title="特徵識別" description="尋找故障特徵頻率（BPFO/BPFI）及其諧波" />
          </el-steps>

          <h4 style="margin-top: 20px;">振幅指標:</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="包絡RMS (Envelope RMS)">
              <code>ERMS = √(1/N * ΣA²(t))</code>
              <p>包絡信號的均方根值，反映整體振動能量</p>
            </el-descriptions-item>
            <el-descriptions-item label="包絡峰值 (Envelope Peak)">
              <code>Peak = max(A(t))</code>
              <p>包絡信號的最大值，用於檢測衝擊強度</p>
            </el-descriptions-item>
            <el-descriptions-item label="總功率 (Total Power)">
              <code>Power = ΣMagnitude²(f)</code>
              <p>包絡頻譜的總能量</p>
            </el-descriptions-item>
            <el-descriptions-item label="信噪比 (SNR)">
              <code>SNR = Peak_Signal / Noise_Level</code>
              <p>信號與噪聲的比值，> 3 表示缺陷顯著</p>
            </el-descriptions-item>
          </el-descriptions>

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

          <h4 style="margin-top: 20px;">共振頻帶選擇:</h4>
          <el-table :data="resonanceBands" border>
            <el-table-column prop="series" label="滑軌系列" />
            <el-table-column prop="band" label="共振頻帶 (Hz)" />
            <el-table-column prop="reason" label="說明" />
          </el-table>

          <h4 style="margin-top: 20px;">應用場景:</h4>
          <el-tag type="danger" style="margin: 5px;">調幅信號分析</el-tag>
          <el-tag type="warning" style="margin: 5px;">軸承故障檢測</el-tag>
          <el-tag type="info" style="margin: 5px;">瞬時特徵提取</el-tag>

          <el-alert
            title="診斷準則"
            type="warning"
            style="margin-top: 15px;"
            :closable="false"
          >
            <ul style="margin: 5px 0; padding-left: 20px;">
              <li>包絡譜出現 BPFO/BPFI → 滾動體或軌道缺陷</li>
              <li>信噪比 > 3 → 缺陷顯著</li>
              <li>多個諧波 (2×BPFO, 3×BPFO...) → 缺陷嚴重</li>
              <li>包絡 RMS 上升 → 振動能量增加</li>
              <li>NB4 > 3 → 包絡線存在顯著峰值（可能有衝擊）</li>
              <li>瞬時頻率波動大 → 非穩態運轉</li>
            </ul>
          </el-alert>

          <h4 style="margin-top: 20px;">診斷嚴重程度標準:</h4>
          <el-table :data="severityLevels" border>
            <el-table-column prop="severity" label="嚴重程度" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.tagType">{{ scope.row.severity }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="envelope_rms" label="包絡RMS" width="120" />
            <el-table-column prop="snr" label="信噪比" width="100" />
            <el-table-column prop="harmonics" label="諧波數量" width="100" />
            <el-table-column prop="action" label="維護建議" />
          </el-table>

          <!-- 包絡分析計算區域 -->
          <el-divider>即時計算演示</el-divider>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form label-width="120px">
                <el-form-item label="選擇軸承">
                  <el-select v-model="envelopeParams.bearingName" placeholder="請選擇軸承">
                    <el-option label="Bearing1_1" value="Bearing1_1" />
                    <el-option label="Bearing1_2" value="Bearing1_2" />
                    <el-option label="Bearing2_1" value="Bearing2_1" />
                    <el-option label="Bearing2_2" value="Bearing2_2" />
                    <el-option label="Bearing3_1" value="Bearing3_1" />
                  </el-select>
                </el-form-item>
                <el-form-item label="檔案編號">
                  <el-input-number v-model="envelopeParams.fileNumber" :min="1" :max="100" />
                </el-form-item>
                <el-form-item label="低通頻率 (Hz)">
                  <el-input-number v-model="envelopeParams.lowcut" :min="0" :step="100" />
                </el-form-item>
                <el-form-item label="高通頻率 (Hz)">
                  <el-input-number v-model="envelopeParams.highcut" :min="0" :step="100" />
                </el-form-item>
                <el-form-item label="分段數量">
                  <el-input-number v-model="envelopeParams.segmentCount" :min="5" :max="20" />
                  <el-text size="small" type="info">用於計算 NB4 特徵</el-text>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="calculateEnvelope" :loading="envelopeLoading">
                    計算完整分析
                  </el-button>
                </el-form-item>
              </el-form>
            </el-col>
            <el-col :span="12" v-if="envelopeResult">
              <el-card shadow="hover">
                <template #header>
                  <h4>包絡分析與希爾伯特轉換結果</h4>
                </template>

                <!-- 包絡頻譜特徵 -->
                <h5 style="margin-bottom: 10px;">📊 包絡頻譜特徵</h5>
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item label="水平 Envelope RMS">
                    <el-tag type="info" size="large">{{ envelopeResult.horizontal.envelope_rms.toFixed(4) }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直 Envelope RMS">
                    <el-tag type="info" size="large">{{ envelopeResult.vertical.envelope_rms.toFixed(4) }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="水平峰值頻率" :span="2">
                    {{ envelopeResult.horizontal.peak_frequencies.slice(0, 5).map(f => f.toFixed(2)).join(', ') }} Hz
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直峰值頻率" :span="2">
                    {{ envelopeResult.vertical.peak_frequencies.slice(0, 5).map(f => f.toFixed(2)).join(', ') }} Hz
                  </el-descriptions-item>
                  <el-descriptions-item label="濾波頻帶" :span="2">
                    {{ envelopeResult.filter_band.lowcut }} - {{ envelopeResult.filter_band.highcut }} Hz
                  </el-descriptions-item>
                </el-descriptions>

                <!-- 希爾伯特轉換特徵 -->
                <h5 style="margin-top: 15px; margin-bottom: 10px;">🔬 希爾伯特轉換特徵 (NB4 & 包絡統計)</h5>
                <el-descriptions :column="2" border size="small" v-if="hilbertResult">
                  <el-descriptions-item label="水平 NB4">
                    <el-tag :type="hilbertResult.horizontal.nb4 > 3 ? 'danger' : 'success'">
                      {{ hilbertResult.horizontal.nb4.toFixed(4) }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直 NB4">
                    <el-tag :type="hilbertResult.vertical.nb4 > 3 ? 'danger' : 'success'">
                      {{ hilbertResult.vertical.nb4.toFixed(4) }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="水平包絡峰值">
                    {{ hilbertResult.horizontal.envelope_max.toFixed(4) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直包絡峰值">
                    {{ hilbertResult.vertical.envelope_max.toFixed(4) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="水平峰峰值">
                    {{ hilbertResult.horizontal.envelope_peak_to_peak.toFixed(4) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直峰峰值">
                    {{ hilbertResult.vertical.envelope_peak_to_peak.toFixed(4) }}
                  </el-descriptions-item>
                </el-descriptions>
                <el-alert v-else type="info" :closable="false" style="margin-top: 10px;">
                  希爾伯特轉換特徵正在計算中...
                </el-alert>

                <!-- 故障頻率識別 -->
                <el-divider>故障頻率識別</el-divider>
                <div v-if="detectedFaults.length > 0">
                  <el-alert
                    v-for="fault in detectedFaults"
                    :key="fault.type"
                    :title="fault.title"
                    :type="fault.severity"
                    style="margin-bottom: 10px;"
                    show-icon
                  >
                    <p>檢測到頻率: {{ fault.detected_freq.toFixed(2) }} Hz</p>
                    <p>理論頻率: {{ fault.expected_freq.toFixed(2) }} Hz</p>
                    <p>諧波次數: {{ fault.harmonics.join(', ') }}</p>
                  </el-alert>
                </div>
                <el-empty v-else description="未檢測到明顯故障特徵頻率" :image-size="80" />
              </el-card>
            </el-col>
          </el-row>

          <!-- 包絡頻譜圖 -->
          <div v-if="envelopeResult" style="margin-top: 20px;">
            <el-card>
              <template #header>
                <h4>包絡頻譜圖</h4>
              </template>
              <div ref="envelopeChart" style="width: 100%; height: 400px;"></div>
            </el-card>
          </div>

          <!-- 故障頻率參考圖 -->
          <div v-if="envelopeResult" style="margin-top: 20px;">
            <el-card>
              <template #header>
                <h4>故障頻率參考圖 (Fault Frequency Reference)</h4>
              </template>
              <div ref="faultFreqReferenceChart" style="width: 100%; height: 300px;"></div>
              <el-alert
                type="info"
                :closable="false"
                style="margin-top: 10px;"
              >
                <template #title>
                  <strong>說明：</strong>此圖顯示當前軸承的理論故障頻率位置，用於對照包絡頻譜圖進行故障診斷
                </template>
              </el-alert>
            </el-card>
          </div>

          <!-- 包絡線波形與瞬時頻率圖 -->
          <div v-if="hilbertResult" style="margin-top: 20px;">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <h4>包絡線波形 (Envelope Waveform)</h4>
                  </template>
                  <div ref="hilbertEnvelopeChart" style="width: 100%; height: 400px;"></div>
                  <el-alert type="info" :closable="false" style="margin-top: 10px;">
                    <template #title>
                      <strong>說明：</strong>包絡線反映信號的瞬時振幅變化，可識別週期性衝擊
                    </template>
                  </el-alert>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <h4>瞬時頻率 (Instantaneous Frequency)</h4>
                  </template>
                  <div ref="hilbertFreqChart" style="width: 100%; height: 400px;"></div>
                  <el-alert type="info" :closable="false" style="margin-top: 10px;">
                    <template #title>
                      <strong>說明：</strong>瞬時頻率反映信號頻率的時間變化，適合分析非穩態信號
                    </template>
                  </el-alert>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-collapse-item>

      </el-collapse>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <h2>演算法應用對應表</h2>
      </template>

      <el-table :data="algorithmMapping" border stripe>
        <el-table-column prop="module" label="專案模組" width="180" />
        <el-table-column prop="application" label="應用於線性滑軌" width="180" />
        <el-table-column prop="fault_type" label="檢測故障類型" />
        <el-table-column prop="cpc_params" label="CPC 參數關聯" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import * as echarts from 'echarts'

const activeAlgorithms = ref('time-domain')

// 時域計算參數
const timeDomainParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1
})

const timeDomainLoading = ref(false)
const trendLoading = ref(false)
const timeDomainResult = ref(null)
const trendResult = ref(null)

// Envelope 參數
const envelopeParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1,
  lowcut: 4000,
  highcut: 10000,
  segmentCount: 10
})
const envelopeLoading = ref(false)
const envelopeResult = ref(null)

// Hilbert Transform 參數
const hilbertParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1,
  segmentCount: 10
})
const hilbertLoading = ref(false)
const hilbertResult = ref(null)

// Chart refs
const timeDomainSignalChart = ref(null)
const timeDomainTrendChart = ref(null)
const envelopeChart = ref(null)
const faultFreqReferenceChart = ref(null)
const hilbertEnvelopeChart = ref(null)
const hilbertFreqChart = ref(null)

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

// 計算包絡頻譜與希爾伯特轉換（合併）
const calculateEnvelope = async () => {
  envelopeLoading.value = true
  hilbertLoading.value = true
  try {
    const { bearingName, fileNumber, lowcut, highcut, segmentCount } = envelopeParams.value

    // 並行調用包絡分析和希爾伯特轉換 API
    const [envelopeResponse, hilbertResponse] = await Promise.all([
      fetch(`http://localhost:8081/api/algorithms/envelope/${bearingName}/${fileNumber}?lowcut=${lowcut}&highcut=${highcut}`),
      fetch(`http://localhost:8081/api/algorithms/hilbert/${bearingName}/${fileNumber}?segment_count=${segmentCount}`)
    ])

    if (!envelopeResponse.ok || !hilbertResponse.ok) {
      throw new Error('計算失敗')
    }

    envelopeResult.value = await envelopeResponse.json()
    hilbertResult.value = await hilbertResponse.json()

    // 執行故障頻率檢測
    detectFaultFrequencies()

    await nextTick()
    drawEnvelopeChart()
    drawFaultFreqReferenceChart()
    drawHilbertEnvelopeChart()
    drawHilbertFreqChart()
  } catch (error) {
    console.error('計算包絡分析與希爾伯特轉換失敗:', error)
    alert('計算失敗: ' + error.message)
  } finally {
    envelopeLoading.value = false
    hilbertLoading.value = false
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

// 繪製包絡頻譜圖（不含故障頻率標記）
const drawEnvelopeChart = () => {
  if (!envelopeChart.value || !envelopeResult.value) return

  const chart = echarts.init(envelopeChart.value)

  const { frequency, horizontal_magnitude, vertical_magnitude } = envelopeResult.value.envelope_spectrum

  // 獲取當前軸承的故障頻率
  const bearingName = envelopeResult.value.bearing_name
  const bearingInfo = bearingFaultFrequencies.find(b => b.bearing === bearingName)

  const option = {
    title: {
      text: `包絡頻譜 - ${bearingName}`,
      subtext: bearingInfo ? `轉速: ${bearingInfo.rpm} RPM, 軸頻率: ${bearingInfo.shaft_freq.toFixed(2)} Hz` : ''
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        if (!params || params.length === 0) return ''
        const dataIndex = params[0].dataIndex
        const freq = frequency[dataIndex]
        let result = `頻率: ${freq.toFixed(2)} Hz<br/>`
        params.forEach(p => {
          const value = Array.isArray(p.value) ? p.value[1] : p.value
          result += `${p.seriesName}: ${value.toFixed(6)}<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['水平方向', '垂直方向'],
      top: '5%',
      right: '5%'
    },
    grid: {
      left: '60px',
      right: '40px',
      bottom: '80px',  // 增加底部空間給 dataZoom slider
      top: '80px',
      containLabel: false
    },
    xAxis: {
      type: 'value',
      name: '頻率 (Hz)',
      nameLocation: 'middle',
      nameGap: 30,
      min: 0,
      max: Math.max(...frequency)
    },
    yAxis: {
      type: 'value',
      name: '幅值',
      nameLocation: 'middle',
      nameGap: 40,
      min: 0,
      max: 0.05
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        start: 0,
        end: 50,  // 預設顯示前50%
        height: 20,
        bottom: 10,
        brushSelect: false,
        handleSize: '80%',
        showDetail: true
      },
      {
        type: 'inside',
        xAxisIndex: [0],
        zoomOnMouseWheel: true,
        moveOnMouseMove: true,
        moveOnMouseWheel: false
      }
    ],
    series: [
      {
        name: '水平方向',
        type: 'line',
        data: frequency.map((f, i) => [f, horizontal_magnitude[i]]),
        showSymbol: false,
        lineStyle: { width: 1.5, color: '#5470c6' },
        sampling: 'lttb'
      },
      {
        name: '垂直方向',
        type: 'line',
        data: frequency.map((f, i) => [f, vertical_magnitude[i]]),
        showSymbol: false,
        lineStyle: { width: 1.5, color: '#91cc75' },
        sampling: 'lttb'
      }
    ]
  }

  chart.setOption(option)
}

// 繪製故障頻率參考圖
const drawFaultFreqReferenceChart = () => {
  if (!faultFreqReferenceChart.value || !envelopeResult.value) return

  const chart = echarts.init(faultFreqReferenceChart.value)

  const bearingName = envelopeResult.value.bearing_name
  const bearingInfo = bearingFaultFrequencies.find(b => b.bearing === bearingName)

  if (!bearingInfo) return

  // 準備故障頻率數據（顯示基頻及諧波）
  const faultTypes = [
    { name: 'BPFO', freq: bearingInfo.bpfo, color: '#f56c6c', harmonics: 3 },
    { name: 'BPFI', freq: bearingInfo.bpfi, color: '#e6a23c', harmonics: 3 },
    { name: 'BSF', freq: bearingInfo.bsf, color: '#409eff', harmonics: 2 },
    { name: 'FTF', freq: bearingInfo.ftf, color: '#67c23a', harmonics: 2 }
  ]

  // 計算最大頻率範圍
  const maxFreq = Math.max(...faultTypes.map(f => f.freq * f.harmonics)) * 1.2

  // 準備標記線數據
  const markLines = []
  faultTypes.forEach(faultType => {
    // 基頻
    markLines.push({
      name: `${faultType.name}: ${faultType.freq.toFixed(2)} Hz`,
      xAxis: faultType.freq,
      lineStyle: { color: faultType.color, type: 'solid', width: 2 },
      label: {
        show: true,
        formatter: `${faultType.name}\n${faultType.freq.toFixed(2)}Hz`,
        position: 'end',
        fontSize: 11,
        color: faultType.color,
        fontWeight: 'bold'
      }
    })

    // 諧波
    for (let h = 2; h <= faultType.harmonics; h++) {
      markLines.push({
        name: `${h}×${faultType.name}`,
        xAxis: faultType.freq * h,
        lineStyle: { color: faultType.color, type: 'dashed', width: 1 },
        label: {
          show: true,
          formatter: `${h}×${faultType.name}\n${(faultType.freq * h).toFixed(2)}Hz`,
          position: 'end',
          fontSize: 9,
          color: faultType.color
        }
      })
    }
  })

  const option = {
    title: {
      text: `故障頻率參考 - ${bearingName}`,
      subtext: `轉速: ${bearingInfo.rpm} RPM`,
      left: 'left',
      top: '1%'
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        return `頻率位置: {b} Hz`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '8%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '頻率 (Hz)',
      min: 0,
      max: maxFreq,
      splitLine: {
        show: true,
        lineStyle: {
          type: 'dotted',
          color: '#e0e0e0'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '參考強度',
      min: 0,
      max: 1,
      show: false
    },
    series: [
      {
        name: '故障頻率參考',
        type: 'line',
        data: [[0, 0], [maxFreq, 0]],
        showSymbol: false,
        lineStyle: { width: 0 },
        markLine: {
          silent: false,
          symbol: ['none', 'none'],
          data: markLines,
          animation: true
        }
      }
    ]
  }

  chart.setOption(option)
}

// 繪製希爾伯特包絡線圖
const drawHilbertEnvelopeChart = () => {
  if (!hilbertEnvelopeChart.value || !hilbertResult.value) return

  const chart = echarts.init(hilbertEnvelopeChart.value)

  const { time, horizontal, vertical } = hilbertResult.value.envelope_data

  const option = {
    title: {
      text: '包絡線波形'
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
      data: time,
      name: '樣本點'
    },
    yAxis: {
      type: 'value',
      name: '包絡振幅'
    },
    series: [
      {
        name: '水平方向',
        type: 'line',
        data: horizontal,
        showSymbol: false,
        lineStyle: { width: 1.5 }
      },
      {
        name: '垂直方向',
        type: 'line',
        data: vertical,
        showSymbol: false,
        lineStyle: { width: 1.5 }
      }
    ]
  }

  chart.setOption(option)
}

// 繪製希爾伯特瞬時頻率圖
const drawHilbertFreqChart = () => {
  if (!hilbertFreqChart.value || !hilbertResult.value) return

  const chart = echarts.init(hilbertFreqChart.value)

  const { horizontal, vertical } = hilbertResult.value.instantaneous_frequency
  const time = Array.from({ length: horizontal.length }, (_, i) => i)

  const option = {
    title: {
      text: '瞬時頻率'
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
      data: time,
      name: '樣本點'
    },
    yAxis: {
      type: 'value',
      name: '頻率 (Hz)'
    },
    series: [
      {
        name: '水平方向',
        type: 'line',
        data: horizontal,
        showSymbol: false,
        lineStyle: { width: 1.5 },
        smooth: true
      },
      {
        name: '垂直方向',
        type: 'line',
        data: vertical,
        showSymbol: false,
        lineStyle: { width: 1.5 },
        smooth: true
      }
    ]
  }

  chart.setOption(option)
}

// IEEE PHM 2012 SKF 6205 軸承故障頻率計算 (基於文檔 13.1.2 節)
const bearingFaultFrequencies = [
  { bearing: 'Bearing1_1', rpm: 1800, shaft_freq: 30.0, bpfo: 95.59, bpfi: 144.41, bsf: 70.70, ftf: 11.95, description: '外圈故障頻率為主要監測對象' },
  { bearing: 'Bearing1_2', rpm: 1650, shaft_freq: 27.5, bpfo: 87.63, bpfi: 132.37, bsf: 64.81, ftf: 10.95, description: '外圈故障頻率為主要監測對象' },
  { bearing: 'Bearing2_1', rpm: 1650, shaft_freq: 27.5, bpfo: 87.63, bpfi: 132.37, bsf: 64.81, ftf: 10.95, description: '外圈故障頻率為主要監測對象' },
  { bearing: 'Bearing2_2', rpm: 1800, shaft_freq: 30.0, bpfo: 95.59, bpfi: 144.41, bsf: 70.70, ftf: 11.95, description: '外圈故障頻率為主要監測對象' },
  { bearing: 'Bearing3_1', rpm: 1500, shaft_freq: 25.0, bpfo: 79.66, bpfi: 120.34, bsf: 58.92, ftf: 9.96, description: '外圈故障頻率為主要監測對象' },
  { bearing: 'Bearing3_2', rpm: 1650, shaft_freq: 27.5, bpfo: 87.63, bpfi: 132.37, bsf: 64.81, ftf: 10.95, description: '外圈故障頻率為主要監測對象' }
]

// 診斷嚴重程度標準 (基於文檔 13.4 節)
const severityLevels = [
  { severity: '正常', envelope_rms: '< 0.03', snr: '< 2.0', harmonics: '0-1', action: '正常監測', tagType: 'success' },
  { severity: '輕微異常', envelope_rms: '0.03-0.06', snr: '2.0-3.0', harmonics: '1-2', action: '加強監測', tagType: 'info' },
  { severity: '中度故障', envelope_rms: '0.06-0.10', snr: '3.0-5.0', harmonics: '2-3', action: '計畫維護', tagType: 'warning' },
  { severity: '嚴重故障', envelope_rms: '> 0.10', snr: '> 5.0', harmonics: '> 3', action: '立即維護', tagType: 'danger' }
]

const resonanceBands = [
  { series: '微型 (MR)', band: '8,000 - 15,000', reason: '尺寸小，共振頻率高' },
  { series: '小型 (15/20/25)', band: '4,000 - 10,000', reason: '標準共振範圍' },
  { series: '中型 (30/35/45)', band: '2,000 - 8,000', reason: '尺寸增大，頻率降低' },
  { series: '大型 (55/65)', band: '1,000 - 6,000', reason: '大尺寸，低頻共振' }
]


const algorithmMapping = [
  { module: '時域特徵', application: '整體健康監控', fault_type: '磨損程度、振動異常', cpc_params: 'C₀, C₁₀₀, 負荷等級' },
  { module: '頻域特徵', application: '故障頻率識別', fault_type: '滾動體缺陷、軌道剝落', cpc_params: '滑座型式、滾動體數量' },
  { module: '時頻分析 (STFT/CWT)', application: '瞬態衝擊檢測', fault_type: '異物、局部缺陷、非穩態信號', cpc_params: '密封片類型、環境條件' },
  { module: '高階統計', application: '早期故障檢測', fault_type: '微小缺陷、潤滑不良', cpc_params: '潤滑系統、摩擦阻力' },
  { module: '希爾伯特包絡', application: '滾動體故障', fault_type: '滾珠/滾子剝落', cpc_params: '基本動負荷 C₁₀₀' },
  { module: '諧波與邊帶', application: '安裝問題', fault_type: '平行度不良、安裝偏差', cpc_params: '安裝精度、剛性' }
]

// 故障頻率檢測 (基於文檔 13.3 節)
const detectedFaults = ref([])

// 檢測故障頻率函數
const detectFaultFrequencies = () => {
  if (!envelopeResult.value) {
    detectedFaults.value = []
    return
  }

  const bearingName = envelopeResult.value.bearing_name
  const bearingInfo = bearingFaultFrequencies.find(b => b.bearing === bearingName)

  if (!bearingInfo) {
    detectedFaults.value = []
    return
  }

  const faults = []
  const tolerance = 0.05 // 5% 容差

  // 取水平和垂直方向的峰值頻率
  const allPeakFreqs = [
    ...envelopeResult.value.horizontal.peak_frequencies.slice(0, 10),
    ...envelopeResult.value.vertical.peak_frequencies.slice(0, 10)
  ]

  // 檢測 BPFO (外圈故障頻率)
  const bpfoMatches = findHarmonics(allPeakFreqs, bearingInfo.bpfo, tolerance)
  if (bpfoMatches.length > 0) {
    const severity = bpfoMatches.length >= 3 ? 'error' : (bpfoMatches.length >= 2 ? 'warning' : 'info')
    faults.push({
      type: 'BPFO',
      title: `檢測到外圈故障頻率 (BPFO) - ${bpfoMatches.length} 個諧波`,
      detected_freq: bpfoMatches[0],
      expected_freq: bearingInfo.bpfo,
      harmonics: bpfoMatches.map((f, i) => `${(i + 1)}×BPFO`),
      severity: severity
    })
  }

  // 檢測 BPFI (內圈故障頻率)
  const bpfiMatches = findHarmonics(allPeakFreqs, bearingInfo.bpfi, tolerance)
  if (bpfiMatches.length > 0) {
    const severity = bpfiMatches.length >= 3 ? 'error' : (bpfiMatches.length >= 2 ? 'warning' : 'info')
    faults.push({
      type: 'BPFI',
      title: `檢測到內圈故障頻率 (BPFI) - ${bpfiMatches.length} 個諧波`,
      detected_freq: bpfiMatches[0],
      expected_freq: bearingInfo.bpfi,
      harmonics: bpfiMatches.map((f, i) => `${(i + 1)}×BPFI`),
      severity: severity
    })
  }

  // 檢測 BSF (滾動體自轉頻率)
  const bsfMatches = findHarmonics(allPeakFreqs, bearingInfo.bsf, tolerance)
  if (bsfMatches.length > 0) {
    faults.push({
      type: 'BSF',
      title: `檢測到滾動體故障頻率 (BSF)`,
      detected_freq: bsfMatches[0],
      expected_freq: bearingInfo.bsf,
      harmonics: bsfMatches.map((f, i) => `${(i + 1)}×BSF`),
      severity: 'warning'
    })
  }

  detectedFaults.value = faults
}

// 尋找諧波頻率
const findHarmonics = (peakFreqs, targetFreq, tolerance) => {
  const matches = []

  // 檢測基頻和前5個諧波
  for (let harmonic = 1; harmonic <= 5; harmonic++) {
    const expectedFreq = targetFreq * harmonic
    const match = peakFreqs.find(f => {
      const error = Math.abs(f - expectedFreq) / expectedFreq
      return error <= tolerance
    })

    if (match) {
      matches.push(match)
    }
  }

  return matches
}
</script>

<style scoped>
/* ===== 原始：淺色主題 ===== */
/* ===== 修改為：Apple Keynote 深色漸層主題 ===== */

.algorithms-page {
  padding: 20px;
}

h3 {
  /* 原始：#303133 */
  /* 修改：深色主題主要文字 */
  color: var(--text-primary);
  margin-top: 15px;
  margin-bottom: 10px;
}

h4 {
  /* 原始：#606266 */
  /* 修改：深色主題次要文字 */
  color: var(--accent-primary);
  margin-top: 15px;
  margin-bottom: 10px;
  /* 確保標題在深色背景下可讀 */
  background: var(--bg-secondary);
  padding: 10px 15px;
  border-radius: 6px;
  border-left: 4px solid var(--accent-primary);
}

code {
  /* 原始：#f5f7fa */
  /* 修改：深色主題代碼背景 */
  background-color: var(--bg-tertiary);
  padding: 2px 8px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  /* 原始：#e6a23c */
  /* 修改：使用強調色 */
  color: var(--accent-warning);
}

p {
  /* 原始：#606266 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 8px 0;
}
</style>
