<template>
  <div class="stock-categories">
    <el-page-header 
      title="股票分类" 
      content="按行业板块查看股票"
    />

    <el-row :gutter="16">
      <el-col :lg="8">
        <el-card class="industry-list" shadow="hover">
          <template #header>
            <span class="card-title">行业板块</span>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="20" animated />
          </div>
          <div v-else-if="industries.length > 0" class="industry-content">
            <el-tree
              :data="industries"
              :props="industryProps"
              @node-click="handleIndustryClick"
              node-key="code"
              :default-expand-all="false"
            />
          </div>
          <div v-else class="empty-state">
            <el-empty description="无法获取行业板块" />
          </div>
        </el-card>
      </el-col>

      <el-col :lg="16">
        <el-card class="stock-list-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">{{ selectedIndustry ? selectedIndustry.name : '选择行业' }}</span>
              <el-button 
                v-if="selectedStocks.length > 0"
                type="primary" 
                size="small"
                @click="batchAddToWatchlist"
              >
                <el-icon><StarFilled /></el-icon>
                批量添加到自选股 ({{ selectedStocks.length }})
              </el-button>
            </div>
          </template>
          <div v-if="industryLoading" class="loading-container">
            <el-skeleton :rows="15" animated />
          </div>
          <div v-else-if="industryStocks.length > 0" class="stock-content">
            <el-table 
              :data="industryStocks" 
              style="width: 100%"
              @selection-change="handleStockSelectionChange"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="code" label="股票代码" width="120">
                <template #default="scope">
                  <el-link @click="navigateToDetail(scope.row.code)">{{ scope.row.code }}</el-link>
                </template>
              </el-table-column>
              <el-table-column prop="name" label="股票名称" width="180">
                <template #default="scope">
                  <el-link @click="navigateToDetail(scope.row.code)">{{ scope.row.name }}</el-link>
                </template>
              </el-table-column>
              <el-table-column prop="current" label="当前价格" width="100" align="right" />
              <el-table-column prop="change" label="涨跌幅" width="100" align="right">
                <template #default="scope">
                  <span 
                    :class="{
                      'rise': scope.row.change > 0,
                      'fall': scope.row.change < 0
                    }"
                  >
                    {{ scope.row.change }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="scope">
                  <el-button 
                    type="primary" 
                    size="small"
                    @click="addToWatchlist(scope.row)"
                  >
                    <el-icon><StarFilled /></el-icon>
                    添加
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div v-else class="empty-state">
            <el-empty 
              :description="selectedIndustry ? '该行业暂无股票' : '请选择一个行业'"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useWatchlistStore } from '@/stores/watchlist'

const router = useRouter()
const watchlistStore = useWatchlistStore()

const loading = ref(true)
const industryLoading = ref(false)
const industries = ref<any[]>([])
const industryStocks = ref<any[]>([])
const selectedIndustry = ref<any>(null)
const selectedStocks = ref<any[]>([])

// 行业树的属性
const industryProps = {
  children: 'children',
  label: 'name'
}

// 获取行业板块列表
const fetchIndustries = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/xueqiu/industries')
    if (response.data.status === 'success') {
      industries.value = response.data.data
    }
  } catch (error) {
    console.error('获取行业板块失败:', error)
    ElMessage.error('获取行业板块失败')
  } finally {
    loading.value = false
  }
}

// 获取行业股票列表
const fetchIndustryStocks = async (industryCode: string) => {
  industryLoading.value = true
  try {
    const response = await axios.get(`/api/v1/xueqiu/industry/${industryCode}/stocks`)
    if (response.data.status === 'success') {
      industryStocks.value = response.data.data
    }
  } catch (error) {
    console.error('获取行业股票失败:', error)
    ElMessage.error('获取行业股票失败')
  } finally {
    industryLoading.value = false
  }
}

// 处理行业点击
const handleIndustryClick = (industry: any) => {
  selectedIndustry.value = industry
  selectedStocks.value = []
  if (industry.code) {
    fetchIndustryStocks(industry.code)
  } else {
    industryStocks.value = []
  }
}

// 处理股票选择变化
const handleStockSelectionChange = (val: any[]) => {
  selectedStocks.value = val
}

// 添加股票到自选股
const addToWatchlist = async (stock: any) => {
  try {
    await watchlistStore.addStock(stock.code, stock.name)
    ElMessage.success('添加成功')
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

// 批量添加到自选股
const batchAddToWatchlist = async () => {
  if (selectedStocks.value.length === 0) return

  try {
    for (const stock of selectedStocks.value) {
      await watchlistStore.addStock(stock.code, stock.name)
    }
    ElMessage.success(`成功添加 ${selectedStocks.value.length} 只股票到自选股`)
    // 清空选择
    selectedStocks.value = []
  } catch (error) {
    ElMessage.error('批量添加失败')
  }
}

// 跳转到股票详情页面
const navigateToDetail = (stockCode: string) => {
  router.push(`/stock/${stockCode}`)
}

// 初始化
onMounted(async () => {
  await fetchIndustries()
  // 获取自选股列表
  await watchlistStore.fetchWatchlist()
})
</script>

<style scoped>
.stock-categories {
  padding-bottom: 24px;
}

.industry-list {
  height: calc(100vh - 200px);
  overflow: auto;
}

.stock-list-card {
  min-height: calc(100vh - 200px);
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

.industry-content {
  padding: 10px 0;
}

.stock-content {
  padding: 10px 0;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}

.rise {
  color: #f56c6c;
}

.fall {
  color: #67c23a;
}
</style>
