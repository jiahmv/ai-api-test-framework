# HTTP接口自动化测试框架

一个基于Python的HTTP接口自动化测试框架，支持Excel测试用例管理、参数化数据依赖、多环境配置和多种测试报告格式。

## 特性

- **Excel用例管理**：从Excel文件加载测试用例，可视化编辑
- **多Sheet支持**：支持执行所有sheet或指定sheet，灵活管理不同模块的用例
- **参数化支持**：支持 `${variable}` 语法实现用例间数据依赖
- **多环境配置**：支持开发、测试、生产等多环境切换
- **数据提取**：从响应中提取数据并保存到YAML文件，供后续用例使用
- **测试报告**：支持HTML和Allure两种报告格式，自动按时间戳归档
- **完整日志**：详细的日志记录，自动按时间戳归档，便于问题排查

## 技术栈

- **测试框架**: pytest 7.4.3
- **HTTP请求**: requests 2.31.0
- **Excel处理**: openpyxl 3.1.2
- **配置管理**: PyYAML 6.0.1
- **测试报告**: pytest-html 4.1.1, allure-pytest 2.13.5
- **日志**: loguru 0.7.2

## 项目结构

```
ai-api-test-framework/
├── config/                      # 配置文件目录
│   ├── config.yaml              # 环境配置
│   └── settings.py              # 配置加载器
├── core/                        # 核心业务逻辑
│   ├── case_loader.py           # Excel用例加载器
│   ├── api_executor.py          # 接口执行器
│   ├── data_extractor.py        # 数据提取器
│   ├── data_manager.py          # 数据管理器
│   └── request_builder.py       # 请求构建器
├── utils/                       # 工具类
│   ├── logger.py                # 日志工具
│   └── assertions.py            # 断言工具
├── data/                        # 数据目录
│   ├── test_cases/              # Excel测试用例
│   └── extract_data/            # 提取的数据存储
├── reports/                     # 测试报告目录
│   ├── html/                    # HTML报告
│   └── allure/                  # Allure报告
├── tests/                       # 测试执行入口
│   ├── conftest.py              # pytest配置
│   └── test_api.py              # 测试执行主程序
├── logs/                        # 日志目录
├── requirements.txt             # 依赖包
└── pytest.ini                   # pytest配置
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

编辑 `config/config.yaml`，修改环境配置：

```yaml
env:
  current: test  # 修改为 dev/test/prod

environments:
  test:
    base_url: "http://test.api.example.com"  # 修改为实际API地址
    timeout: 30
```

### 3. 编写测试用例

在 `data/test_cases/test_cases.xlsx` 中编写测试用例：

| 测试用例ID | 模块 | 接口名称 | 请求地址 | 前置条件 | 请求方法 | 请求参数类型 | 请求参数 | 期望结果 | 是否运行 | 请求头 | 状态码 |
|-----------|------|---------|---------|---------|---------|------------|---------|---------|---------|--------|--------|
| CASE001 | 用户模块 | 用户登录 | /api/login | {"token": "data.token"} | POST | json | {"username":"test","password":"123"} | {"code":200} | Y | {"Content-Type":"application/json"} | 200 |
| CASE002 | 用户模块 | 获取用户信息 | /api/user/info | | GET | params | {"user_id":"10001"} | {"code":200} | Y | {"Authorization": "Bearer ${token}"} | 200 |

### 4. 运行测试

```bash
# 运行所有测试（加载配置文件中指定的所有Excel文件和所有sheet）
pytest tests/

# 运行指定模块
pytest tests/ -k "用户模块"

# 指定Excel文件运行
pytest tests/ --excel-files data/test_cases/test_cases_users.xlsx

# 指定多个Excel文件运行
pytest tests/ --excel-files "data/test_cases/test_cases_users.xlsx,data/test_cases/test_cases_orders.xlsx"

# 指定sheet运行（执行所有sheet中的用例）
pytest tests/ --sheet-names all

# 指定单个sheet运行
pytest tests/ --sheet-names 用户模块

# 指定多个sheet运行（逗号分隔）
pytest tests/ --sheet-names "用户模块,订单模块,商品模块"

# 指定文件和sheet运行
pytest tests/ --excel-files data/test_cases/api_test.xlsx --sheet-names 用户模块

# 生成HTML报告
pytest tests/ --html=reports/html/report.html --self-contained-html

# 生成Allure报告
pytest tests/ --alluredir=reports/allure
allure serve reports/allure
```

**Sheet选择功能说明**：

框架支持灵活的sheet选择，满足不同的测试场景：

1. **执行所有sheet（默认）**
   - 不指定 `--sheet-names` 参数时，自动执行Excel文件中的所有sheet
   - 每个sheet可以代表不同的功能模块

2. **执行指定sheet**
   - 使用 `--sheet-names` 参数指定要执行的sheet名称
   - 支持单个sheet：`--sheet-names 用户模块`
   - 支持多个sheet（逗号分隔）：`--sheet-names "用户模块,订单模块"`

3. **组合使用**
   - 可以同时指定Excel文件和sheet：`--excel-files file.xlsx --sheet-names 用户模块`
   - 适合运行特定模块的测试用例

**多Excel文件支持**：

框架支持三种模式：
1. **目录模式**：加载目录下所有Excel文件
2. **单文件模式**：只加载指定的单个文件
3. **命令行模式**：运行时指定文件

详细说明请查看：[MULTI_EXCEL_GUIDE.md](MULTI_EXCEL_GUIDE.md)

## Excel用例编写规范

### 列定义

| 列名 | 字段名 | 类型 | 必填 | 说明 |
|-----|-------|------|------|------|
| 测试用例ID | case_id | string | 是 | 用例唯一标识 |
| 模块 | module | string | 是 | 功能模块 |
| 接口名称 | api_name | string | 是 | 接口描述 |
| 请求地址 | url | string | 是 | 相对路径 |
| 前置条件 | pre_condition | string | 否 | 数据提取规则(JSON) |
| 请求方法 | method | string | 是 | GET/POST/PUT/DELETE |
| 请求参数类型 | param_type | string | 是 | params/data/json |
| 请求参数 | params | string | 是 | 参数(JSON字符串) |
| 期望结果 | expected_result | string | 否 | 期望响应(JSON) |
| 是否运行 | is_run | string | 是 | Y/N |
| 请求头 | headers | string | 否 | 请求头(JSON) |
| 状态码 | expected_status | int | 是 | 期望HTTP状态码 |

### 参数类型说明

- **params**: URL查询参数，拼接在URL后面
- **data**: 表单数据，Content-Type为application/x-www-form-urlencoded
- **json**: JSON数据，Content-Type为application/json

## 参数化数据依赖

### 基本语法

使用 `${variable_name}` 语法引用已提取的数据：

```json
// 请求头中使用
{
  "Authorization": "Bearer ${token}"
}

// 请求参数中使用
{
  "user_id": "${user_id}",
  "order_id": "${order_id}"
}

// URL中使用
/api/user/${user_id}/info
```

### 数据提取规则

在 `前置条件` 字段中定义提取规则：

```json
{
  "token": "data.token",
  "user_id": "data.user.id",
  "order_id": "data.order_list.0.id"
}
```

**支持的提取方式：**

1. **JSON路径提取**（推荐）：
   - `data.token` - 提取响应体中data.token的值
   - `data.user.id` - 提取嵌套字段
   - `data.list.0.id` - 提取数组元素

2. **正则表达式提取**：
   - `"code": (\\d+)` - 提取匹配的数字

### 数据依赖流程示例

**场景：登录获取token，后续接口使用token**

1. **第一个接口（登录）**
   - 请求：`POST /api/login`
   - 响应：`{"code": 200, "data": {"token": "abc123xyz"}}`
   - 前置条件：`{"token": "data.token"}`
   - 提取结果：保存到 `extract_data.yaml` → `{"token": "abc123xyz"}`

2. **第二个接口（使用token）**
   - 请求：`GET /api/user/info`
   - 请求头：`{"Authorization": "Bearer ${token}"}`
   - 参数化替换：`{"Authorization": "Bearer abc123xyz"}`

## 环境配置

### 切换环境

修改 `config/config.yaml`：

```yaml
env:
  current: test  # dev/test/prod
```

### 环境配置说明

```yaml
environments:
  dev:
    base_url: "http://dev.api.example.com"  # 开发环境
    timeout: 30
    headers:
      Content-Type: "application/json"

  test:
    base_url: "http://test.api.example.com"  # 测试环境
    timeout: 30
    headers:
      Content-Type: "application/json"

  prod:
    base_url: "http://api.example.com"  # 生产环境
    timeout: 30
    headers:
      Content-Type: "application/json"
```

## 测试报告

框架支持HTML和Allure两种报告格式，包含完整的请求和响应信息。

**报告路径说明**：

框架会自动为每次测试运行创建带时间戳的报告文件，避免覆盖历史报告：

```
reports/
├── html/
│   ├── report-20240112-143025.html
│   ├── report-20240112-150830.html
│   └── ...
└── allure/
    ├── allure_20240112_143025/
    ├── allure_20240112_150830/
    └── ...
```

- **HTML报告**：直接在 `html/` 目录下生成 `report-YYYYMMDD-HHMMSS.html` 文件
- **Allure报告**：在 `allure/` 目录下创建 `allure_YYYYMMDD_HHMMSS/` 子目录

### HTML报告

```bash
# 运行测试（自动生成带时间戳的HTML报告）
pytest tests/

# HTML报告会自动保存到 reports/html/report-YYYYMMDD-HHMMSS.html
# 运行时会在控制台输出完整路径，直接用浏览器打开即可
```

HTML报告包含：
- **测试用例信息**: 用例ID、名称、模块
- **执行结果**: PASSED/FAILED状态
- **请求信息**:
  - 请求方法和URL
  - 请求头（JSON格式）
  - 请求参数（JSON格式）
- **响应信息**:
  - 响应状态码
  - 响应时间
  - 响应体（JSON格式，超过5000字符自动截断）

### Allure报告（推荐）

```bash
# 1. 运行测试（自动生成带时间戳的Allure报告数据）
pytest tests/

# Allure报告数据会自动保存到 reports/allure/allure_YYYYMMDD_HHMMSS/
# 运行时会在控制台输出完整路径

# 2. 使用最新生成的报告数据
# 方法1：实时查看（自动刷新）
allure serve reports/allure/allure_20240112_143025

# 方法2：生成静态HTML报告
allure generate reports/allure/allure_20240112_143025 -o reports/allure/report-20240112-143025

# 3. 打开静态报告
allure open reports/allure/report-20240112-143025
```

**使用工具类获取最新报告路径**：

```python
from utils.path_helper import PathHelper

# 获取最新的Allure报告目录
latest_allure = PathHelper.get_latest_dir("reports/allure", "allure")
print(latest_allure)  # reports/allure/allure_20240112_143025

# 获取最新的HTML报告文件
latest_html = PathHelper.get_latest_file("reports/html", "report", "html")
print(latest_html)  # reports/html/report-20240112-143025.html
```

Allure报告功能：
- **完整的请求/响应详情**: 支持下载附件
- **测试步骤记录**: 清晰的执行流程
- **统计图表**: 状态分布、趋势分析
- **历史对比**: 多次运行结果对比
- **环境信息**: 测试环境配置展示
- **失败分析**: 详细的失败原因

**详细使用说明请查看**: [REPORT_GUIDE.md](REPORT_GUIDE.md)

## 日志

**日志路径说明**：

框架会自动为每次测试运行创建带时间戳的日志文件，避免日志文件被覆盖：

```
logs/
├── api-log-20240112-143025.log
├── api-log-20240112-150830.log
└── ...
```

日志文件直接在 `logs/` 目录下生成，文件名格式为 `api-log-YYYYMMDD-HHMMSS.log`。

日志文件包含：
- 测试执行流程
- 请求和响应详情
- 数据提取信息
- 错误和异常信息
- 报告和日志路径信息

运行测试时，控制台会输出完整的日志文件路径，方便快速定位。

## 错误处理

框架提供清晰的错误信息，便于快速定位问题。

### 错误类型

1. **状态码错误**
```
[ERROR] HTTP状态码不匹配

[Details]
  - expected_status: 200
  - actual_status: 404
  - response_body: {...}
```

2. **字段不匹配**
```
[ERROR] 响应字段 'status' 不匹配

[Details]
  - field: status
  - expected_value: active
  - actual_value: inactive
  - response_context: {...}
```

3. **缺少字段**
```
[ERROR] 响应中缺少字段 'email'

[Details]
  - missing_field: email
  - available_fields: ["id", "name", "status"]
```

### 断言方法

```python
from utils.assertions import Assertions

assertions = Assertions()

# 状态码断言
assertions.assert_status_code(actual=200, expected=200, response_body=body)

# 响应体断言
assertions.assert_response_body(actual={"code": 200}, expected={"code": 200})

# 包含断言
assertions.assert_contains(actual="Hello World", expected="Hello")

# Schema断言
assertions.assert_schema(
    response_body={"id": 1, "name": "test"},
    schema={"id": "int", "name": "str"}
)
```

**详细说明请查看**: [ASSERTION_IMPROVEMENT.md](ASSERTION_IMPROVEMENT.md)

## 常见问题

### 1. 如何跳过某个测试用例？

在Excel的 `是否运行` 列设置为 `N`。

### 2. 如何处理超时的请求？

在 `config/config.yaml` 中修改 `timeout` 配置。

### 3. 如何添加自定义断言？

在 `utils/assertions.py` 中添加自定义断言方法。

### 4. 如何清空提取的数据？

删除 `data/extract_data/extract_data.yaml` 文件或手动清空内容。

### 5. 为什么错误输出很长？

框架已优化错误输出：
- 使用自定义异常类，提供结构化的错误信息
- 使用`--tb=short`配置，简化堆栈跟踪
- 显示完整的上下文信息（响应体、可用字段等）
- 自动格式化JSON数据，便于阅读

### 6. 如何查看Excel文件中有哪些sheet？

框架会在运行时输出所有sheet信息。你也可以使用Python脚本查看：

```python
import openpyxl

workbook = openpyxl.load_workbook('data/test_cases/test_cases.xlsx')
print("Sheet列表:", workbook.sheetnames)
workbook.close()
```

### 7. 指定的sheet不存在会怎样？

框架会给出明确的错误提示，显示可用的sheet列表：

```
ValueError: 指定的sheet不存在: ['不存在的sheet']，文件中的sheet: ['Sheet1', '用户模块', '订单模块']
```

### 8. 如何将不同模块的用例放在不同的sheet中？

在Excel文件中创建多个sheet，每个sheet命名为模块名称（如"用户模块"、"订单模块"），然后使用 `--sheet-names` 参数选择执行：

```bash
# 只执行用户模块的用例
pytest tests/ --sheet-names 用户模块
```

### 9. 报告和日志为什么要用时间戳？

使用时间戳的好处：
- **避免覆盖**：每次运行都会生成新的报告文件，不会覆盖之前的测试结果
- **历史追溯**：可以方便地查看任意一次测试运行的报告
- **对比分析**：可以对比不同时间点的测试结果
- **简化结构**：HTML报告和日志文件直接在目录下，不需要额外文件夹

### 10. 如何快速找到最新的报告？

使用框架提供的工具类：

```python
from utils.path_helper import PathHelper

# 获取最新的Allure报告目录
latest_allure = PathHelper.get_latest_dir("reports/allure", "allure")

# 获取最新的HTML报告文件
latest_html = PathHelper.get_latest_file("reports/html", "report", "html")

# 获取最新的日志文件
latest_log = PathHelper.get_latest_file("logs", "api-log", "log")
```

或者查看控制台输出，运行测试时会自动显示完整的报告路径。

## 开发规范

- 遵循PEP 8代码规范
- 单一职责原则
- 中文注释，英文代码
- 使用conventional commits提交规范

## 后续扩展

- [ ] 数据库验证功能
- [ ] Mock服务支持
- [ ] CI/CD集成
- [ ] 性能测试支持
- [ ] 自定义断言扩展

## License

MIT License
