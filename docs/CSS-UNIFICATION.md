# 前端CSS樣式統一紀錄

**專案**: Viberation-RUL-Prognostics 振動剩餘壽命預測系統
**更新日期**: 2025-12-25
**作者**: Claude

---

## 更新概述

本次更新統一了前端Vue文件的CSS樣式,實現了與 `frontend/css/gradient.css` 和 `docs/FONT.md` 規範的一致性。

## 主要變更

### 1. 創建統一樣式文件

**文件**: `frontend/src/styles/common-styles.css`

**功能**:
- 定義統一的標題層級樣式 (h1-h6)
- 統一段落、代碼、按鈕、連結等基礎元素樣式
- 參照 FONT.md 的字體規範
- 使用 theme-dark.css 中定義的 CSS 變數
- 包含響應式設計調整

**主要樣式規範**:

```css
/* 標題層級 */
h1 { font-size: 3.2em; line-height: 1.1; color: var(--text-primary); }
h2 { font-size: 1.5em; line-height: 1.3; color: var(--text-primary); }
h3 { font-size: 1.25em; line-height: 1.4; color: var(--accent-primary); font-weight: 600; }
h4 { font-size: 1.1em; line-height: 1.4; color: var(--accent-info); font-weight: 600; }

/* 段落與內文 */
p { font-size: 16px; line-height: 1.6; color: var(--text-secondary); }

/* 代碼區塊 */
code {
  background: var(--bg-tertiary);
  color: var(--accent-info);
  padding: 2px 8px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

/* 按鈕 */
button {
  font-size: 1em;
  font-weight: 500;
  font-family: inherit;
}

/* 連結 */
a {
  font-weight: 500;
  color: var(--accent-info);
  transition: color var(--transition-speed) var(--transition-timing);
}
a:hover { color: var(--accent-primary); }
```

### 2. 更新 main.js

**文件**: `frontend/src/main.js`

**變更**:
- 在 theme-dark.css 之後導入 common-styles.css
- 確保樣式加載順序正確

```javascript
// 修改：導入全局深色主題樣式（Apple Keynote 漸層深色系）
import './styles/theme-dark.css'
// 修改：導入統一通用樣式（字體、文字、顏色等，參照 FONT.md）
import './styles/common-styles.css'
```

### 3. 簡化各Vue文件的樣式

**更新文件列表**:
1. ✅ Dashboard.vue (已有深色主題,保留組件特定樣式)
2. ✅ Algorithms.vue (已有深色主題,保留組件特定樣式)
3. ✅ TimeDomainAnalysis.vue (已有深色主題,保留組件特定樣式)
4. ✅ FrequencyDomainAnalysis.vue (簡化冗餘樣式定義)
5. ✅ TimeFrequencyAnalysis.vue (移除冗餘的h3, h4, p, code樣式)
6. ✅ EnvelopeAnalysis.vue (移除冗餘的h3, h4, h5, p, code樣式)
7. ✅ HigherOrderStatistics.vue (簡化樣式,保留card-header特定樣式)
8. ✅ ProjectAnalysis.vue (保留所有組件特定樣式)
9. ✅ PHMDatabase.vue (移除冗餘註釋,簡化樣式)
10. ✅ PHMTraining.vue (移除冗餘註釋,簡化樣式)

**變更原則**:
- 移除已在 common-styles.css 中定義的基礎樣式 (h1-h6, p, code, button, a等)
- 保留組件特定的樣式 (如 .dashboard, .card-header, .bearing-card 等)
- 統一使用 theme-dark.css 中的 CSS 變數
- 簡化冗餘的註釋,保留關鍵說明

## CSS 變數對照表

所有文件現在統一使用以下CSS變數(定義在 theme-dark.css):

| 變數名稱 | 用途 | 值 |
|---------|------|-----|
| `--text-primary` | 主要文字 | #ffffff |
| `--text-secondary` | 次要文字 | rgba(255, 255, 255, 0.75) |
| `--text-tertiary` | 第三級文字 | rgba(255, 255, 255, 0.6) |
| `--bg-card` | 卡片背景 | rgba(20, 25, 50, 0.7) |
| `--bg-secondary` | 次要背景 | rgba(15, 19, 48, 0.75) |
| `--bg-tertiary` | 第三級背景 | rgba(64, 64, 74, 0.65) |
| `--border-color` | 邊框顏色 | rgba(255, 255, 255, 0.12) |
| `--accent-primary` | 主要強調色 | #667eea |
| `--accent-info` | 資訊色 | #409eff |
| `--accent-success` | 成功色 | #67c23a |
| `--accent-warning` | 警告色 | #e6a23c |
| `--accent-danger` | 危險色 | #f56c6c |

## 響應式設計

根據 FONT.md 規範,實現以下響應式調整:

### 平板與手機 (≤768px)
- h1 字體從 3.2em 調整為固定 28px
- 其他標題相應調整

### 小螢幕手機 (≤480px)
- h1 字體調整為 24px
- 段落字體調整為 14px
- 減少內邊距,優化小螢幕顯示

## 深色漸層主題特色

保留並強化了以下 Apple Keynote 風格特色:

1. **深色漸層背景**: #030406 → #0f1330 → #40404a → #8b8b93
2. **Vignette 內陰影效果**: 增強深度感
3. **玻璃態卡片效果**: 半透明背景搭配模糊
4. **統一的白色文字**: 確保可讀性
5. **強調色系統**: 使用紫色系(#667eea)作為主要強調色

## 預期效果

1. **樣式一致性**: 所有頁面使用統一的文字大小、顏色和間距
2. **可維護性提升**: 集中管理基礎樣式,修改更方便
3. **代碼精簡**: 減少重複的CSS代碼
4. **視覺統一**: 所有頁面保持一致的深色漸層主題風格
5. **響應式優化**: 在不同設備上都有良好的顯示效果

## 後續建議

1. **測試所有頁面**: 確保每個Vue文件的顯示效果正常
2. **檢查ECharts圖表**: 確保圖表文字顏色與深色主題協調
3. **驗證響應式**: 在不同螢幕尺寸下測試顯示效果
4. **性能優化**: 考慮使用CSS變數的性能影響
5. **文檔更新**: 如需修改樣式,請先參考 FONT.md 和 common-styles.css

## 參考文檔

- `frontend/css/gradient.css` - Apple Keynote 風格深色漸層背景
- `docs/FONT.md` - 字體規範文檔
- `frontend/src/styles/theme-dark.css` - 深色主題CSS變數定義
- `frontend/src/styles/common-styles.css` - 統一通用樣式

---

**文件版本**: 1.0
**最後更新**: 2025-12-25
