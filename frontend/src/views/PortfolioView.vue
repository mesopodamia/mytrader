<template>
  <div class="portfolio-page">
    <el-page-header title="投资组合" content="管理您的模拟投资组合" />

    <el-row :gutter="16" class="portfolio-stats">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">总资产</div>
            <div class="stat-value">¥1,234,567.89</div>
            <div class="stat-change up">
              <el-icon><ArrowUp /></el-icon>
              <span>+¥34,567.89 (+2.88%)</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">累计收益</div>
            <div class="stat-value">¥234,567.89</div>
            <div class="stat-change up">
              <el-icon><ArrowUp /></el-icon>
              <span>+23.46%</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">今日收益</div>
            <div class="stat-value">¥12,345.67</div>
            <div class="stat-change up">
              <el-icon><ArrowUp /></el-icon>
              <span>+1.01%</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-label">夏普比率</div>
            <div class="stat-value">1.85</div>
            <div class="stat-change">
              <span>风险调整后收益</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="positions-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>持仓明细</span>
          <el-button type="primary" :icon="Refresh" @click="refreshPositions">刷新</el-button>
        </div>
      </template>
      <el-table :data="positions" style="width: 100%" v-loading="loading">
        <el-table-column prop="stock" label="股票">
          <template #default="{ row }">
            <div class="stock-info">
              <div class="stock-name">{{ row.name }}</div>
              <div class="stock-code">{{ row.code }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="持仓数量" align="right" />
        <el-table-column prop="avgCost" label="成本价" align="right" />
        <el-table-column prop="currentPrice" label="现价" align="right" />
        <el-table-column prop="marketValue" label="市值" align="right" />
        <el-table-column prop="profit" label="盈亏" align="right">
          <template #default="{ row }">
            <span :class="row.profit >= 0 ? 'up' : 'down'">
              {{ row.profit >= 0 ? '+' : '' }}¥{{ row.profit.toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profitRate" label="盈亏率" align="right">
          <template #default="{ row }">
            <span :class="row.profitRate >= 0 ? 'up' : 'down'">
              {{ row.profitRate >= 0 ? '+' : '' }}{{ row.profitRate }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="ratio" label="占比" align="right">
          <template #default="{ row }">
            <el-progress :percentage="row.ratio" :color="customColors" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default>
            <el-button type="primary" link size="small">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row :gutter="16" class="bottom-row">
      <el-col :lg="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>行业分布</span>
            </div>
          </template>
          <div class="chart-placeholder">
            <el-empty description="行业分布图（Demo）">
              <el-icon :size="64" color="#dcdfe6"><PieChart /></el-icon>
            </el-empty>
          </div>
        </el-card>
      </el-col>
      <el-col :lg="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>收益走势</span>
            </div>
          </template>
          <div class="chart-placeholder">
            <el-empty description="收益走势图（Demo）">
              <el-icon :size="64" color="#dcdfe6"><TrendCharts /></el-icon>
            </el-empty>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)

const customColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 }
]

const positions = ref([
  { name: '贵州茅台', code: '600519', quantity: 100, avgCost: '1,650.00', currentPrice: '1,680.00', marketValue: '168,000.00', profit: 3000, profitRate: 1.82, ratio: 13.6 },
  { name: '腾讯控股', code: '00700', quantity: 500, avgCost: '295.00', currentPrice: '298.60', marketValue: '149,300.00', profit: 1800, profitRate: 1.22, ratio: 12.1 },
  { name: '宁德时代', code: '300750', quantity: 800, avgCost: '155.00', currentPrice: '158.50', marketValue: '126,800.00', profit: 2800, profitRate: 2.26, ratio: 10.3 },
  { name: '比亚迪', code: '002594', quantity: 600, avgCost: '192.00', currentPrice: '198.20', marketValue: '118,920.00', profit: 3720, profitRate: 3.23, ratio: 9.6 },
  { name: '阿里巴巴', code: '09988', quantity: 1500, avgCost: '70.50', currentPrice: '72.35', marketValue: '108,525.00', profit: 2775, profitRate: 2.62, ratio: 8.8 },
  { name: '美团', code: '03690', quantity: 1200, avgCost: '86.50', currentPrice: '88.90', marketValue: '106,680.00', profit: 2880, profitRate: 2.78, ratio: 8.6 },
  { name: '五粮液', code: '000858', quantity: 400, avgCost: '145.00', currentPrice: '148.50', marketValue: '59,400.00', profit: 1400, profitRate: 2.41, ratio: 4.8 },
  { name: '中国平安', code: '601318', quantity: 1000, avgCost: '42.50', currentPrice: '43.80', marketValue: '43,800.00', profit: 1300, profitRate: 3.06, ratio: 3.5 }
])

const refreshPositions = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('刷新成功')
  }, 1000)
}
</script>

<style scoped>
.portfolio-page {
  padding-bottom: 24px;
}

.portfolio-stats {
  margin: 24px 0;
}

.stat-item {
  text-align: center;
  padding: 8px;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.stat-change {
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.stat-change.up {
  color: #f5222d;
}

.stat-change.down {
  color: #52c41a;
}

.positions-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-info .stock-name {
  font-weight: 500;
  color: #333;
}

.stock-info .stock-code {
  font-size: 12px;
  color: #999;
}

.up {
  color: #f5222d;
}

.down {
  color: #52c41a;
}

.bottom-row {
  margin-top: 16px;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
