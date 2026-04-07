<template>
  <div class="trading-page">
    <el-page-header title="模拟交易" content="AI驱动的智能股票交易模拟" />

    <el-row :gutter="16" class="trading-layout">
      <!-- 左侧：股票列表 -->
      <el-col :lg="6">
        <el-card class="stock-list" shadow="never">
          <template #header>
            <div class="card-header">
              <span>自选股</span>
              <el-button type="primary" :icon="Plus" circle size="small" @click="$router.push('/stocks')" />
            </div>
          </template>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索股票代码/名称"
            :prefix-icon="Search"
            class="search-input"
          />
          <el-table :data="filteredWatchlist" style="width: 100%" size="small" @row-click="selectStock">
            <el-table-column prop="stock_name" label="股票" min-width="100">
              <template #default="{ row }">
                <div class="stock-name">
                  <div class="name">{{ row.stock_name }}</div>
                  <div class="code">{{ row.stock_code }}</div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="80" align="right">
              <template #default="{ row }">
                <span :class="row.change >= 0 ? 'up' : 'down'">{{ row.price || '--' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="change" label="涨跌幅" width="80" align="right">
              <template #default="{ row }">
                <span :class="row.change >= 0 ? 'up' : 'down'">
                  {{ row.change >= 0 ? '+' : '' }}{{ row.change || '--' }}%
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 中间：行情图表 -->
      <el-col :lg="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="stock-header">
              <div class="stock-info">
                <span class="stock-name">{{ selectedStock.name }}</span>
                <span class="stock-code">{{ selectedStock.code }}</span>
                <el-tag :type="selectedStock.change >= 0 ? 'danger' : 'success'" size="small">
                  {{ selectedStock.change >= 0 ? '涨' : '跌' }}
                </el-tag>
              </div>
              <div class="stock-price">
                <span class="current-price" :class="selectedStock.change >= 0 ? 'up' : 'down'">
                  {{ selectedStock.price }}
                </span>
                <span class="price-change" :class="selectedStock.change >= 0 ? 'up' : 'down'">
                  {{ selectedStock.change >= 0 ? '+' : '' }}{{ selectedStock.change }}%
                </span>
              </div>
            </div>
          </template>
          <div class="chart-placeholder">
            <el-empty description="K线图（Demo）">
              <el-icon :size="64" color="#dcdfe6"><Histogram /></el-icon>
              <p>功能开发中...</p>
            </el-empty>
          </div>
        </el-card>

        <!-- AI分析建议 -->
        <el-card class="ai-analysis" shadow="never">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><MagicStick /></el-icon>
                AI 交易建议
              </span>
              <el-tag type="warning">Beta</el-tag>
            </div>
          </template>
          <div class="analysis-content">
            <el-alert
              title="功能开发中"
              description="AI交易建议功能正在开发中，将基于OpenClaw提供智能交易决策支持。"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：交易面板 -->
      <el-col :lg="6">
        <el-card class="trade-panel" shadow="never">
          <template #header>
            <div class="card-header">
              <span>交易面板</span>
            </div>
          </template>

          <el-tabs v-model="tradeType" type="border-card">
            <el-tab-pane label="买入" name="buy">
              <el-form :model="buyForm" label-width="60px">
                <el-form-item label="价格">
                  <el-input-number v-model="buyForm.price" :precision="2" :step="0.01" style="width: 100%" />
                </el-form-item>
                <el-form-item label="数量">
                  <el-input-number v-model="buyForm.quantity" :min="100" :step="100" style="width: 100%" />
                </el-form-item>
                <el-form-item label="金额">
                  <el-input :model-value="buyAmount" disabled />
                </el-form-item>
                <el-form-item>
                  <el-button type="danger" style="width: 100%" size="large" disabled>
                    买入 (Demo)
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            <el-tab-pane label="卖出" name="sell">
              <el-form :model="sellForm" label-width="60px">
                <el-form-item label="价格">
                  <el-input-number v-model="sellForm.price" :precision="2" :step="0.01" style="width: 100%" />
                </el-form-item>
                <el-form-item label="数量">
                  <el-input-number v-model="sellForm.quantity" :min="100" :step="100" style="width: 100%" />
                </el-form-item>
                <el-form-item label="金额">
                  <el-input :model-value="sellAmount" disabled />
                </el-form-item>
                <el-form-item>
                  <el-button type="success" style="width: 100%" size="large" disabled>
                    卖出 (Demo)
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>

          <div class="account-info">
            <div class="info-item">
              <span>可用资金</span>
              <span class="value">¥{{ account.available }}</span>
            </div>
            <div class="info-item">
              <span>持仓市值</span>
              <span class="value">¥{{ account.positionValue }}</span>
            </div>
            <div class="info-item">
              <span>总资产</span>
              <span class="value">¥{{ account.total }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useWatchlistStore } from '@/stores/watchlist'

const watchlistStore = useWatchlistStore()
const searchKeyword = ref('')
const tradeType = ref('buy')

const buyForm = ref({
  price: 168.50,
  quantity: 100
})

const sellForm = ref({
  price: 168.50,
  quantity: 100
})

const buyAmount = computed(() => {
  return (buyForm.value.price * buyForm.value.quantity).toFixed(2)
})

const sellAmount = computed(() => {
  return (sellForm.value.price * sellForm.value.quantity).toFixed(2)
})

const account = ref({
  available: '856,432.50',
  positionValue: '377,567.50',
  total: '1,234,000.00'
})

const selectedStock = ref({
  name: '贵州茅台',
  code: '600519',
  price: '1,680.00',
  change: 2.35
})

// 计算属性：过滤后的自选股票列表
const filteredWatchlist = computed(() => {
  const keyword = searchKeyword.value.toLowerCase()
  return watchlistStore.watchlist.map(stock => ({
    ...stock,
    price: '--', // 模拟数据，实际应该从API获取
    change: 0 // 模拟数据，实际应该从API获取
  })).filter(stock => 
    stock.stock_code.toLowerCase().includes(keyword) ||
    stock.stock_name.toLowerCase().includes(keyword)
  )
})

// 选择股票
const selectStock = (row: any) => {
  selectedStock.value = {
    name: row.stock_name,
    code: row.stock_code,
    price: row.price || '168.50',
    change: row.change || 0
  }
}

// 获取自选股票列表
onMounted(async () => {
  await watchlistStore.fetchWatchlist()
})
</script>

<style scoped>
.trading-page {
  padding-bottom: 24px;
}

.trading-layout {
  margin-top: 24px;
}

.stock-list {
  margin-bottom: 16px;
}

.search-input {
  margin-bottom: 12px;
}

.stock-name .name {
  font-weight: 500;
  color: #333;
}

.stock-name .code {
  font-size: 12px;
  color: #999;
}

.up {
  color: #f5222d;
}

.down {
  color: #52c41a;
}

.chart-card {
  margin-bottom: 16px;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stock-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.stock-code {
  font-size: 14px;
  color: #999;
}

.stock-price {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.current-price {
  font-size: 28px;
  font-weight: 600;
}

.price-change {
  font-size: 16px;
}

.chart-placeholder {
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-analysis {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.trade-panel {
  margin-bottom: 16px;
}

.account-info {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
}

.info-item .value {
  font-weight: 600;
  color: #333;
}
</style>
