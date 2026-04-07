<template>
  <div class="not-found">
    <div class="not-found-content">
      <el-icon :size="120" color="#dcdfe6"><Warning /></el-icon>
      <h1>404</h1>
      <p>抱歉，您访问的页面不存在</p>
      <el-button type="primary" @click="$router.push('/')">
        返回首页
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}

.not-found-content {
  text-align: center;
}

.not-found-content h1 {
  font-size: 72px;
  font-weight: 600;
  color: #333;
  margin: 24px 0 16px;
}

.not-found-content p {
  font-size: 16px;
  color: #666;
  margin-bottom: 32px;
}
</style>
