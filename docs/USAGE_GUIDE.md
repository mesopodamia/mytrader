# AI Trader 使用文档

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Trader 系统                            │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API服务层 (FastAPI)                      │   │
│  │  - 雪球网API                                          │   │
│  │  - AI交易API                                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                             │                                │
│  ┌──────────────────────────┼─────────────────────────────┐  │
│  │                          │                             │  │
│  │  ┌────────────────┐  ┌───▼────────────────┐          │  │
│  │  │  雪球适配器     │  │   AI交易引擎        │          │  │
│  │  │  (XueqiuAdapter)│  │   (AITradingEngine)│         │  │
│  │  └────────────────┘  └────────────────────┘          │  │
│  │              │              │                         │  │
│  │  ┌───────────▼──────────┐  │  ┌─────────────────────┐ │  │
│  │  │   数据采集Agent       │  │  │   调度系统           │ │  │
│  │  │   (DataCollection)    │  │  │   (Scheduler)       │ │  │
│  │  └──────────────────────┘  │  └─────────────────────┘ │  │
│  │              │              │                         │  │
│  │  ┌───────────▼──────────┐  │                         │  │
│  │  │   分析Agent           │  │                         │  │
│  │  │   - 技术分析          │  │                         │  │
│  │  │   - 基本面分析        │  │                         │  │
│  │  └──────────────────────┘  │                         │  │
│  │              │              │                         │  │
│  │  ┌───────────▼──────────┐  │                         │  │
│  │  │   决策Agent           │  │                         │  │
│  │  │   (DecisionAgent)     │  │                         │  │
│  │  └──────────────────────┘  │                         │  │
│  │              │              │                         │  │
│  │  ┌───────────▼──────────┐  │  ┌─────────────────────┐ │  │
│  │  │   风险管理模块        │  │  │   回测模块           │ │  │
│  │  │   (RiskManager)       │  │  │   (Backtester)      │ │  │
│  │  └──────────────────────┘  │  └─────────────────────┘ │  │
│  └────────────────────────────┴───────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              数据存储层                                │   │
│  │  - SQLite (本地数据库)                                │   │
│  │  - 内存缓存                                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件：

```env
# 数据配置
DATA_DB_URL=sqlite:///./ai_trader.db

# 雪球网配置
XUEQIU_USERNAME=your_username
XUEQIU_PASSWORD=your_password

# API服务配置
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/ai_trader.log

# 交易配置
INITIAL_CAPITAL=1000000.0
MAX_POSITION_RATIO=0.2
DAILY_LOSS_LIMIT=0.02
TRADING_FREQUENCY_LIMIT=10
```

### 3. 运行系统

```bash
# 启动API服务
python main.py

# 或使用uvicorn
uvicorn ai_trader.api.main:app --host 0.0.0.0 --port 8000
```

## 核心功能

### 1. 数据采集Agent

自动采集股票的实时行情、历史数据和基本面信息。

```python
from ai_trader.core.agents.data import DataCollectionAgent

agent = DataCollectionAgent()
result = await agent.execute({
    "stock_codes": ["000001", "600519", "000858"]
})
```

### 2. 技术分析Agent

计算技术指标（MA、MACD、RSI等）并生成交易信号。

```python
from ai_trader.core.agents.analysis import TechnicalAnalysisAgent

agent = TechnicalAnalysisAgent()
result = await agent.execute({
    "historical_data": {...}
})
```

### 3. 基本面分析Agent

分析财务指标（PE、PB、ROE等）并评估估值水平。

```python
from ai_trader.core.agents.analysis import FundamentalAnalysisAgent

agent = FundamentalAnalysisAgent()
result = await agent.execute({
    "stock_info": {...}
})
```

### 4. 决策Agent

综合技术面和基本面分析，生成买卖决策。

```python
from ai_trader.core.agents.decision import DecisionAgent

agent = DecisionAgent()
result = await agent.execute({
    "technical_analysis": {...},
    "fundamental_analysis": {...}
})
```

### 5. AI交易引擎

协调所有Agent运行完整交易流程。

```python
from ai_trader.core.engine import AITradingEngine

engine = AITradingEngine()
result = await engine.run_pipeline(["000001", "600519"])
```

### 6. 调度系统

定时执行交易流程。

```python
from ai_trader.core.scheduler import TradingScheduler

scheduler = TradingScheduler()
scheduler.start()  # 启动调度器

# 手动运行一次
result = await scheduler.run_once(["000001"])
```

### 7. 风险管理

检查交易风险限制。

```python
from ai_trader.core.risk_manager import RiskManager

manager = RiskManager()
allowed = manager.check_all(
    stock_code="000001",
    new_position=0.1,
    potential_loss=0.02
)
```

### 8. 回测系统

验证交易策略。

```python
from ai_trader.core.backtester import Backtester

backtester = Backtester(initial_capital=1000000)
result = backtester.run_backtest(
    stock_data={...},
    signals={...}
)
```

## API接口

### 雪球网API (`/api/v1/xueqiu/`)

- `POST /login` - 登录
- `POST /portfolio` - 创建组合
- `GET /portfolio/{id}` - 获取组合信息
- `GET /portfolio/{id}/positions` - 查询持仓
- `POST /order` - 下单
- `POST /order/{id}/cancel` - 撤单
- `GET /quotes` - 实时行情
- `GET /history/{code}` - 历史数据
- `GET /stock/{code}` - 股票信息

### AI交易API (`/api/v1/ai/`)

- `GET /status` - 系统状态
- `POST /analyze` - 分析股票
- `POST /trade` - 执行交易
- `GET /pipeline` - 运行完整流程
- `POST /start` - 启动调度器
- `POST /stop` - 停止调度器

## 配置说明

### 交易参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| INITIAL_CAPITAL | 1000000.0 | 初始资金 |
| MAX_POSITION_RATIO | 0.2 | 单股最大持仓比例 |
| DAILY_LOSS_LIMIT | 0.02 | 单日最大亏损限制 |
| TRADING_FREQUENCY_LIMIT | 10 | 每日最大交易次数 |

### 调度计划

- **早盘分析**：每天 8:30
- **盘中分析**：每天 9:00-15:00 每小时
- **收盘总结**：每天 15:30

## 项目结构

```
ai_trader/
├── api/              # API服务层
│   ├── main.py       # FastAPI应用
│   └── routers/      # 路由
│       ├── xueqiu.py
│       └── ai_trading.py
├── core/             # 核心模块
│   ├── agents/       # Agent
│   │   ├── base.py
│   │   ├── data.py
│   │   ├── analysis.py
│   │   └── decision.py
│   ├── engine.py     # 交易引擎
│   ├── scheduler.py  # 调度系统
│   ├── risk_manager.py
│   └── backtester.py
├── adapters/         # 数据适配器
│   └── xueqiu.py
└── utils/            # 工具模块
    └── config.py
```

## 注意事项

1. **雪球网登录**：需要配置有效的雪球网账号密码
2. **API限制**：雪球网有API调用频率限制，请合理设置调度计划
3. **风险控制**：建议先使用模拟组合测试，再考虑实盘
4. **数据存储**：所有数据存储在SQLite数据库中
5. **日志监控**：定期查看日志文件，监控系统运行状态

## 常见问题

### Q: 如何添加自定义股票？
A: 修改 `ai_trader/core/engine.py` 中的 `stock_list` 配置

### Q: 如何调整分析参数？
A: 修改 `ai_trader/core/agents/analysis.py` 中的指标计算逻辑

### Q: 如何自定义决策规则？
A: 修改 `ai_trader/core/agents/decision.py` 中的评分和决策逻辑

## 下一步计划

- [ ] 集成本地LLM（Ollama）进行智能分析
- [ ] 添加更多技术指标和分析方法
- [ ] 实现策略回测优化
- [ ] 添加邮件/微信通知
- [ ] 实现多策略组合
- [ ] 添加实盘交易支持

## 许可证

MIT License
