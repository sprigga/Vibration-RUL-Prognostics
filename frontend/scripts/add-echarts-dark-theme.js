#!/usr/bin/env node
/**
 * 輔助腳本：為 ECharts 配置添加深色主題
 *
 * 使用方式：
 * node scripts/add-echarts-dark-theme.js
 *
 * 此腳本會在 frontend/src/views/ 目錄下的所有 .vue 文件中
 * 為 ECharts option 配置添加深色主題樣式
 */

const fs = require('fs');
const path = require('path');

const viewsDir = path.join(__dirname, '../src/views');

// ECharts 深色主題配置模板
const darkThemeConfig = {
  title: {
    textStyle: { color: '#ffffff' }
  },
  legend: {
    textStyle: { color: '#ffffff' }
  },
  xAxis: {
    axisLabel: { color: '#ffffff' },
    nameTextStyle: { color: '#ffffff' }
  },
  yAxis: {
    axisLabel: { color: '#ffffff' },
    nameTextStyle: { color: '#ffffff' },
    splitLine: {
      lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
    }
  }
};

// 處理單個 Vue 文件
function processVueFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;

  // 檢查文件是否已包含深色主題配置
  if (content.includes("color: '#ffffff'") && content.includes("dark theme")) {
    console.log(`✓ 跳過（已包含深色主題）: ${path.basename(filePath)}`);
    return false;
  }

  // 查找 ECharts option 配置並添加深色主題
  // 匹配 const option = { ... } 或類似的配置對象

  // 在 title 後添加 textStyle
  content = content.replace(
    /title:\s*\{([^}]*text:\s*['"`][^'"`]+['"`](?![^}]*textStyle))/g,
    (match, inner) => {
      modified = true;
      return match.replace(/text:\s*['"`][^'"`]+['"`]/, `$&\n      // 原始：繼承預設顏色\n      // 修改：深色主題白色文字\n      textStyle: { color: '#ffffff' }`);
    }
  );

  // 在 legend 後添加 textStyle
  content = content.replace(
    /legend:\s*\{[^}]*data:\s*\[[^\]]+\][^}]*\}/g,
    (match) => {
      if (!match.includes('textStyle')) {
        modified = true;
        return match.replace(/}$/, `      // 原始：繼承預設顏色\n      // 修改：深色主題白色文字\n      textStyle: { color: '#ffffff' }\n    }`);
      }
      return match;
    }
  );

  // 在 xAxis 中添加 axisLabel 和 nameTextStyle
  content = content.replace(
    /xAxis:\s*\{[^}]*name:\s*['"`][^'"`]+['"`][^}]*\}/g,
    (match) => {
      if (!match.includes('axisLabel') && !match.includes('nameTextStyle')) {
        modified = true;
        return match.replace(/}$/, `      // 原始：繼承預設顏色\n      // 修改：深色主題白色文字\n      axisLabel: { color: '#ffffff' },\n      nameTextStyle: { color: '#ffffff' }\n    }`);
      }
      return match;
    }
  );

  // 在 yAxis 中添加 axisLabel, nameTextStyle 和 splitLine
  content = content.replace(
    /yAxis:\s*\{[^}]*name:\s*['"`][^'"`]+['"`][^}]*\}/g,
    (match) => {
      if (!match.includes('axisLabel')) {
        modified = true;
        return match.replace(/}$/, `      // 原始：繼承預設顏色\n      // 修改：深色主題白色文字\n      axisLabel: { color: '#ffffff' },\n      nameTextStyle: { color: '#ffffff' },\n      splitLine: {\n        // 原始：繼承預設顏色\n        // 修改：深色主題淺色網格\n        lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }\n      }\n    }`);
      }
      return match;
    }
  );

  if (modified) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`✓ 已更新: ${path.basename(filePath)}`);
    return true;
  }

  return false;
}

// 主函數
function main() {
  console.log('開始為 ECharts 配置添加深色主題...\n');

  const files = fs.readdirSync(viewsDir).filter(f => f.endsWith('.vue'));
  let updatedCount = 0;

  files.forEach(file => {
    const filePath = path.join(viewsDir, file);
    if (processVueFile(filePath)) {
      updatedCount++;
    }
  });

  console.log(`\n完成！共更新 ${updatedCount} 個文件。`);
  console.log('\n注意：此腳本僅處理常見的 ECharts 配置模式。');
  console.log('複雜的配置可能需要手動調整。');
}

// 運行腳本
main();
