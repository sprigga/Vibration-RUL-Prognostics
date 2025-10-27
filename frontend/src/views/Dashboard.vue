<template>
  <div class="dashboard">
    <el-row :gutter="20" class="header-stats">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #67c23a;">
            <el-icon size="30"><Check /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ healthyCount }}</h3>
            <p>健康設備</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #e6a23c;">
            <el-icon size="30"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ warningCount }}</h3>
            <p>警告</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #f56c6c;">
            <el-icon size="30"><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ criticalCount }}</h3>
            <p>嚴重異常</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #909399;">
            <el-icon size="30"><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ totalAnalyses }}</h3>
            <p>總分析次數</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>健康趨勢</span>
              <el-select v-model="selectedGuide" placeholder="選擇滑軌" style="width: 200px;" @change="loadTrendData">
                <el-option
                  v-for="spec in guideSpecs"
                  :key="spec.id"
                  :label="`${spec.series}-${spec.type}`"
                  :value="spec.id"
                />
              </el-select>
            </div>
          </template>
          <div style="height: 300px;">
            <Line v-if="chartData" :data="chartData" :options="chartOptions" />
            <el-empty v-else description="選擇滑軌以查看趨勢" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span>最近分析</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="result in recentResults"
              :key="result.id"
              :timestamp="formatDate(result.timestamp)"
              :color="getHealthColor(result.health_score)"
            >
              <div>
                <strong>健康分數: {{ result.health_score }}</strong>
                <p style="font-size: 12px; color: #909399;">速度: {{ result.velocity }} m/s</p>
              </div>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-if="recentResults.length === 0" description="暫無記錄" />
        </el-card>
      </el-col>
    </el-row>

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
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <el-space wrap>
            <el-button type="primary" @click="$router.push('/analysis')">
              <el-icon><DataAnalysis /></el-icon>
              開始分析
            </el-button>
            <el-button type="success" @click="$router.push('/frequency')">
              <el-icon><Connection /></el-icon>
              頻率計算
            </el-button>
            <el-button type="info" @click="$router.push('/algorithms')">
              <el-icon><Operation /></el-icon>
              演算法展示
            </el-button>
            <el-button @click="$router.push('/guide-specs')">
              <el-icon><Setting /></el-icon>
              管理滑軌規格
            </el-button>
            <el-button type="warning" @click="$router.push('/phm-database')">
              <el-icon><Folder /></el-icon>
              PHM 資料庫
            </el-button>
            <el-button @click="$router.push('/phm-training')">
              <el-icon><TrendCharts /></el-icon>
              PHM 訓練數據
            </el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { Check, Warning, CircleClose, DataLine, DataAnalysis, Connection, Operation, Setting, Aim, Tools, Folder, TrendCharts } from '@element-plus/icons-vue'
import api from '../stores/api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

const healthyCount = ref(0)
const warningCount = ref(0)
const criticalCount = ref(0)
const totalAnalyses = ref(0)
const recentResults = ref([])
const guideSpecs = ref([])
const selectedGuide = ref(null)
const chartData = ref(null)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      title: {
        display: true,
        text: '健康分數'
      }
    }
  }
}

const loadDashboardData = async () => {
  try {
    const results = await api.getResults(null, 100)
    totalAnalyses.value = results.length

    healthyCount.value = results.filter(r => r.health_score >= 90).length
    warningCount.value = results.filter(r => r.health_score >= 60 && r.health_score < 90).length
    criticalCount.value = results.filter(r => r.health_score < 60).length

    recentResults.value = results.slice(0, 10)
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
}

const loadGuideSpecs = async () => {
  try {
    guideSpecs.value = await api.getGuideSpecs()
    if (guideSpecs.value.length > 0) {
      selectedGuide.value = guideSpecs.value[0].id
      await loadTrendData()
    }
  } catch (error) {
    console.error('Failed to load guide specs:', error)
  }
}

const loadTrendData = async () => {
  if (!selectedGuide.value) return

  try {
    const trend = await api.getHealthTrend(selectedGuide.value, 30)

    chartData.value = {
      labels: trend.trend.map(t => new Date(t.timestamp).toLocaleDateString()),
      datasets: [
        {
          label: '健康分數',
          data: trend.trend.map(t => t.health_score),
          borderColor: '#667eea',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          tension: 0.4
        }
      ]
    }
  } catch (error) {
    console.error('Failed to load trend data:', error)
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-TW')
}

const getHealthColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 75) return '#e6a23c'
  if (score >= 60) return '#f56c6c'
  return '#909399'
}

onMounted(() => {
  loadDashboardData()
  loadGuideSpecs()
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
</style>
