<template>
  <div class="category-view">
    <el-page-header 
      title="自定义分类" 
      content="管理您的股票分类"
    />

    <el-row :gutter="16">
      <!-- 分类列表 -->
      <el-col :lg="8">
        <el-card class="category-list" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">分类列表</span>
              <el-button type="primary" size="small" @click="showCreateDialog = true">
                <el-icon><Plus /></el-icon>
                新建分类
              </el-button>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="10" animated />
          </div>
          <div v-else-if="categories.length > 0" class="category-content">
            <el-tree
              :data="categories"
              :props="categoryProps"
              @node-click="handleCategoryClick"
              node-key="id"
              default-expand-all
            />
          </div>
          <div v-else class="empty-state">
            <el-empty description="暂无分类" />
          </div>
        </el-card>
      </el-col>

      <!-- 分类详情 -->
      <el-col :lg="16">
        <el-card class="category-detail" shadow="hover" v-if="selectedCategory">
          <template #header>
            <div class="card-header">
              <span class="card-title">{{ selectedCategory.name }}</span>
              <div>
                <el-button type="primary" size="small" style="margin-right: 8px" @click="showEditDialog = true">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="confirmDeleteCategory">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </div>
          </template>
          <div class="category-info">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="分类名称">{{ selectedCategory.name }}</el-descriptions-item>
              <el-descriptions-item label="描述">{{ selectedCategory.description || '无' }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDate(selectedCategory.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="股票数量">{{ categoryStocks.length }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 股票列表 -->
          <div class="stock-section">
            <div class="section-header">
              <span class="section-title">分类股票</span>
              <el-button type="primary" size="small" @click="showAddStockDialog = true">
                <el-icon><Plus /></el-icon>
                添加股票
              </el-button>
            </div>
            <div v-if="stockLoading" class="loading-container">
              <el-skeleton :rows="8" animated />
            </div>
            <div v-else-if="categoryStocks.length > 0" class="stock-list">
              <el-table :data="categoryStocks" style="width: 100%">
                <el-table-column prop="stock_code" label="股票代码" width="120" />
                <el-table-column prop="stock_name" label="股票名称" width="180" />
                <el-table-column prop="added_at" label="添加时间" width="180">
                  <template #default="scope">
                    {{ formatDate(scope.row.added_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="120" fixed="right">
                  <template #default="scope">
                    <el-button 
                      type="danger" 
                      size="small" 
                      @click="removeStockFromCategory(scope.row.stock_code)"
                    >
                      <el-icon><Delete /></el-icon>
                      移除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div v-else class="empty-state">
              <el-empty description="暂无股票" />
            </div>
          </div>
        </el-card>
        <el-card v-else class="category-detail-placeholder" shadow="hover">
          <el-empty description="请选择一个分类" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建分类对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建分类"
      width="400px"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createFormRules"
        label-width="80px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入分类名称" maxlength="50" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="createForm.description" 
            placeholder="请输入分类描述" 
            maxlength="200"
            type="textarea"
            rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createCategory">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑分类对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑分类"
      width="400px"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editFormRules"
        label-width="80px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入分类名称" maxlength="50" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="editForm.description" 
            placeholder="请输入分类描述" 
            maxlength="200"
            type="textarea"
            rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateCategory">保存</el-button>
      </template>
    </el-dialog>

    <!-- 添加股票对话框 -->
    <el-dialog
      v-model="showAddStockDialog"
      title="添加股票到分类"
      width="400px"
    >
      <el-form
        ref="addStockFormRef"
        :model="addStockForm"
        :rules="addStockFormRules"
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
            readonly
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddStockDialog = false">取消</el-button>
        <el-button type="primary" @click="addStockToCategory">添加</el-button>
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
const stockLoading = ref(false)
const categories = ref<any[]>([])
const categoryStocks = ref<any[]>([])
const selectedCategory = ref<any>(null)

// 对话框状态
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showAddStockDialog = ref(false)

// 表单引用
const createFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const addStockFormRef = ref<FormInstance>()

// 创建分类表单
const createForm = reactive({
  name: '',
  description: ''
})

// 编辑分类表单
const editForm = reactive({
  name: '',
  description: ''
})

// 添加股票表单
const addStockForm = reactive({
  stock_code: '',
  stock_name: ''
})

// 表单验证规则
const createFormRules = reactive<FormRules>({
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 50, message: '分类名称长度在 1 到 50 个字符', trigger: 'blur' }
  ]
})

const editFormRules = reactive<FormRules>({
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 50, message: '分类名称长度在 1 到 50 个字符', trigger: 'blur' }
  ]
})

const addStockFormRules = reactive<FormRules>({
  stock_code: [
    { required: true, message: '请选择股票', trigger: 'blur' }
  ]
})

// 分类树属性
const categoryProps = {
  children: 'children',
  label: 'name'
}

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

// 获取分类列表
const fetchCategories = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/category')
    categories.value = response.data
  } catch (error) {
    console.error('获取分类列表失败:', error)
    ElMessage.error('获取分类列表失败')
  } finally {
    loading.value = false
  }
}

// 获取分类股票
const fetchCategoryStocks = async (categoryId: number) => {
  stockLoading.value = true
  try {
    const response = await axios.get(`/api/v1/category/${categoryId}/stocks`)
    categoryStocks.value = response.data
  } catch (error) {
    console.error('获取分类股票失败:', error)
    ElMessage.error('获取分类股票失败')
  } finally {
    stockLoading.value = false
  }
}

// 处理分类点击
const handleCategoryClick = (category: any) => {
  selectedCategory.value = category
  fetchCategoryStocks(category.id)
}

// 创建分类
const createCategory = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await axios.post('/api/v1/category', createForm)
        ElMessage.success('分类创建成功')
        showCreateDialog.value = false
        // 重置表单
        createForm.name = ''
        createForm.description = ''
        // 重新获取分类列表
        await fetchCategories()
      } catch (error) {
        ElMessage.error('分类创建失败')
      }
    }
  })
}

// 打开编辑对话框
const openEditDialog = () => {
  if (selectedCategory.value) {
    editForm.name = selectedCategory.value.name
    editForm.description = selectedCategory.value.description
    showEditDialog.value = true
  }
}

// 更新分类
const updateCategory = async () => {
  if (!editFormRef.value || !selectedCategory.value) return

  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await axios.put(`/api/v1/category/${selectedCategory.value.id}`, editForm)
        ElMessage.success('分类更新成功')
        showEditDialog.value = false
        // 重新获取分类列表
        await fetchCategories()
        // 重新选择当前分类
        selectedCategory.value = categories.value.find(cat => cat.id === selectedCategory.value.id)
      } catch (error) {
        ElMessage.error('分类更新失败')
      }
    }
  })
}

// 确认删除分类
const confirmDeleteCategory = () => {
  if (!selectedCategory.value) return

  ElMessageBox.confirm(
    `确定要删除分类 "${selectedCategory.value.name}" 吗？删除后分类下的所有股票也会被移除。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.delete(`/api/v1/category/${selectedCategory.value.id}`)
      ElMessage.success('分类删除成功')
      // 重置状态
      selectedCategory.value = null
      categoryStocks.value = []
      // 重新获取分类列表
      await fetchCategories()
    } catch (error) {
      ElMessage.error('分类删除失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 处理股票选择
const handleStockSelect = (stock: any) => {
  addStockForm.stock_code = stock.code
  addStockForm.stock_name = stock.name
}

// 添加股票到分类
const addStockToCategory = async () => {
  if (!addStockFormRef.value || !selectedCategory.value) return

  await addStockFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await axios.post(`/api/v1/category/${selectedCategory.value.id}/stocks`, addStockForm)
        ElMessage.success('股票添加成功')
        showAddStockDialog.value = false
        // 重置表单
        addStockForm.stock_code = ''
        addStockForm.stock_name = ''
        // 重新获取分类股票
        await fetchCategoryStocks(selectedCategory.value.id)
      } catch (error) {
        ElMessage.error('股票添加失败')
      }
    }
  })
}

// 从分类中移除股票
const removeStockFromCategory = async (stockCode: string) => {
  if (!selectedCategory.value) return

  try {
    await axios.delete(`/api/v1/category/${selectedCategory.value.id}/stocks/${stockCode}`)
    ElMessage.success('股票移除成功')
    // 重新获取分类股票
    await fetchCategoryStocks(selectedCategory.value.id)
  } catch (error) {
    ElMessage.error('股票移除失败')
  }
}

// 初始化
onMounted(async () => {
  await fetchCategories()
})
</script>

<style scoped>
.category-view {
  padding-bottom: 24px;
}

.category-list {
  height: calc(100vh - 200px);
  overflow: auto;
}

.category-detail {
  min-height: calc(100vh - 200px);
}

.category-detail-placeholder {
  height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
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

.category-content {
  padding: 10px 0;
}

.stock-section {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.stock-list {
  margin-top: 10px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.category-info {
  margin-bottom: 20px;
}
</style>
