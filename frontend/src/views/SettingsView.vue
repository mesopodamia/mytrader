<template>
  <div class="settings-page">
    <el-page-header title="系统设置" content="管理您的账户和系统配置" />

    <el-row :gutter="24" class="settings-content">
      <el-col :lg="16">
        <el-card shadow="never">
          <template #header>
            <span>个人资料</span>
          </template>
          <el-form :model="userForm" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="userForm.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="userForm.email" />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="userForm.fullName" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveProfile">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never" style="margin-top: 24px;">
          <template #header>
            <span>修改密码</span>
          </template>
          <el-form :model="passwordForm" label-width="100px">
            <el-form-item label="当前密码">
              <el-input v-model="passwordForm.oldPassword" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="passwordForm.newPassword" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码">
              <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :lg="8">
        <el-card shadow="never">
          <template #header>
            <span>账户信息</span>
          </template>
          <div class="account-info">
            <div class="info-item">
              <span class="label">用户ID</span>
              <span class="value">{{ userStore.userInfo?.id }}</span>
            </div>
            <div class="info-item">
              <span class="label">角色</span>
              <el-tag :type="userStore.isAdmin ? 'danger' : 'success'">
                {{ userStore.isAdmin ? '管理员' : '普通用户' }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">状态</span>
              <el-tag type="success">正常</el-tag>
            </div>
            <div class="info-item">
              <span class="label">注册时间</span>
              <span class="value">{{ formatDate(userStore.userInfo?.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="label">最后登录</span>
              <span class="value">{{ formatDate(userStore.userInfo?.last_login) }}</span>
            </div>
          </div>
        </el-card>

        <el-card shadow="never" style="margin-top: 24px;">
          <template #header>
            <span>股票数据同步</span>
          </template>
          <div class="stock-sync">
            <el-form :model="syncForm" label-width="120px">
              <el-form-item label="自动同步时间">
                <el-time-picker
                  v-model="syncForm.syncTime"
                  format="HH:mm"
                  value-format="HH:mm"
                  placeholder="选择时间"
                  @change="handleSyncTimeChange"
                />
              </el-form-item>
              <el-form-item label="数据源">
                <el-select v-model="syncSource" placeholder="选择数据源">
                  <el-option label="自动选择（推荐）" value="auto"></el-option>
                  <el-option label="AKShare" value="akshare"></el-option>
                  <el-option label="Baostock" value="baostock"></el-option>
                  <el-option label="必盈API" value="biying"></el-option>
                  <el-option label="内置股票" value="built_in"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="上次同步时间">
                <span class="sync-time">{{ lastSyncTime }}</span>
              </el-form-item>
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="syncStockData" 
                  :loading="syncLoading"
                >
                  手动同步股票数据
                </el-button>
                <el-button @click="loadSyncSettings">刷新设置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>

        <el-card shadow="never" style="margin-top: 24px;">
          <template #header>
            <span>系统信息</span>
          </template>
          <div class="system-info">
            <div class="info-item">
              <span class="label">版本</span>
              <span class="value">v0.1.0</span>
            </div>
            <div class="info-item">
              <span class="label">构建时间</span>
              <span class="value">2024-01-15</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const userStore = useUserStore()

const userForm = ref({
  username: '',
  email: '',
  fullName: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const syncForm = ref({
  syncTime: '01:00'
})

const syncSource = ref('auto')
const syncLoading = ref(false)
const lastSyncTime = ref('-')

onMounted(() => {
  if (userStore.userInfo) {
    userForm.value.username = userStore.userInfo.username
    userForm.value.email = userStore.userInfo.email
    userForm.value.fullName = userStore.userInfo.full_name || ''
  }
  // 加载同步设置
  loadSyncSettings()
})

const formatDate = (date: string | undefined) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const saveProfile = async () => {
  const result = await userStore.updateProfile({
    full_name: userForm.value.fullName,
    email: userForm.value.email
  })

  if (result.success) {
    ElMessage.success('保存成功')
  } else {
    ElMessage.error(result.message)
  }
}

const changePassword = async () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  const result = await userStore.changePassword(
    passwordForm.value.oldPassword,
    passwordForm.value.newPassword
  )

  if (result.success) {
    ElMessage.success('密码修改成功')
    passwordForm.value.oldPassword = ''
    passwordForm.value.newPassword = ''
    passwordForm.value.confirmPassword = ''
  } else {
    ElMessage.error(result.message)
  }
}

const loadSyncSettings = async () => {
  try {
    const response = await fetch('/api/v1/sync/stock/time')
    const data = await response.json()
    if (data.status === 'success') {
      syncForm.value.syncTime = data.data.sync_time
    }
  } catch (error) {
    console.error('加载同步设置失败:', error)
  }
}

const syncStockData = async () => {
  syncLoading.value = true
  try {
    console.log('开始同步股票数据，token:', userStore.token, 'source:', syncSource.value)
    const response = await fetch('/api/v1/sync/stock', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify({ source: syncSource.value })
    })
    console.log('同步请求响应状态:', response.status)
    const data = await response.json()
    console.log('同步请求响应数据:', data)
    if (data.status === 'success') {
      ElMessage.success('股票数据同步成功')
      lastSyncTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss')
    } else {
      ElMessage.error(data.message || '同步失败')
    }
  } catch (error) {
    console.error('同步股票数据失败:', error)
    ElMessage.error('同步失败，请检查网络连接')
  } finally {
    syncLoading.value = false
  }
}

const handleSyncTimeChange = async (time: string) => {
  if (!time) return
  try {
    const response = await fetch('/api/v1/sync/stock/time', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify({ sync_time: time })
    })
    const data = await response.json()
    if (data.status === 'success') {
      ElMessage.success('同步时间设置成功')
    } else {
      ElMessage.error(data.message || '设置失败')
      // 恢复原来的时间
      loadSyncSettings()
    }
  } catch (error) {
    console.error('设置同步时间失败:', error)
    ElMessage.error('设置失败，请检查网络连接')
    // 恢复原来的时间
    loadSyncSettings()
  }
}
</script>

<style scoped>
.settings-page {
  padding-bottom: 24px;
}

.settings-content {
  margin-top: 24px;
}

.account-info,
.system-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.info-item .label {
  color: #999;
}

.info-item .value {
  color: #333;
  font-weight: 500;
}
</style>
