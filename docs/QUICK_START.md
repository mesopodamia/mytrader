# AI Trader - 快速开始指南

## 项目概述

AI Trader 是一个基于 OpenClaw 和雪球网模拟组合的AI自动交易系统。

## 已完成的功能

- ✅ 项目结构搭建
- ✅ 雪球网API适配器实现
- ✅ REST API接口
- ✅ 配置管理系统
- ✅ 基础测试脚本

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 雪球网配置（必需）
XUEQIU_USERNAME=your_username
XUEQIU_PASSWORD=your_password

# OpenClaw配置（后续使用）
OPENCLAW_API_KEY=your_api_key
```

### 3. 验证安装

```bash
python verify_setup.py
```

### 4. 启动API服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口列表

### 雪球网接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/xueqiu/health` | 健康检查 |
| POST | `/api/v1/xueqiu/login` | 登录雪球网 |
| POST | `/api/v1/xueqiu/portfolio` | 创建模拟组合 |
| GET | `/api/v1/xueqiu/portfolio/{id}` | 获取组合信息 |
| GET | `/api/v1/xueqiu/portfolio/{id}/positions` | 获取持仓 |
| POST | `/api/v1/xueqiu/order` | 下单 |
| POST | `/api/v1/xueqiu/order/{portfolio_id}/{order_id}/cancel` | 撤单 |
| GET | `/api/v1/xueqiu/quotes` | 获取实时行情 |
| GET | `/api/v1/xueqiu/history/{stock_code}` | 获取历史数据 |
| GET | `/api/v1/xueqiu/stock/{stock_code}` | 获取股票信息 |

## 使用示例

### Python代码示例

```python
from ai_trader.adapters import XueqiuAdapter

# 创建适配器
adapter = XueqiuAdapter(username="your_name", password="your_pass")

# 登录
adapter.login()

# 获取实时行情
quotes = adapter.get_realtime_quotes(["000001", "000002", "600000"])
print(quotes)

# 创建模拟组合
portfolio = adapter.create_portfolio(
    name="AI Trader测试组合",
    initial_capital=1000000.0
)

# 下单
order = adapter.place_order(
    portfolio_id="your_portfolio_id",
    stock_code="000001",
    action="buy",
    quantity=1000
)
```

### cURL示例

```bash
# 获取实时行情
curl "http://localhost:8000/api/v1/xueqiu/quotes?stock_codes=000001,000002"

# 获取历史数据
curl "http://localhost:8000/api/v1/xueqiu/history/000001?period=1day&count=30"
```

## 项目结构

```
mytrader/
├── ai_trader/
│   ├── api/              # API服务层
│   │   ├── main.py      # FastAPI主入口
│   │   └── routers/     # API路由
│   │       └── xueqiu.py # 雪球网API路由 ✅
│   ├── adapters/         # 数据适配器
│   │   └── xueqiu.py    # 雪球网适配器 ✅
│   ├── core/             # 核心引擎（待实现）
│   ├── models/           # AI模型（待实现）
│   ├── analysis/         # 分析模块（待实现）
│   └── utils/            # 工具模块
│       └── config.py    # 配置管理 ✅
├── tests/                # 测试代码
├── docs/                 # 文档
├── main.py              # 主程序入口 ✅
├── requirements.txt     # Python依赖 ✅
├── .env.example        # 环境变量模板 ✅
├── verify_setup.py     # 验证脚本 ✅
└── README.md           # 项目说明 ✅
```

## 下一步开发计划

- [ ] AI决策引擎（集成OpenClaw）
- [ ] 交易执行引擎
- [ ] 风险管理模块
- [ ] 实时监控面板
- [ ] 回测验证系统

## 常见问题

### 1. 如何获取雪球网账号？

访问 https://xueqiu.com 注册账号。

### 2. 股票代码格式？

- 上海证券交易所：6位代码（如：600000）
- 深圳证券交易所：6位代码（如：000001）
- 适配器会自动添加SH/SZ前缀

### 3. 模拟组合初始资金是多少？

默认100万元，可以在创建时自定义。

## 技术支持

如有问题，请查看：
- 完整技术方案：`docs/AI_TRADER_PLAN.md`
- API文档：http://localhost:8000/docs
