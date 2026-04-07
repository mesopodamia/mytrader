<template>
  <div class="sentiment-page">
    <el-page-header title="舆情分析" content="资本市场舆情监控与分析" />

    <el-row :gutter="16" class="sentiment-stats">
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover">
          <div class="sentiment-item">
            <div class="sentiment-icon positive">
              <el-icon :size="32"><ArrowUp /></el-icon>
            </div>
            <div class="sentiment-info">
              <div class="sentiment-value">68%</div>
              <div class="sentiment-label">看涨情绪</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover">
          <div class="sentiment-item">
            <div class="sentiment-icon neutral">
              <el-icon :size="32"><Minus /></el-icon>
            </div>
            <div class="sentiment-info">
              <div class="sentiment-value">24%</div>
              <div class="sentiment-label">中性情绪</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover">
          <div class="sentiment-item">
            <div class="sentiment-icon negative">
              <el-icon :size="32"><ArrowDown /></el-icon>
            </div>
            <div class="sentiment-info">
              <div class="sentiment-value">8%</div>
              <div class="sentiment-label">看跌情绪</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="sentiment-chart" shadow="never">
      <template #header>
        <div class="card-header">
          <span>舆情趋势分析</span>
          <el-select v-model="selectedStock" placeholder="选择股票" style="width: 200px;">
            <el-option label="全部股票" value="all" />
            <el-option 
              v-for="stock in watchlist" 
              :key="stock.stock_code" 
              :label="`${stock.stock_name} (${stock.stock_code})`" 
              :value="stock.stock_code" 
            />
          </el-select>
        </div>
      </template>
      <div class="chart-placeholder">
        <el-empty description="舆情趋势图（Demo）">
          <el-icon :size="64" color="#dcdfe6"><DataLine /></el-icon>
          <p>功能开发中...</p>
        </el-empty>
      </div>
    </el-card>

    <el-card class="hot-topics" shadow="never">
      <template #header>
        <div class="card-header">
          <span>热门话题</span>
          <el-button type="primary" link>刷新</el-button>
        </div>
      </template>
      <el-table :data="hotTopics" style="width: 100%">
        <el-table-column prop="rank" label="排名" width="80">
          <template #default="{ $index }">
            <el-tag :type="$index < 3 ? 'danger' : 'info'">{{ $index + 1 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="topic" label="话题" />
        <el-table-column prop="heat" label="热度">
          <template #default="{ row }">
            <el-progress :percentage="row.heat" :color="heatColors" />
          </template>
        </el-table-column>
        <el-table-column prop="sentiment" label="情绪" width="100">
          <template #default="{ row }">
            <el-tag :type="row.sentiment === 'positive' ? 'success' : row.sentiment === 'negative' ? 'danger' : 'info'">
              {{ row.sentimentText }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useWatchlistStore } from '@/stores/watchlist'

const watchlistStore = useWatchlistStore()
const selectedStock = ref('all')

const heatColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 }
]

const hotTopics = ref([
  { topic: '新能源汽车销量创新高', heat: 98, sentiment: 'positive', sentimentText: '看涨' },
  { topic: '央行降准释放流动性', heat: 95, sentiment: 'positive', sentimentText: '看涨' },
  { topic: '科技股回调风险', heat: 87, sentiment: 'negative', sentimentText: '看跌' },
  { topic: '消费复苏预期增强', heat: 82, sentiment: 'positive', sentimentText: '看涨' },
  { topic: '海外市场波动影响', heat: 76, sentiment: 'neutral', sentimentText: '中性' },
  { topic: 'AI概念股持续火热', heat: 71, sentiment: 'positive', sentimentText: '看涨' },
  { topic: '房地产政策调整', heat: 65, sentiment: 'neutral', sentimentText: '中性' },
  { topic: '医药板块估值修复', heat: 58, sentiment: 'positive', sentimentText: '看涨' }
])

// 计算属性：自选股票列表
const watchlist = computed(() => watchlistStore.watchlist)

// 获取自选股票列表
onMounted(async () => {
  await watchlistStore.fetchWatchlist()
})
</script>

<style scoped>
.sentiment-page {
  padding-bottom: 24px;
}

.sentiment-stats {
  margin: 24px 0;
}

.sentiment-item {
  display: flex;
  align-items: center;
  padding: 8px;
}

.sentiment-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}

.sentiment-icon.positive {
  background: #f6ffed;
  color: #52c41a;
}

.sentiment-icon.neutral {
  background: #f5f5f5;
  color: #999;
}

.sentiment-icon.negative {
  background: #fff1f0;
  color: #f5222d;
}

.sentiment-value {
  font-size: 32px;
  font-weight: 600;
  color: #333;
}

.sentiment-label {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}

.sentiment-chart {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-placeholder {
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hot-topics {
  margin-top: 16px;
}
</style>
