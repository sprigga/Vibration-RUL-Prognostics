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

        <!-- Frequency Domain -->
        <el-collapse-item title="頻域特徵分析" name="frequency-domain">
          <h3>原理說明</h3>
          <p>透過快速傅立葉轉換（FFT）將時域信號轉換為頻域，識別故障特徵頻率。</p>

          <h4>關鍵概念:</h4>
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
                  <el-descriptions-item label="水平 MGS">
                    {{ (frequencyDomainResult.horizontal?.total_fft_mgs || frequencyDomainResult.horizontal?.total_tsa_fft_mgs)?.toFixed(6) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直 MGS">
                    {{ (frequencyDomainResult.vertical?.total_fft_mgs || frequencyDomainResult.vertical?.total_tsa_fft_mgs)?.toFixed(6) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="水平 BI">
                    {{ (frequencyDomainResult.horizontal?.total_fft_bi || frequencyDomainResult.horizontal?.total_tsa_fft_bi)?.toFixed(6) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直 BI">
                    {{ (frequencyDomainResult.vertical?.total_fft_bi || frequencyDomainResult.vertical?.total_tsa_fft_bi)?.toFixed(6) }}
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

        <!-- Wavelet Analysis / Time-Frequency Analysis -->
        <el-collapse-item title="時頻分析（STFT & CWT）" name="wavelet">
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
        </el-collapse-item>

        <!-- Consolidated Higher Order Statistics & Advanced Filter Features -->
        <el-collapse-item title="高階統計特徵分析 (NA4, FM4, M6A, M8A, ER)" name="higher-order-stats">
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
                    {{ filterResult.horizontal.na4.toFixed(4) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直 NA4">
                    {{ filterResult.vertical.na4.toFixed(4) }}
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

// 高階統計參數
const higherOrderParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1
})
const higherOrderLoading = ref(false)
const higherOrderResult = ref(null)

// Spectrogram 參數
const spectrogramParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1
})
const spectrogramLoading = ref(false)
const spectrogramResult = ref(null)

// Hilbert Transform 參數
const hilbertParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1,
  segmentCount: 10
})
const hilbertLoading = ref(false)
const hilbertResult = ref(null)

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
const timeDomainSignalChart = ref(null)
const timeDomainTrendChart = ref(null)
const stftChart = ref(null)
const cwtChartHoriz = ref(null)
const cwtEnergyChart = ref(null)
const higherOrderChart = ref(null)
const envelopeChart = ref(null)
const faultFreqReferenceChart = ref(null)
const frequencyDomainChart = ref(null)
const spectrogramChart = ref(null)
const hilbertEnvelopeChart = ref(null)
const hilbertFreqChart = ref(null)
const filterChartNA4 = ref(null)
const filterChartFM4 = ref(null)
const filterChartM6A = ref(null)
const filterChartM8A = ref(null)
const filterChartER = ref(null)
const filterTrendChart = ref(null)

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

// 計算頻域特徵
const frequencyDomainParams = ref({
  bearingName: 'Bearing1_1',
  fileNumber: 1
})
const frequencyMethod = ref('fft')
const frequencyDomainLoading = ref(false)
const frequencyDomainResult = ref(null)

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

// 計算高階統計
const calculateHigherOrder = async () => {
  higherOrderLoading.value = true
  try {
    const response = await fetch(
      `http://localhost:8081/api/algorithms/higher-order/${higherOrderParams.value.bearingName}/${higherOrderParams.value.fileNumber}`
    )
    if (!response.ok) throw new Error('計算失敗')

    higherOrderResult.value = await response.json()

    // 繪製比較圖
    await nextTick()
    drawHigherOrderChart()
  } catch (error) {
    console.error('計算高階統計失敗:', error)
    alert('計算失敗: ' + error.message)
  } finally {
    higherOrderLoading.value = false
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

// 繪製高階統計圖
const drawHigherOrderChart = () => {
  if (!higherOrderChart.value || !higherOrderResult.value) return

  const chart = echarts.init(higherOrderChart.value)

  const option = {
    title: {
      text: '高階統計特徵比較'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['水平方向', '垂直方向'],
      top: '5%',
      right: '5%'
    },
    xAxis: {
      type: 'category',
      data: ['NA4', 'FM4', 'ER', 'Kurtosis']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '水平方向',
        type: 'bar',
        data: [
          higherOrderResult.value.horizontal.na4,
          higherOrderResult.value.horizontal.fm4,
          higherOrderResult.value.horizontal.er * 10, // 放大顯示
          higherOrderResult.value.horizontal.kurtosis
        ]
      },
      {
        name: '垂直方向',
        type: 'bar',
        data: [
          higherOrderResult.value.vertical.na4,
          higherOrderResult.value.vertical.fm4,
          higherOrderResult.value.vertical.er * 10, // 放大顯示
          higherOrderResult.value.vertical.kurtosis
        ]
      }
    ]
  }

  chart.setOption(option)
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

const faultFrequencies = [
  { type: '滾動體缺陷', frequency: 'BPF（Ball Pass Frequency）', description: '滾動體通過頻率及諧波' },
  { type: '滾動體自轉', frequency: 'BSF（Ball Spin Frequency）', description: '滾動體自身旋轉頻率' },
  { type: '保持鏈', frequency: 'Cage Frequency', description: '保持鏈旋轉頻率' }
]

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
.algorithms-page {
  padding: 20px;
}

h3 {
  color: #303133;
  margin-top: 15px;
  margin-bottom: 10px;
}

h4 {
  color: #606266;
  margin-top: 15px;
  margin-bottom: 10px;
}

code {
  background-color: #f5f7fa;
  padding: 2px 8px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #e6a23c;
}

p {
  color: #606266;
  line-height: 1.6;
  margin: 8px 0;
}
</style>
