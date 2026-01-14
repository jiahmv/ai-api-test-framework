# 断言错误处理优化总结

## 优化内容

### 1. 自定义异常类

创建了三种自定义异常类，提供结构化的错误信息：

#### APIAssertionError（基类）
- 提供统一的错误消息格式
- 支持上下文信息（context）
- 自动格式化JSON数据

#### StatusCodeError
专门处理HTTP状态码断言错误
```python
raise StatusCodeError(
    expected=200,
    actual=404,
    response_body={"code": 404, "message": "Not Found"}
)
```

**错误输出示例：**
```
[ERROR] HTTP状态码不匹配

[Details]
  - expected_status: 200
  - actual_status: 404
  - response_body:
    {
      "code": 404,
      "message": "Not Found"
    }
```

#### ResponseBodyError
专门处理响应体字段断言错误
```python
raise ResponseBodyError(
    field="data.status",
    expected="active",
    actual="inactive",
    full_response={...}
)
```

**错误输出示例：**
```
[ERROR] 响应字段 'data.status' 不匹配

[Details]
  - field: data.status
  - expected_value: active
  - actual_value: inactive
  - response_context: {...}
```

#### MissingFieldError
专门处理缺少字段错误
```python
raise MissingFieldError(
    field="data.email",
    available_fields=["id", "name", "status"]
)
```

**错误输出示例：**
```
[ERROR] 响应中缺少字段 'data.email'

[Details]
  - missing_field: data.email
  - available_fields: [...]
```

### 2. 优化断言方法

更新了所有断言方法，使用自定义异常：

```python
# utils/assertions.py

class Assertions:
    def assert_status_code(self, actual: int, expected: int, response_body: Any = None):
        """断言HTTP状态码，支持传入响应体以显示更多上下文"""
        if actual != expected:
            raise StatusCodeError(expected, actual, response_body)

    def assert_response_body(self, actual: Dict, expected: Dict):
        """断言响应体，使用更详细的错误信息"""
        # 检查字段是否存在
        if key not in actual:
            raise MissingFieldError(key, list(actual.keys()))

        # 检查字段值是否匹配
        if actual_value != expected_value:
            raise ResponseBodyError(key, expected_value, actual_value, actual)
```

### 3. pytest配置优化

#### pytest.ini配置
```ini
[pytest]
addopts =
    -v
    --tb=short              # 使用简短的堆栈跟踪
    --showlocals           # 显示局部变量
```

#### conftest.py钩子
```python
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """优化自定义异常的错误输出"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        if call.excinfo:
            exc_type = call.excinfo.type
            exc_value = call.excinfo.value

            # 如果是自定义异常，使用格式化的消息
            if issubclass(exc_type, APIAssertionError):
                report.longrepr = str(exc_value)
```

### 4. 测试代码优化

更新了test_api.py，在断言时传入更多上下文：

```python
# 传入响应体，错误时可以显示更多信息
self.assertions.assert_status_code(
    response['status_code'],
    case.expected_status,
    response_body=response.get('body')  # 新增参数
)
```

## 错误输出对比

### 优化前
```
FAILED tests/test_api.py::TestAPI::test_api_case[case1]
    def assert_status_code(self, actual: int, expected: int):
        assert actual == expected, \
>           f"状态码不匹配: 期望 {expected}, 实际 {actual}"
E       AssertionError: 状态码不匹配: 期望 200, 实际 404
```

### 优化后
```
FAILED tests/test_api.py::TestAPI::test_api_case[case1]
    E       [ERROR] HTTP状态码不匹配
    E
    E       [Details]
    E         - expected_status: 200
    E         - actual_status: 404
    E         - response_body:
    E           {
    E             "code": 404,
    E             "message": "Not Found",
    E             "detail": "Resource not found"
    E           }
```

## 优势

### 1. 信息更完整
- 显示期望值和实际值
- 显示完整的响应体（便于调试）
- 显示可用的字段列表（字段缺失时）

### 2. 结构更清晰
- 使用分层结构（ERROR -> Details -> 具体字段）
- JSON格式化显示，便于阅读
- 符号标记清晰（[ERROR]、[Details]、-）

### 3. 上下文更丰富
- 状态码错误：显示响应体
- 字段错误：显示完整响应
- 缺失字段：显示可用字段列表

### 4. 输出更简洁
- 移除了冗长的堆栈跟踪
- 使用--tb=short配置
- 自定义异常直接显示核心信息

## 使用建议

### 1. 状态码断言
```python
# 推荐：传入响应体
assertions.assert_status_code(
    response['status_code'],
    200,
    response_body=response.get('body')
)
```

### 2. 响应体断言
```python
# 在Excel中定义期望字段
{
  "code": 200,
  "data.status": "active",
  "data.user.id": 123
}

# 断言时会自动检查字段是否存在和值是否匹配
```

### 3. Schema断言
```python
# 验证字段类型
assertions.assert_schema(
    response_body,
    {
        "id": "int",
        "name": "str",
        "status": "str"
    }
)
```

## 错误级别

- **[ERROR]**: 严重错误，测试失败
- **[Details]**: 详细信息，帮助调试
- **-**: 列表项标记

## 兼容性

- ✅ 支持Windows/Linux/Mac
- ✅ 支持Python 3.7+
- ✅ 支持pytest 7.0+
- ✅ 支持中文输出
- ✅ 兼容Allure报告
- ✅ 兼容HTML报告

## 后续优化建议

1. **添加更多断言类型**
   - assert_time_range() - 响应时间断言
   - assert_json_schema() - JSON Schema验证
   - assert_headers() - 响应头断言

2. **国际化支持**
   - 支持英文/中文错误消息切换
   - 支持自定义错误消息模板

3. **错误分组**
   - 按错误类型分组显示
   - 统计各类错误的出现频率

4. **智能建议**
   - 根据错误类型提供修复建议
   - 显示类似用例的对比
