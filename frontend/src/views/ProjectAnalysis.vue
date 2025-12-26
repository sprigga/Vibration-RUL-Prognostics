<template>
  <div class="project-analysis">
    <!-- 頁面標題 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <h2>📊 專案分析報告 <el-tag type="success" style="margin-left: 10px;">基於 EDWIN2012 論文對照</el-tag></h2>
          </template>
          <el-alert
            title="分析說明"
            type="info"
            :closable="false"
            show-icon
          >
            <p>本報告基於 EDWIN2012.md 論文內容，對專案 codebase 進行全面分析，比對已實現與待補強的功能。</p>
          </el-alert>
        </el-card>
      </el-col>
    </el-row>

    <!-- 整體實現狀態概覽 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card class="stats-card">
          <el-statistic title="整體完成度" :value="73" suffix="%">
            <template #prefix>
              <el-icon><TrendCharts /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <el-statistic title="已實現功能" :value="9" suffix="個視圖">
            <template #prefix>
              <el-icon style="color: #67c23a;"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <el-statistic title="待補強功能" :value="5" suffix="個模組">
            <template #prefix>
              <el-icon style="color: #e6a23c;"><Warning /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <el-statistic title="後端 API" :value="8" suffix="個模組">
            <template #prefix>
              <el-icon style="color: #409eff;"><Connection /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 論文方法實現對照 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <h2>🎯 論文三種方法實現對照</h2>
          </template>

          <el-tabs type="border-card">
            <!-- 方法一 -->
            <el-tab-pane>
              <template #label>
                <span><el-icon><Document /></el-icon> 方法一</span>
              </template>
              <div class="method-analysis">
                <h3>
                  <el-tag type="primary">方法一</el-tag>
                  移動平均光譜峭度與貝葉斯蒙地卡羅
                </h3>
                <el-divider />

                <el-row :gutter="20">
                  <el-col :span="12">
                    <h4>✅ 已實現功能</h4>
                    <el-timeline>
                      <el-timeline-item color="#67c23a" timestamp="Dashboard.vue">
                        光譜峭度（Spectral Kurtosis）計算
                      </el-timeline-item>
                      <el-timeline-item color="#67c23a" timestamp="Frontend">
                        移動平均處理實現
                      </el-timeline-item>
                      <el-timeline-item color="#67c23a" timestamp="Dashboard.vue">
                        故障閾值檢測（峭度閾值參考）
                      </el-timeline-item>
                    </el-timeline>
                  </el-col>

                  <el-col :span="12">
                    <h4>❌ 待補強功能</h4>
                    <el-timeline>
                      <el-timeline-item color="#f56c6c" timestamp="高優先級">
                        貝葉斯蒙地卡羅參數更新方法
                      </el-timeline-item>
                      <el-timeline-item color="#f56c6c" timestamp="高優先級">
                        指數模型 y = a × exp(b×t²) 擬合
                      </el-timeline-item>
                      <el-timeline-item color="#e6a23c" timestamp="中優先級">
                        RUL 機率分佈生成與視覺化
                      </el-timeline-item>
                    </el-timeline>
                  </el-col>
                </el-row>

                <el-alert
                  title="實現狀態"
                  type="warning"
                  :closable="false"
                  show-icon
                  style="margin-top: 15px;"
                >
                  <p><strong>部分實現（約 55%）</strong> - 特徵提取完成，但缺少核心預測演算法</p>
                </el-alert>
              </div>
            </el-tab-pane>

            <!-- 方法二 -->
            <el-tab-pane>
              <template #label>
                <span><el-icon><DataAnalysis /></el-icon> 方法二</span>
              </template>
              <div class="method-analysis">
                <h3>
                  <el-tag type="warning">方法二</el-tag>
                  支持向量迴歸與 PCA 降維
                </h3>
                <el-divider />

                <el-row :gutter="20">
                  <el-col :span="12">
                    <h4>✅ 已實現功能</h4>
                    <el-timeline>
                      <el-timeline-item color="#67c23a" timestamp="timefrequency.py">
                        小波變換（CWT）部分實現
                      </el-timeline-item>
                      <el-timeline-item color="#67c23a" timestamp="timedomain.py">
                        時域特徵（累積信號能量、峰值）
                      </el-timeline-item>
                    </el-timeline>
                  </el-col>

                  <el-col :span="12">
                    <h4>❌ 待補強功能</h4>
                    <el-timeline>
                      <el-timeline-item color="#f56c6c" timestamp="關鍵缺失">
                        高階過零點計數法（5 個特徵）
                      </el-timeline-item>
                      <el-timeline-item color="#f56c6c" timestamp="關鍵缺失">
                        PCA 降維模組（34 → 3 主成分）
                      </el-timeline-item>
                      <el-timeline-item color="#f56c6c" timestamp="關鍵缺失">
                        LS-SVR 機器學習預測模型
                      </el-timeline-item>
                      <el-timeline-item color="#e6a23c" timestamp="需改進">
                        小波變換能量特徵提取（前 5 層）
                      </el-timeline-item>
                    </el-timeline>
                  </el-col>
                </el-row>

                <el-alert
                  title="實現狀態"
                  type="error"
                  :closable="false"
                  show-icon
                  style="margin-top: 15px;"
                >
                  <p><strong>低度實現（約 20%）</strong> - 僅有基礎特徵，缺少完整的 34 特徵流程與機器學習模組</p>
                </el-alert>
              </div>
            </el-tab-pane>

            <!-- 方法三 -->
            <el-tab-pane>
              <template #label>
                <span><el-icon><Trophy /></el-icon> 方法三（冠軍）</span>
              </template>
              <div class="method-analysis">
                <h3>
                  <el-tag type="success">方法三 🏆</el-tag>
                  振動頻譜特徵異常檢測與存活時間比
                </h3>
                <el-divider />

                <el-row :gutter="20">
                  <el-col :span="12">
                    <h4>✅ 已實現功能</h4>
                    <el-timeline>
                      <el-timeline-item color="#67c23a" timestamp="frequencydomain.py">
                        FFT 頻譜分析完整實現
                      </el-timeline-item>
                      <el-timeline-item color="#67c23a" timestamp="EnvelopeAnalysis.vue">
                        頻譜異常檢測功能
                      </el-timeline-item>
                      <el-timeline-item color="#67c23a" timestamp="可手動計算">
                        預後特徵提取（前 5 個最大加速度值平均）
                      </el-timeline-item>
                      <el-timeline-item color="#67c23a" timestamp="Frontend">
                        指數曲線擬合實現
                      </el-timeline-item>
                    </el-timeline>
                  </el-col>

                  <el-col :span="12">
                    <h4>⚠️ 待補強功能</h4>
                    <el-timeline>
                      <el-timeline-item color="#e6a23c" timestamp="中優先級">
                        自動化異常階段劃分
                      </el-timeline-item>
                      <el-timeline-item color="#e6a23c" timestamp="中優先級">
                        存活時間比自動計算與預測
                      </el-timeline-item>
                      <el-timeline-item color="#e6a23c" timestamp="低優先級">
                        退化趨勢自動分類策略
                      </el-timeline-item>
                    </el-timeline>
                  </el-col>
                </el-row>

                <el-alert
                  title="實現狀態"
                  type="success"
                  :closable="false"
                  show-icon
                  style="margin-top: 15px;"
                >
                  <p><strong>高度實現（約 85%）</strong> - 核心功能完善，僅需自動化預測流程</p>
                </el-alert>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- 特徵提取方法對照表 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <h2>🔍 特徵提取方法實現對照</h2>
          </template>

          <el-table :data="featureData" stripe border style="width: 100%">
            <el-table-column prop="category" label="特徵類別" width="150" />
            <el-table-column prop="feature" label="論文要求" width="250" />
            <el-table-column prop="status" label="實現狀態" width="120" align="center">
              <template #default="scope">
                <el-tag
                  :type="scope.row.statusType"
                  size="small"
                >
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="location" label="實現位置" />
            <el-table-column prop="notes" label="備註" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 已實現功能總結 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <h2>✅ 高度完善的功能模組</h2>
          </template>

          <el-row :gutter="15">
            <el-col :span="8" v-for="(module, index) in completedModules" :key="index">
              <el-card shadow="hover" class="module-card">
                <div class="module-header">
                  <el-icon :color="module.color" :size="24">
                    <component :is="module.icon" />
                  </el-icon>
                  <h4>{{ module.name }}</h4>
                </div>
                <el-progress
                  :percentage="module.progress"
                  :status="module.progressStatus"
                  :stroke-width="8"
                />
                <ul class="module-features">
                  <li v-for="(feature, idx) in module.features" :key="idx">
                    {{ feature }}
                  </li>
                </ul>
                <div class="module-files">
                  <el-tag
                    v-for="(file, idx) in module.files"
                    :key="idx"
                    size="small"
                    style="margin: 2px;"
                  >
                    {{ file }}
                  </el-tag>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 優先改進建議 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <h2>🚀 優先改進建議</h2>
          </template>

          <el-collapse accordion>
            <el-collapse-item name="priority1">
              <template #title>
                <div class="priority-title">
                  <el-tag type="danger" size="large">🔥 高優先級</el-tag>
                  <span>實現方法三的自動化 RUL 預測流程</span>
                </div>
              </template>
              <div class="priority-content">
                <p><strong>重要性：</strong>方法三是冠軍方法，已有 85% 基礎，投資報酬率最高</p>
                <h4>具體任務：</h4>
                <ol>
                  <li>實現自動化異常階段劃分演算法</li>
                  <li>開發存活時間比自動計算模組</li>
                  <li>建立完整的 RUL 預測 API 端點</li>
                  <li>創建預測結果視覺化介面</li>
                </ol>
                <el-alert type="info" :closable="false" style="margin-top: 10px;">
                  <strong>預期效益：</strong>能夠完整重現論文冠軍方法，提供端到端的 RUL 預測服務
                </el-alert>
              </div>
            </el-collapse-item>

            <el-collapse-item name="priority2">
              <template #title>
                <div class="priority-title">
                  <el-tag type="warning" size="large">⚡ 中優先級</el-tag>
                  <span>補齊方法二的機器學習預測模組</span>
                </div>
              </template>
              <div class="priority-content">
                <p><strong>重要性：</strong>擴展專案的 ML 能力，提供多樣化的預測策略</p>
                <h4>具體任務：</h4>
                <ol>
                  <li>實現高階過零點計數法（5 個特徵）</li>
                  <li>開發 PCA 降維模組（支持 34 → 3 主成分）</li>
                  <li>整合 scikit-learn 的 SVR 或實現 LS-SVR</li>
                  <li>建立完整的特徵提取流程（水平 + 垂直振動）</li>
                  <li>創建訓練與預測 API</li>
                </ol>
                <el-alert type="warning" :closable="false" style="margin-top: 10px;">
                  <strong>預期效益：</strong>提供基於機器學習的 RUL 預測，適用於有充足訓練資料的場景
                </el-alert>
              </div>
            </el-collapse-item>

            <el-collapse-item name="priority3">
              <template #title>
                <div class="priority-title">
                  <el-tag type="info" size="large">📊 中優先級</el-tag>
                  <span>完善方法一的貝葉斯預測功能</span>
                </div>
              </template>
              <div class="priority-content">
                <p><strong>重要性：</strong>提供 RUL 機率分佈，增強風險管理能力</p>
                <h4>具體任務：</h4>
                <ol>
                  <li>實現貝葉斯蒙地卡羅參數更新演算法</li>
                  <li>開發指數模型擬合模組（y = a × exp(b×t²)）</li>
                  <li>建立 RUL 機率分佈計算與視覺化</li>
                  <li>創建序列更新預測 API</li>
                </ol>
                <el-alert type="success" :closable="false" style="margin-top: 10px;">
                  <strong>預期效益：</strong>提供不確定性量化的 RUL 預測，支持基於風險的維護決策
                </el-alert>
              </div>
            </el-collapse-item>

            <el-collapse-item name="priority4">
              <template #title>
                <div class="priority-title">
                  <el-tag size="large">🔧 低優先級</el-tag>
                  <span>增強特徵提取與資料處理</span>
                </div>
              </template>
              <div class="priority-content">
                <p><strong>重要性：</strong>提升特徵品質，支持更多研究應用</p>
                <h4>具體任務：</h4>
                <ol>
                  <li>改進小波變換能量特徵提取（前 5 層近似 + 細節係數）</li>
                  <li>增加累積信號能量時間序列功能</li>
                  <li>實現更多頻域特徵（譜密度、功率譜等）</li>
                  <li>優化特徵平滑化與標準化處理</li>
                </ol>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-col>
    </el-row>

    <!-- 總結與建議 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <h2>📝 總結與建議</h2>
          </template>

          <el-row :gutter="20">
            <el-col :span="12">
              <h3>🎯 專案優勢</h3>
              <ul class="summary-list">
                <li>✅ 專案架構清晰，前後端分離良好</li>
                <li>✅ 時域、頻域、時頻分析功能完整</li>
                <li>✅ 包絡分析與故障診斷非常專業</li>
                <li>✅ PHM 資料庫系統完善</li>
                <li>✅ Dashboard 提供完整的論文方法說明</li>
                <li>✅ 信號處理和特徵提取實現完善（約 73%）</li>
              </ul>
            </el-col>

            <el-col :span="12">
              <h3>🔍 關鍵缺失</h3>
              <ul class="summary-list gap">
                <li>❌ 方法一缺少貝葉斯蒙地卡羅實現</li>
                <li>❌ 方法二幾乎未實現（高階過零點、PCA、LS-SVR）</li>
                <li>⚠️ 方法三缺少自動化預測流程</li>
                <li>❌ 缺少端到端的 RUL 預測演示</li>
                <li>❌ 缺少預測結果的信賴區間</li>
              </ul>
            </el-col>
          </el-row>

          <el-divider />

          <el-alert
            title="開發建議"
            type="success"
            :closable="false"
            show-icon
          >
            <p>建議優先完成<strong>方法三的自動化流程</strong>（冠軍方法，已有 85% 基礎），
            這將使專案具備完整的 RUL 預測能力。接著可以考慮實現<strong>方法二的機器學習模組</strong>，
            擴展專案的預測策略多樣性。方法一的貝葉斯方法則可以作為進階功能，提供不確定性量化能力。</p>
          </el-alert>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  TrendCharts,
  CircleCheck,
  Warning,
  Connection,
  Document,
  DataAnalysis,
  Trophy
} from '@element-plus/icons-vue'

// 特徵提取對照表數據
const featureData = ref([
  {
    category: '時域特徵',
    feature: 'RMS',
    status: '✅ 已實現',
    statusType: 'success',
    location: 'timedomain.py, TimeDomainAnalysis.vue',
    notes: '完整實現'
  },
  {
    category: '時域特徵',
    feature: 'Peak（峰值）',
    status: '✅ 已實現',
    statusType: 'success',
    location: 'timedomain.py',
    notes: '完整實現'
  },
  {
    category: '時域特徵',
    feature: 'Kurtosis（峰度）⭐',
    status: '✅ 已實現',
    statusType: 'success',
    location: 'timedomain.py, Dashboard.vue',
    notes: '核心特徵，完整實現'
  },
  {
    category: '時域特徵',
    feature: 'Crest Factor',
    status: '✅ 已實現',
    statusType: 'success',
    location: 'timedomain.py',
    notes: '完整實現'
  },
  {
    category: '時域特徵',
    feature: '累積信號能量',
    status: '⚠️ 可計算',
    statusType: 'warning',
    location: '需手動累加',
    notes: '需自動化'
  },
  {
    category: '頻域特徵',
    feature: 'FFT',
    status: '✅ 已實現',
    statusType: 'success',
    location: 'frequencydomain.py',
    notes: '完整實現'
  },
  {
    category: '頻域特徵',
    feature: '光譜峭度',
    status: '✅ 已實現',
    statusType: 'success',
    location: 'Dashboard.vue（5.5-6.0 kHz）',
    notes: '方法一核心特徵'
  },
  {
    category: '頻域特徵',
    feature: '軸承缺陷頻率幅度',
    status: '✅ 已實現',
    statusType: 'success',
    location: 'FrequencyDomainAnalysis.vue',
    notes: 'BPFO/BPFI/BSF/FTF'
  },
  {
    category: '頻域特徵',
    feature: '峰值頻率變化檢測',
    status: '✅ 已實現',
    statusType: 'success',
    location: 'EnvelopeAnalysis.vue',
    notes: '異常檢測功能'
  },
  {
    category: '進階方法',
    feature: '小波變換',
    status: '✅ 已實現',
    statusType: 'success',
    location: 'timefrequency.py (CWT)',
    notes: '需補充能量特徵'
  },
  {
    category: '進階方法',
    feature: '高階過零點計數',
    status: '❌ 未實現',
    statusType: 'danger',
    location: '-',
    notes: '方法二需要（5 特徵）'
  },
  {
    category: '進階方法',
    feature: 'PCA 降維',
    status: '❌ 未實現',
    statusType: 'danger',
    location: '-',
    notes: '34 → 3 主成分'
  },
  {
    category: '進階方法',
    feature: '移動平均平滑化',
    status: '✅ 已實現',
    statusType: 'success',
    location: 'Dashboard.vue',
    notes: 'MAS Kurtosis'
  },
  {
    category: '進階方法',
    feature: 'NA4, FM4, M6A, M8A',
    status: '✅ 已實現',
    statusType: 'success',
    location: 'filterprocess.py, HigherOrderStatistics.vue',
    notes: '高階統計特徵完整'
  },
  {
    category: '進階方法',
    feature: 'NB4（希爾伯特）',
    status: '✅ 已實現',
    statusType: 'success',
    location: 'hilberttransform.py, EnvelopeAnalysis.vue',
    notes: '包絡分析完整'
  }
])

// 已完成模組數據
const completedModules = ref([
  {
    name: '時域分析',
    icon: 'TrendCharts',
    color: '#409eff',
    progress: 90,
    progressStatus: 'success',
    features: ['Peak', 'RMS', 'Kurtosis', 'Crest Factor'],
    files: ['timedomain.py', 'TimeDomainAnalysis.vue']
  },
  {
    name: '頻域分析',
    icon: 'DataAnalysis',
    color: '#67c23a',
    progress: 85,
    progressStatus: 'success',
    features: ['FFT', 'FM0', 'TSA', '軸承故障頻率'],
    files: ['frequencydomain.py', 'FrequencyDomainAnalysis.vue']
  },
  {
    name: '包絡分析',
    icon: 'Connection',
    color: '#e6a23c',
    progress: 95,
    progressStatus: 'success',
    features: ['帶通濾波', '希爾伯特轉換', '故障頻率識別', 'NB4'],
    files: ['hilberttransform.py', 'EnvelopeAnalysis.vue']
  },
  {
    name: '時頻分析',
    icon: 'TrendCharts',
    color: '#409eff',
    progress: 90,
    progressStatus: 'success',
    features: ['STFT', 'CWT', 'Spectrogram', 'NP4'],
    files: ['timefrequency.py', 'TimeFrequencyAnalysis.vue']
  },
  {
    name: '高階統計特徵',
    icon: 'DataAnalysis',
    color: '#67c23a',
    progress: 90,
    progressStatus: 'success',
    features: ['NA4', 'FM4', 'M6A', 'M8A', 'ER'],
    files: ['filterprocess.py', 'HigherOrderStatistics.vue']
  },
  {
    name: 'PHM 資料庫',
    icon: 'Folder',
    color: '#909399',
    progress: 95,
    progressStatus: 'success',
    features: ['查詢系統', '視覺化', '溫度數據', '異常搜尋'],
    files: ['phm_processor.py', 'phm_query.py', 'PHMDatabase.vue']
  }
])
</script>

<style scoped>
/* ===== 原始：淺色主題 ===== */
/* ===== 修改為：Apple Keynote 深色漸層主題 ===== */

/* ===== 字體設定 - 與 FONT.md 規範對齊 ===== */
/* 原始設定: h1=3.2em, h2=1.5em, h3=1.25em, h4=1.1em, h5=1em, p=16px */
/* 修改: 增大標題與內容文字,提供更舒適的閱讀體驗 */
.project-analysis h1 {
  font-size: 3.2em;
  line-height: 1.1;
  font-weight: bold;
  color: var(--text-primary);
}
.project-analysis h2 {
  /* 原始: 1.5em (≈24px) */
  /* 第一次修改: 1.75em (≈28px) - 增大主要區塊標題 */
  /* 第二次修改: 1.85em (≈29.6px) - 進一步增大標題以提升可讀性 */
  font-size: 1.85em;
  line-height: 1.3;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0;
}
.project-analysis h3 {
  /* 原始: 1.25em (≈20px) */
  /* 第一次修改: 1.4em (≈22.4px) - 增大小區塊標題 */
  /* 第二次修改: 1.5em (≈24px) - 進一步增大小區塊標題 */
  font-size: 1.5em;
  line-height: 1.4;
  font-weight: bold;
  color: var(--text-primary);
  margin-top: 0;
}
.project-analysis h4 {
  /* 原始: 1.1em (≈17.6px) */
  /* 第一次修改: 1.2em (≈19.2px) - 增大小標題 */
  /* 第二次修改: 1.25em (≈20px) - 進一步增大小標題 */
  font-size: 1.25em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--accent-primary);
  margin-top: 20px;
  /* 確保標題在深色背景下可讀 */
  background: var(--bg-secondary);
  padding: 10px 15px;
  border-radius: 6px;
  border-left: 4px solid var(--accent-primary);
}
.project-analysis h5 {
  /* 原始: 1em (16px) */
  /* 修改: 1.1em (≈17.6px) - 增大次級標題 */
  font-size: 1.1em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--text-primary);
}
.project-analysis p {
  /* 原始: 16px */
  /* 第一次修改: 17px - 略微增大內容文字 */
  /* 第二次修改: 18px - 進一步增大內容文字以提升閱讀舒適度 */
  font-size: 18px;
  line-height: 1.6;
  color: var(--text-secondary);
}
.project-analysis a {
  font-weight: 500;
  color: var(--accent-primary);
}

.project-analysis {
  padding: 20px;
  min-height: 100%;
}

/* ===== 表單區域樣式 ===== */
.project-analysis :deep(.el-form) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題表單樣式 */
  color: var(--text-primary);
}

.project-analysis :deep(.el-form-item__label) {
  /* 表單標籤文字顏色 */
  color: var(--text-primary) !important;
  font-weight: 500;
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大表單標籤文字 */
  /* 第二次修改: 16px - 進一步增大表單標籤文字 */
  font-size: 16px;
}

/* ===== 輸入框樣式 ===== */
.project-analysis :deep(.el-input__wrapper) {
  /* 原始：繼承預設顏色 */
  /* 修改：深色主題輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.project-analysis :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.project-analysis :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.project-analysis :deep(.el-input__inner) {
  /* 輸入框內部樣式 */
  background-color: transparent;
  color: var(--text-primary);
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大輸入框文字 */
  /* 第二次修改: 16px - 進一步增大輸入框文字 */
  font-size: 16px;
}

/* ===== 下拉選擇框樣式 ===== */
.project-analysis :deep(.el-select) {
  /* 確保下拉框繼承正確的顏色 */
  color: var(--text-primary);
}

.project-analysis :deep(.el-select .el-input__wrapper) {
  /* 下拉選擇框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.project-analysis :deep(.el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.project-analysis :deep(.el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.project-analysis :deep(.el-select .el-input__inner) {
  /* 下拉選擇框文字 */
  color: var(--text-primary);
}

.project-analysis :deep(.el-select__placeholder) {
  /* 下拉選擇框佔位符 */
  color: var(--text-secondary);
}

.project-analysis :deep(.el-select__caret) {
  /* 下拉選擇框箭頭圖標 */
  color: var(--text-secondary);
}

/* ===== 數字輸入框樣式 ===== */
.project-analysis :deep(.el-input-number) {
  /* 數字輸入框整體 */
  color: var(--text-primary);
}

.project-analysis :deep(.el-input-number .el-input__wrapper) {
  /* 數字輸入框外層包裝 */
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.project-analysis :deep(.el-input-number .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.project-analysis :deep(.el-input-number .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--accent-primary) inset;
}

.project-analysis :deep(.el-input-number__decrease),
.project-analysis :deep(.el-input-number__increase) {
  /* 數字輸入框 +/- 按鈕 */
  background-color: var(--bg-secondary);
  border: none;
  color: var(--text-primary);
}

.project-analysis :deep(.el-input-number__decrease:hover),
.project-analysis :deep(.el-input-number__increase:hover) {
  /* 按鈕懸停效果 */
  color: var(--accent-primary);
  background-color: var(--bg-tertiary);
}

.project-analysis :deep(.el-input-number__decrease.is-disabled),
.project-analysis :deep(.el-input-number__increase.is-disabled) {
  /* 禁用狀態按鈕 */
  color: var(--text-disabled);
  background-color: var(--bg-secondary);
}

/* ===== 按鈕樣式 ===== */
.project-analysis :deep(.el-button) {
  /* 按鈕整體樣式 */
  color: var(--text-primary);
  border-color: var(--border-color);
  /* 原始: 繼承預設 (≈14px) */
  /* 修改: 15px - 增大按鈕文字 */
  font-size: 15px;
}

.project-analysis :deep(.el-button--primary) {
  /* 主要按鈕 */
  background-color: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #ffffff;
}

.project-analysis :deep(.el-button--primary:hover) {
  /* 主要按鈕懸停 */
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.project-analysis :deep(.el-button--default) {
  /* 預設按鈕 */
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.project-analysis :deep(.el-button--default:hover) {
  /* 預設按鈕懸停 */
  background-color: var(--bg-tertiary);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* ===== 分隔線樣式 ===== */
.project-analysis :deep(.el-divider) {
  /* 分隔線整體樣式 */
  border-top-color: var(--border-color);
}

.project-analysis :deep(.el-divider__text) {
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

.project-analysis :deep(.el-divider--horizontal) {
  /* 水平分隔線 */
  display: flex;
  align-items: center;
  margin: 24px 0;
}

/* ===== 代碼樣式 ===== */
.project-analysis code {
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
/* 針對 el-table 表格組件的樣式優化 */
.project-analysis :deep(.el-table) {
  /* 表格整體樣式 */
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.project-analysis :deep(.el-table__header-wrapper) {
  /* 表頭樣式 */
  background-color: var(--bg-secondary);
}

.project-analysis :deep(.el-table thead) {
  color: var(--text-primary);
}

.project-analysis :deep(.el-table th) {
  /* 表頭單元格 */
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  font-weight: 600;
  border-color: var(--border-color) !important;
  /* 原始: 繼承預設 */
  /* 第一次修改: 14px - 增大表格標題 */
  /* 第二次修改: 15px - 進一步增大表格標題 */
  font-size: 15px;
}

.project-analysis :deep(.el-table td) {
  /* 表格內容單元格 */
  border-color: var(--border-color) !important;
  color: var(--text-primary);
  /* 原始: 繼承預設 */
  /* 第一次修改: 14px - 增大表格內容 */
  /* 第二次修改: 15px - 進一步增大表格內容 */
  font-size: 15px;
}

.project-analysis :deep(.el-table__row) {
  /* 表格行樣式 */
  background-color: var(--bg-primary);
}

.project-analysis :deep(.el-table__row:hover td) {
  /* 表格行懸停 */
  background-color: var(--bg-secondary) !important;
}

.project-analysis :deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  /* 斑馬紋行 */
  background-color: var(--bg-secondary);
}

/* ===== el-descriptions 表格樣式 ===== */
.project-analysis :deep(.el-descriptions) {
  /* 確保表格在深色背景下可讀 */
  background-color: transparent;
}

.project-analysis :deep(.el-descriptions__label) {
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

.project-analysis :deep(.el-descriptions__content) {
  /* 表格內容列樣式 */
  color: var(--text-primary) !important;
  padding: 12px 16px !important;
  /* 原始: 繼承預設 */
  /* 第一次修改: 15px - 增大表格內容文字 */
  /* 第二次修改: 16px - 進一步增大表格內容文字 */
  font-size: 16px;
}

.project-analysis :deep(.el-descriptions__cell) {
  /* 表格單元格邊框 */
  border-color: var(--border-color) !important;
}

.project-analysis :deep(.el-descriptions--bordered .el-descriptions__cell) {
  /* 邊框表格的單元格樣式 */
  border: 1px solid var(--border-color);
}

/* ===== 卡片樣式 ===== */
.project-analysis :deep(.el-card__header) {
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.project-analysis :deep(.el-card__body) {
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

/* ===== Tabs 標籤頁樣式 ===== */
.project-analysis :deep(.el-tabs) {
  /* 標籤頁整體 */
  background-color: var(--bg-primary);
}

.project-analysis :deep(.el-tabs__item) {
  /* 標籤項目 */
  color: var(--text-secondary);
}

.project-analysis :deep(.el-tabs__item:hover) {
  /* 標籤項目懸停 */
  color: var(--accent-primary);
}

.project-analysis :deep(.el-tabs__item.is-active) {
  /* 啟用的標籤項目 */
  color: var(--accent-primary);
}

.project-analysis :deep(.el-tabs__active-bar) {
  /* 啟用標示條 */
  background-color: var(--accent-primary);
}

.project-analysis :deep(.el-tabs--border-card) {
  /* 邊框標籤頁 */
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}

.project-analysis :deep(.el-tabs--border-card > .el-tabs__header) {
  background-color: var(--bg-secondary);
}

.project-analysis :deep(.el-tabs--border-card > .el-tabs__header .el-tabs__item) {
  color: var(--text-secondary);
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}

.project-analysis :deep(.el-tabs--border-card > .el-tabs__header .el-tabs__item.is-active) {
  background-color: var(--bg-primary);
  color: var(--accent-primary);
  border-color: var(--border-color);
}

/* ===== Collapse 折疊面板樣式 ===== */
.project-analysis :deep(.el-collapse) {
  background-color: transparent;
  border-color: var(--border-color);
}

.project-analysis :deep(.el-collapse-item__header) {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--border-color);
}

.project-analysis :deep(.el-collapse-item__header:hover) {
  background-color: var(--bg-tertiary);
}

.project-analysis :deep(.el-collapse-item__wrap) {
  background-color: var(--bg-primary);
  border-color: var(--border-color);
}

.project-analysis :deep(.el-collapse-item__content) {
  background-color: var(--bg-primary);
  color: var(--text-secondary);
}

/* ===== Alert 警告框樣式 ===== */
.project-analysis :deep(.el-alert) {
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}

.project-analysis :deep(.el-alert__title) {
  color: var(--text-primary);
}

.project-analysis :deep(.el-alert__description) {
  color: var(--text-secondary);
}

.project-analysis :deep(.el-alert--info) {
  background-color: var(--bg-secondary);
  border-color: var(--accent-info);
}

.project-analysis :deep(.el-alert--success) {
  background-color: var(--bg-secondary);
  border-color: var(--accent-success);
}

.project-analysis :deep(.el-alert--warning) {
  background-color: var(--bg-secondary);
  border-color: var(--accent-warning);
}

.project-analysis :deep(.el-alert--error) {
  background-color: var(--bg-secondary);
  border-color: var(--accent-danger);
}

.project-analysis :deep(.el-alert__content) {
  background: transparent;
}

/* ===== Timeline 時間軸樣式 ===== */
.project-analysis :deep(.el-timeline) {
  color: var(--text-primary);
}

.project-analysis :deep(.el-timeline-item__timestamp) {
  color: var(--text-secondary);
}

.project-analysis :deep(.el-timeline-item__wrapper) {
  color: var(--text-primary);
}

/* ===== Progress 進度條樣式 ===== */
.project-analysis :deep(.el-progress__text) {
  color: var(--text-primary);
}

/* ===== Tag 標籤樣式 ===== */
.project-analysis :deep(.el-tag) {
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.project-analysis :deep(.el-tag--success) {
  background-color: rgba(103, 194, 58, 0.2);
  border-color: var(--accent-success);
  color: var(--accent-success);
}

.project-analysis :deep(.el-tag--warning) {
  background-color: rgba(230, 162, 60, 0.2);
  border-color: var(--accent-warning);
  color: var(--accent-warning);
}

.project-analysis :deep(.el-tag--danger) {
  background-color: rgba(245, 108, 108, 0.2);
  border-color: var(--accent-danger);
  color: var(--accent-danger);
}

.project-analysis :deep(.el-tag--info) {
  background-color: rgba(64, 158, 255, 0.2);
  border-color: var(--accent-info);
  color: var(--accent-info);
}

.project-analysis :deep(.el-tag--primary) {
  background-color: rgba(64, 158, 255, 0.2);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* 組件特定樣式保留 */
.stats-card {
  text-align: center;
}

.method-analysis {
  padding: 20px;
}

/* 覆蓋 h4 樣式以配合深色主題背景 */
.method-analysis h3 {
  margin-bottom: 15px;
  margin-top: 0;
  color: var(--text-primary);
}

.method-analysis h4 {
  margin-top: 15px;
  margin-bottom: 10px;
  color: var(--text-primary);
  /* 確保標題在深色背景下可讀 */
  background: var(--bg-secondary);
  padding: 10px 15px;
  border-radius: 6px;
  border-left: 4px solid var(--accent-primary);
}

.method-analysis ul,
.method-analysis ol {
  padding-left: 20px;
  line-height: 1.8;
}

.method-analysis li {
  margin: 8px 0;
  color: var(--text-secondary);
}

.priority-title {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.priority-content {
  padding: 15px;
}

.priority-content h4 {
  margin-top: 15px;
  margin-bottom: 10px;
  color: var(--text-primary);
  /* 確保標題在深色背景下可讀 */
  background: var(--bg-secondary);
  padding: 10px 15px;
  border-radius: 6px;
  border-left: 4px solid var(--accent-primary);
}

.priority-content ol {
  padding-left: 20px;
  line-height: 1.8;
}

.priority-content li {
  margin: 8px 0;
  color: var(--text-secondary);
}

.module-card {
  margin-bottom: 15px;
  min-height: 280px;
}

.module-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.module-header h4 {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary);
  background: none;
  padding: 0;
  border: none;
}

.module-features {
  margin: 15px 0;
  padding-left: 20px;
  line-height: 1.8;
}

.module-features li {
  /* 原始: 14px */
  /* 第一次修改: 15px - 增大模組功能列表文字 */
  /* 第二次修改: 16px - 進一步增大列表文字 */
  font-size: 16px;
  color: var(--text-secondary);
}

.module-files {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border-color);
}

.summary-list {
  padding-left: 20px;
  line-height: 2;
}

.summary-list li {
  margin: 8px 0;
  /* 原始: 15px */
  /* 第一次修改: 16px - 增大總結列表文字 */
  /* 第二次修改: 17px - 進一步增大列表文字 */
  font-size: 17px;
  color: var(--text-secondary);
}

.summary-list.gap li {
  color: var(--accent-danger);
}

.method-title {
  display: flex;
  align-items: center;
  gap: 12px;
  /* 原始: 15px */
  /* 第一次修改: 16px - 增大方法標題文字 */
  /* 第二次修改: 17px - 進一步增大標題文字 */
  font-size: 17px;
  color: var(--text-primary);
}

:deep(.el-collapse-item__header) {
  height: auto;
  padding: 12px 0;
}

:deep(.el-table) {
  /* 原始: 14px */
  /* 第一次修改: 15px - 增大表格整體文字 */
  /* 第二次修改: 16px - 進一步增大表格文字 */
  font-size: 16px;
}

:deep(.el-statistic__head) {
  /* 原始: 14px */
  /* 第一次修改: 15px - 增大統計標題文字 */
  /* 第二次修改: 16px - 進一步增大統計標題 */
  font-size: 16px;
  color: var(--text-secondary);
}

:deep(.el-statistic__content) {
  /* 原始: 28px */
  /* 第一次修改: 30px - 增大統計內容數值 */
  /* 第二次修改: 32px - 進一步增大統計數值 */
  font-size: 32px;
  font-weight: bold;
  color: var(--text-primary);
}
</style>
