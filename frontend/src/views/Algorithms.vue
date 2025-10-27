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
          <el-tag type="info" style="margin: 5px;">預壓狀態評估</el-tag>
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
              <li>RMS 突然下降 → 預壓可能失效</li>
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

        <!-- Envelope Analysis -->
        <el-collapse-item title="包絡分析（Envelope Analysis）" name="envelope">
          <h3>原理說明</h3>
          <p>包絡分析透過希爾伯特轉換提取信號包絡，特別適合檢測週期性衝擊。</p>

          <h4>處理流程:</h4>
          <el-steps direction="vertical" :active="4">
            <el-step title="帶通濾波" description="選擇共振頻帶（如 4-10 kHz）" />
            <el-step title="希爾伯特轉換" description="計算解析信號" />
            <el-step title="提取包絡" description="取振幅包絡" />
            <el-step title="FFT 分析" description="對包絡做頻譜分析" />
            <el-step title="特徵識別" description="尋找 BPF 及諧波" />
          </el-steps>

          <h4 style="margin-top: 20px;">共振頻帶選擇:</h4>
          <el-table :data="resonanceBands" border>
            <el-table-column prop="series" label="滑軌系列" />
            <el-table-column prop="band" label="共振頻帶 (Hz)" />
            <el-table-column prop="reason" label="說明" />
          </el-table>

          <el-alert
            title="診斷準則"
            type="warning"
            style="margin-top: 15px;"
            :closable="false"
          >
            <ul style="margin: 5px 0; padding-left: 20px;">
              <li>包絡譜出現 BPF → 滾動體或軌道缺陷</li>
              <li>SNR > 3 → 缺陷顯著</li>
              <li>多個諧波 → 缺陷嚴重</li>
            </ul>
          </el-alert>

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
                <el-form-item>
                  <el-button type="primary" @click="calculateEnvelope" :loading="envelopeLoading">
                    計算包絡頻譜
                  </el-button>
                </el-form-item>
              </el-form>
            </el-col>
            <el-col :span="12" v-if="envelopeResult">
              <el-card shadow="hover">
                <template #header>
                  <h4>包絡頻譜計算結果</h4>
                </template>
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="水平 Envelope RMS">
                    {{ envelopeResult.horizontal.envelope_rms.toFixed(4) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直 Envelope RMS">
                    {{ envelopeResult.vertical.envelope_rms.toFixed(4) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="水平峰值頻率">
                    {{ envelopeResult.horizontal.peak_frequencies.map(f => f.toFixed(2)).join(', ') }} Hz
                  </el-descriptions-item>
                    <el-descriptions-item label="垂直峰值頻率">
                    {{ envelopeResult.vertical.peak_frequencies.map(f => f.toFixed(2)).join(', ') }} Hz
                  </el-descriptions-item>
                </el-descriptions>
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

          <h4 style="margin-top: 20px;">應用場景:</h4>
          <el-tag type="danger" style="margin: 5px;">瞬態衝擊檢測</el-tag>
          <el-tag type="warning" style="margin: 5px;">異物進入檢測</el-tag>
          <el-tag type="info" style="margin: 5px;">早期微裂紋</el-tag>
        </el-collapse-item>

        <!-- Higher Order Statistics -->
        <el-collapse-item title="高階統計（Higher Order Statistics）" name="higher-order">
          <h3>原理說明</h3>
          <p>高階統計特徵對早期故障敏感，可檢測傳統方法難以發現的微小缺陷。</p>

          <h4>關鍵指標:</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="NA4">
              <p>正規化四次矩（帶分段）</p>
              <code>NA4 = N·Σ(x-μ)⁴ / [Σ(x-μ)²/M]²</code>
              <p>檢測諧波能量異常</p>
            </el-descriptions-item>
            <el-descriptions-item label="FM4">
              <p>四次矩比值</p>
              <code>FM4 = N·Σ(x-μ)⁴ / [Σ(x-μ)²]²</code>
              <p>檢測邊帶能量</p>
            </el-descriptions-item>
            <el-descriptions-item label="M6A / M8A">
              <p>六次矩 / 八次矩</p>
              <p>對極早期故障敏感</p>
            </el-descriptions-item>
            <el-descriptions-item label="ER">
              <p>能量比</p>
              <code>ER = RMS_sideband / RMS_total</code>
              <p>邊帶能量占比</p>
            </el-descriptions-item>
          </el-descriptions>

          <el-alert
            title="診斷準則"
            type="success"
            style="margin-top: 15px;"
            :closable="false"
          >
            <ul style="margin: 5px 0; padding-left: 20px;">
              <li>NA4 > 3 → 早期微裂紋</li>
              <li>FM4 異常 → 邊帶能量增加</li>
              <li>M6A / M8A 上升 → 潤滑不良或極早期故障</li>
            </ul>
          </el-alert>

          <!-- 高階統計計算區域 -->
          <el-divider>即時計算演示</el-divider>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form label-width="120px">
                <el-form-item label="選擇軸承">
                  <el-select v-model="higherOrderParams.bearingName" placeholder="請選擇軸承">
                    <el-option label="Bearing1_1" value="Bearing1_1" />
                    <el-option label="Bearing1_2" value="Bearing1_2" />
                    <el-option label="Bearing2_1" value="Bearing2_1" />
                    <el-option label="Bearing2_2" value="Bearing2_2" />
                    <el-option label="Bearing3_1" value="Bearing3_1" />
                  </el-select>
                </el-form-item>
                <el-form-item label="檔案編號">
                  <el-input-number v-model="higherOrderParams.fileNumber" :min="1" :max="100" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="calculateHigherOrder" :loading="higherOrderLoading">
                    計算高階統計
                  </el-button>
                </el-form-item>
              </el-form>
            </el-col>
            <el-col :span="12" v-if="higherOrderResult">
              <el-card shadow="hover">
                <template #header>
                  <h4>高階統計結果</h4>
                </template>
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item label="水平 NA4">
                    {{ higherOrderResult.horizontal.na4.toFixed(4) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直 NA4">
                    {{ higherOrderResult.vertical.na4.toFixed(4) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="水平 FM4">
                    {{ higherOrderResult.horizontal.fm4.toFixed(4) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直 FM4">
                    {{ higherOrderResult.vertical.fm4.toFixed(4) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="水平 M6A">
                    {{ higherOrderResult.horizontal.m6a.toFixed(6) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直 M6A">
                    {{ higherOrderResult.vertical.m6a.toFixed(6) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="水平 M8A">
                    {{ higherOrderResult.horizontal.m8a.toFixed(8) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直 M8A">
                    {{ higherOrderResult.vertical.m8a.toFixed(8) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="水平 ER">
                    {{ higherOrderResult.horizontal.er.toFixed(4) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="垂直 ER">
                    {{ higherOrderResult.vertical.er.toFixed(4) }}
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
          </el-row>

          <!-- 高階統計比較圖 -->
          <div v-if="higherOrderResult" style="margin-top: 20px;">
            <el-card>
              <template #header>
                <h4>高階統計特徵比較</h4>
              </template>
              <div ref="higherOrderChart" style="width: 100%; height: 400px;"></div>
            </el-card>
          </div>
        </el-collapse-item>

        <!-- Preload Assessment -->
        <el-collapse-item title="預壓狀態評估" name="preload">
          <h3>原理說明</h3>
          <p>基於時域特徵評估線性滑軌的預壓狀態，確保設計預壓與實際相符。</p>

          <h4>CPC 預壓等級:</h4>
          <el-table :data="preloadLevels" border>
            <el-table-column prop="level" label="預壓等級" />
            <el-table-column prop="value" label="預壓值" />
            <el-table-column prop="rms_threshold" label="RMS 閾值" />
            <el-table-column prop="kurt_threshold" label="峰度閾值" />
          </el-table>

          <h4 style="margin-top: 20px;">診斷邏輯:</h4>
          <el-steps direction="vertical" :active="3">
            <el-step title="RMS 過低" description="振動 < 閾值 × 0.7 → 預壓失效（鬆動）" status="error" />
            <el-step title="峰度過高" description="Kurtosis > 閾值 → 預壓不足（產生間隙衝擊）" status="warning" />
            <el-step title="正常狀態" description="兩項指標均在範圍內" status="success" />
          </el-steps>

          <h4 style="margin-top: 20px;">維護建議:</h4>
          <el-tag type="danger" style="margin: 5px;">檢查預壓設定</el-tag>
          <el-tag type="warning" style="margin: 5px;">檢查安裝精度</el-tag>
          <el-tag type="info" style="margin: 5px;">重新預壓</el-tag>
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
  highcut: 10000
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

// Chart refs
const timeDomainSignalChart = ref(null)
const timeDomainTrendChart = ref(null)
const stftChart = ref(null)
const cwtChartHoriz = ref(null)
const cwtEnergyChart = ref(null)
const higherOrderChart = ref(null)
const envelopeChart = ref(null)
const frequencyDomainChart = ref(null)

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

// 計算包絡頻譜
const calculateEnvelope = async () => {
  envelopeLoading.value = true
  try {
    const { bearingName, fileNumber, lowcut, highcut } = envelopeParams.value
    const response = await fetch(
      `http://localhost:8081/api/algorithms/envelope/${bearingName}/${fileNumber}?lowcut=${lowcut}&highcut=${highcut}`
    )
    if (!response.ok) throw new Error('計算失敗')

    envelopeResult.value = await response.json()

    await nextTick()
    drawEnvelopeChart()
  } catch (error) {
    console.error('計算包絡頻譜失敗:', error)
    alert('計算失敗: ' + error.message)
  } finally {
    envelopeLoading.value = false
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

// 繪製包絡頻譜圖
const drawEnvelopeChart = () => {
  if (!envelopeChart.value || !envelopeResult.value) return

  const chart = echarts.init(envelopeChart.value)

  const { frequency, horizontal_magnitude, vertical_magnitude } = envelopeResult.value.envelope_spectrum

  const option = {
    title: {
      text: '包絡頻譜'
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
      data: frequency.map(f => f.toFixed(1)),
      name: '頻率 (Hz)'
    },
    yAxis: {
      type: 'value',
      name: '幅值',
      min: 0,
      max: 0.05
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: '水平方向',
        type: 'line',
        data: horizontal_magnitude,
        showSymbol: false,
        lineStyle: { width: 1 }
      },
      {
        name: '垂直方向',
        type: 'line',
        data: vertical_magnitude,
        showSymbol: false,
        lineStyle: { width: 1 }
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

const faultFrequencies = [
  { type: '滾動體缺陷', frequency: 'BPF（Ball Pass Frequency）', description: '滾動體通過頻率及諧波' },
  { type: '滾動體自轉', frequency: 'BSF（Ball Spin Frequency）', description: '滾動體自身旋轉頻率' },
  { type: '保持鏈', frequency: 'Cage Frequency', description: '保持鏈旋轉頻率' }
]

const resonanceBands = [
  { series: '微型 (MR)', band: '8,000 - 15,000', reason: '尺寸小，共振頻率高' },
  { series: '小型 (15/20/25)', band: '4,000 - 10,000', reason: '標準共振範圍' },
  { series: '中型 (30/35/45)', band: '2,000 - 8,000', reason: '尺寸增大，頻率降低' },
  { series: '大型 (55/65)', band: '1,000 - 6,000', reason: '大尺寸，低頻共振' }
]

const preloadLevels = [
  { level: 'VC', value: '微間隙', rms_threshold: '0.05', kurt_threshold: '4.0' },
  { level: 'V0', value: '0.02C（標準）', rms_threshold: '0.08', kurt_threshold: '4.5' },
  { level: 'V1', value: '0.05C（中預壓）', rms_threshold: '0.12', kurt_threshold: '5.0' },
  { level: 'V2', value: '0.08C（高預壓）', rms_threshold: '0.15', kurt_threshold: '5.5' }
]

const algorithmMapping = [
  { module: '時域特徵', application: '整體健康監控', fault_type: '磨損程度、預壓狀態', cpc_params: 'C₀, C₁₀₀, 預壓等級' },
  { module: '頻域特徵', application: '故障頻率識別', fault_type: '滾動體缺陷、軌道剝落', cpc_params: '滑座型式、滾動體數量' },
  { module: '時頻分析 (STFT/CWT)', application: '瞬態衝擊檢測', fault_type: '異物、局部缺陷、非穩態信號', cpc_params: '密封片類型、環境條件' },
  { module: '高階統計', application: '早期故障檢測', fault_type: '微小缺陷、潤滑不良', cpc_params: '潤滑系統、摩擦阻力' },
  { module: '希爾伯特包絡', application: '滾動體故障', fault_type: '滾珠/滾子剝落', cpc_params: '基本動負荷 C₁₀₀' },
  { module: '諧波與邊帶', application: '安裝問題', fault_type: '平行度不良、預壓不均', cpc_params: '安裝精度、剛性' }
]
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
