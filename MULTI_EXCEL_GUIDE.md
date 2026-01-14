# 多Excel文件测试用例管理

## 功能概述

框架支持从单个或多个Excel文件中加载测试用例并执行，提供灵活的测试用例管理方式。

## 支持的模式

### 1. 目录模式（默认）

加载指定目录下的所有Excel文件（`.xlsx`和`.xls`）。

**配置文件**：`config/config.yaml`
```yaml
excel:
  file_path: "data/test_cases"  # 指向目录
  sheet_name: "Sheet1"
```

**运行命令**：
```bash
# 加载并运行目录下所有Excel文件的测试用例
pytest tests/test_api.py -v
```

**特点**：
- 自动扫描目录下所有Excel文件
- 每个文件的用例都会被加载
- 支持不同模块的测试用例分开管理

### 2. 单文件模式

只加载指定的单个Excel文件。

**配置文件**：`config/config.yaml`
```yaml
excel:
  file_path: "data/test_cases/test_cases.xlsx"  # 指向单个文件
  sheet_name: "Sheet1"
```

**运行命令**：
```bash
# 只运行test_cases.xlsx中的用例
pytest tests/test_api.py -v
```

### 3. 命令行指定文件（推荐）

运行时通过命令行参数指定要运行的Excel文件。

```bash
# 运行单个文件
pytest tests/test_api.py --excel-files data/test_cases/test_cases_users.xlsx -v

# 运行多个文件（逗号分隔）
pytest tests/test_api.py --excel-files "data/test_cases/test_cases_users.xlsx,data/test_cases/test_cases_orders.xlsx" -v

# 运行指定文件，忽略配置文件中的设置
pytest tests/test_api.py --excel-files "data/test_cases/test_cases_users.xlsx" -v
```

**优点**：
- 无需修改配置文件
- 灵活选择要运行的测试
- 支持并行执行不同文件

## 目录结构示例

```
data/test_cases/
├── test_cases.xlsx           # 主测试用例文件
├── test_cases_users.xlsx     # 用户模块测试
├── test_cases_orders.xlsx    # 订单模块测试
├── test_cases_products.xlsx  # 产品模块测试
└── test_cases_payments.xlsx  # 支付模块测试
```

## 使用场景

### 场景1：运行所有测试用例

```bash
# 方式1：配置文件设置为目录路径
# config.yaml: file_path: "data/test_cases"
pytest tests/test_api.py -v

# 方式2：使用通配符（需要引号）
pytest tests/test_api.py --excel-files "data/test_cases/*.xlsx" -v
```

### 场景2：运行特定模块的测试

```bash
# 只运行用户模块测试
pytest tests/test_api.py --excel-files data/test_cases/test_cases_users.xlsx -v

# 只运行订单模块测试
pytest tests/test_api.py --excel-files data/test_cases/test_cases_orders.xlsx -v
```

### 场景3：运行多个模块的测试

```bash
# 运行用户和订单模块
pytest tests/test_api.py --excel-files "data/test_cases/test_cases_users.xlsx,data/test_cases/test_cases_orders.xlsx" -v
```

### 场景4：并行执行不同模块

```bash
# 终端1：运行用户模块
pytest tests/test_api.py --excel-files data/test_cases/test_cases_users.xlsx

# 终端2：运行订单模块
pytest tests/test_api.py --excel-files data/test_cases/test_cases_orders.xlsx
```

## 配置管理

### 1. 默认配置（推荐）

`config/config.yaml`：
```yaml
excel:
  # 使用目录路径，默认运行所有文件
  file_path: "data/test_cases"
  sheet_name: "Sheet1"
```

**优点**：
- 无需手动指定文件
- 新增Excel文件自动被加载
- 适合运行全部测试

### 2. 单文件配置

`config/config.yaml`：
```yaml
excel:
  # 指定单个文件
  file_path: "data/test_cases/test_cases.xlsx"
  sheet_name: "Sheet1"
```

**优点**：
- 明确指定测试文件
- 避免加载不需要的文件
- 适合日常开发调试

## Excel文件命名规范

建议使用描述性的文件名：

- `test_cases.xlsx` - 主测试用例
- `test_cases_users.xlsx` - 用户模块
- `test_cases_orders.xlsx` - 订单模块
- `test_cases_products.xlsx` - 产品模块
- `smoke_tests.xlsx` - 冒烟测试
- `regression_tests.xlsx` - 回归测试

## 运行示例

### 示例1：加载所有文件

```bash
$ pytest tests/test_api.py -v

# 输出：
从目录加载Excel文件: PosixPath('data/test_cases')
找到 3 个Excel文件
加载Excel文件: test_cases.xlsx
加载Excel文件: test_cases_users.xlsx
加载Excel文件: test_cases_orders.xlsx

collected 14 items
```

### 示例2：只运行用户模块

```bash
$ pytest tests/test_api.py --excel-files data/test_cases/test_cases_users.xlsx -v

# 输出：
加载指定的Excel文件: ['data/test_cases/test_cases_users.xlsx']
加载Excel文件: test_cases_users.xlsx

collected 2 items
tests/test_api.py::TestAPI::test_api_case[API001] PASSED
tests/test_api.py::TestAPI::test_api_case[API002] PASSED
```

### 示例3：运行多个模块

```bash
$ pytest tests/test_api.py --excel-files "data/test_cases/test_cases_users.xlsx,data/test_cases/test_cases_orders.xlsx" -v

# 输出：
加载指定的Excel文件: ['data/test_cases/test_cases_users.xlsx', 'data/test_cases/test_cases_orders.xlsx']
加载Excel文件: test_cases_users.xlsx
加载Excel文件: test_cases_orders.xlsx

collected 4 items
```

## 高级用法

### 1. 结合pytest标记

在Excel中添加"模块"字段，然后结合pytest标记：

```python
# tests/test_api.py
@pytest.mark.parametrize("case", get_test_cases())
@pytest.mark.users  # 自定义标记
def test_api_case(self, case):
    if "用户模块" in case.module:
        # 只运行用户模块用例
        ...
```

运行特定模块：
```bash
pytest tests/test_api.py -m users
```

### 2. 按文件名分组

```bash
# 运行所有用户相关文件
pytest tests/test_api.py --excel-files "data/test_cases/*users*.xlsx" -v

# 运行所有冒烟测试
pytest tests/test_api.py --excel-files "data/test_cases/smoke*.xlsx" -v
```

### 3. 持续集成（CI/CD）

```yaml
# .github/workflows/test.yml
- name: 运行冒烟测试
  run: pytest tests/test_api.py --excel-files data/test_cases/smoke_tests.xlsx

- name: 运行完整测试
  run: pytest tests/test_api.py

- name: 运行指定模块
  run: pytest tests/test_api.py --excel-files "data/test_cases/test_cases_users.xlsx,data/test_cases/test_cases_orders.xlsx"
```

## 注意事项

### 1. 文件路径

- 相对路径：相对于项目根目录
- 绝对路径：完整路径
- 多个文件用逗号分隔，需要引号

```bash
# 正确
pytest tests/test_api.py --excel-files "file1.xlsx,file2.xlsx"

# 错误（未加引号）
pytest tests/test_api.py --excel-files file1.xlsx,file2.xlsx
```

### 2. 目录扫描

- 只扫描`.xlsx`和`.xls`文件
- 不扫描子目录
- 按文件名字母顺序加载

### 3. Sheet名称

- 默认使用"Sheet1"
- 可在配置文件中修改
- 所有Excel文件应使用相同的sheet名称

## 故障排除

### 1. 文件未找到

```
FileNotFoundError: Excel文件不存在: data/test_cases/test.xlsx
```

**解决**：
- 检查文件路径是否正确
- 确认文件确实存在
- 使用相对路径（从项目根目录）

### 2. 没有加载到用例

```
从目录加载Excel文件: data/test_cases
找到 0 个Excel文件
```

**解决**：
- 确认目录中有`.xlsx`或`.xls`文件
- 检查文件权限
- 查看日志确认扫描的目录

### 3. 加载了错误的文件

**解决**：
- 使用`--excel-files`明确指定文件
- 检查文件命名是否规范
- 将测试用例分类到不同目录

## 最佳实践

### 1. 目录组织

```
data/test_cases/
├── smoke/                     # 冒烟测试
│   ├── smoke_api.xlsx
│   └── smoke_ui.xlsx
├── user_module/               # 用户模块
│   ├── user_login.xlsx
│   ├── user_register.xlsx
│   └── user_profile.xlsx
└── order_module/              # 订单模块
    ├── order_create.xlsx
    ├── order_list.xlsx
    └── order_detail.xlsx
```

### 2. 文件命名

- 使用描述性名称
- 包含模块信息
- 使用小写和下划线
- 避免特殊字符

### 3. 运行策略

- **开发调试**：使用`--excel-files`指定单个文件
- **冒烟测试**：创建专门的smoke测试文件
- **完整测试**：使用目录模式运行所有文件
- **并行执行**：不同文件在不同终端运行

## 总结

| 模式 | 配置方式 | 运行命令 | 适用场景 |
|-----|---------|---------|---------|
| 目录模式 | file_path指向目录 | pytest tests/ -v | 运行全部测试 |
| 单文件模式 | file_path指向文件 | pytest tests/ -v | 日常开发 |
| 命令行模式 | 无需配置 | --excel-files files | 灵活选择 |
