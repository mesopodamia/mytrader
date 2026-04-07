<template>
  <div class="analysis-page">
    <el-page-header title="数据分析" content="深度数据分析与回测验证" />

    <el-alert
      title="功能开发中"
      description="数据分析模块正在开发中，将提供完整的数据分析、策略回测和绩效评估功能。"
      type="info"
      show-icon
      :closable="false"
      style="margin: 24px 0;"
    />

    <el-row :gutter="16">
      <el-col :lg="8">
        <el-card shadow="hover">
          <template #header>
            <div class="feature-header">
              <el-icon :size="32" color="#409EFF"><DataAnalysis /></el-icon>
              <span>策略回测</span>
            </div>
          </template>
          <p class="feature-desc">基于历史数据验证交易策略的有效性，支持多种回测指标和可视化分析。</p>
          <el-button type="primary" disabled>即将推出</el-button>
        </el-card>
      </el-col>
      <el-col :lg="8">
        <el-card shadow="hover">
          <template #header>
            <div class="feature-header">
              <el-icon :size="32" color="#67C23A"><TrendCharts /></el-icon>
              <span>绩效分析</span>
            </div>
          </template>
          <p class="feature-desc">全面的投资组合绩效评估，包括收益率、风险指标、最大回撤等多维度分析。</p>
          <el-button type="success" disabled>即将推出</el-button>
        </el-card>
      </el-col>
      <el-col :lg="8">
        <el-card shadow="hover">
          <template #header>
            <div class="feature-header">
              <el-icon :size="32" color="#E6A23C"><Histogram /></el-icon>
              <span>风险分析</span>
            </div>
          </template>
          <p class="feature-desc">专业的风险评估工具，帮助识别和管理投资组合中的各类风险。</p>
          <el-button type="warning" disabled>即将推出</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="demo-chart" shadow="never">
      <template #header>
        <div class="card-header">
          <span>收益分析（Demo）</span>
        </div>
      </template>
      <div class="chart-placeholder">
        <el-empty description="数据分析图表">
          <el-icon :size="64" color="#dcdfe6"><DataLine /></el-icon>
          <p>功能开发中...</p>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.analysis-page {
  padding-bottom: 24px;
}

.feature-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
}

.feature-desc {
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}

.demo-chart {
  margin-top: 24px;
}

.card-header {
  font-weight: 600;
}

.chart-placeholder {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
