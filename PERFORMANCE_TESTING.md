# 性能测试使用指南

本指南介绍如何使用 AI API 测试框架进行接口性能测试。

## 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [运行性能测试](#运行性能测试)
- [查看性能报告](#查看性能报告)
- [性能测试场景](#性能测试场景)
- [性能指标解读](#性能指标解读)
- [性能优化建议](#性能优化建议)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [快速参考](#快速参考)

---

## 功能特性

- ✅ **并发压力测试** - 支持多线程并发执行测试用例
- ✅ **响应时间统计** - 记录最小、最大、平均、P95、P99响应时间
- ✅ **性能阈值断言** - 支持设置响应时间上限并自动断言
- ✅ **性能报告** - 生成详细的 HTML 和 JSON 性能报告
- ✅ **Excel 集成** - 在现有 Excel 用例中添加性能配置

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

性能测试需要的依赖：
- `pytest-xdist` - 并发执行支持
- `locust` - 专业性能测试框架（可选）

### 2. 准备测试用例

在 Excel 文件中添加性能测试相关列：

| 列名 | 说明 | 示例 | 必填 |
|------|------|------|------|
| 测试用例ID | 用例唯一标识 | PERF_001 | 是 |
| 模块 | 功能模块 | 用户模块 | 是 |
| 接口名称 | 接口描述 | 登录接口 | 是 |
| 请求地址 | 相对路径 | /api/login | 是 |
| 前置条件 | 数据提取规则 | | 否 |
| 请求方法 | GET/POST/PUT/DELETE | POST | 是 |
| 请求参数类型 | params/data/json | json | 是 |
| 请求参数 | JSON格式 | {"username":"test"} | 是 |
| 期望结果 | JSON格式 | {"code":200} | 否 |
| 是否运行 | Y/N | Y | 是 |
| 请求头 | JSON格式 | {"token":"xxx"} | 否 |
| 状态码 | HTTP状态码 | 200 | 是 |
| **性能配置** | JSON格式配置 | 见下方 | 否 |
| **最大响应时间** | 毫秒 | 2000 | 否 |

### 3. 配置性能测试参数

在 Excel 中有两种方式配置性能测试：

#### 方式1: 性能配置列（JSON 格式）

```json
{
  "concurrent_users": 50,
  "duration": 60,
  "ramp_up": 10,
  "target_tps": 100,
  "thresholds": {
    "avg_time": 2.0,
    "p95_time": 3.0,
    "p99_time": 5.0,
    "success_rate": 0.99
  }
}
```

**参数说明**：
- `concurrent_users` - 并发用户数
- `duration` - 测试持续时间（秒）
- `ramp_up` - 启动时间（秒），在此时间内逐步增加并发
- `target_tps` - 目标 TPS
- `thresholds` - 性能阈值
  - `avg_time` - 平均响应时间阈值（秒）
  - `p95_time` - P95响应时间阈值（秒）
  - `p99_time` - P99响应时间阈值（秒）
  - `success_rate` - 成功率阈值（0-1）

#### 方式2: 最大响应时间列（简单方式）

只需填写最大响应时间（毫秒），例如：`2000`（表示2秒）

## 运行性能测试

### 基本用法

```bash
# 使用默认配置运行
pytest tests/test_performance.py

# 指定并发用户数
pytest tests/test_performance.py --concurrent-users 50

# 指定测试持续时间
pytest tests/test_performance.py --duration 300

# 指定启动时间
pytest tests/test_performance.py --ramp-up 30
```

### 高级用法

```bash
# 指定 Excel 文件
pytest tests/test_performance.py --excel-files data/test_cases/perf_cases.xlsx

# 指定 Sheet
pytest tests/test_performance.py --sheet-names "Sheet1,Sheet2"

# 组合使用
pytest tests/test_performance.py \
  --excel-files perf_cases.xlsx \
  --concurrent-users 100 \
  --duration 300 \
  --ramp-up 60
```

### 使用配置文件

在 `config/config.yaml` 中配置默认值：

```yaml
# 性能测试配置
performance:
  enabled: true
  default_concurrent_users: 10  # 默认并发用户数
  default_duration: 60          # 默认测试持续时间（秒）
  default_ramp_up: 0            # 默认启动时间（秒）

  # 性能阈值
  thresholds:
    response_time_p95: 3000     # P95响应时间阈值（毫秒）
    response_time_p99: 5000     # P99响应时间阈值（毫秒）
    success_rate: 0.99          # 成功率阈值（0-1）
    tps: 100                    # TPS阈值
```

## 查看性能报告

测试完成后，报告会自动生成在 `reports/performance/` 目录：

### HTML 报告

```bash
# 报告文件名格式：perf_report_YYYYMMDD_HHMMSS.html
# 例如：perf_report_20240114_143025.html

# 使用浏览器打开
start reports/performance/perf_report_20240114_143025.html  # Windows
open reports/performance/perf_report_20240114_143025.html   # Mac
```

**报告内容**：
- 📊 测试概要（总请求数、成功数、失败数、成功率）
- ⏱️ 响应时间统计（最小、最大、平均、中位数、P95、P99）
- 📈 吞吐量统计（TPS、实际测试时长）
- 📋 用例级别统计（每个用例的详细性能数据）
- ❌ 错误统计（错误类型和次数）

### JSON 报告

```json
{
  "timestamp": "2024-01-14T14:30:25",
  "test_config": {
    "concurrent_users": 50,
    "duration": 60,
    "ramp_up": 10
  },
  "summary": {
    "total_requests": 5000,
    "success_count": 4950,
    "failure_count": 50,
    "success_rate": 99.0,
    "tps": 82.5,
    "actual_duration": 60.0
  },
  "response_times": {
    "min": 0.123,
    "max": 2.456,
    "avg": 0.856,
    "median": 0.789,
    "p95": 1.234,
    "p99": 1.567
  },
  "case_stats": {
    "PERF_001": {
      "count": 2500,
      "success_count": 2475,
      "response_times": [0.123, 0.456, ...]
    }
  }
}
```

## 性能测试场景

### 场景1: 基准性能测试

测试接口在正常负载下的性能表现。

**配置**：
- 并发用户数：10
- 测试时长：60秒
- 启动时间：0秒

```bash
pytest tests/test_performance.py --concurrent-users 10 --duration 60
```

### 场景2: 压力测试

测试接口在高负载下的性能表现。

**配置**：
- 并发用户数：100
- 测试时长：300秒（5分钟）
- 启动时间：30秒

```bash
pytest tests/test_performance.py --concurrent-users 100 --duration 300 --ramp-up 30
```

### 场景3: 稳定性测试

测试接口在长时间运行下的稳定性。

**配置**：
- 并发用户数：50
- 测试时长：3600秒（1小时）
- 启动时间：60秒

```bash
pytest tests/test_performance.py --concurrent-users 50 --duration 3600 --ramp-up 60
```

### 场景4: 峰值测试

测试接口在峰值负载下的性能表现。

**配置**：
- 并发用户数：500
- 测试时长：120秒
- 启动时间：0秒（立即全负载）

```bash
pytest tests/test_performance.py --concurrent-users 500 --duration 120
```

## 性能指标解读

### 响应时间指标

| 指标 | 说明 | 建议值 |
|------|------|--------|
| 最小响应时间 | 最快的请求响应时间 | 参考值 |
| 最大响应时间 | 最慢的请求响应时间 | 关注异常值 |
| 平均响应时间 | 所有请求的平均响应时间 | < 1秒 |
| 中位数响应时间 | 50%的请求快于此值 | < 800ms |
| **P95响应时间** | 95%的请求快于此值 | **< 2秒** |
| **P99响应时间** | 99%的请求快于此值 | **< 3秒** |

### 吞吐量指标

| 指标 | 说明 | 计算公式 |
|------|------|----------|
| TPS | 每秒事务数 | 成功请求数 / 测试时长 |

### 成功率指标

| 指标 | 说明 | 建议值 |
|------|------|--------|
| 成功率 | 成功请求占比 | **> 99%** |

## 性能优化建议

### 1. 响应时间优化

- ✅ **平均响应时间 < 1秒** - 性能良好
- ⚠️ **平均响应时间 1-3秒** - 需要优化
- ❌ **平均响应时间 > 3秒** - 性能差，急需优化

**优化方向**：
- 数据库查询优化
- 接口逻辑优化
- 缓存机制
- CDN 加速

### 2. 并发能力优化

- ✅ **支持 100+ 并发** - 并发能力强
- ⚠️ **支持 50-100 并发** - 并发能力一般
- ❌ **支持 < 50 并发** - 并发能力弱，需要优化

**优化方向**：
- 连接池优化
- 异步处理
- 负载均衡
- 水平扩展

### 3. 成功率优化

- ✅ **成功率 > 99.5%** - 稳定性优秀
- ⚠️ **成功率 99%-99.5%** - 稳定性良好
- ❌ **成功率 < 99%** - 稳定性差，需要优化

**优化方向**：
- 异常处理
- 降级机制
- 熔断机制
- 重试机制

## 最佳实践

### 1. 渐进式压测

从低并发开始，逐步增加并发数：

```bash
# 第1轮：10并发
pytest tests/test_performance.py --concurrent-users 10 --duration 60

# 第2轮：50并发
pytest tests/test_performance.py --concurrent-users 50 --duration 60

# 第3轮：100并发
pytest tests/test_performance.py --concurrent-users 100 --duration 60

# 第4轮：200并发
pytest tests/test_performance.py --concurrent-users 200 --duration 60
```

### 2. 设置合理的阈值

根据业务需求设置性能阈值：

- 用户登录接口：平均响应时间 < 500ms
- 数据查询接口：平均响应时间 < 1s
- 报表导出接口：平均响应时间 < 5s

### 3. 关注 P95 和 P99

不要只关注平均响应时间，P95 和 P99 更能反映用户体验：

- P95 响应时间：95%的用户请求快于此时间
- P99 响应时间：99%的用户请求快于此时间

### 4. 监控资源使用

在性能测试时，同时监控服务器资源：

- CPU 使用率
- 内存使用率
- 网络带宽
- 数据库连接数

### 5. 测试环境隔离

- ✅ 在独立的测试环境进行性能测试
- ❌ 不要在生产环境进行压力测试

## 常见问题

### Q1: 性能测试会影响生产环境吗？

**A**: 不会。性能测试应该在测试环境进行，不要在生产环境运行压力测试。

### Q2: 如何确定合理的并发数？

**A**:
1. 根据预期用户量估算
2. 参考历史峰值流量
3. 从小并发开始，逐步增加

### Q3: 性能测试持续时间多长合适？

**A**:
- **基准测试**：60秒
- **压力测试**：300秒（5分钟）
- **稳定性测试**：3600秒（1小时）

### Q4: 响应时间阈值设置多少合理？

**A**: 根据业务类型和用户体验要求：
- **普通接口**：< 1秒
- **复杂查询**：< 3秒
- **批量操作**：< 10秒

### Q5: 如何处理性能测试失败？

**A**:
1. 查看错误统计，分析失败原因
2. 检查服务器资源使用情况
3. 查看应用日志，定位性能瓶颈
4. 进行优化后重新测试

---

## 📋 快速参考

> 本节提供常用的命令、参数和配置,方便快速查阅。

### Excel列定义速查

在现有的 Excel 测试用例基础上，添加以下两列：

| 列序号 | 列名 | 类型 | 必填 | 说明 |
|--------|------|------|------|------|
| 13 | 性能配置 | JSON | 否 | 性能测试配置 |
| 14 | 最大响应时间 | 整数 | 否 | 响应时间上限（毫秒） |

### Excel示例

| 测试用例ID | 模块 | 接口名称 | 请求地址 | ... | 状态码 | 性能配置 | 最大响应时间 |
|-----------|------|---------|---------|-----|--------|----------|-------------|
| PERF_001 | 用户 | 登录 | /api/login | ... | 200 | | 2000 |
| PERF_002 | 订单 | 创建订单 | /api/order | ... | 200 | {"concurrent_users":100,"duration":120} | 3000 |

### 命令行参数速查

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| --concurrent-users | int | 10 | 并发用户数 |
| --duration | int | 60 | 测试持续时间（秒） |
| --ramp-up | int | 0 | 启动时间（秒） |
| --excel-files | str | 配置文件 | Excel文件路径 |
| --sheet-names | str | all | Sheet名称 |

### 常用命令速查

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

### 性能指标速查

| 指标 | 说明 | 良好值 |
|------|------|--------|
| 平均响应时间 | 所有请求的平均响应时间 | < 1秒 |
| P95响应时间 | 95%的请求快于此时间 | < 2秒 |
| P99响应时间 | 99%的请求快于此时间 | < 3秒 |
| 成功率 | 成功请求占比 | > 99% |
| TPS | 每秒事务数 | 视业务而定 |

### 配置文件示例

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

### 报告位置

- HTML报告：`reports/performance/perf_report_YYYYMMDD_HHMMSS.html`
- JSON报告：`reports/performance/perf_report_YYYYMMDD_HHMMSS.json`

---

## 总结

性能测试是保证 API 质量的重要手段。通过本框架，你可以：

✅ 轻松进行并发压力测试
✅ 获得详细的性能指标
✅ 生成专业的性能报告
✅ 设置性能阈值自动断言

开始你的性能测试之旅吧！🚀
