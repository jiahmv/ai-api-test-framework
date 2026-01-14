# 性能测试快速参考

## Excel 列定义

在现有的 Excel 测试用例基础上，添加以下两列：

| 列序号 | 列名 | 类型 | 必填 | 说明 |
|--------|------|------|------|------|
| 13 | 性能配置 | JSON | 否 | 性能测试配置 |
| 14 | 最大响应时间 | 整数 | 否 | 响应时间上限（毫秒） |

## Excel 示例

| 测试用例ID | 模块 | 接口名称 | 请求地址 | ... | 状态码 | 性能配置 | 最大响应时间 |
|-----------|------|---------|---------|-----|--------|----------|-------------|
| PERF_001 | 用户 | 登录 | /api/login | ... | 200 | | 2000 |
| PERF_002 | 订单 | 创建订单 | /api/order | ... | 200 | {"concurrent_users":100,"duration":120} | 3000 |

## 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| --concurrent-users | int | 10 | 并发用户数 |
| --duration | int | 60 | 测试持续时间（秒） |
| --ramp-up | int | 0 | 启动时间（秒） |
| --excel-files | str | 配置文件 | Excel文件路径 |
| --sheet-names | str | all | Sheet名称 |

## 常用命令

```bash
# 快速性能测试
pytest tests/test_performance.py

# 压力测试（100并发，5分钟）
pytest tests/test_performance.py --concurrent-users 100 --duration 300

# 稳定性测试（50并发，1小时）
pytest tests/test_performance.py --concurrent-users 50 --duration 3600

# 指定测试文件
pytest tests/test_performance.py --excel-files perf_cases.xlsx
```

## 性能指标

| 指标 | 说明 | 良好值 |
|------|------|--------|
| 平均响应时间 | 所有请求的平均响应时间 | < 1秒 |
| P95响应时间 | 95%的请求快于此时间 | < 2秒 |
| P99响应时间 | 99%的请求快于此时间 | < 3秒 |
| 成功率 | 成功请求占比 | > 99% |
| TPS | 每秒事务数 | 视业务而定 |

## 配置文件

在 `config/config.yaml` 中配置默认值：

```yaml
performance:
  enabled: true
  default_concurrent_users: 10
  default_duration: 60
  default_ramp_up: 0

  thresholds:
    response_time_p95: 3000
    response_time_p99: 5000
    success_rate: 0.99
    tps: 100
```

## 报告位置

- HTML报告：`reports/performance/perf_report_YYYYMMDD_HHMMSS.html`
- JSON报告：`reports/performance/perf_report_YYYYMMDD_HHMMSS.json`
