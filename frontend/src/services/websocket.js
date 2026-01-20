/**
 * WebSocket service for real-time data streaming
 *
 * Provides WebSocket connection management with automatic reconnection,
 * event handling, and message parsing for real-time sensor data.
 */

class RealtimeService {
  constructor() {
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 10  // Increased from 5
    this.reconnectDelay = 1000
    this.listeners = new Map()
    this.isConnected = false
    this.manualClose = false  // Track if user intentionally disconnected
  }

  /**
   * Connect to WebSocket for a sensor
   * @param {number} sensorId - Sensor ID to connect to
   */
  connect(sensorId) {
    // Close existing connection if any
    if (this.ws) {
      this.manualClose = true
      this.ws.close()
    }

    const wsUrl = `ws://localhost:8081/ws/realtime/${sensorId}`
    console.log(`Connecting to WebSocket: ${wsUrl}`)

    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log(`WebSocket connected for sensor ${sensorId}`)
      this.isConnected = true
      this.reconnectAttempts = 0
      this.manualClose = false
      this.emit('connected', { sensorId, timestamp: Date.now() })
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)

        // Emit based on message type
        if (message.type) {
          this.emit(message.type, message.data || message)
        } else {
          // For messages without explicit type, emit as 'data'
          this.emit('data', message)
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
        // Emit raw message if JSON parsing fails
        this.emit('raw', event.data)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.emit('error', error)
    }

    this.ws.onclose = (event) => {
      console.log(`WebSocket closed: code=${event.code}, reason=${event.reason}`)
      this.isConnected = false
      this.emit('disconnected', { code: event.code, reason: event.reason })

      // Attempt reconnection if not manually closed and under max attempts
      if (!this.manualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++
        const delay = Math.min(
          this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
          30000  // Max 30 seconds
        )
        console.log(`Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

        setTimeout(() => {
          if (!this.manualClose) {
            this.connect(sensorId)
          }
        }, delay)
      } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached')
        this.emit('reconnect_failed', { attempts: this.reconnectAttempts })
      }
    }
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    this.manualClose = true
    this.reconnectAttempts = this.maxReconnectAttempts  // Prevent reconnection

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.isConnected = false
    console.log('WebSocket disconnected (manual)')
  }

  /**
   * Send message through WebSocket
   * @param {string|object} message - Message to send
   */
  send(message) {
    if (this.ws && this.isConnected) {
      const data = typeof message === 'string' ? message : JSON.stringify(message)
      this.ws.send(data)
    } else {
      console.warn('Cannot send message: WebSocket not connected')
    }
  }

  /**
   * Send ping to keep connection alive
   */
  ping() {
    this.send('ping')
  }

  /**
   * Register event listener
   * @param {string} event - Event name
   * @param {function} callback - Callback function
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  /**
   * Remove event listener
   * @param {string} event - Event name
   * @param {function} callback - Callback function to remove
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  /**
   * Emit event to all listeners
   * @param {string} event - Event name
   * @param {any} data - Event data
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in event handler for '${event}':`, error)
        }
      })
    }
  }

  /**
   * Remove all event listeners
   */
  removeAllListeners() {
    this.listeners.clear()
  }

  /**
   * Get connection status
   * @returns {boolean} Connection status
   */
  getConnectionStatus() {
    return this.isConnected
  }
}

// Export singleton instance
const websocketService = new RealtimeService()

export default websocketService
