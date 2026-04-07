import { defineStore } from 'pinia'
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import webSocketService from '@/services/websocket'

interface WatchlistItem {
  id: number
  stock_code: string
  stock_name: string
  added_at: string
}

const API_BASE_URL = '/api/v1'

export const useWatchlistStore = defineStore('watchlist', () => {
  // State
  const watchlist = ref<WatchlistItem[]>([])
  const loading = ref(false)
  const realtimeQuotes = ref<Record<string, any>>({})
  const wsConnected = ref(false)

  // Actions
  const fetchWatchlist = async () => {
    loading.value = true
    try {
      const response = await axios.get(`${API_BASE_URL}/watchlist`)
      watchlist.value = response.data
    } catch (error) {
      console.error('获取自选股票失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const addStock = async (stockCode: string, stockName: string) => {
    loading.value = true
    try {
      const response = await axios.post(`${API_BASE_URL}/watchlist`, {
        stock_code: stockCode,
        stock_name: stockName
      })
      // 更新本地列表
      await fetchWatchlist()
      return response.data
    } catch (error) {
      console.error('添加股票失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const removeStock = async (stockCode: string) => {
    loading.value = true
    try {
      await axios.delete(`${API_BASE_URL}/watchlist/${stockCode}`)
      // 更新本地列表
      await fetchWatchlist()
    } catch (error) {
      console.error('移除股票失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const checkStock = async (stockCode: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/watchlist/check/${stockCode}`)
      return response.data.is_in_watchlist
    } catch (error) {
      console.error('检查股票失败:', error)
      return false
    }
  }

  // 获取实时行情
  const getRealtimeQuotes = async (stockCodes: string[]): Promise<any> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/xueqiu/quotes`, {
        params: {
          stock_codes: stockCodes.join(',')
        }
      })
      realtimeQuotes.value = response.data.data
      return response.data.data
    } catch (error) {
      console.error('获取实时行情失败:', error)
      throw error
    }
  }

  // 初始化 WebSocket
  const initWebSocket = () => {
    // 连接 WebSocket
    webSocketService.connect()

    // 监听连接状态
    webSocketService.on('connected', () => {
      wsConnected.value = true
      console.log('WebSocket 连接成功')
    })

    webSocketService.on('disconnected', () => {
      wsConnected.value = false
      console.log('WebSocket 连接断开')
    })

    // 监听实时行情数据
    webSocketService.on('realtime_quotes', (data) => {
      if (data.data) {
        realtimeQuotes.value = { ...realtimeQuotes.value, ...data.data }
      }
    })

    // 监听预警触发
    webSocketService.on('alert_triggered', (data) => {
      console.log('预警触发:', data)
      // 可以在这里显示预警通知
    })
  }

  // 发送消息到 WebSocket
  const sendWebSocketMessage = (message: any) => {
    return webSocketService.send(message)
  }

  // 关闭 WebSocket 连接
  const closeWebSocket = () => {
    webSocketService.disconnect()
  }

  // 初始化
  onMounted(() => {
    initWebSocket()
  })

  // 组件卸载时关闭连接
  onUnmounted(() => {
    closeWebSocket()
  })

  return {
    watchlist,
    loading,
    realtimeQuotes,
    wsConnected,
    fetchWatchlist,
    addStock,
    removeStock,
    checkStock,
    getRealtimeQuotes,
    sendWebSocketMessage,
    closeWebSocket
  }
})
