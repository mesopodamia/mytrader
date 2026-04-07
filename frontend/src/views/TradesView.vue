<template>
  <div class="trades">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>交易记录</span>
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" />
        </div>
      </template>

      <el-table :data="trades" v-loading="loading">
        <el-table-column prop="date" label="时间" width="160" />
        <el-table-column prop="stock_code" label="股票代码" width="100" />
        <el-table-column prop="stock_name" label="股票名称" />
        <el-table-column prop="action" label="操作" width="80">
          <template #default="{ row }">
            <el-tag :type="row.action === 'buy' ? 'success' : 'danger'" size="small">
              {{ row.action === 'buy' ? '买入' : '卖出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="price" label="价格" width="80">
          <template #default="{ row }">
            ¥{{ formatNumber(row.price) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            ¥{{ formatNumber(row.amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="fee" label="手续费" width="100">
          <template #default="{ row }">
            ¥{{ formatNumber(row.fee) }}
          </template>
        </el-table-column>
        <el-table-column prop="pnl" label="盈亏" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.pnl >= 0 ? '#67c23a' : '#f56c6c' }">
              {{ row.pnl ? (row.pnl >= 0 ? '+' : '') + '¥' + formatNumber(row.pnl) : '-' }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const trades = ref([
  { id: 1, date: '2026-03-31 10:30:00', stock_code: '600519', stock_name: '贵州茅台', action: 'buy', quantity: 100, price: 1845.00, amount: 184500.00, fee: 18.45, pnl: null },
  { id: 2, date: '2026-03-31 09:45:00', stock_code: '000858', stock_name: '五粮液', action: 'buy', quantity: 200, price: 157.50, amount: 31500.00, fee: 31.50, pnl: null },
  { id: 3, date: '2026-03-30 14:20:00', stock_code: '601318', stock_name: '中国平安', action: 'sell', quantity: 100, price: 49.20, amount: 4920.00, fee: 4.92, pnl: 500.00 },
  { id: 4, date: '2026-03-30 10:15:00', stock_code: '300750', stock_name: '宁德时代', action: 'buy', quantity: 50, price: 215.00, amount: 10750.00, fee: 10.75, pnl: null },
  { id: 5, date: '2026-03-29 15:30:00', stock_code: '000001', stock_name: '平安银行', action: 'buy', quantity: 1000, price: 12.50, amount: 12500.00, fee: 12.50, pnl: null },
  { id: 6, date: '2026-03-29 10:00:00', stock_code: '600519', stock_name: '贵州茅台', action: 'sell', quantity: 50, price: 1820.00, amount: 9100.00, fee: 9.10, pnl: -1500.00 },
  { id: 7, date: '2026-03-28 14:00:00', stock_code: '601318', stock_name: '中国平安', action: 'buy', quantity: 200, price: 48.50, amount: 9700.00, fee: 9.70, pnl: null },
  { id: 8, date: '2026-03-28 09:30:00', stock_code: '000858', stock_name: '五粮液', action: 'sell', quantity: 100, price: 156.80, amount: 1568.00, fee: 1.57, pnl: 80.00 }
])

const formatNumber = (num: number) => {
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadTrades()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadTrades()
}

const loadTrades = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 500)
}
</script>

<style scoped>
.trades {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>
