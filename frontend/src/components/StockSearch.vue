<template>
  <div class="stock-search">
    <el-autocomplete
      v-model="searchKeyword"
      :fetch-suggestions="searchStocks"
      placeholder="搜索股票代码/名称"
      @select="handleSelect"
      :trigger-on-focus="false"
      class="search-input"
    >
      <template #prefix>
        <el-icon class="el-input__icon"><Search /></el-icon>
      </template>
      <template #suffix>
        <el-icon v-if="loading" class="el-input__icon"><Loading /></el-icon>
      </template>
      <template #default="{ item }">
        <div class="stock-item">
          <div class="stock-info">
            <div class="stock-name">{{ item.name }}</div>
            <div class="stock-code">{{ item.code }}</div>
          </div>
          <div class="stock-market">{{ item.market }}</div>
        </div>
      </template>
    </el-autocomplete>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps({
  value: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:value', 'select'])

const searchKeyword = ref(props.value)
const loading = ref(false)

// 搜索股票
const searchStocks = async (query: string, callback: (data: any[]) => void) => {
  if (!query || query.length < 1) {
    callback([])
    return
  }

  loading.value = true
  try {
    const response = await axios.get('/api/v1/stock/search', {
      params: {
        keyword: query,
        limit: 10
      }
    })

    if (response.data.status === 'success') {
      const stocks = response.data.data.map((stock: any) => {
        // 处理数据结构
        let code = stock.code || stock.f12 || stock.symbol
        let name = stock.name || stock.f14 || stock.name_cn
        let market = stock.market || stock.f13 || ''

        return {
          value: code,
          code: code,
          name: name,
          market: market
        }
      })
      callback(stocks)
    } else {
      callback([])
    }
  } catch (error) {
    console.error('搜索股票失败:', error)
    callback([])
  } finally {
    loading.value = false
  }
}

// 处理选择
const handleSelect = (item: any) => {
  searchKeyword.value = item.name
  emit('update:value', item.name)
  emit('select', item)
}
</script>

<style scoped>
.stock-search {
  width: 100%;
}

.search-input {
  width: 100%;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.stock-info {
  flex: 1;
}

.stock-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.stock-code {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.stock-market {
  font-size: 12px;
  color: #666;
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
}
</style>
