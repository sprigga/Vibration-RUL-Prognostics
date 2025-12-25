/**
 * API Configuration
 * 從環境變數讀取 API 配置，避免硬編碼
 */

// 從 Vite 環境變數獲取 API Base URL
// VITE_ 前綴是 Vite 規定的環境變數命名規則
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8081'

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
