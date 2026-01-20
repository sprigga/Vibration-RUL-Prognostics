/**
 * Pinia store for real-time analysis state management
 *
 * Manages real-time sensor data, features, alerts, and WebSocket connections.
 */
import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import websocketService from '@/services/websocket'

export const useRealtimeStore = defineStore('realtime', () => {
  // State
  const isConnected = ref(false)
  const currentSensor = ref(null)
  const latestFeatures = reactive({})
  const alertHistory = ref([])
  const isStreaming = ref(false)
  const connectionStatus = ref('disconnected')  // 'disconnected', 'connecting', 'connected', 'error'

  // Chart data buffers (keep last N points for display)
  const MAX_BUFFER_POINTS = 100

  const signalBuffer = ref({
    timestamps: [],
    horizontal: [],
    vertical: []
  })

  const featureBuffer = ref({
    timestamps: [],
    rms_h: [],
    rms_v: [],
    kurtosis_h: [],
    kurtosis_v: [],
    peak_h: [],
    peak_v: []
  })

  // Computed properties
  const hasAlerts = computed(() => alertHistory.value.length > 0)

  const latestAlert = computed(() => {
    return alertHistory.value.length > 0 ? alertHistory.value[0] : null
  })

  const featureCount = computed(() => {
    return featureBuffer.value.timestamps.length
  })

  /**
   * Connect to a sensor's real-time data stream
   * @param {number} sensorId - Sensor ID to connect to
   */
  function connect(sensorId) {
    if (currentSensor.value === sensorId && isConnected.value) {
      console.log('Already connected to sensor', sensorId)
      return
    }

    currentSensor.value = sensorId
    connectionStatus.value = 'connecting'

    // Set up WebSocket event handlers
    websocketService.on('connected', (data) => {
      isConnected.value = true
      isStreaming.value = true
      connectionStatus.value = 'connected'
      console.log('Connected to real-time stream:', data)
    })

    websocketService.on('disconnected', () => {
      isConnected.value = false
      isStreaming.value = false
      connectionStatus.value = 'disconnected'
    })

    websocketService.on('feature_update', (data) => {
      updateFeatures(data)
    })

    websocketService.on('alert', (alert) => {
      addAlert(alert)
    })

    websocketService.on('error', (error) => {
      connectionStatus.value = 'error'
      console.error('WebSocket error:', error)
    })

    websocketService.on('pong', (data) => {
      console.log('Pong received:', data)
    })

    // Connect
    websocketService.connect(sensorId)
  }

  /**
   * Disconnect from current sensor
   */
  function disconnect() {
    websocketService.disconnect()
    isConnected.value = false
    isStreaming.value = false
    connectionStatus.value = 'disconnected'
    currentSensor.value = null
  }

  /**
   * Update features with new data
   * @param {object} data - Feature data from WebSocket
   */
  function updateFeatures(data) {
    // Update latest features
    Object.assign(latestFeatures, data)

    // Create timestamp
    const timestamp = data.timestamp || data.window_end || new Date().toISOString()

    // Update feature buffers (keep last MAX_BUFFER_POINTS points)
    featureBuffer.value.timestamps.push(timestamp)

    // Add features if present
    if (data.rms_h !== undefined) featureBuffer.value.rms_h.push(data.rms_h)
    if (data.rms_v !== undefined) featureBuffer.value.rms_v.push(data.rms_v)
    if (data.kurtosis_h !== undefined) featureBuffer.value.kurtosis_h.push(data.kurtosis_h)
    if (data.kurtosis_v !== undefined) featureBuffer.value.kurtosis_v.push(data.kurtosis_v)
    if (data.peak_h !== undefined) featureBuffer.value.peak_h.push(data.peak_h)
    if (data.peak_v !== undefined) featureBuffer.value.peak_v.push(data.peak_v)

    // Trim buffers to max size
    trimBuffers()
  }

  /**
   * Add alert to history
   * @param {object} alert - Alert data
   */
  function addAlert(alert) {
    alertHistory.value.unshift({
      ...alert,
      received_at: new Date().toISOString()
    })

    // Keep only last 50 alerts
    if (alertHistory.value.length > 50) {
      alertHistory.value = alertHistory.value.slice(0, 50)
    }

    console.warn('Alert received:', alert.message)
  }

  /**
   * Trim buffers to max size
   */
  function trimBuffers() {
    while (featureBuffer.value.timestamps.length > MAX_BUFFER_POINTS) {
      featureBuffer.value.timestamps.shift()
      featureBuffer.value.rms_h.shift()
      featureBuffer.value.rms_v.shift()
      featureBuffer.value.kurtosis_h.shift()
      featureBuffer.value.kurtosis_v.shift()
      featureBuffer.value.peak_h.shift()
      featureBuffer.value.peak_v.shift()
    }

    while (signalBuffer.value.timestamps.length > MAX_BUFFER_POINTS) {
      signalBuffer.value.timestamps.shift()
      signalBuffer.value.horizontal.shift()
      signalBuffer.value.vertical.shift()
    }
  }

  /**
   * Clear all buffers and history
   */
  function clearBuffers() {
    signalBuffer.value = {
      timestamps: [],
      horizontal: [],
      vertical: []
    }

    featureBuffer.value = {
      timestamps: [],
      rms_h: [],
      rms_v: [],
      kurtosis_h: [],
      kurtosis_v: [],
      peak_h: [],
      peak_v: []
    }

    alertHistory.value = []

    // Clear latest features
    Object.keys(latestFeatures).forEach(key => {
      delete latestFeatures[key]
    })
  }

  /**
   * Acknowledge an alert
   * @param {number} alertId - Alert ID to acknowledge
   */
  async function acknowledgeAlert(alertId) {
    try {
      // Call API to acknowledge alert
      const response = await fetch(`http://localhost:8081/api/alerts/acknowledge/${alertId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          acknowledged_by: 'user'
        })
      })

      if (response.ok) {
        // Remove from local history
        alertHistory.value = alertHistory.value.filter(a => a.alert_id !== alertId)
        console.log('Alert acknowledged:', alertId)
      }
    } catch (error) {
      console.error('Error acknowledging alert:', error)
    }
  }

  /**
   * Get feature value as formatted string
   * @param {string} key - Feature key
   * @returns {string} Formatted value
   */
  function formatFeature(key) {
    const value = latestFeatures[key]
    return value !== undefined ? value.toFixed(4) : '--'
  }

  return {
    // State
    isConnected,
    currentSensor,
    latestFeatures,
    alertHistory,
    isStreaming,
    connectionStatus,
    signalBuffer,
    featureBuffer,

    // Computed
    hasAlerts,
    latestAlert,
    featureCount,

    // Actions
    connect,
    disconnect,
    updateFeatures,
    addAlert,
    clearBuffers,
    acknowledgeAlert,
    formatFeature
  }
})
