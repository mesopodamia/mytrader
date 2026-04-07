<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-cards">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: #e6f7ff; color: #1890ff;">
            <el-icon :size="24"><Wallet /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">¥1,234,567</div>
            <div class="stat-label">总资产</div>
          </div>
          <div class="stat-trend up">
            <el-icon><ArrowUp /></el-icon>
            <span>+12.5%</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: #f6ffed; color: #52c41a;">
            <el-icon :size="24"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">+8.32%</div>
            <div class="stat-label">今日收益</div>
          </div>
          <div class="stat-trend up">
            <el-icon><ArrowUp /></el-icon>
            <span>+2.1%</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: #fff7e6; color: #fa8c16;">
            <el-icon :size="24"><Collection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">15</div>
            <div class="stat-label">持仓数量</div>
          </div>
          <div class="stat-trend">
            <span>持平</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: #f9f0ff; color: #722ed1;">
            <el-icon :size="24"><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">89.5</div>
            <div class="stat-label">AI评分</div>
          </div>
          <div class="stat-trend up">
            <el-icon><ArrowUp /></el-icon>
            <span>+5.3</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :lg="16">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>资产走势</span>
              <el-radio-group v-model="timeRange" size="small">
                <el-radio-button label="day">日</el-radio-button>
                <el-radio-button label="week">周</el-radio-button>
                <el-radio-button label="month">月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-placeholder">
            <el-empty description="资产走势图（Demo）">
              <el-icon :size="64" color="#dcdfe6"><TrendCharts /></el-icon>
            </el-empty>
          </div>
        </el-card>
      </el-col>
      <el-col :lg="8">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>持仓分布</span>
            </div>
          </template>
          <div class="chart-placeholder">
            <el-empty description="持仓分布图（Demo）">
              <el-icon :size="64" color="#dcdfe6"><PieChart /></el-icon>
            </el-empty>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近交易 -->
    <el-card class="recent-trades" shadow="never">
      <template #header>
        <div class="card-header">
          <span>最近交易</span>
          <el-button type="primary" link>查看全部</el-button>
        </div>
      </template>
      <el-table :data="recentTrades" style="width: 100%">
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="stock" label="股票" />
        <el-table-column prop="action" label="操作">
          <template #default="{ row }">
            <el-tag :type="row.action === '买入' ? 'danger' : 'success'">
              {{ row.action }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" />
        <el-table-column prop="quantity" label="数量" />
        <el-table-column prop="amount" label="金额" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === '成交' ? 'success' : 'warning'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const timeRange = ref('day')

const recentTrades = ref([
  { time: '2024-01-15 14:30:25', stock: '贵州茅台 (600519)', action: '买入', price: '¥1,680.00', quantity: 100, amount: '¥168,000.00', status: '成交' },
  { time: '2024-01-15 10:15:30', stock: '腾讯控股 (00700)', action: '卖出', price: '¥298.60', quantity: 500, amount: '¥149,300.00', status: '成交' },
  { time: '2024-01-14 14:20:15', stock: '宁德时代 (300750)', action: '买入', price: '¥158.50', quantity: 200, amount: '¥31,700.00', status: '成交' },
  { time: '2024-01-14 09:45:00', stock: '比亚迪 (002594)', action: '买入', price: '¥198.20', quantity: 150, amount: '¥29,730.00', status: '委托中' },
  { time: '2024-01-13 13:50:20', stock: '阿里巴巴 (09988)', action: '卖出', price: '¥72.35', quantity: 1000, amount: '¥72,350.00', status: '成交' }
])
</script>

<style scoped>
.dashboard {
  padding-bottom: 24px;
}

.stat-cards {
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 8px;
  margin-bottom: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #999;
}

.stat-trend {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-trend.up {
  color: #52c41a;
}

.stat-trend.down {
  color: #f5222d;
}

.chart-row {
  margin-bottom: 16px;
}

.chart-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recent-trades {
  margin-top: 16px;
}
</style>
