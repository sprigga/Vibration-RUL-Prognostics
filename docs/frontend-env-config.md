# 前端環境變數配置說明

## 為什麼要做這個改進？

### 原本的問題
在 `Dashboard.vue` 和 `PHMDatabase.vue` 中，API_BASE 使用硬編碼方式：
```javascript
const API_BASE = 'http://localhost:8081'
```

這種做法有以下缺點：
1. **維護困難**：API URL 改變時需要修改多個檔案
2. **環境切換不便**：開發、測試、生產環境使用不同 URL 時需手動修改
3. **部署彈性差**：無法根據部署環境動態調整
4. **安全性問題**：API 端點暴露在原始碼中

### 改進方案
使用 Vite 環境變數系統，將 API 配置外部化。

## 檔案結構

```
frontend/
├── .env                          # 開發環境配置（不提交到 Git）
├── .env.example                  # 配置範例（提交到 Git）
├── .env.production.example       # 生產環境配置範例（提交到 Git）
└── src/
    └── config/
        └── api.js               # 統一的 API 配置模組
```

## 使用方法

### 1. 本地開發

確保 `frontend/.env` 檔案存在：
```bash
cd frontend
cp .env.example .env
```

`.env` 檔案內容：
```env
VITE_API_BASE_URL=http://localhost:8081
```

### 2. 生產環境部署

建立生產環境配置：
```bash
cd frontend
cp .env.production.example .env.production
```

編輯 `.env.production`：
```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

Vite 會根據執行模式自動載入對應的環境變數檔案：
- `npm run dev` → 載入 `.env`
- `npm run build` → 載入 `.env.production`

### 3. 在程式碼中使用

```javascript
import { getApiUrl } from '@/config/api'

// 自動從環境變數讀取
const API_BASE = getApiUrl('api')
```

## 環境變數命名規則

Vite 規定環境變數必須以 `VITE_` 開頭才能在客戶端程式碼中使用：

```env
VITE_API_BASE_URL=http://localhost:8081    ✅ 可用
API_BASE_URL=http://localhost:8081         ❌ 不可用
```

## 安全性注意事項

1. **不要將敏感資訊放入環境變數**
   - 環境變數會被打包到客戶端程式碼中
   - 任何人都可以在瀏覽器開發者工具中看到

2. **.env 檔案不要提交到 Git**
   - `.env` 已加入 `.gitignore`
   - 只提交 `.env.example` 作為範例

3. **生產環境配置**
   - 使用 CI/CD 工具的 secrets 管理功能
   - 或在部署伺服器上直接建立 `.env.production`

## 優勢總結

✅ **統一管理**：所有 API 配置集中在一個檔案
✅ **環境隔離**：不同環境使用不同配置，無需修改程式碼
✅ **易於維護**：API URL 改變時只需修改環境變數
✅ **安全性提升**：敏感配置不提交到版本控制
✅ **部署彈性**：可根據部署環境動態調整配置

## 常見問題

### Q: 為什麼不直接用 `process.env`？
A: Vite 使用 `import.meta.env` 而不是 Node.js 的 `process.env`

### Q: 環境變數修改後需要重啟嗎？
A: 是的，修改 `.env` 後需要重啟開發伺服器

### Q: 如何在程式碼中判斷當前環境？
A: 使用 `import.meta.env.MODE` 或 `import.meta.env.PROD`
```javascript
if (import.meta.env.DEV) {
  console.log('開發模式')
}
if (import.meta.env.PROD) {
  console.log('生產模式')
}
```

## 相關文件

- [Vite 環境變數官方文件](https://vitejs.dev/guide/env-and-mode.html)
- [Vue 3 環境變數最佳實踐](https://vuejs.org/guide/best-practices/production-deployment.html)
