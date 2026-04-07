<template>
  <div class="stocks-view">
    <el-card class="stock-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">自选股票</span>
          <el-button type="primary" size="small" @click="showAddStockDialog = true">
            <el-icon><Plus /></el-icon>
            添加股票
          </el-button>
        </div>
      </template>

      <!-- 股票列表 -->
      <div v-if="watchlist.length > 0" class="stock-list">
        <div class="batch-actions" v-if="selectedStocks.length > 0">
          <el-button 
            type="danger" 
            size="small" 
            @click="batchRemoveStocks"
            :loading="loading"
          >
            <el-icon><Delete /></el-icon>
            批量移除 ({{ selectedStocks.length }})
          </el-button>
        </div>
        <el-table 
          :data="watchlist" 
          style="width: 100%"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="stock_code" label="股票代码" width="120">
            <template #default="scope">
              <el-link @click="navigateToDetail(scope.row.stock_code)">{{ scope.row.stock_code }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="stock_name" label="股票名称" width="180">
            <template #default="scope">
              <el-link @click="navigateToDetail(scope.row.stock_code)">{{ scope.row.stock_name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column label="当前价格" width="100" align="right">
            <template #default="scope">
              <span v-if="stockQuotes[scope.row.stock_code]">
                {{ stockQuotes[scope.row.stock_code].current }}
              </span>
              <span v-else>--</span>
            </template>
          </el-table-column>
          <el-table-column label="涨跌幅" width="100" align="right">
            <template #default="scope">
              <span 
                v-if="stockQuotes[scope.row.stock_code]"
                :class="{
                  'rise': stockQuotes[scope.row.stock_code].change > 0,
                  'fall': stockQuotes[scope.row.stock_code].change < 0
                }"
              >
                {{ stockQuotes[scope.row.stock_code].change }}%
              </span>
              <span v-else>--</span>
            </template>
          </el-table-column>
          <el-table-column prop="added_at" label="添加时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.added_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                style="margin-right: 8px"
                @click="navigateToDetail(scope.row.stock_code)"
              >
                <el-icon><InfoFilled /></el-icon>
                详情
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                @click="removeStock(scope.row.stock_code)"
                :loading="loading"
              >
                <el-icon><Delete /></el-icon>
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <el-empty 
          description="暂无自选股票"
          :image-size="200"
        >
          <template #description>
            <span class="empty-text">暂无自选股票</span>
          </template>
          <el-button type="primary" @click="showAddStockDialog = true">
            添加股票
          </el-button>
        </el-empty>
      </div>
    </el-card>

    <!-- 添加股票对话框 -->
    <el-dialog
      v-model="showAddStockDialog"
      title="添加自选股票"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="addStockFormRef"
        :model="addStockForm"
        :rules="addStockRules"
        label-width="80px"
      >
        <el-form-item label="股票" prop="stock_code">
          <StockSearch 
            v-model="addStockForm.stock_name"
            @select="handleStockSelect"
          />
        </el-form-item>
        <el-form-item label="股票代码" prop="stock_code">
          <el-input 
            v-model="addStockForm.stock_code" 
            placeholder="请输入股票代码"
            maxlength="20"
            readonly
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddStockDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="loading"
          @click="addStock"
        >
          添加
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useWatchlistStore } from '@/stores/watchlist'
import { StockSearch } from '@/components'

const watchlistStore = useWatchlistStore()
const router = useRouter()
const showAddStockDialog = ref(false)
const addStockFormRef = ref<FormInstance>()
const loading = ref(false)
const stockQuotes = ref<Record<string, any>>({})
const selectedStocks = ref<any[]>([])

const addStockForm = reactive({
  stock_code: '',
  stock_name: ''
})

const addStockRules = reactive<FormRules>({
  stock_code: [
    { required: true, message: '请选择股票', trigger: 'blur' }
  ]
})

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 处理股票选择
const handleStockSelect = (stock: any) => {
  addStockForm.stock_code = stock.code
  addStockForm.stock_name = stock.name
}

// 跳转到股票详情页面
const navigateToDetail = (stockCode: string) => {
  router.push(`/stock/${stockCode}`)
}

// 处理选择变化
const handleSelectionChange = (val: any[]) => {
  selectedStocks.value = val
}

// 批量移除股票
const batchRemoveStocks = async () => {
  if (selectedStocks.value.length === 0) return

  loading.value = true
  try {
    // 逐个删除选中的股票
    for (const stock of selectedStocks.value) {
      await watchlistStore.removeStock(stock.stock_code)
    }
    ElMessage.success(`成功移除 ${selectedStocks.value.length} 只股票`)
    // 清空选择
    selectedStocks.value = []
    // 重新获取实时行情
    await fetchRealtimeQuotes()
  } catch (error) {
    ElMessage.error('批量移除失败')
  } finally {
    loading.value = false
  }
}

// 获取实时行情
const fetchRealtimeQuotes = async () => {
  if (watchlist.value.length === 0) return

  try {
    const stockCodes = watchlist.value.map(stock => stock.stock_code)
    const quotes = await watchlistStore.getRealtimeQuotes(stockCodes)
    
    // 处理行情数据
    const processedQuotes: Record<string, any> = {}
    for (const [key, value] of Object.entries(quotes)) {
      const stockCode = key.replace(/^SH|^SZ/, '') // 移除市场前缀
      processedQuotes[stockCode] = {
        current: value.current,
        change: value.change
      }
    }
    
    stockQuotes.value = processedQuotes
  } catch (error) {
    console.error('获取实时行情失败:', error)
  }
}

// 添加股票
const addStock = async () => {
  if (!addStockFormRef.value) return

  await addStockFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await watchlistStore.addStock(addStockForm.stock_code, addStockForm.stock_name)
        ElMessage.success('股票添加成功')
        showAddStockDialog.value = false
        // 清空表单
        addStockForm.stock_code = ''
        addStockForm.stock_name = ''
        // 重新获取实时行情
        await fetchRealtimeQuotes()
      } catch (error) {
        ElMessage.error('股票添加失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// 移除股票
const removeStock = async (stockCode: string) => {
  loading.value = true
  try {
    await watchlistStore.removeStock(stockCode)
    ElMessage.success('股票移除成功')
    // 重新获取实时行情
    await fetchRealtimeQuotes()
  } catch (error) {
    ElMessage.error('股票移除失败')
  } finally {
    loading.value = false
  }
}

// 获取自选股票列表
onMounted(async () => {
  await watchlistStore.fetchWatchlist()
  // 获取实时行情
  await fetchRealtimeQuotes()
  
  // 设置定时更新（每30秒）
  setInterval(fetchRealtimeQuotes, 30000)
})

// 计算属性：自选股票列表
const watchlist = computed(() => watchlistStore.watchlist)
</script>

<script lang="ts">
import { computed } from 'vue'

export default {
  name: 'StocksView'
}
</script>

<style scoped>
.stocks-view {
  padding: 20px 0;
}

.stock-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.stock-list {
  margin-top: 20px;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}

.empty-text {
  font-size: 16px;
  color: #999;
}

.rise {
  color: #f56c6c;
}

.fall {
  color: #67c23a;
}

.batch-actions {
  margin-bottom: 10px;
  text-align: right;
}
</style>
