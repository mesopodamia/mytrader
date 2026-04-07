<template>
  <div class="alert-view">
    <el-page-header 
      title="股票预警" 
      content="设置价格、涨跌幅等预警条件"
    />

    <el-card class="alert-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">预警列表</span>
          <el-button type="primary" size="small" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建预警
          </el-button>
        </div>
      </template>
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      <div v-else-if="alerts.length > 0" class="alert-list">
        <el-table :data="alerts" style="width: 100%">
          <el-table-column prop="stock_code" label="股票代码" width="120" />
          <el-table-column prop="stock_name" label="股票名称" width="180" />
          <el-table-column label="预警类型" width="120">
            <template #default="scope">
              <el-tag :type="getAlertTypeTag(scope.row.alert_type)">
                {{ getAlertTypeText(scope.row.alert_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="预警条件" width="180">
            <template #default="scope">
              {{ scope.row.condition }} {{ scope.row.target_value }}
              {{ getAlertUnit(scope.row.alert_type) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-switch 
                v-model="scope.row.is_active" 
                @change="handleStatusChange(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="triggered_at" label="触发时间" width="180">
            <template #default="scope">
              {{ scope.row.triggered_at ? formatDate(scope.row.triggered_at) : '未触发' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button 
                type="danger" 
                size="small" 
                @click="deleteAlert(scope.row.id)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-else class="empty-state">
        <el-empty description="暂无预警" />
      </div>
    </el-card>

    <!-- 创建预警对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建预警"
      width="450px"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createFormRules"
        label-width="80px"
      >
        <el-form-item label="股票" prop="stock_code">
          <StockSearch 
            v-model="createForm.stock_name"
            @select="handleStockSelect"
          />
        </el-form-item>
        <el-form-item label="股票代码" prop="stock_code">
          <el-input 
            v-model="createForm.stock_code" 
            placeholder="请输入股票代码"
            readonly
          />
        </el-form-item>
        <el-form-item label="预警类型" prop="alert_type">
          <el-select v-model="createForm.alert_type" placeholder="请选择预警类型">
            <el-option label="价格" value="price" />
            <el-option label="涨跌幅" value="change" />
            <el-option label="成交量" value="volume" />
          </el-select>
        </el-form-item>
        <el-form-item label="条件" prop="condition">
          <el-select v-model="createForm.condition" placeholder="请选择条件">
            <el-option label="大于" value=">" />
            <el-option label="小于" value="<" />
            <el-option label="大于等于" value=">=" />
            <el-option label="小于等于" value="<=" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标值" prop="target_value">
          <el-input 
            v-model="createForm.target_value" 
            placeholder="请输入目标值"
            type="number"
            :step="0.01"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createAlert">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import axios from 'axios'
import { StockSearch } from '@/components'

// 状态
const loading = ref(true)
const alerts = ref<any[]>([])

// 对话框状态
const showCreateDialog = ref(false)

// 表单引用
const createFormRef = ref<FormInstance>()

// 创建预警表单
const createForm = reactive({
  stock_code: '',
  stock_name: '',
  alert_type: 'price',
  condition: '>',
  target_value: 0
})

// 表单验证规则
const createFormRules = reactive<FormRules>({
  stock_code: [
    { required: true, message: '请选择股票', trigger: 'blur' }
  ],
  alert_type: [
    { required: true, message: '请选择预警类型', trigger: 'blur' }
  ],
  condition: [
    { required: true, message: '请选择条件', trigger: 'blur' }
  ],
  target_value: [
    { required: true, message: '请输入目标值', trigger: 'blur' },
    { type: 'number', message: '请输入有效的数值', trigger: 'blur' }
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

// 获取预警类型文本
const getAlertTypeText = (type: string) => {
  const typeMap = {
    price: '价格',
    change: '涨跌幅',
    volume: '成交量'
  }
  return typeMap[type] || type
}

// 获取预警类型标签
const getAlertTypeTag = (type: string) => {
  const tagMap = {
    price: 'primary',
    change: 'success',
    volume: 'warning'
  }
  return tagMap[type] || 'info'
}

// 获取预警单位
const getAlertUnit = (type: string) => {
  const unitMap = {
    price: '元',
    change: '%',
    volume: '手'
  }
  return unitMap[type] || ''
}

// 获取预警列表
const fetchAlerts = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/alert')
    alerts.value = response.data
  } catch (error) {
    console.error('获取预警列表失败:', error)
    ElMessage.error('获取预警列表失败')
  } finally {
    loading.value = false
  }
}

// 处理股票选择
const handleStockSelect = (stock: any) => {
  createForm.stock_code = stock.code
  createForm.stock_name = stock.name
}

// 创建预警
const createAlert = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await axios.post('/api/v1/alert', createForm)
        ElMessage.success('预警创建成功')
        showCreateDialog.value = false
        // 重置表单
        createForm.stock_code = ''
        createForm.stock_name = ''
        createForm.alert_type = 'price'
        createForm.condition = '>'
        createForm.target_value = 0
        // 重新获取预警列表
        await fetchAlerts()
      } catch (error) {
        ElMessage.error('预警创建失败')
      }
    }
  })
}

// 处理预警状态变更
const handleStatusChange = async (alert: any) => {
  try {
    await axios.put(`/api/v1/alert/${alert.id}`, { is_active: alert.is_active })
    ElMessage.success('预警状态更新成功')
  } catch (error) {
    console.error('更新预警状态失败:', error)
    ElMessage.error('更新预警状态失败')
    // 恢复原来的状态
    alert.is_active = !alert.is_active
  }
}

// 删除预警
const deleteAlert = async (alertId: number) => {
  try {
    await axios.delete(`/api/v1/alert/${alertId}`)
    ElMessage.success('预警删除成功')
    // 重新获取预警列表
    await fetchAlerts()
  } catch (error) {
    ElMessage.error('预警删除失败')
  }
}

// 初始化
onMounted(async () => {
  await fetchAlerts()
})
</script>

<style scoped>
.alert-view {
  padding-bottom: 24px;
}

.alert-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.loading-container {
  padding: 20px 0;
}

.alert-list {
  margin-top: 10px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}
</style>
