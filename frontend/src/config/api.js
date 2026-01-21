/**
 * API Configuration
 * 從環境變數讀取 API 配置，避免硬編碼
 */

// 原始配置: const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8081'
// 修改: 在 nginx proxy 環境下使用相對路徑，由 nginx 轉發到後端
// 開發環境可以透過 VITE_API_BASE_URL 設定完整的後端 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

/**
 * API 配置物件
 */
export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json'
  }
}

/**
 * 取得完整的 API 端點 URL
 * @param {string} endpoint - API 端點路徑
 * @returns {string} 完整的 URL
 */
export const getApiUrl = (endpoint) => {
  // 移除端點開頭的斜線以避免雙斜線
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint
  return `${API_BASE_URL}/${cleanEndpoint}`
}

export default apiConfig
