import axios from 'axios'

// 原始配置: const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
// 第一次修改: Backend 伺服器運行在 port 8000，更新預設 URL 以匹配
// 修改: 統一 Backend 伺服器運行在 port 8081
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8081'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {

  // Analysis
  analyzeVibration(data) {
    return api.post('/api/analyze', data)
  },

  uploadCSV(file, guideSpecId, fs, velocity) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/api/upload-csv?guide_spec_id=${guideSpecId}&fs=${fs}&velocity=${velocity}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // PHM 2012 Challenge APIs
  getPHMTrainingSummary() {
    return api.get('/api/phm/training-summary')
  },

  getPHMAnalysisData() {
    return api.get('/api/phm/analysis-data')
  },

  uploadBearingData(file, bearingName) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/api/phm/upload-bearing-data?bearing_name=${bearingName}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  getBearingTestData(bearingName) {
    return api.get(`/api/phm/test-data/${bearingName}`)
  },

  predictRUL(bearingName, modelType = 'baseline') {
    return api.post('/api/phm/predict-rul', null, {
      params: { bearing_name: bearingName, model_type: modelType }
    })
  }
}
