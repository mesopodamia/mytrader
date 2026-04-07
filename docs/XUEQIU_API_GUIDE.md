# AI 模拟炒股系统 - 雪球网 API 使用指南

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
# 雪球网配置
XUEQIU_USERNAME=your_username
XUEQIU_PASSWORD=your_password

# OpenClaw配置
OPENCLAW_API_KEY=your_api_key

# 数据库配置
DATA_DB_URL=sqlite:///./ai_trader.db
REDIS_URL=redis://localhost:6379/0
```

### 3. 运行API服务

```bash
python main.py
```

API服务将在 `http://localhost:8000` 启动

### 4. 访问API文档

打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 雪球网 API 使用示例

### Python 代码示例

```python
from ai_trader.adapters import XueqiuAdapter

# 创建适配器实例
adapter = XueqiuAdapter(
    username="your_username",
    password="your_password"
)

# 登录
adapter.login()

# 创建模拟组合
portfolio = adapter.create_portfolio(
    name="AI Trader测试组合",
    initial_capital=1000000.0
)

# 获取实时行情
quotes = adapter.get_realtime_quotes(["000001", "000002", "600000"])
print(quotes)

# 下单
order = adapter.place_order(
    portfolio_id="your_portfolio_id",
    stock_code="000001",
    action="buy",
    quantity=1000,
    price=None  # 市价单
)

# 获取持仓
positions = adapter.get_positions(portfolio_id="your_portfolio_id")
print(positions)

# 获取历史数据
history = adapter.get_historical_data(
    stock_code="000001",
    period="1day",
    count=100
)
print(history)
```

### cURL 示例

#### 获取实时行情

```bash
curl -X GET "http://localhost:8000/api/v1/quotes?codes=000001,000002"
```

#### 下单

```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": "your_portfolio_id",
    "stock_code": "000001",
    "action": "buy",
    "quantity": 1000
  }'
```

## 项目结构说明

```
mytrader/
├── ai_trader/              # 主应用目录
│   ├── api/               # API服务层
│   ├── core/              # 核心引擎（待实现）
│   ├── adapters/          # 数据适配器
│   │   └── xueqiu.py      # 雪球网适配器 ✅
│   ├── models/            # AI模型（待实现）
│   ├── analysis/          # 分析模块（待实现）
│   └── utils/             # 工具模块
├── tests/                 # 测试代码（待实现）
├── docs/                  # 文档
│   ├── AI_TRADER_PLAN.md  # 完整技术方案
│   └── XUEQIU_API_GUIDE.md # 本文件
├── main.py               # 主程序入口
├── requirements.txt       # Python依赖
└── .env.example          # 环境变量模板
```

## 雪球网适配器功能列表

| 功能 | 状态 | 说明 |
|------|------|------|
| 登录认证 | ✅ | 用户名密码登录 |
| 创建模拟组合 | ✅ | 创建新的模拟投资组合 |
| 获取组合信息 | ✅ | 查询组合详情和净值 |
| 获取持仓 | ✅ | 查询当前持仓情况 |
| 下单 | ✅ | 买入/卖出股票 |
| 撤单 | ✅ | 撤销未成交订单 |
| 获取实时行情 | ✅ | 实时股价查询 |
| 获取历史数据 | ✅ | 历史K线数据 |
| 获取股票信息 | ✅ | 股票基本信息 |

## 注意事项

1. **雪球网反爬虫**：雪球网可能有反爬虫机制，建议合理控制请求频率
2. **数据准确性**：模拟交易数据仅供参考，不构成投资建议
3. **账户安全**：请妥善保管您的雪球网账号密码
4. **合规性**：确保您的使用符合雪球网的使用条款

## 下一步开发

- [ ] 实现AI决策引擎（集成OpenClaw）
- [ ] 实现交易执行引擎
- [ ] 实现风险管理模块
- [ ] 实现数据分析模块
- [ ] 添加API路由（交易、分析、持仓）
- [ ] 添加WebSocket实时推送
- [ ] 添加前端监控界面
- [ ] 编写单元测试
- [ ] 性能优化和安全加固

## 常见问题

### 1. 登录失败怎么办？

检查用户名密码是否正确，如果还是失败，可能是雪球网更新了登录接口。

### 2. 如何获取股票代码？

- 上海证券交易所：SH + 6位代码（如：SH600000）
- 深圳证券交易所：SZ + 6位代码（如：SZ000001）
- 本适配器支持简写（如：000001、600000），会自动添加前缀

### 3. 市价单和限价单有什么区别？

- **市价单**：以当前最优价格立即成交
- **限价单**：指定价格成交，可能部分成交或不成交

## 技术支持

如有问题，请查看：
- 完整技术方案：`docs/AI_TRADER_PLAN.md`
- API文档：http://localhost:8000/docs
