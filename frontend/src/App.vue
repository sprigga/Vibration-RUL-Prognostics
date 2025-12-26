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
/* ===== 原始：淺色動畫漸層主題 ===== */
/* ===== 修改為：Apple Keynote 深色漸層主題 ===== */
/* ===== 修改：字體設定對齊 FONT.md 規範 ===== */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 背景漸層和動畫由 theme-dark.css 處理 */
/* 原始字體：font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; */
/* 修改：對齊 FONT.md 規範的 system-ui 字體堆疊 */
#app {
  /* FONT.md 規範的 font-family */
  font-family: system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;

  /* 字體渲染優化 (FONT.md 規範) */
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;

  /* 深色漸層背景和動畫由 theme-dark.css 定義 */
}

.el-container {
  height: 100%;
}

/* ===== Header 樣式 - 深色漸層 ===== */
.el-header {
  /* 原始：linear-gradient(135deg, #667eea 0%, #764ba2 100%) */
  /* 修改：使用深色主題變數的漸層 */
  background: linear-gradient(135deg, var(--theme-mid), var(--theme-lower-mid));
  color: var(--text-primary);
  display: flex;
  align-items: center;
  box-shadow: 0 4px 16px var(--shadow-md);
  border-bottom: 1px solid var(--border-color);
  position: relative;
  z-index: 10;
}

/* 原始：font-size: 24px; font-weight: 600; */
/* 修改：對齊 FONT.md h2 規範 (1.5em) */
.header-content h1 {
  margin: 0;
  font-size: 1.5em;  /* FONT.md: h2 = 1.5em */
  line-height: 1.3;   /* FONT.md: h2 line-height = 1.3 */
  font-weight: bold;   /* FONT.md: h2 font-weight = bold */
  /* 原始：linear-gradient(135deg, #ffffff, #e0e7ff) */
  /* 修改：深色主題的漸層文字效果 */
  background: linear-gradient(135deg, #ffffff, var(--text-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 原始：font-size: 12px; */
/* 修改：對齊 FONT.md 段落文字規範 (16px) */
.header-content p {
  margin: 5px 0 0;
  font-size: 16px;    /* FONT.md: 段落文字 = 16px */
  line-height: 1.6;   /* FONT.md: 段落 line-height = 1.6 */
  /* 原始：opacity: 0.9 */
  /* 修改：使用深色主題變數 */
  color: var(--text-secondary);
}

/* ===== Sidebar 樣式 - 深色半透明 ===== */
.el-aside {
  /* 原始：rgba(255, 255, 255, 0.5) */
  /* 修改：深色半透明背景 */
  background: var(--bg-secondary);
  backdrop-filter: blur(12px);
  /* 原始：rgba(255, 255, 255, 0.4) */
  /* 修改：深色邊框 */
  border-right: 1px solid var(--border-color);
  box-shadow: 2px 0 8px var(--shadow-md);
}

.sidebar-menu {
  border: none;
  background-color: transparent;
  padding: 10px 0;
}

.sidebar-menu .el-menu-item {
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 6px 10px;
  padding: 0 18px;
  height: 50px;
  line-height: 50px;
  /* 原始：繼承預設顏色 */
  /* 修改：使用深色主題文字顏色 */
  color: var(--text-secondary);
  background: transparent;
  /* 原始：繼承預設字體大小 */
  /* 修改：增大字體以提供舒適閱讀體驗 */
  font-size: 16px;
}

.sidebar-menu .el-menu-item:hover {
  /* 原始：rgba(102, 126, 234, 0.15) */
  /* 修改：使用深色主題卡片背景 */
  background: var(--bg-card);
  color: var(--text-primary);
  transform: translateX(4px);
}

.sidebar-menu .el-menu-item.is-active {
  /* 原始：linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) */
  /* 修改：使用深色主題漸層 */
  background: linear-gradient(135deg, var(--bg-card), var(--bg-card-hover));
  color: var(--accent-primary);
  font-weight: 600;
  border: 1px solid var(--border-color-focus);
  /* 確保激活狀態也使用相同字體大小 */
  font-size: 16px;
}

.el-main {
  background: transparent;
  padding: 20px;
  overflow-y: auto;
  color: var(--text-primary);
}

/* ===== 卡片樣式 - 深色玻璃態 ===== */
.el-main .el-card {
  /* 原始：rgba(255, 255, 255, 0.5) */
  /* 修改：使用深色主題變數 */
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  /* 原始：rgba(255, 255, 255, 0.4) */
  /* 修改：深色邊框 */
  border: 1px solid var(--border-color);
  /* 原始：rgba(0, 0, 0, 0.15) */
  /* 修改：深色陰影 */
  box-shadow: 0 10px 40px var(--shadow-md);
  transition: all 0.3s ease;
  color: var(--text-primary);
}

.el-main .el-card:hover {
  /* 原始：rgba(0, 0, 0, 0.2) */
  /* 修改：深色陰影 */
  box-shadow: 0 12px 48px var(--shadow-lg);
  transform: translateY(-2px);
  border-color: var(--border-color-focus);
  background: var(--bg-card-hover);
}

/* ===== Card Header 樣式 ===== */
.el-card__header {
  /* 原始：繼承卡片背景 */
  /* 修改：深色次要背景 */
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

/* ===== Typography 覆蓋 - 對齊 FONT.md 規範 ===== */
/* FONT.md 標題層級規範 */
h1 {
  font-size: 3.2em;
  line-height: 1.1;
  font-weight: bold;
  color: var(--text-primary);
}

h2 {
  font-size: 1.5em;
  line-height: 1.3;
  font-weight: bold;
  color: var(--text-primary);
}

h3 {
  font-size: 1.25em;
  line-height: 1.4;
  font-weight: bold;
  color: var(--text-primary);
}

h4 {
  font-size: 1.1em;
  line-height: 1.4;
  font-weight: 600;
  color: var(--text-primary);
}

h5, h6 {
  color: var(--text-primary);
}

/* FONT.md 段落文字規範 */
p {
  font-size: 16px;
  line-height: 1.6;
  color: var(--text-secondary);
}

span, div {
  color: var(--text-secondary);
}
</style>
