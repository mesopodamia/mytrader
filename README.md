# AI Trader - 智能量化交易平台

基于 OpenClaw 和雪球网模拟组合的AI自动交易系统，采用公有云后台管理界面风格。

## 功能特点

- 🤖 **AI智能分析** - 基于OpenClaw的多维度股票分析
- 📊 **舆情监控** - 实时资本市场舆情分析
- 💰 **模拟交易** - 雪球网模拟组合自动交易
- 📈 **数据可视化** - 丰富的图表和数据分析
- 🔐 **用户认证** - 完整的用户登录和权限管理
- 🎨 **云管理风格** - 类似公有云的后台管理界面

## 技术栈

### 后端
- **FastAPI** - 高性能Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **JWT** - 用户认证
- **雪球网API** - 股票数据获取和交易

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Element Plus** - UI组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理

## 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
```

### 2. 检查 Ollama 安装状态

本项目使用 Ollama 进行 AI 处理，优化后的下载脚本已移除自动下载功能：

```bash
# Windows 用户 (PowerShell):
./download.ps1

# Unix/Linux/macOS 用户:
./download.sh

# 或手动检查 Ollama 是否已安装:
ollama --version
```

**注**: 如果 Ollama 未安装，请手动下载安装：
- **macOS**: https://ollama.com/download/mac  
- **Linux**: https://ollama.com/download/linux  
- **Windows**: https://ollama.com/download/windows

### 3. 初始化数据库

```bash
python init_db.py
```

默认账号：
- 管理员：`admin` / `admin123`
- 测试用户：`test` / `test123`

### 4. 构建前端

```bash
cd frontend
npm run build
```

### 5. 启动服务

```bash
python main.py
```

访问 http://localhost:8000

## 项目结构

```
mytrader/
├── ai_trader/              # 后端主应用
│   ├── api/               # API服务
│   │   ├── main.py       # FastAPI入口
│   │   └── routers/      # API路由
│   │       ├── auth.py   # 认证路由
│   │       └── xueqiu.py # 雪球网路由
│   ├── adapters/         # 数据适配器
│   │   └── xueqiu.py     # 雪球网适配器
│   ├── database/         # 数据库
│   │   ├── models.py     # 数据模型
│   │   └── operations.py # 数据库操作
│   ├── core/             # 核心引擎（待实现）
│   ├── models/           # AI模型（待实现）
│   ├── analysis/         # 分析模块（待实现）
│   └── utils/            # 工具模块
├── frontend/              # 前端项目
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── layouts/      # 布局组件
│   │   ├── router/       # 路由配置
│   │   └── stores/       # 状态管理
│   └── dist/             # 构建输出
├── tests/                 # 测试代码
├── docs/                  # 文档
├── main.py               # 启动入口
├── init_db.py            # 数据库初始化
└── requirements.txt      # Python依赖
```

## 功能模块

### 已完成 ✅

1. **用户认证系统**
   - 用户注册/登录
   - JWT Token认证
   - 权限管理（管理员/普通用户）
   - 个人资料管理

2. **控制台 Dashboard**
   - 资产统计卡片
   - 收益走势图（占位）
   - 持仓分布图（占位）
   - 最近交易记录

3. **舆情分析**
   - 情绪指标展示
   - 舆情趋势图（占位）
   - 热门话题列表

4. **模拟交易**
   - 自选股列表
   - 行情K线图（占位）
   - 交易面板（买入/卖出）
   - AI分析建议（占位）

5. **投资组合**
   - 持仓明细
   - 盈亏统计
   - 行业分布（占位）
   - 收益走势（占位）

6. **数据分析**
   - 策略回测（占位）
   - 绩效分析（占位）
   - 风险分析（占位）

7. **系统设置**
   - 个人资料修改
   - 密码修改
   - 账户信息展示

### 开发中 🚧

- AI决策引擎集成（OpenClaw）
- 实时行情数据对接
- 自动交易执行
- 策略回测系统

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发计划

- [x] 项目架构搭建
- [x] 用户认证系统
- [x] 前端界面开发
- [x] 雪球网API对接
- [ ] AI引擎集成
- [ ] 实时数据推送
- [ ] 自动交易执行
- [ ] 策略回测系统

## 贡献

欢迎提交Issue和Pull Request。

## 许可证

MIT License
