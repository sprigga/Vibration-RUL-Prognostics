<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>🔧 CPC 線性滑軌振動分析系統</h1>
          <p>Linear Guide Vibration Analysis System</p>
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
              <span>儀表板</span>
            </el-menu-item>
            <el-menu-item index="/algorithms">
              <el-icon><Operation /></el-icon>
              <span>演算法展示</span>
            </el-menu-item>
            <el-sub-menu index="phm">
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
            </el-sub-menu>
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
import { Odometer, Operation, TrendCharts, DataBoard } from '@element-plus/icons-vue'
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
}

.el-container {
  height: 100%;
}

.el-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.header-content p {
  margin: 5px 0 0;
  font-size: 12px;
  opacity: 0.9;
}

.el-aside {
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
}

.sidebar-menu {
  border: none;
  background-color: transparent;
  padding: 10px 0;
}

.el-main {
  background-color: #ffffff;
  padding: 20px;
  overflow-y: auto;
}
</style>
