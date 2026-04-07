/**
 * WebSocket 服务
 * 
 * 用于管理 WebSocket 连接和实时数据推送
 */

class WebSocketService {
  private socket: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000 // 1秒
  private listeners: Map<string, ((data: any) => void)[]> = new Map()
  private isConnected = false

  // 连接 WebSocket
  connect() {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return
    }

    const wsUrl = `ws://${window.location.host}/ws`
    this.socket = new WebSocket(wsUrl)

    this.socket.onopen = () => {
      console.log('WebSocket 连接成功')
      this.isConnected = true
      this.reconnectAttempts = 0
      this.emit('connected')
    }

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.emit('message', data)
        if (data.type) {
          this.emit(data.type, data)
        }
      } catch (error) {
        console.error('WebSocket 消息解析失败:', error)
      }
    }

    this.socket.onclose = () => {
      console.log('WebSocket 连接关闭')
      this.isConnected = false
      this.emit('disconnected')
      this.attemptReconnect()
    }

    this.socket.onerror = (error) => {
      console.error('WebSocket 错误:', error)
      this.emit('error', error)
    }
  }

  // 断开 WebSocket 连接
  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
      this.isConnected = false
    }
  }

  // 发送消息
  send(message: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message))
      return true
    }
    return false
  }

  // 尝试重连
  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`尝试重连 WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      setTimeout(() => {
        this.connect()
      }, this.reconnectDelay * this.reconnectAttempts)
    } else {
      console.error('WebSocket 重连失败，已达到最大尝试次数')
    }
  }

  // 注册事件监听器
  on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event)?.push(callback)
  }

  // 移除事件监听器
  off(event: string, callback: (data: any) => void) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      if (callbacks) {
        const index = callbacks.indexOf(callback)
        if (index > -1) {
          callbacks.splice(index, 1)
        }
      }
    }
  }

  // 触发事件
  private emit(event: string, data?: any) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      callbacks?.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`WebSocket 事件处理错误 (${event}):`, error)
        }
      })
    }
  }

  // 获取连接状态
  getConnectionStatus() {
    return this.isConnected
  }
}

// 导出单例
const webSocketService = new WebSocketService()
export default webSocketService
