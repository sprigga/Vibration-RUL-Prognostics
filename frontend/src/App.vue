<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>軸承 RUL 預測系統</h1>
          <p>振動信號分析工具 - IEEE PHM 2012 Data Challenge</p>
        </div>
      </el-header>

      <el-container>
        <el-aside width="200px">
          <el-menu
            :default-active="$route.path"
            router
            class="sidebar-menu"
          >
            <el-menu-item index="/">
              <el-icon><Odometer /></el-icon>
              <span>PHM 2012</span>
            </el-menu-item>
            <el-menu-item index="/time-domain">
              <el-icon><DataLine /></el-icon>
              <span>時域特徵分析</span>
            </el-menu-item>
            <el-menu-item index="/frequency-domain">
              <el-icon><DataAnalysis /></el-icon>
              <span>頻域特徵分析</span>
            </el-menu-item>
            <el-menu-item index="/envelope-analysis">
              <el-icon><TrendCharts /></el-icon>
              <span>包絡分析</span>
            </el-menu-item>
            <el-menu-item index="/time-frequency">
              <el-icon><TrendCharts /></el-icon>
              <span>時頻分析</span>
            </el-menu-item>
            <el-menu-item index="/higher-order-statistics">
              <el-icon><DataAnalysis /></el-icon>
              <span>高階統計特徵</span>
            </el-menu-item>
            <el-menu-item index="/project-analysis">
              <el-icon><Document /></el-icon>
              <span>專案分析</span>
            </el-menu-item>
            <!-- <el-menu-item index="/algorithms">
              <el-icon><Operation /></el-icon>
              <span>演算法展示</span>
            </el-menu-item> -->
            <!-- <el-sub-menu index="phm">
              <template #title>
                <el-icon><TrendCharts /></el-icon>
                <span>PHM 2012</span>
              </template>
              <el-menu-item index="/phm-database">
                <el-icon><DataBoard /></el-icon>
                <span>資料庫查詢</span>
              </el-menu-item>
              <el-menu-item index="/phm-training">
                <el-icon><TrendCharts /></el-icon>
                <span>訓練數據</span>
              </el-menu-item>
            </el-sub-menu> -->
          </el-menu>
        </el-aside>

        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { Odometer, TrendCharts, DataLine, DataAnalysis, Document } from '@element-plus/icons-vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  height: 100vh;
  background: radial-gradient(circle at top left, #7f7fd5, #86a8e7, #91eae4);
  background-size: 200% 200%;
  animation: bgFlow 10s ease-in-out infinite alternate;
}

@keyframes bgFlow {
  0% { background-position: 0% 0%; }
  100% { background-position: 100% 100%; }
}

.el-container {
  height: 100%;
}

.el-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  position: relative;
  z-index: 10;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  background: linear-gradient(135deg, #ffffff, #e0e7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-content p {
  margin: 5px 0 0;
  font-size: 12px;
  opacity: 0.9;
}

.el-aside {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  border-right: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-menu {
  border: none;
  background-color: transparent;
  padding: 10px 0;
}

.sidebar-menu .el-menu-item {
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 4px 8px;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(102, 126, 234, 0.15);
  transform: translateX(4px);
}

.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
  color: #667eea;
  font-weight: 600;
}

.el-main {
  background: transparent;
  padding: 20px;
  overflow-y: auto;
}

/* 全局卡片样式 */
.el-main .el-card {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.el-main .el-card:hover {
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}
</style>
