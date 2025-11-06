<template>
  <div class="dashboard">

    <!-- IEEE PHM 2012 實驗摘要 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>🔬 IEEE PHM 2012 數據挑戰實驗摘要</span>
              <el-tag type="info">Remaining Useful Life 預測</el-tag>
            </div>
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
                  <p style="margin-bottom: 16px; font-style: italic; color: #606266;">
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
            <div class="card-header">
              <span>📊 PHM 2012 訓練數據視覺化</span>
              <el-tag type="info">共 {{ trainingData?.total_bearings || 0 }} 個軸承</el-tag>
            </div>
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
                <div class="card-header">
                  <span>振動趨勢分析</span>
                  <el-select
                    v-model="selectedTrainingBearing"
                    placeholder="選擇軸承"
                    style="width: 200px"
                  >
                    <el-option
                      v-for="bearing in trainingBearingOptions"
                      :key="bearing"
                      :label="bearing"
                      :value="bearing"
                    />
                  </el-select>
                </div>
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
            <div class="card-header">
              <span>💾 PHM 資料庫查詢</span>
              <el-tag type="success">查詢 PHM IEEE 2012 訓練資料集</el-tag>
            </div>
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

const API_BASE = 'http://localhost:8081'

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

    // 載入摘要數據
    const summaryData = await api.getPHMTrainingSummary()
    trainingData.value = summaryData
    console.log('Training summary loaded:', summaryData)

    // 載入統計數據
    const analysisData = await api.getPHMAnalysisData()
    const stats = analysisData.statistics

    statisticsData.value = stats
    trainingBearingOptions.value = [...new Set(stats.map(s => s.bearing_name))]
    console.log('Statistics data loaded:', stats.length, 'records')
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
  renderVibrationChart()
  renderKurtosisChart()
}

const renderVibrationChart = () => {
  if (!chartContainer.value) {
    console.error('Chart container not found')
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
          text: `${selectedTrainingBearing.value} - 振動 RMS 趨勢`
        },
        legend: {
          position: 'top'
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: '時間 (分鐘)'
          }
        },
        y: {
          title: {
            display: true,
            text: 'RMS 值'
          },
          beginAtZero: false
        }
      }
    }
  })
  console.log('Vibration chart rendered successfully')
}

const renderKurtosisChart = () => {
  if (!kurtosisChartContainer.value) {
    console.error('Kurtosis chart container not found')
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
          text: `${selectedTrainingBearing.value} - 峰度趨勢（故障指標）`
        },
        legend: {
          position: 'top'
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: '時間 (分鐘)'
          }
        },
        y: {
          title: {
            display: true,
            text: '峰度值'
          },
          beginAtZero: false
        }
      }
    }
  })
  console.log('Kurtosis chart rendered successfully')
}

const viewBearingDetails = (bearing) => {
  selectedTrainingBearing.value = bearing.name
  renderVibrationChart()
  renderKurtosisChart()

  // 滾動到圖表區域
  const chartCard = document.querySelector('.chart-card')
  if (chartCard) {
    chartCard.scrollIntoView({ behavior: 'smooth' })
  }
}

watch(selectedTrainingBearing, () => {
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
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 5px;
  color: #303133;
}

.stat-info p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* IEEE PHM 2012 實驗摘要樣式 */
.summary-card {
  height: 100%;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
}

.summary-card :deep(.el-card__header) {
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  padding: 12px 16px;
}

.summary-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.summary-content {
  padding: 16px;
  font-size: 13px;
  line-height: 1.5;
}

.summary-content p {
  margin-bottom: 8px;
  color: #606266;
}

.summary-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.summary-content li {
  margin-bottom: 4px;
  color: #606266;
}

.summary-content strong {
  color: #303133;
}

.challenge-item {
  text-align: center;
  padding: 12px 8px;
  border-radius: 6px;
  background-color: #fafafa;
  height: 100%;
}

.challenge-item p {
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
}

.scoring-info {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}

/* PHM Database Query Styles */
.section-title {
  color: #34495e;
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 2px solid #409eff;
  padding-bottom: 8px;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 30px;
  color: #909399;
  font-size: 14px;
}

.error {
  color: #f56c6c;
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
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
}

.bearing-card:hover {
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.bearing-card.active {
  border-color: #67c23a;
  background: #f0f9ff;
}

.bearing-card h4 {
  color: #303133;
  margin-bottom: 12px;
  font-size: 15px;
}

.bearing-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.stat-label {
  color: #909399;
}

.stat-value {
  font-weight: 600;
  color: #409eff;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 15px;
}

.info-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.info-card :deep(.el-card__header) {
  background-color: #fafafa;
  border-bottom: 1px solid #e4e7ed;
  padding: 12px 16px;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #409eff;
}

.info-content {
  padding: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f5f7fa;
  font-size: 13px;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #909399;
}

.info-item .value {
  font-weight: 600;
  color: #303133;
}

.controls {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.page-info {
  color: #909399;
  font-size: 13px;
  margin-left: auto;
}

.anomaly-value {
  color: #f56c6c;
  font-weight: 600;
}

/* PHM Training Styles */
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
  color: #409EFF;
}

.info-card-phm ul {
  margin: 8px 0;
  padding-left: 24px;
}

.info-card-phm li {
  margin: 8px 0;
  line-height: 1.6;
}

/* CALCE 方法樣式 */
.method-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 600;
}

.method-content {
  padding: 16px 20px;
  background-color: #fafafa;
  border-radius: 6px;
  margin-top: 8px;
}

.method-content h4 {
  color: #409EFF;
  font-size: 14px;
  margin: 16px 0 8px 0;
  font-weight: 600;
}

.method-content h4:first-child {
  margin-top: 0;
}

.method-content p {
  color: #606266;
  line-height: 1.6;
  margin: 8px 0;
}

.method-content ol,
.method-content ul {
  margin: 8px 0;
  padding-left: 24px;
  color: #606266;
}

.method-content li {
  margin: 6px 0;
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
  background-color: #f0f9ff;
  padding: 12px 16px;
  border-radius: 6px;
  border-left: 4px solid #67c23a;
  color: #67c23a;
  font-weight: 600;
}

.feature-summary {
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.feature-summary h4 {
  color: #303133;
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 600;
}

.feature-card {
  background-color: white;
  padding: 12px 16px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  height: 100%;
}

.feature-card h5 {
  color: #409EFF;
  font-size: 13px;
  font-weight: 600;
  margin: 0 0 10px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #409EFF;
}

.feature-card ul {
  margin: 0;
  padding-left: 20px;
}

.feature-card li {
  color: #606266;
  font-size: 12px;
  line-height: 1.8;
  margin: 4px 0;
}

.contribution-section h4 {
  color: #303133;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
}

.contribution-section ol {
  margin: 0;
  padding-left: 24px;
}

.contribution-section li {
  color: #606266;
  line-height: 1.8;
  margin: 10px 0;
}
</style>
