<template>
  <div class="stock-detail">
    <el-page-header 
      :title="stockInfo.name || '股票详情'" 
      :content="stockInfo.code || '股票代码'"
      @back="$router.back"
    />

    <el-row :gutter="16" class="stock-info-section">
      <el-col :lg="12">
        <el-card class="stock-basic-info" shadow="hover">
          <template #header>
            <span class="card-title">基本信息</span>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="10" animated />
          </div>
          <div v-else-if="stockInfo" class="info-content">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="股票代码">{{ stockInfo.code }}</el-descriptions-item>
              <el-descriptions-item label="股票名称">{{ stockInfo.name }}</el-descriptions-item>
              <el-descriptions-item label="市场">{{ stockInfo.market }}</el-descriptions-item>
              <el-descriptions-item label="行业">{{ stockInfo.industry || '未知' }}</el-descriptions-item>
              <el-descriptions-item label="当前价格">{{ stockInfo.current || '--' }}</el-descriptions-item>
              <el-descriptions-item label="涨跌幅">{{ stockInfo.change || '--' }}</el-descriptions-item>
              <el-descriptions-item label="成交量">{{ stockInfo.volume || '--' }}</el-descriptions-item>
              <el-descriptions-item label="市值">{{ stockInfo.market_cap || '--' }}</el-descriptions-item>
            </el-descriptions>
            <div class="action-buttons">
              <el-button 
                type="primary" 
                :icon="isInWatchlist ? 'Star' : 'StarFilled'"
                @click="toggleWatchlist"
              >
                {{ isInWatchlist ? '从自选股移除' : '添加到自选股' }}
              </el-button>
            </div>
          </div>
          <div v-else class="empty-state">
            <el-empty description="无法获取股票信息" />
          </div>
        </el-card>
      </el-col>

      <el-col :lg="12">
        <el-card class="stock-chart" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">K线图</span>
              <el-select v-model="chartPeriod" size="small" style="width: 100px;">
                <el-option label="日K" value="1day" />
                <el-option label="周K" value="1week" />
                <el-option label="月K" value="1month" />
              </el-select>
            </div>
          </template>
          <div v-if="chartLoading" class="loading-container">
            <el-skeleton :rows="8" animated />
          </div>
          <div v-else class="chart-container">
            <div ref="chartRef" class="kline-chart"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="stock-history-section">
      <el-col :lg="24">
        <el-card class="stock-history" shadow="hover">
          <template #header>
            <span class="card-title">历史数据</span>
          </template>
          <div v-if="historyLoading" class="loading-container">
            <el-skeleton :rows="15" animated />
          </div>
          <div v-else-if="historicalData.length > 0" class="history-content">
            <el-table :data="historicalData" style="width: 100%">
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="open" label="开盘价" width="100" align="right" />
              <el-table-column prop="high" label="最高价" width="100" align="right" />
              <el-table-column prop="low" label="最低价" width="100" align="right" />
              <el-table-column prop="close" label="收盘价" width="100" align="right" />
              <el-table-column prop="volume" label="成交量" width="120" align="right" />
            </el-table>
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="10"
              layout="prev, pager, next"
              :total="historicalData.length"
              style="margin-top: 20px; text-align: right"
            />
          </div>
          <div v-else class="empty-state">
            <el-empty description="无法获取历史数据" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'
import { useWatchlistStore } from '@/stores/watchlist'

const route = useRoute()
const watchlistStore = useWatchlistStore()

const stockCode = computed(() => route.params.code as string)

const loading = ref(true)
const chartLoading = ref(true)
const historyLoading = ref(true)
const stockInfo = ref<any>(null)
const historicalData = ref<any[]>([])
const chartPeriod = ref('1day')
const currentPage = ref(1)
const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

// 计算属性：是否在自选股中
const isInWatchlist = computed(() => {
  return watchlistStore.watchlist.some(stock => stock.stock_code === stockCode.value)
})

// 获取股票基本信息
const fetchStockInfo = async () => {
  loading.value = true
  try {
    const response = await axios.get(`/api/v1/xueqiu/stock/${stockCode.value}`)
    if (response.data.status === 'success') {
      stockInfo.value = response.data.data
    }
  } catch (error) {
    console.error('获取股票信息失败:', error)
    ElMessage.error('获取股票信息失败')
  } finally {
    loading.value = false
  }
}

// 获取历史数据
const fetchHistoricalData = async () => {
  historyLoading.value = true
  try {
    const response = await axios.get(`/api/v1/xueqiu/history/${stockCode.value}`, {
      params: {
        period: chartPeriod.value,
        count: 100
      }
    })
    if (response.data.status === 'success') {
      // 处理历史数据
      const data = response.data.data
      historicalData.value = data.map((item: any) => ({
        date: new Date(item[0]).toLocaleDateString(),
        open: item[1],
        high: item[2],
        low: item[3],
        close: item[4],
        volume: item[5]
      }))
    }
  } catch (error) {
    console.error('获取历史数据失败:', error)
    ElMessage.error('获取历史数据失败')
  } finally {
    historyLoading.value = false
  }
}

// 切换自选股状态
const toggleWatchlist = async () => {
  try {
    if (isInWatchlist.value) {
      await watchlistStore.removeStock(stockCode.value)
      ElMessage.success('已从自选股移除')
    } else {
      await watchlistStore.addStock(stockCode.value, stockInfo.value.name)
      ElMessage.success('已添加到自选股')
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

// 监听周期变化
const handlePeriodChange = () => {
  fetchHistoricalData()
}

// 初始化ECharts实例
const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    // 监听窗口大小变化
    window.addEventListener('resize', handleResize)
  }
}

// 处理窗口大小变化
const handleResize = () => {
  chartInstance?.resize()
}

// 绘制K线图
const drawKlineChart = () => {
  if (!chartInstance || historicalData.value.length === 0) return

  // 准备K线数据
  const klineData = historicalData.value.map(item => [
    item.date,
    item.open,
    item.close,
    item.low,
    item.high,
    item.volume
  ])

  // 配置项
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['K线', '成交量']
    },
    grid: [
      {
        left: '3%',
        right: '3%',
        height: '60%'
      },
      {
        left: '3%',
        right: '3%',
        top: '70%',
        height: '20%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: klineData.map(item => item[0]),
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#8392A5' } },
        splitLine: { show: false }
      },
      {
        type: 'category',
        gridIndex: 1,
        data: klineData.map(item => item[0]),
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#8392A5' } },
        axisLabel: { show: false },
        splitLine: { show: false }
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData.map(item => [item[1], item[2], item[3], item[4]]),
        itemStyle: {
          color: '#f56c6c',
          color0: '#67c23a',
          borderColor: '#f56c6c',
          borderColor0: '#67c23a'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: klineData.map(item => item[5])
      }
    ]
  }

  // 设置配置项
  chartInstance.setOption(option)
}

// 销毁图表实例
const destroyChart = () => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', handleResize)
}

// 初始化
onMounted(async () => {
  // 获取自选股列表
  await watchlistStore.fetchWatchlist()
  // 获取股票信息
  await fetchStockInfo()
  // 获取历史数据
  await fetchHistoricalData()
  // 初始化图表
  initChart()
  // 绘制K线图
  drawKlineChart()
  // 图表加载完成
  chartLoading.value = false
})

// 组件卸载时销毁图表
onUnmounted(() => {
  destroyChart()
})
</script>

<style scoped>
.stock-detail {
  padding-bottom: 24px;
}

.stock-info-section {
  margin: 24px 0;
}

.stock-basic-info,
.stock-chart {
  margin-bottom: 16px;
}

.stock-history-section {
  margin-top: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container {
  padding: 20px 0;
}

.info-content {
  padding: 10px 0;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

.chart-container {
  height: 350px;
  position: relative;
}

.kline-chart {
  width: 100%;
  height: 100%;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.history-content {
  padding: 10px 0;
}
</style>
