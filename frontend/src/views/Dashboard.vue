<template>
  <div class="dashboard">

    <!-- IEEE PHM 2012 實驗摘要 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <!-- 原始：使用 card-header class 包含 span 和 el-tag -->
            <!-- 修改：簡化為 h2 標題，與 TimeDomainAnalysis.vue 保持一致 -->
            <h2>🔬 IEEE PHM 2012 數據挑戰實驗摘要</h2>
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

          <!-- CALCE 團隊預測方法 (基於 Edwin2012 論文) -->
          <el-row style="margin-top: 15px;">
            <el-col :span="24">
              <el-card shadow="never" class="summary-card">
                <template #header>
                  <div class="summary-header">
                    <el-icon><Document /></el-icon>
                    <span>CALCE 團隊 RUL 預測方法</span>
                    <el-tag type="success" size="small">學術組冠軍</el-tag>
                  </div>
                </template>
                <div class="summary-content">
                  <!-- 原始：color: #606266 -->
                  <!-- 修改：深色主題次要文字 -->
                  <p style="margin-bottom: 16px; font-style: italic; color: var(--text-secondary);">
                    馬里蘭大學 CALCE 中心提出三種基於數據驅動的軸承剩餘使用壽命（RUL）預測方法，
                    其中方法三（異常檢測與存活時間比）贏得了 2012 年 PHM 資料挑戰賽學術組冠軍。
                  </p>

                  <el-collapse accordion>
                    <!-- 方法一 -->
                    <el-collapse-item name="method1">
                      <template #title>
                        <div class="method-title">
                          <el-tag type="primary" size="small">方法一</el-tag>
                          <span>移動平均光譜峭度與貝葉斯蒙地卡羅</span>
                        </div>
                      </template>
                      <div class="method-content">
                        <h4>核心思想</h4>
                        <p>利用特定頻帶（5.5-6.0 kHz）的峭度（Kurtosis）作為監測軸承退化的最有效單調特徵。</p>

                        <h4>技術步驟</h4>
                        <ol>
                          <li><strong>特徵提取：</strong>對振動信號進行帶通濾波，計算光譜峭度並進行移動平均（MAS Kurtosis）</li>
                          <li><strong>退化建模：</strong>使用指數模型 y = a × exp(b×t²) 擬合退化趨勢</li>
                          <li><strong>參數更新：</strong>利用貝葉斯蒙地卡羅方法，隨著新資料加入不斷更新模型參數</li>
                          <li><strong>RUL 預測：</strong>預測峭度值何時超過故障閾值（4.0）</li>
                        </ol>

                        <h4>優勢與特點</h4>
                        <ul>
                          <li>✅ 能提供 RUL 的機率分佈，有助於風險管理</li>
                          <li>✅ 基於健康軸承峭度值應為 3.0 的物理理論</li>
                          <li>⚠️ 需要明確的故障閾值設定</li>
                        </ul>
                      </div>
                    </el-collapse-item>

                    <!-- 方法二 -->
                    <el-collapse-item name="method2">
                      <template #title>
                        <div class="method-title">
                          <el-tag type="warning" size="small">方法二</el-tag>
                          <span>帶有支持向量迴歸的軟計算模型</span>
                        </div>
                      </template>
                      <div class="method-content">
                        <h4>核心思想</h4>
                        <p>融合多種特徵並使用機器學習方法建立從特徵到 RUL 的映射關係。</p>

                        <h4>技術步驟</h4>
                        <ol>
                          <li><strong>多特徵提取：</strong>從水平和垂直振動信號各提取 17 個特徵（共 34 個）
                            <ul>
                              <li>高階過零點計數法：5 個特徵</li>
                              <li>小波變換：10 個特徵（前 5 層近似係數能量 + 前 5 層細節係數能量）</li>
                              <li>其他時域特徵：累積信號能量、振動信號峰值</li>
                            </ul>
                          </li>
                          <li><strong>特徵降維：</strong>使用主成分分析（PCA）將 34 個特徵降至 3 個主成分，保留超過 99.5% 的資料變異性</li>
                          <li><strong>機器學習：</strong>訓練最小二乘支持向量迴歸（LS-SVR）模型，學習從主成分到 RUL 的映射</li>
                        </ol>

                        <h4>優勢與特點</h4>
                        <ul>
                          <li>✅ 融合多種特徵，信息更全面</li>
                          <li>✅ 自動學習特徵與 RUL 的複雜關係</li>
                          <li>⚠️ 模式識別能力受限於訓練資料的多樣性</li>
                          <li>⚠️ 需要較多的標註訓練數據</li>
                        </ul>
                      </div>
                    </el-collapse-item>

                    <!-- 方法三 -->
                    <el-collapse-item name="method3">
                      <template #title>
                        <div class="method-title">
                          <el-tag type="success" size="small">方法三 ⭐</el-tag>
                          <span>振動頻譜特徵異常檢測與存活時間比</span>
                          <el-tag type="success" size="small" style="margin-left: 8px;">冠軍方法</el-tag>
                        </div>
                      </template>
                      <div class="method-content">
                        <h4>核心思想</h4>
                        <p>基於快速傅立葉變換（FFT）檢測頻譜異常，將軸承退化過程分為多個可識別的階段，
                          針對有無明顯退化趨勢採用不同的預測策略。</p>

                        <h4>技術步驟</h4>
                        <ol>
                          <li><strong>異常檢測：</strong>使用 FFT 觀察頻譜中峰值頻率的變化，標記退化階段的開始</li>
                          <li><strong>預後特徵：</strong>提取每次觀測中絕對加速度值最高的 5 個點的平均值</li>
                          <li><strong>分類預測策略：</strong>
                            <ul>
                              <li><strong>有明顯退化趨勢的軸承：</strong>使用指數曲線擬合來外插預測故障時間</li>
                              <li><strong>無明顯趨勢的軸承：</strong>計算訓練資料中各異常階段的持續時間比例，
                                根據測試資料第一個異常階段的持續時間推算剩餘壽命</li>
                            </ul>
                          </li>
                        </ol>

                        <h4>優勢與特點</h4>
                        <ul>
                          <li>🏆 在 11 個測試案例中有 4 個的誤差在 10% 以內</li>
                          <li>✅ 能同時處理有無明顯退化趨勢的兩種情況</li>
                          <li>✅ 基於物理意義（頻譜異常）的半經驗模型，魯棒性高</li>
                          <li>✅ 在訓練資料有限、故障模式未知的條件下依然有效</li>
                          <li>✅ 適合處理軸承壽命差異極大的挑戰</li>
                        </ul>

                        <el-divider />

                        <div class="winner-info">
                          <el-icon><Trophy /></el-icon>
                          <span>此方法幫助 CALCE 團隊贏得 2012 年 PHM 資料挑戰賽學術組冠軍</span>
                        </div>
                      </div>
                    </el-collapse-item>
                  </el-collapse>

                  <el-divider />

                  <!-- 特徵提取方法總結 -->
                  <div class="feature-summary">
                    <h4>📊 振動信號特徵提取方法總結</h4>
                    <el-row :gutter="15" style="margin-top: 12px;">
                      <el-col :span="8">
                        <div class="feature-card">
                          <h5>時域特徵</h5>
                          <ul>
                            <li>均方根 (RMS)</li>
                            <li>峰值 (Peak)</li>
                            <li>波峰因數 (Crest Factor)</li>
                            <li>峭度 (Kurtosis) ⭐</li>
                            <li>累積信號能量</li>
                          </ul>
                        </div>
                      </el-col>
                      <el-col :span="8">
                        <div class="feature-card">
                          <h5>頻域特徵</h5>
                          <ul>
                            <li>快速傅立葉變換 (FFT)</li>
                            <li>光譜峭度 (Spectral Kurtosis)</li>
                            <li>軸承缺陷頻率幅度</li>
                            <li>峰值頻率變化檢測</li>
                          </ul>
                        </div>
                      </el-col>
                      <el-col :span="8">
                        <div class="feature-card">
                          <h5>進階方法</h5>
                          <ul>
                            <li>小波變換 (Wavelet Transform)</li>
                            <li>高階過零點計數</li>
                            <li>主成分分析 (PCA)</li>
                            <li>移動平均平滑化</li>
                          </ul>
                        </div>
                      </el-col>
                    </el-row>
                  </div>

                  <el-divider />

                  <!-- 研究貢獻 -->
                  <div class="contribution-section">
                    <h4>🎯 主要研究貢獻</h4>
                    <ol>
                      <li><strong>開發新穎且有效的預測方法：</strong>特別是方法三，在訓練資料有限、故障模式未知且故障時間差異巨大的挑戰性條件下，
                        依然取得優異的預測精度</li>
                      <li><strong>比較不同預測策略：</strong>方法一能提供 RUL 的機率分佈有助於風險管理；
                        方法二的模式識別能力受限於訓練資料多樣性；方法三的半經驗模型最具魯棒性</li>
                      <li><strong>實踐性見解：</strong>在資料有限的情況下，基於物理意義的半經驗模型可能比純粹的機器學習模型更具魯棒性</li>
                    </ol>
                  </div>

                  <el-alert
                    title="📚 參考文獻"
                    type="info"
                    :closable="false"
                    style="margin-top: 16px;"
                  >
                    <p style="font-size: 12px; margin: 0;">
                      Edwin Sutrisno et al., "Estimation of Remaining Useful Life of Ball Bearings using Data Driven Methodologies",
                      IEEE PHM 2012 Data Challenge, CALCE Center, University of Maryland
                    </p>
                  </el-alert>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- PHM 訓練數據視覺化 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <!-- 原始：使用 card-header class 包含 span 和 el-tag -->
            <!-- 修改：簡化為 h2 標題，與 TimeDomainAnalysis.vue 保持一致 -->
            <h2>📊 PHM 2012 訓練數據視覺化</h2>
          </template>

          <!-- 載入狀態 -->
          <div v-if="trainingLoading" class="loading-container">
            <el-icon class="is-loading"><Loading /></el-icon>
            <p>載入訓練數據中...</p>
          </div>

          <!-- 數據摘要表格 -->
          <div v-if="!trainingLoading && trainingData">
            <el-table :data="trainingData.bearings" stripe style="width: 100%">
              <el-table-column prop="name" label="軸承編號" width="120" />
              <el-table-column label="操作條件" width="120">
                <template #default="scope">
                  <el-tag :type="getConditionType(scope.row.condition)">
                    Condition {{ scope.row.condition }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="load_N" label="負載 (N)" width="100" />
              <el-table-column prop="speed_rpm" label="轉速 (RPM)" width="120" />
              <el-table-column prop="actual_RUL_min" label="實際 RUL (分鐘)" width="150">
                <template #default="scope">
                  <strong>{{ scope.row.actual_RUL_min }}</strong>
                </template>
              </el-table-column>
              <el-table-column prop="num_files" label="數據文件數" width="120" />
              <el-table-column prop="total_duration_min" label="總時長 (分鐘)" width="130" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button
                    type="primary"
                    size="small"
                    @click="viewBearingDetails(scope.row)"
                  >
                    查看詳情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 統計圖表 -->
          <div v-if="!trainingLoading && statisticsData.length > 0" style="margin-top: 30px;">
            <el-card class="chart-card">
              <template #header>
                <!-- 原始：使用 card-header class 包含 span 和 el-select -->
                <!-- 修改：簡化為 h4 標題，el-select 移到內容區域 -->
                <h4>振動趨勢分析</h4>
              </template>

              <canvas ref="chartContainer" style="width: 100%; height: 400px"></canvas>
            </el-card>

            <!-- 峰度趨勢圖 -->
            <el-card class="chart-card" style="margin-top: 20px;">
              <template #header>
                <span>峰度趨勢分析（故障指標）</span>
              </template>

              <canvas ref="kurtosisChartContainer" style="width: 100%; height: 400px"></canvas>
            </el-card>

            <!-- 數據分析說明 -->
            <el-card class="info-card-phm" style="margin-top: 20px;">
              <template #header>
                <span>📖 數據說明</span>
              </template>

              <el-descriptions :column="2" border>
                <el-descriptions-item label="數據集">PHM IEEE 2012 Challenge - Learning Set</el-descriptions-item>
                <el-descriptions-item label="採樣率">25,600 Hz</el-descriptions-item>
                <el-descriptions-item label="操作條件">3 種不同負載-轉速組合</el-descriptions-item>
                <el-descriptions-item label="數據類型">水平 + 垂直振動</el-descriptions-item>
                <el-descriptions-item label="峰度正常值">≈ 3</el-descriptions-item>
                <el-descriptions-item label="峰度異常值">> 5-10 表示故障</el-descriptions-item>
              </el-descriptions>

              <el-divider />

              <h4>關鍵發現：</h4>
              <ul>
                <li>✅ <strong>峰度是最可靠的早期故障指標</strong>，在多數案例中提供 1000-3000 分鐘預警</li>
                <li>✅ <strong>垂直振動通常比水平振動更早顯示退化跡象</strong></li>
                <li>⚠️ Bearing3_1 (高負載 5000N) 具有最短壽命 (5730 分鐘) 和最突發的故障模式</li>
                <li>⭐ Bearing1_1 擁有最豐富數據 (2803 files) 和最長壽命 (28020 分鐘)</li>
              </ul>
            </el-card>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- PHM 資料庫查詢 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <!-- 原始：使用 card-header class 包含 span 和 el-tag -->
            <!-- 修改：簡化為 h2 標題，與 TimeDomainAnalysis.vue 保持一致 -->
            <h2>💾 PHM 資料庫查詢</h2>
          </template>

          <!-- Bearings List -->
          <div class="bearings-section">
            <h3 class="section-title">軸承列表</h3>
            <div v-if="loading" class="loading">載入中...</div>
            <div v-else-if="error" class="error">{{ error }}</div>
            <div v-else class="bearings-grid">
              <div
                v-for="bearing in bearings"
                :key="bearing.bearing_id"
                class="bearing-card"
                :class="{ active: selectedBearing === bearing.bearing_name }"
                @click="selectBearing(bearing.bearing_name)"
              >
                <h4>{{ bearing.bearing_name }}</h4>
                <div class="bearing-stats">
                  <div class="stat-item">
                    <span class="stat-label">檔案數:</span>
                    <span class="stat-value">{{ bearing.file_count?.toLocaleString() }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">測量記錄:</span>
                    <span class="stat-value">{{ bearing.measurement_count?.toLocaleString() }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Bearing Details -->
          <div v-if="selectedBearing" style="margin-top: 30px;">
            <h3 class="section-title">{{ selectedBearing }} 詳細資訊</h3>

            <!-- Tabs -->
            <el-tabs v-model="activeTab" @tab-change="handleTabChange">
              <el-tab-pane label="基本資訊" name="info">
                <div v-if="bearingInfo" class="info-grid">
                  <el-card shadow="never" class="info-card">
                    <template #header>
                      <div class="info-header">
                        <el-icon><DataBoard /></el-icon>
                        <span>統計摘要</span>
                      </div>
                    </template>
                    <div class="info-content">
                      <div class="info-item">
                        <span class="label">軸承 ID:</span>
                        <span class="value">{{ bearingInfo.bearing_id }}</span>
                      </div>
                      <div class="info-item">
                        <span class="label">檔案數量:</span>
                        <span class="value">{{ bearingInfo.file_count?.toLocaleString() }}</span>
                      </div>
                      <div class="info-item">
                        <span class="label">測量記錄:</span>
                        <span class="value">{{ bearingInfo.measurement_count?.toLocaleString() }}</span>
                      </div>
                    </div>
                  </el-card>

                  <el-card shadow="never" class="info-card">
                    <template #header>
                      <div class="info-header">
                        <el-icon><DataLine /></el-icon>
                        <span>水平加速度統計</span>
                      </div>
                    </template>
                    <div class="info-content">
                      <div class="info-item">
                        <span class="label">平均值:</span>
                        <span class="value">{{ bearingInfo.acceleration_stats?.avg_h_acc?.toFixed(3) }}</span>
                      </div>
                      <div class="info-item">
                        <span class="label">最小值:</span>
                        <span class="value">{{ bearingInfo.acceleration_stats?.min_h_acc?.toFixed(3) }}</span>
                      </div>
                      <div class="info-item">
                        <span class="label">最大值:</span>
                        <span class="value">{{ bearingInfo.acceleration_stats?.max_h_acc?.toFixed(3) }}</span>
                      </div>
                      <div class="info-item">
                        <span class="label">平均絕對值:</span>
                        <span class="value">{{ bearingInfo.acceleration_stats?.avg_abs_h_acc?.toFixed(3) }}</span>
                      </div>
                    </div>
                  </el-card>

                  <el-card shadow="never" class="info-card">
                    <template #header>
                      <div class="info-header">
                        <el-icon><DataLine /></el-icon>
                        <span>垂直加速度統計</span>
                      </div>
                    </template>
                    <div class="info-content">
                      <div class="info-item">
                        <span class="label">平均值:</span>
                        <span class="value">{{ bearingInfo.acceleration_stats?.avg_v_acc?.toFixed(3) }}</span>
                      </div>
                      <div class="info-item">
                        <span class="label">最小值:</span>
                        <span class="value">{{ bearingInfo.acceleration_stats?.min_v_acc?.toFixed(3) }}</span>
                      </div>
                      <div class="info-item">
                        <span class="label">最大值:</span>
                        <span class="value">{{ bearingInfo.acceleration_stats?.max_v_acc?.toFixed(3) }}</span>
                      </div>
                      <div class="info-item">
                        <span class="label">平均絕對值:</span>
                        <span class="value">{{ bearingInfo.acceleration_stats?.avg_abs_v_acc?.toFixed(3) }}</span>
                      </div>
                    </div>
                  </el-card>
                </div>
              </el-tab-pane>

              <el-tab-pane label="檔案列表" name="files">
                <div class="controls">
                  <el-button @click="loadFiles(0)" :loading="filesLoading" size="small">
                    重新載入
                  </el-button>
                  <span class="page-info">
                    顯示 {{ filesOffset + 1 }} - {{ Math.min(filesOffset + filesLimit, filesTotalCount) }}
                    / 共 {{ filesTotalCount }} 筆
                  </span>
                </div>

                <div v-if="filesLoading" class="loading">載入中...</div>
                <div v-else-if="files.length === 0" class="empty">無檔案資料</div>
                <el-table v-else :data="files" stripe style="width: 100%">
                  <el-table-column prop="file_number" label="檔案編號" width="100" />
                  <el-table-column prop="file_name" label="檔案名稱" width="180" />
                  <el-table-column prop="record_count" label="記錄數" width="120">
                    <template #default="scope">
                      {{ scope.row.record_count?.toLocaleString() }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="avg_h_acc" label="平均水平加速度" width="140">
                    <template #default="scope">
                      {{ scope.row.avg_h_acc?.toFixed(3) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="avg_v_acc" label="平均垂直加速度" width="140">
                    <template #default="scope">
                      {{ scope.row.avg_v_acc?.toFixed(3) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="max_abs_h_acc" label="最大絕對值(H)" width="130">
                    <template #default="scope">
                      {{ scope.row.max_abs_h_acc?.toFixed(3) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="max_abs_v_acc" label="最大絕對值(V)" width="130">
                    <template #default="scope">
                      {{ scope.row.max_abs_v_acc?.toFixed(3) }}
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="100">
                    <template #default="scope">
                      <el-button size="small" @click="loadFileData(scope.row.file_number)">
                        查看資料
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>

                <el-pagination
                  v-if="filesTotalCount > 0"
                  :current-page="Math.floor(filesOffset / filesLimit) + 1"
                  :page-size="filesLimit"
                  :total="filesTotalCount"
                  layout="prev, pager, next"
                  @current-change="handleFilesPageChange"
                  style="margin-top: 20px; justify-content: center;"
                />
              </el-tab-pane>

              <el-tab-pane label="測量資料" name="measurements">
                <div class="controls">
                  <el-input
                    v-model.number="fileNumberFilter"
                    placeholder="輸入檔案編號 (選填)"
                    style="width: 200px;"
                    size="small"
                  />
                  <el-button @click="loadMeasurements(0)" :loading="measurementsLoading" size="small">
                    查詢
                  </el-button>
                  <span class="page-info">
                    顯示 {{ measurementsOffset + 1 }} -
                    {{ Math.min(measurementsOffset + measurementsLimit, measurementsTotalCount) }}
                    / 共 {{ measurementsTotalCount?.toLocaleString() }} 筆
                  </span>
                </div>

                <div v-if="measurementsLoading" class="loading">載入中...</div>
                <div v-else-if="measurements.length === 0" class="empty">無測量資料</div>
                <el-table v-else :data="measurements" stripe style="width: 100%">
                  <el-table-column prop="file_number" label="檔案編號" width="100" />
                  <el-table-column label="時:分:秒.微秒" width="180">
                    <template #default="scope">
                      {{ scope.row.hour }}:{{ scope.row.minute }}:{{ scope.row.second }}.{{ scope.row.microsecond }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="horizontal_acceleration" label="水平加速度" width="150">
                    <template #default="scope">
                      {{ scope.row.horizontal_acceleration?.toFixed(3) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="vertical_acceleration" label="垂直加速度" width="150">
                    <template #default="scope">
                      {{ scope.row.vertical_acceleration?.toFixed(3) }}
                    </template>
                  </el-table-column>
                </el-table>

                <el-pagination
                  v-if="measurementsTotalCount > 0"
                  :current-page="Math.floor(measurementsOffset / measurementsLimit) + 1"
                  :page-size="measurementsLimit"
                  :total="measurementsTotalCount"
                  layout="prev, pager, next"
                  @current-change="handleMeasurementsPageChange"
                  style="margin-top: 20px; justify-content: center;"
                />
              </el-tab-pane>

              <el-tab-pane label="異常檢測" name="anomalies">
                <div class="controls">
                  <el-input-number
                    v-model="thresholdH"
                    :precision="1"
                    :step="0.5"
                    :min="0"
                    size="small"
                    style="width: 150px;"
                  >
                    <template #prefix>水平閾值:</template>
                  </el-input-number>
                  <el-input-number
                    v-model="thresholdV"
                    :precision="1"
                    :step="0.5"
                    :min="0"
                    size="small"
                    style="width: 150px;"
                  >
                    <template #prefix>垂直閾值:</template>
                  </el-input-number>
                  <el-button @click="searchAnomalies" :loading="anomaliesLoading" type="primary" size="small">
                    搜尋異常
                  </el-button>
                </div>

                <div v-if="anomaliesLoading" class="loading">載入中...</div>
                <div v-else-if="anomalies.length === 0" class="empty">
                  無異常資料 (閾值: H={{ thresholdH }}, V={{ thresholdV }})
                </div>
                <div v-else>
                  <el-alert
                    :title="`找到 ${anomalies.length} 筆異常資料`"
                    type="warning"
                    :closable="false"
                    style="margin-bottom: 15px;"
                  />
                  <el-table :data="anomalies" stripe style="width: 100%">
                    <el-table-column prop="file_number" label="檔案編號" width="100" />
                    <el-table-column prop="file_name" label="檔案名稱" width="150" />
                    <el-table-column label="時間" width="180">
                      <template #default="scope">
                        {{ scope.row.hour }}:{{ scope.row.minute }}:{{ scope.row.second }}.{{ scope.row.microsecond }}
                      </template>
                    </el-table-column>
                    <el-table-column label="水平加速度" width="150">
                      <template #default="scope">
                        <span :class="{ 'anomaly-value': Math.abs(scope.row.horizontal_acceleration) > thresholdH }">
                          {{ scope.row.horizontal_acceleration?.toFixed(3) }}
                        </span>
                      </template>
                    </el-table-column>
                    <el-table-column label="垂直加速度" width="150">
                      <template #default="scope">
                        <span :class="{ 'anomaly-value': Math.abs(scope.row.vertical_acceleration) > thresholdV }">
                          {{ scope.row.vertical_acceleration?.toFixed(3) }}
                        </span>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import { Aim, Tools, Folder, TrendCharts, DataBoard, DataLine, Loading, Document, Trophy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/stores/api'
import { Chart } from 'chart.js/auto'

// 使用環境變數配置 API_BASE URL，避免硬編碼
// 原始配置: const API_BASE = 'http://localhost:8000'
// 第一次修改: Backend 伺服器運行在 port 8000，更新 API_BASE 以匹配
// 修改: 統一 Backend 伺服器運行在 port 8081
// 第二次修改: 使用環境變數 VITE_API_BASE_URL 從 .env 檔案讀取 (getApiUrl 取代 'api' 字串)
// 第三次修改: 修正 API_BASE 定義，直接使用環境變數，避免重複的 /api 路徑
// 問題: getApiUrl('api') 會產生 http://localhost:8081/api，導致後續請求變成 /api/api/...
// 解決: 直接使用 baseURL，後續請求路徑包含 /api
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8081'

// State
const loading = ref(false)
const error = ref(null)
const bearings = ref([])
const selectedBearing = ref(null)
const bearingInfo = ref(null)
const activeTab = ref('info')

// Files
const files = ref([])
const filesLoading = ref(false)
const filesOffset = ref(0)
const filesLimit = ref(20)
const filesTotalCount = ref(0)

// Measurements
const measurements = ref([])
const measurementsLoading = ref(false)
const measurementsOffset = ref(0)
const measurementsLimit = ref(100)
const measurementsTotalCount = ref(0)
const fileNumberFilter = ref(null)

// Anomalies
const anomalies = ref([])
const anomaliesLoading = ref(false)
const thresholdH = ref(10.0)
const thresholdV = ref(10.0)

// PHM Training Data
const trainingLoading = ref(true)
const trainingData = ref(null)
const statisticsData = ref([])
const selectedTrainingBearing = ref('Bearing1_1')
const trainingBearingOptions = ref([])
const chartContainer = ref(null)
const kurtosisChartContainer = ref(null)
let vibrationChart = null
let kurtosisChart = null

// Load bearings list
const loadBearings = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get(`${API_BASE}/api/phm/database/bearings`)
    bearings.value = response.data.bearings
  } catch (err) {
    error.value = err.response?.data?.detail || err.message
    console.warn('Failed to load bearings:', err.response?.data?.detail || err.message)
  } finally {
    loading.value = false
  }
}

// Select bearing
const selectBearing = async (bearingName) => {
  selectedBearing.value = bearingName
  activeTab.value = 'info'
  await loadBearingInfo(bearingName)
}

// Load bearing info
const loadBearingInfo = async (bearingName) => {
  try {
    const response = await axios.get(
      `${API_BASE}/api/phm/database/bearing/${bearingName}`
    )
    bearingInfo.value = response.data
  } catch (err) {
    console.error('Error loading bearing info:', err)
  }
}

// Load files
const loadFiles = async (offset) => {
  if (!selectedBearing.value) return

  filesLoading.value = true
  filesOffset.value = offset
  try {
    const response = await axios.get(
      `${API_BASE}/api/phm/database/bearing/${selectedBearing.value}/files`,
      { params: { offset, limit: filesLimit.value } }
    )
    files.value = response.data.files
    filesTotalCount.value = response.data.total_count
  } catch (err) {
    console.error('Error loading files:', err)
  } finally {
    filesLoading.value = false
  }
}

// Load measurements
const loadMeasurements = async (offset) => {
  if (!selectedBearing.value) return

  measurementsLoading.value = true
  measurementsOffset.value = offset
  try {
    const params = { offset, limit: measurementsLimit.value }
    if (fileNumberFilter.value) {
      params.file_number = fileNumberFilter.value
    }

    const response = await axios.get(
      `${API_BASE}/api/phm/database/bearing/${selectedBearing.value}/measurements`,
      { params }
    )
    measurements.value = response.data.measurements
    measurementsTotalCount.value = response.data.total_count
  } catch (err) {
    console.error('Error loading measurements:', err)
  } finally {
    measurementsLoading.value = false
  }
}

// Load file data
const loadFileData = async (fileNumber) => {
  activeTab.value = 'measurements'
  fileNumberFilter.value = fileNumber
  await loadMeasurements(0)
}

// Search anomalies
const searchAnomalies = async () => {
  if (!selectedBearing.value) return

  anomaliesLoading.value = true
  try {
    const response = await axios.get(
      `${API_BASE}/api/phm/database/bearing/${selectedBearing.value}/anomalies`,
      {
        params: {
          threshold_h: thresholdH.value,
          threshold_v: thresholdV.value,
          limit: 100
        }
      }
    )
    anomalies.value = response.data.anomalies
  } catch (err) {
    console.error('Error searching anomalies:', err)
  } finally {
    anomaliesLoading.value = false
  }
}

// Tab change handler
const handleTabChange = (tabName) => {
  if (tabName === 'files' && files.value.length === 0) {
    loadFiles(0)
  } else if (tabName === 'measurements' && measurements.value.length === 0) {
    loadMeasurements(0)
  }
}

// Pagination handlers
const handleFilesPageChange = (page) => {
  loadFiles((page - 1) * filesLimit.value)
}

const handleMeasurementsPageChange = (page) => {
  loadMeasurements((page - 1) * measurementsLimit.value)
}

// PHM Training Functions
const getConditionType = (condition) => {
  const types = { 1: 'primary', 2: 'warning', 3: 'success' }
  return types[condition] || 'info'
}

const loadTrainingData = async () => {
  try {
    trainingLoading.value = true

    // 載入分析數據（包含完整的 summary 和 statistics）
    // 原始代碼: 使用 getPHMTrainingSummary() 和 getPHMAnalysisData() 兩個 API
    // 修改原因: getPHMTrainingSummary() 返回的數據缺少 num_files 和 total_duration_min 字段
    // 解決方案: 改用 getPHMAnalysisData() 返回的 summary.bearings，該數據包含所有必要字段
    const analysisData = await api.getPHMAnalysisData()

    // 使用 summary.bearings 作為訓練數據（包含 num_files 和 total_duration_min）
    trainingData.value = {
      total_bearings: analysisData.summary.total_bearings,
      bearings: analysisData.summary.bearings
    }

    // 使用 statistics 用於圖表渲染
    statisticsData.value = analysisData.statistics
    trainingBearingOptions.value = [...new Set(analysisData.statistics.map(s => s.bearing_name))]

    console.log('Training summary loaded:', trainingData.value)
    console.log('Statistics data loaded:', analysisData.statistics.length, 'records')
    console.log('Bearing options:', trainingBearingOptions.value)

    trainingLoading.value = false

    // 等待 DOM 更新後再渲染圖表
    await nextTick()
    renderCharts()
  } catch (error) {
    console.error('Failed to load training data:', error)
    ElMessage.error('載入訓練數據失敗: ' + (error.response?.data?.detail || error.message))
    trainingLoading.value = false
  }
}

const renderCharts = () => {
  // 只在容器和數據都準備好時才渲染
  if (chartContainer.value && kurtosisChartContainer.value && statisticsData.value.length > 0) {
    renderVibrationChart()
    renderKurtosisChart()
  } else {
    console.log('Charts not rendered - containers or data not ready')
  }
}

const renderVibrationChart = () => {
  // 檢查容器是否存在
  if (!chartContainer.value) {
    console.warn('Chart container not found - DOM may not be ready yet')
    return
  }

  // 檢查是否有統計數據
  if (!statisticsData.value || statisticsData.value.length === 0) {
    console.warn('No statistics data available yet')
    return
  }

  const bearingData = statisticsData.value.filter(
    d => d.bearing_name === selectedTrainingBearing.value
  )

  console.log('Rendering vibration chart for:', selectedTrainingBearing.value)
  console.log('Bearing data points:', bearingData.length)

  if (bearingData.length === 0) {
    console.warn('No data for bearing:', selectedTrainingBearing.value)
    return
  }

  if (vibrationChart) {
    vibrationChart.destroy()
  }

  const ctx = chartContainer.value.getContext('2d')
  vibrationChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: bearingData.map(d => d.time_min),
      datasets: [
        {
          label: '水平振動 RMS',
          data: bearingData.map(d => d.horiz_rms),
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          tension: 0.1,
          pointRadius: 1,
          borderWidth: 2
        },
        {
          label: '垂直振動 RMS',
          data: bearingData.map(d => d.vert_rms),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.1)',
          tension: 0.1,
          pointRadius: 1,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: `${selectedTrainingBearing.value} - 振動 RMS 趨勢`,
          // 原始：繼承預設顏色
          // 修改：深色主題白色文字
          color: '#ffffff',
          font: {
            // 原始: 16
            // 第一次修改: 18 - 增大圖表標題
            // 第二次修改: 20 - 進一步增大圖表標題
            size: 20,
            weight: '600'
          }
        },
        legend: {
          position: 'top',
          // 原始：繼承預設顏色
          // 修改：深色主題白色文字
          labels: {
            color: '#ffffff',
            font: {
              // 原始: 12
              // 第一次修改: 14 - 增大圖例文字
              // 第二次修改: 15 - 進一步增大圖例文字
              size: 15
            }
          }
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: '時間 (分鐘)',
            // 原始：繼承預設顏色
            // 修改：深色主題白色文字
            color: '#ffffff',
            font: {
              // 原始: 14
              // 修改: 15 - 增大軸標題
              size: 15,
              weight: '500'
            }
          },
          ticks: {
            // 原始：繼承預設顏色
            // 修改：深色主題白色文字
            color: '#ffffff',
            font: {
              // 原始: 11
              // 第一次修改: 12 - 增大軸刻度文字
              // 第二次修改: 14 - 進一步增大軸刻度文字
              size: 14
            }
          },
          grid: {
            // 原始：繼承預設顏色
            // 修改：深色主題淺色網格
            color: 'rgba(255, 255, 255, 0.1)'
          }
        },
        y: {
          title: {
            display: true,
            text: 'RMS 值',
            // 原始：繼承預設顏色
            // 修改：深色主題白色文字
            color: '#ffffff',
            font: {
              // 原始: 14
              // 第一次修改: 15 - 增大軸標題
              // 第二次修改: 15 - 保持軸標題大小
              size: 15,
              weight: '500'
            }
          },
          ticks: {
            // 原始：繼承預設顏色
            // 修改：深色主題白色文字
            color: '#ffffff',
            font: {
              // 原始: 11
              // 第一次修改: 12 - 增大軸刻度文字
              // 第二次修改: 14 - 進一步增大軸刻度文字
              size: 14
            }
          },
          grid: {
            // 原始：繼承預設顏色
            // 修改：深色主題淺色網格
            color: 'rgba(255, 255, 255, 0.1)'
          },
          beginAtZero: false
        }
      }
    }
  })
  console.log('Vibration chart rendered successfully')
}

const renderKurtosisChart = () => {
  // 檢查容器是否存在
  if (!kurtosisChartContainer.value) {
    console.warn('Kurtosis chart container not found - DOM may not be ready yet')
    return
  }

  // 檢查是否有統計數據
  if (!statisticsData.value || statisticsData.value.length === 0) {
    console.warn('No statistics data available yet')
    return
  }

  const bearingData = statisticsData.value.filter(
    d => d.bearing_name === selectedTrainingBearing.value
  )

  console.log('Rendering kurtosis chart for:', selectedTrainingBearing.value)
  console.log('Bearing data points:', bearingData.length)

  if (bearingData.length === 0) {
    console.warn('No data for bearing:', selectedTrainingBearing.value)
    return
  }

  if (kurtosisChart) {
    kurtosisChart.destroy()
  }

  const ctx = kurtosisChartContainer.value.getContext('2d')
  kurtosisChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: bearingData.map(d => d.time_min),
      datasets: [
        {
          label: '水平振動峰度',
          data: bearingData.map(d => d.horiz_kurtosis),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          tension: 0.1,
          pointRadius: 1,
          borderWidth: 2
        },
        {
          label: '垂直振動峰度',
          data: bearingData.map(d => d.vert_kurtosis),
          borderColor: 'rgb(153, 102, 255)',
          backgroundColor: 'rgba(153, 102, 255, 0.1)',
          tension: 0.1,
          pointRadius: 1,
          borderWidth: 2
        },
        {
          label: '正常閾值 (≈3)',
          data: Array(bearingData.length).fill(3),
          borderColor: 'rgb(255, 206, 86)',
          borderDash: [5, 5],
          borderWidth: 2,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: `${selectedTrainingBearing.value} - 峰度趨勢（故障指標）`,
          // 原始：繼承預設顏色
          // 修改：深色主題白色文字
          color: '#ffffff',
          font: {
            // 原始: 16
            // 第一次修改: 18 - 增大圖表標題
            // 第二次修改: 20 - 進一步增大圖表標題
            size: 20,
            weight: '600'
          }
        },
        legend: {
          position: 'top',
          // 原始：繼承預設顏色
          // 修改：深色主題白色文字
          labels: {
            color: '#ffffff',
            font: {
              // 原始: 12
              // 第一次修改: 14 - 增大圖例文字
              // 第二次修改: 15 - 進一步增大圖例文字
              size: 15
            }
          }
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: '時間 (分鐘)',
            // 原始：繼承預設顏色
            // 修改：深色主題白色文字
            color: '#ffffff',
            font: {
              // 原始: 14
              // 修改: 15 - 增大軸標題
              size: 15,
              weight: '500'
            }
          },
          ticks: {
            // 原始：繼承預設顏色
            // 修改：深色主題白色文字
            color: '#ffffff',
            font: {
              // 原始: 11
              // 第一次修改: 12 - 增大軸刻度文字
              // 第二次修改: 14 - 進一步增大軸刻度文字
              size: 14
            }
          },
          grid: {
            // 原始：繼承預設顏色
            // 修改：深色主題淺色網格
            color: 'rgba(255, 255, 255, 0.1)'
          }
        },
        y: {
          title: {
            display: true,
            text: '峰度值',
            // 原始：繼承預設顏色
            // 修改：深色主題白色文字
            color: '#ffffff',
            font: {
              // 原始: 14
              // 第一次修改: 15 - 增大軸標題
              // 第二次修改: 15 - 保持軸標題大小
              size: 15,
              weight: '500'
            }
          },
          ticks: {
            // 原始：繼承預設顏色
            // 修改：深色主題白色文字
            color: '#ffffff',
            font: {
              // 原始: 11
              // 第一次修改: 12 - 增大軸刻度文字
              // 第二次修改: 14 - 進一步增大軸刻度文字
              size: 14
            }
          },
          grid: {
            // 原始：繼承預設顏色
            // 修改：深色主題淺色網格
            color: 'rgba(255, 255, 255, 0.1)'
          },
          beginAtZero: false
        }
      }
    }
  })
  console.log('Kurtosis chart rendered successfully')
}

const viewBearingDetails = async (bearing) => {
  selectedTrainingBearing.value = bearing.name

  // 等待 DOM 更新後再渲染圖表
  await nextTick()

  renderVibrationChart()
  renderKurtosisChart()

  // 滾動到圖表區域
  await nextTick()
  const chartCard = document.querySelector('.chart-card')
  if (chartCard) {
    chartCard.scrollIntoView({ behavior: 'smooth' })
  }
}

watch(selectedTrainingBearing, async () => {
  // 等待 DOM 更新後再渲染圖表
  await nextTick()
  renderVibrationChart()
  renderKurtosisChart()
})

// Initialize
onMounted(() => {
  loadBearings()
  loadTrainingData()
})
</script>

<style scoped>
/* ===== 原始：淺色主題 ===== */
/* ===== 修改為：Apple Keynote 深色漸層主題 ===== */

/* ===== 字體設定 - 與 FONT.md 規範對齊 ===== */
/* 全局字體族設定（繼承自 style.css） */
/* font-family: system-ui, Avenir, Helvetica, Arial, sans-serif; */

/* ===== 標題層級字體大小設定（與 FONT.md 一致）===== */
/* 原始設定: h1=3.2em, h2=1.5em, h3=1.25em, h4=1.1em, h5=1em */
/* 修改: 增大標題字體,提供更舒適的閱讀體驗 */
.dashboard h1 {
  font-size: 3.2em;
  line-height: 1.1;
  font-weight: bold;
  color: var(--text-primary);
}

.dashboard h2 {
  /* 原始: 1.5em (≈24px) */
  /* 第一次修改: 1.75em (≈28px) - 增大主要區塊標題 */
  /* 第二次修改: 1.85em (≈29.6px) - 進一步增大標題以提升可讀性 */
  font-size: 1.85em;
  line-height: 1.3;
  font-weight: bold;
  color: var(--text-primary);
}

.dashboard h3 {
  /* 原始: 1.25em (≈20px) */
  /* 第一次修改: 1.4em (≈22.4px) - 增大小區塊標題 */
  /* 第二次修改: 1.5em (≈24px) - 進一步增大小區塊標題 */
  font-size: 1.5em;
  line-height: 1.4;
  font-weight: bold;
  color: var(--text-primary);
}

.dashboard h4 {
  /* 原始: 1.1em (≈17.6px) */
  /* 第一次修改: 1.2em (≈19.2px) - 增大小標題 */
  /* 第二次修改: 1.25em (≈20px) - 進一步增大小標題 */
  font-size: 1.25em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--accent-primary);
}

.dashboard h5 {
  /* 原始: 1em (16px) */
  /* 修改: 1.1em (≈17.6px) - 增大次級標題 */
  font-size: 1.1em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--text-primary);
}

/* ===== 段落與文字內容字體（與 FONT.md 一致）===== */
/* 原始設定: 16px */
/* 第一次修改: 17px - 略微增大內容文字,提升可讀性 */
/* 第二次修改: 18px - 進一步增大內容文字以提升閱讀舒適度 */
.dashboard p {
  font-size: 18px;
  line-height: 1.6;
  color: var(--text-secondary);
}

/* ===== 連結字體（與 FONT.md 一致）===== */
.dashboard a {
  font-weight: 500;
  color: var(--accent-primary);
}

.dashboard a:hover {
  color: var(--accent-hover);
}

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
  /* 原始：font-size: 28px */
  /* 修改：與 FONT.md h2 規範對齊 (1.5em ≈ 24px) */
  font-size: 1.5em;
  font-weight: bold;
  margin: 0 0 5px;
  /* 原始：#303133 */
  /* 修改：深色主題主要文字 */
  color: var(--text-primary);
}

.stat-info p {
  /* 原始: 14px -> 16px */
  /* 修改: 17px - 略微增大統計資訊文字 */
  font-size: 17px;
  /* 原始：#909399 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
  margin: 0;
}

/* 原始：.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-primary);
} */

/* ===== IEEE PHM 2012 實驗摘要樣式 - 深色主題 ===== */
.summary-card {
  height: 100%;
  /* 原始：#f0f0f0 */
  /* 修改：深色邊框 */
  border: 1px solid var(--border-color);
  border-radius: 8px;
  /* 原始：繼承白色背景 */
  /* 修改：深色卡片背景 */
  background: var(--bg-card);
}

.summary-card :deep(.el-card__header) {
  /* 原始：#fafafa */
  /* 修改：深色次要背景 */
  background-color: var(--bg-secondary);
  /* 原始：#f0f0f0 */
  /* 修改：深色邊框 */
  border-bottom: 1px solid var(--border-color);
  padding: 12px 16px;
}

.summary-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  /* 原始：#303133 */
  /* 修改：深色主題主要文字 */
  color: var(--text-primary);
}

.summary-content {
  padding: 16px;
  /* 原始: 13px -> 16px */
  /* 第一次修改: 17px - 略微增大卡片內容文字 */
  /* 第二次修改: 18px - 進一步增大卡片內容文字 */
  font-size: 18px;
  line-height: 1.5;
}

.summary-content p {
  margin-bottom: 8px;
  /* 原始：#606266 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
}

.summary-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.summary-content li {
  margin-bottom: 4px;
  /* 原始：#606266 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
}

.summary-content strong {
  /* 原始：#303133 */
  /* 修改：深色主題主要文字 */
  color: var(--text-primary);
}

.challenge-item {
  text-align: center;
  padding: 12px 8px;
  border-radius: 6px;
  /* 原始：#fafafa */
  /* 修改：深色次要背景 */
  background-color: var(--bg-secondary);
  height: 100%;
}

.challenge-item p {
  margin-top: 8px;
  /* 原始: 12px */
  /* 第一次修改: 15px - 增大挑戰項目描述文字 */
  /* 第二次修改: 17px - 進一步增大描述文字 */
  font-size: 17px;
  /* 原始：#606266 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
  line-height: 1.4;
}

.scoring-info {
  /* 原始：#f8f9fa */
  /* 修改：深色次要背景 */
  background-color: var(--bg-secondary);
  padding: 12px;
  border-radius: 6px;
  /* 原始: 12px */
  /* 第一次修改: 15px - 增大評分資訊文字 */
  /* 第二次修改: 17px - 進一步增大評分資訊文字 */
  font-size: 17px;
  /* 原始：#606266 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
  line-height: 1.5;
}

/* ===== PHM Database Query Styles - 深色主題 ===== */
.section-title {
  /* 原始：font-size: 16px */
  /* 修改：與 FONT.md h3 規範對齊 (1.25em ≈ 20px) */
  font-size: 1.25em;
  font-weight: 600;
  /* 原始：#34495e */
  /* 修改：深色主題主要文字 */
  color: var(--text-primary);
  margin-bottom: 15px;
  /* 原始：#409eff */
  /* 修改：使用強調色（保持一致） */
  border-bottom: 2px solid var(--accent-primary);
  padding-bottom: 8px;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 30px;
  /* 原始：#909399 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
  /* 原始: 14px */
  /* 第一次修改: 16px - 增大狀態訊息文字 */
  /* 第二次修改: 17px - 進一步增大狀態訊息文字 */
  font-size: 17px;
}

.error {
  color: var(--accent-danger);
}

.bearings-section {
  margin-bottom: 20px;
}

.bearings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.bearing-card {
  /* 原始：#e4e7ed */
  /* 修改：深色邊框 */
  border: 2px solid var(--border-color);
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
  /* 原始：#fff */
  /* 修改：深色卡片背景 */
  background: var(--bg-card);
  color: var(--text-primary);
}

.bearing-card:hover {
  /* 原始：#409eff */
  /* 修改：使用強調色 */
  border-color: var(--accent-primary);
  transform: translateY(-2px);
  /* 原始：rgba(64, 158, 255, 0.2) */
  /* 修改：深色發光陰影 */
  box-shadow: 0 4px 12px var(--shadow-glow);
}

.bearing-card.active {
  /* 原始：#67c23a */
  /* 修改：使用成功色 */
  border-color: var(--accent-success);
  /* 原始：#f0f9ff */
  /* 修改：深色次要背景 */
  background: var(--bg-secondary);
}

.bearing-card h4 {
  /* 原始：font-size: 15px */
  /* 修改：與 FONT.md h4 規範對齊 (1.1em ≈ 17.6px) */
  font-size: 1.1em;
  font-weight: 600;
  /* 原始：#303133 */
  /* 修改：深色主題主要文字 */
  color: var(--text-primary);
  margin-bottom: 12px;
}

.bearing-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  /* 原始: 13px -> 16px */
  /* 第一次修改: 17px - 略微增大統計項目文字 */
  /* 第二次修改: 18px - 進一步增大統計項目文字 */
  font-size: 18px;
}

.stat-label {
  /* 原始：#909399 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
}

.stat-value {
  font-weight: 600;
  /* 原始：#409eff */
  /* 修改：使用強調色 */
  color: var(--accent-primary);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 15px;
}

.info-card {
  /* 原始：#e4e7ed */
  /* 修改：深色邊框 */
  border: 1px solid var(--border-color);
  border-radius: 8px;
  /* 原始：繼承白色背景 */
  /* 修改：深色卡片背景 */
  background: var(--bg-card);
}

.info-card :deep(.el-card__header) {
  /* 原始：#fafafa */
  /* 修改：深色次要背景 */
  background-color: var(--bg-secondary);
  /* 原始：#e4e7ed */
  /* 修改：深色邊框 */
  border-bottom: 1px solid var(--border-color);
  padding: 12px 16px;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  /* 原始：#409eff */
  /* 修改：使用強調色 */
  color: var(--accent-primary);
}

.info-content {
  padding: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  /* 原始：#f5f7fa */
  /* 修改：深色淺邊框 */
  border-bottom: 1px solid var(--border-color-light);
  /* 原始: 13px -> 16px */
  /* 第一次修改: 17px - 略微增大資訊項目文字 */
  /* 第二次修改: 18px - 進一步增大資訊項目文字 */
  font-size: 18px;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  /* 原始：#909399 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
}

.info-item .value {
  font-weight: 600;
  /* 原始：#303133 */
  /* 修改：深色主題主要文字 */
  color: var(--text-primary);
}

.controls {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.page-info {
  /* 原始: 13px -> 16px */
  /* 修改: 16px - 維持頁面資訊文字大小 */
  font-size: 16px;
  /* 原始：#909399 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
  margin-left: auto;
}

.anomaly-value {
  color: var(--accent-danger);
  font-weight: 600;
}

/* ===== PHM Training Styles - 深色主題 ===== */
.loading-container {
  text-align: center;
  padding: 60px;
}

.loading-container .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.info-card-phm h4 {
  margin: 16px 0 8px 0;
  /* 原始：#409EFF */
  /* 修改：使用強調色 */
  color: var(--accent-info);
}

.info-card-phm ul {
  margin: 8px 0;
  padding-left: 24px;
}

.info-card-phm li {
  margin: 8px 0;
  line-height: 1.6;
  /* 原始：繼承預設 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
}

/* ===== CALCE 方法樣式 - 深色主題 ===== */
.method-title {
  display: flex;
  align-items: center;
  gap: 12px;
  /* 原始：font-size: 14px */
  /* 修改：與 FONT.md h4 規範對齊 (1.1em ≈ 17.6px) */
  font-size: 1.1em;
  font-weight: 600;
}

.method-content {
  padding: 16px 20px;
  /* 原始：#fafafa */
  /* 修改：深色次要背景 */
  background-color: var(--bg-secondary);
  border-radius: 6px;
  margin-top: 8px;
}

.method-content h4 {
  /* 原始：font-size: 14px */
  /* 修改：與 FONT.md h4 規範對齊 (1.1em ≈ 17.6px) */
  font-size: 1.1em;
  margin: 16px 0 8px 0;
  font-weight: 600;
  /* 原始：#409EFF */
  /* 修改：使用強調色 */
  color: var(--accent-info);
}

.method-content h4:first-child {
  margin-top: 0;
}

.method-content p {
  /* 原始：#606266 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 8px 0;
}

.method-content ol,
.method-content ul {
  margin: 8px 0;
  padding-left: 24px;
  /* 原始：#606266 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
}

.method-content li {
  margin: 6px 0;
  /* 原始: 繼承 */
  /* 第一次修改: 16px - 增大列表項目文字 */
  /* 第二次修改: 17px - 進一步增大列表項目文字 */
  font-size: 17px;
  line-height: 1.6;
}

.method-content ul ul {
  margin-top: 6px;
  padding-left: 20px;
}

.winner-info {
  display: flex;
  align-items: center;
  gap: 10px;
  /* 原始：#f0f9ff */
  /* 修改：深色卡片背景 */
  background-color: var(--bg-card);
  padding: 12px 16px;
  border-radius: 6px;
  border-left: 4px solid var(--accent-success);
  color: var(--accent-success);
  font-weight: 600;
}

.feature-summary {
  /* 原始：#f8f9fa */
  /* 修改：深色次要背景 */
  background-color: var(--bg-secondary);
  padding: 16px;
  border-radius: 8px;
}

.feature-summary h4 {
  /* 原始：font-size: 15px */
  /* 修改：與 FONT.md h4 規範對齊 (1.1em ≈ 17.6px) */
  font-size: 1.1em;
  font-weight: 600;
  /* 原始：#303133 */
  /* 修改：深色主題主要文字 */
  color: var(--text-primary);
  margin-bottom: 12px;
}

.feature-card {
  /* 原始：white */
  /* 修改：深色卡片背景 */
  background-color: var(--bg-card);
  padding: 12px 16px;
  border-radius: 6px;
  /* 原始：#e4e7ed */
  /* 修改：深色邊框 */
  border: 1px solid var(--border-color);
  height: 100%;
}

.feature-card h5 {
  /* 原始：font-size: 13px */
  /* 修改：與 FONT.md h5 規範對齊 (1em = 16px) */
  font-size: 1em;
  font-weight: 600;
  margin: 0 0 10px 0;
  padding-bottom: 8px;
  /* 原始：#409EFF */
  /* 修改：使用強調色 */
  color: var(--accent-info);
  /* 原始：#409EFF */
  /* 修改：使用強調色 */
  border-bottom: 2px solid var(--accent-info);
}

.feature-card ul {
  margin: 0;
  padding-left: 20px;
}

.feature-card li {
  /* 原始: 12px -> 16px */
  /* 第一次修改: 17px - 略微增大特徵卡片列表文字 */
  /* 第二次修改: 18px - 進一步增大特徵卡片列表文字 */
  font-size: 18px;
  line-height: 1.8;
  margin: 4px 0;
  /* 原始：#606266 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
}

.contribution-section h4 {
  /* 原始：font-size: 15px */
  /* 修改：與 FONT.md h4 規範對齊 (1.1em ≈ 17.6px) */
  font-size: 1.1em;
  font-weight: 600;
  /* 原始：#303133 */
  /* 修改：深色主題主要文字 */
  color: var(--text-primary);
  margin-bottom: 12px;
}

.contribution-section ol {
  margin: 0;
  padding-left: 24px;
}

.contribution-section li {
  /* 原始：#606266 */
  /* 修改：深色主題次要文字 */
  color: var(--text-secondary);
  line-height: 1.8;
  margin: 10px 0;
  /* 原始: 繼承 */
  /* 第一次修改: 16px - 增大貢獻區塊列表文字 */
  /* 第二次修改: 17px - 進一步增大列表文字 */
  font-size: 17px;
}

/* ===== 表格樣式修正 ===== */
/* 針對 el-table 表格組件的深色主題樣式優化 */
.dashboard :deep(.el-table) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題表格樣式 */
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.dashboard :deep(.el-table__header-wrapper) {
  /* 表頭背景 */
  background-color: var(--bg-secondary);
}

.dashboard :deep(.el-table th) {
  /* 表頭單元格樣式 */
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  font-weight: 600;
  border-color: var(--border-color) !important;
}

.dashboard :deep(.el-table td) {
  /* 表格內容單元格樣式 */
  background-color: var(--bg-primary) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-color) !important;
}

.dashboard :deep(.el-table__row:hover td) {
  /* 表格行懸停效果 */
  background-color: var(--bg-secondary) !important;
}

.dashboard :deep(.el-table__row.current-row td) {
  /* 當前行樣式 */
  background-color: var(--bg-tertiary) !important;
}

.dashboard :deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  /* 斑馬紋行樣式 */
  background-color: var(--bg-secondary) !important;
}

.dashboard :deep(.el-table--striped .el-table__body tr.el-table__row--striped:hover td) {
  /* 斑馬紋行懸停效果 */
  background-color: var(--bg-tertiary) !important;
}

.dashboard :deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  /* 啟用行懸停效果 */
  background-color: var(--bg-secondary) !important;
}

/* ===== el-descriptions 表格樣式 ===== */
.dashboard :deep(.el-descriptions) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題描述列表樣式 */
  background-color: transparent;
}

.dashboard :deep(.el-descriptions__label) {
  /* 描述列表標籤列樣式 */
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  font-weight: 500;
  padding: 12px 16px !important;
}

.dashboard :deep(.el-descriptions__content) {
  /* 描述列表內容列樣式 */
  color: var(--text-primary) !important;
  padding: 12px 16px !important;
}

.dashboard :deep(.el-descriptions__cell) {
  /* 描述列表單元格邊框 */
  border-color: var(--border-color) !important;
}

.dashboard :deep(.el-descriptions--bordered .el-descriptions__cell) {
  /* 邊框描述列表的單元格樣式 */
  border: 1px solid var(--border-color);
}

/* 數字值的特殊樣式 */
.dashboard :deep(.el-descriptions__content strong) {
  font-family: 'Consolas', 'Monaco', monospace;
  font-weight: 600;
  color: var(--accent-primary) !important;
}

/* ===== el-alert 樣式 ===== */
.dashboard :deep(.el-alert) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題提示框樣式 */
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}

.dashboard :deep(.el-alert__content) {
  /* 提示框內容區域 */
  background: transparent;
}

.dashboard :deep(.el-alert__title) {
  /* 提示框標題 */
  color: var(--text-primary);
}

.dashboard :deep(.el-alert__description) {
  /* 提示框描述 */
  color: var(--text-secondary);
}

.dashboard :deep(.el-alert--info) {
  /* Info 類型提示框 */
  background: var(--bg-secondary);
  border-color: var(--accent-info);
}

.dashboard :deep(.el-alert--info .el-alert__title) {
  color: var(--accent-info);
}

/* ===== el-tag 樣式 ===== */
.dashboard :deep(.el-tag) {
  /* 標籤樣式 */
  color: var(--text-primary);
  border-color: var(--border-color);
}

.dashboard :deep(.el-tag--info) {
  /* Info 類型標籤 */
  background-color: var(--bg-secondary);
  border-color: var(--accent-info);
  color: var(--accent-info);
}

.dashboard :deep(.el-tag--success) {
  /* Success 類型標籤 */
  background-color: var(--bg-secondary);
  border-color: var(--accent-success);
  color: var(--accent-success);
}

.dashboard :deep(.el-tag--warning) {
  /* Warning 類型標籤 */
  background-color: var(--bg-secondary);
  border-color: var(--accent-warning);
  color: var(--accent-warning);
}

.dashboard :deep(.el-tag--danger) {
  /* Danger 類型標籤 */
  background-color: var(--bg-secondary);
  border-color: var(--accent-danger);
  color: var(--accent-danger);
}

.dashboard :deep(.el-tag--primary) {
  /* Primary 類型標籤 */
  background-color: var(--bg-secondary);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* ===== el-collapse 摺疊面板樣式 ===== */
.dashboard :deep(.el-collapse) {
  /* 摺疊面板整體樣式 */
  background-color: transparent;
  border-color: var(--border-color);
}

.dashboard :deep(.el-collapse-item__header) {
  /* 摺疊面板標題 */
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--border-color);
}

.dashboard :deep(.el-collapse-item__wrap) {
  /* 摺疊面板內容包裝 */
  background-color: transparent;
  border-color: var(--border-color);
}

.dashboard :deep(.el-collapse-item__content) {
  /* 摺疊面板內容 */
  background-color: transparent;
  color: var(--text-secondary);
}

.dashboard :deep(.el-collapse-item__header:hover) {
  /* 摺疊面板標題懸停 */
  background-color: var(--bg-tertiary);
}

/* ===== el-divider 分隔線樣式 ===== */
.dashboard :deep(.el-divider) {
  /* 分隔線整體樣式 */
  border-top-color: var(--border-color);
}

.dashboard :deep(.el-divider__text) {
  /* 分隔線文字樣式 */
  background-color: var(--bg-card);
  color: var(--accent-primary);
  font-weight: 600;
}

.dashboard :deep(.el-divider--horizontal) {
  /* 水平分隔線 */
  display: flex;
  align-items: center;
}

/* ===== h3, h4, p, code 等基礎元素樣式 ===== */
/* 注意：h1, h2, h3, h4, h5, p 已在文件開頭定義，與 FONT.md 規範對齊 */
/* 以下僅定義特殊變體樣式 */

/* dashboard h4 特殊變體：帶背景的卡片式標題 */
.dashboard h4.card-title {
  margin-top: 20px;
  /* 確保標題在深色背景下可讀 */
  background: var(--bg-secondary);
  padding: 10px 15px;
  border-radius: 6px;
  border-left: 4px solid var(--accent-primary);
}

.dashboard code {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題代碼背景 */
  background: var(--bg-tertiary);
  padding: 2px 8px;
  border-radius: 6px;
  /* 原始：#667eea */
  /* 修改：使用強調色 */
  color: var(--accent-primary);
  /* 原始：繼承預設 */
  /* 修改：深色邊框 */
  border: 1px solid var(--border-color);
  font-family: 'Consolas', 'Monaco', monospace;
}

/* ===== el-card 卡片樣式 ===== */
.dashboard :deep(.el-card) {
  /* 卡片整體樣式 */
  background-color: var(--bg-card);
  border-color: var(--border-color);
}

.dashboard :deep(.el-card__header) {
  /* 卡片標題區域 */
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.dashboard :deep(.el-card__body) {
  /* 卡片內容區域 */
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

/* ===== el-pagination 分頁器樣式 ===== */
.dashboard :deep(.el-pagination) {
  /* 分頁器整體樣式 */
  color: var(--text-primary);
}

.dashboard :deep(.el-pagination button) {
  /* 分頁器按鈕 */
  background-color: var(--bg-secondary);
  color: var(--text-primary);
}

.dashboard :deep(.el-pagination button:hover) {
  /* 分頁器按鈕懸停 */
  color: var(--accent-primary);
}

.dashboard :deep(.el-pagination .el-pager li) {
  /* 分頁器頁碼 */
  background-color: var(--bg-secondary);
  color: var(--text-primary);
}

.dashboard :deep(.el-pagination .el-pager li:hover) {
  /* 分頁器頁碼懸停 */
  color: var(--accent-primary);
}

.dashboard :deep(.el-pagination .el-pager li.active) {
  /* 當前頁碼 */
  color: var(--accent-primary);
  background-color: var(--bg-tertiary);
}

/* ===== el-tabs 標籤頁樣式 ===== */
.dashboard :deep(.el-tabs) {
  /* 標籤頁整體樣式 */
  color: var(--text-primary);
}

.dashboard :deep(.el-tabs__nav) {
  /* 標籤導航條 */
  border-color: var(--border-color);
}

.dashboard :deep(.el-tabs__item) {
  /* 標籤項 */
  color: var(--text-secondary);
}

.dashboard :deep(.el-tabs__item:hover) {
  /* 標籤項懸停 */
  color: var(--accent-primary);
}

.dashboard :deep(.el-tabs__item.is-active) {
  /* 激活的標籤項 */
  color: var(--accent-primary);
}

.dashboard :deep(.el-tabs__active-bar) {
  /* 激活指示條 */
  background-color: var(--accent-primary);
}

.dashboard :deep(.el-tabs__content) {
  /* 標籤內容區域 */
  color: var(--text-primary);
}

/* ===== el-select 下拉選擇框樣式 ===== */
.dashboard :deep(.el-select) {
  /* 確保下拉框繼承正確的顏色 */
  color: var(--text-primary);
}

.dashboard :deep(.el-select .el-input__wrapper) {
  /* 下拉選擇框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.dashboard :deep(.el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.dashboard :deep(.el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.dashboard :deep(.el-select .el-input__inner) {
  /* 下拉選擇框文字 */
  color: var(--text-primary);
}

.dashboard :deep(.el-select__placeholder) {
  /* 下拉選擇框佔位符 */
  color: var(--text-secondary);
}

.dashboard :deep(.el-select__caret) {
  /* 下拉選擇框箭頭圖標 */
  color: var(--text-secondary);
}

/* ===== 下拉選單選項樣式 ===== */
.dashboard :deep(.el-select-dropdown) {
  /* 下拉選單背景 */
  background-color: var(--bg-card);
  border-color: var(--border-color);
}

.dashboard :deep(.el-select-dropdown__item) {
  /* 下拉選單選項 */
  color: var(--text-primary);
  background-color: transparent;
}

.dashboard :deep(.el-select-dropdown__item:hover) {
  /* 下拉選單選項懸停 */
  background-color: var(--bg-secondary);
  color: var(--accent-primary);
}

.dashboard :deep(.el-select-dropdown__item.is-selected) {
  /* 下拉選單選項已選中 */
  background-color: var(--bg-tertiary);
  color: var(--accent-primary);
  font-weight: 500;
}

/* ===== el-input 輸入框樣式 ===== */
.dashboard :deep(.el-input__wrapper) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.dashboard :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.dashboard :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.dashboard :deep(.el-input__inner) {
  /* 輸入框內部樣式 */
  background-color: transparent;
  color: var(--text-primary);
}

/* ===== el-input-number 數字輸入框樣式 ===== */
.dashboard :deep(.el-input-number) {
  /* 數字輸入框整體 */
  color: var(--text-primary);
}

.dashboard :deep(.el-input-number .el-input__wrapper) {
  /* 數字輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.dashboard :deep(.el-input-number .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.dashboard :deep(.el-input-number .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.dashboard :deep(.el-input-number__decrease),
.dashboard :deep(.el-input-number__increase) {
  /* 數字輸入框 +/- 按鈕 */
  background-color: var(--bg-secondary);
  border: none;
  color: var(--text-primary);
}

.dashboard :deep(.el-input-number__decrease:hover),
.dashboard :deep(.el-input-number__increase:hover) {
  /* 按鈕懸停效果 */
  color: var(--accent-primary);
  background-color: var(--bg-tertiary);
}

.dashboard :deep(.el-input-number__decrease.is-disabled),
.dashboard :deep(.el-input-number__increase.is-disabled) {
  /* 禁用狀態按鈕 */
  color: var(--text-disabled);
  background-color: var(--bg-secondary);
}

/* ===== el-button 按鈕樣式 ===== */
.dashboard :deep(.el-button) {
  /* 按鈕整體樣式 */
  color: var(--text-primary);
  border-color: var(--border-color);
}

.dashboard :deep(.el-button--primary) {
  /* 主要按鈕 */
  background-color: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #ffffff;
}

.dashboard :deep(.el-button--primary:hover) {
  /* 主要按鈕懸停 */
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.dashboard :deep(.el-button--default) {
  /* 預設按鈕 */
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.dashboard :deep(.el-button--default:hover) {
  /* 預設按鈕懸停 */
  background-color: var(--bg-tertiary);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.dashboard :deep(.el-button--small) {
  /* 小按鈕 */
  padding: 5px 12px;
  /* 原始: 12px -> 16px */
  /* 修改: 15px - 略微增大小按鈕文字,避免過大影響版面 */
  font-size: 15px;
}
</style>
