# 测试报告查看指南

本框架支持HTML和Allure两种格式的测试报告，报告包含完整的请求和响应信息。

## HTML报告

### 生成报告

```bash
# 运行测试并生成HTML报告
pytest tests/ --html=reports/html/report.html --self-contained-html
```

### 查看报告

直接在浏览器中打开 `reports/html/report.html` 文件。

### 报告内容

HTML报告包含以下信息：
- **测试用例名称**: `[CASE001] 获取用户列表`
- **测试结果**: PASSED/FAILED
- **执行时间**: 测试用例执行耗时
- **请求信息**:
  - 请求方法和URL
  - 请求头（JSON格式）
  - 请求参数（JSON格式）
- **响应信息**:
  - 响应状态码
  - 响应时间
  - 响应体（JSON格式，超过5000字符会截断）

## Allure报告

### 生成报告

```bash
# 1. 运行测试生成Allure数据
pytest tests/ --alluredir=reports/allure

# 2. 实时查看报告（自动刷新）
allure serve reports/allure

# 3. 生成静态HTML报告
allure generate reports/allure -o reports/allure/html

# 4. 在浏览器中打开静态报告
allure open reports/allure/html
```

### 查看报告

**方式一：实时查看（推荐）**
```bash
allure serve reports/allure
```
会自动打开浏览器并显示报告，修改测试后自动刷新。

**方式二：生成静态报告**
```bash
allure generate reports/allure -o reports/allure/html
allure open reports/allure/html
```

### Allure报告功能

#### 1. 测试用例列表
- 按照状态分类显示（通过、失败、跳过）
- 显示用例ID和名称
- 显示执行时间

#### 2. 测试用例详情
点击任意测试用例查看详细信息：

**基本信息**
- 用例名称: `[CASE001] 获取用户列表`
- 描述: 包含模块、接口名称、用例ID

**测试步骤**
1. **1. 构建请求**
   - 请求信息: `GET https://jsonplaceholder.typicode.com/users`
   - 请求头: JSON格式显示
   - 请求参数: JSON格式显示

2. **2. 发送HTTP请求**
   - 执行HTTP请求

3. **3. 解析响应**
   - 响应状态码: `200`
   - 响应头: JSON格式显示（前10个）
   - 响应体: JSON格式显示完整内容
   - 响应时间: `2.175秒`

4. **4. 断言状态码**
   - 验证HTTP状态码

5. **5. 断言响应体**
   - 验证响应字段

6. **6. 提取并保存数据**（如果有）
   - 提取的数据: JSON格式显示

#### 3. 附件下载
每个附件（请求头、请求参数、响应体等）都可以下载到本地：
- 点击附件右侧的下载图标
- 保存为JSON或文本文件

#### 4. 统计图表
- **测试用例状态分布**: 饼图显示通过/失败/跳过的比例
- **测试套件**: 按模块分组显示
- **执行时间趋势**: 历史运行时间对比
- **环境信息**: 显示测试环境配置

### Allure报告优势

| 功能 | HTML报告 | Allure报告 |
|-----|---------|-----------|
| 请求/响应详情 | ✅ | ✅ |
| 测试步骤 | ❌ | ✅ |
| 附件下载 | ❌ | ✅ |
| 历史趋势 | ❌ | ✅ |
| 统计图表 | ❌ | ✅ |
| 实时刷新 | ❌ | ✅ |
| 按模块筛选 | ❌ | ✅ |
| 失败分析 | ❌ | ✅ |

## 报告示例

### 请求信息示例

```json
// 请求头
{
  "Content-Type": "application/json"
}

// 请求参数
{
  "name": "测试用户",
  "username": "testuser",
  "email": "test@example.com"
}
```

### 响应信息示例

```json
// 响应状态码
201

// 响应时间
0.523秒

// 响应体
{
  "id": 11,
  "name": "测试用户",
  "username": "testuser",
  "email": "test@example.com"
}
```

## 数据提取信息

如果测试用例配置了数据提取，报告中会显示：

```
提取并保存数据: {"user_id": 11}
```

并在Allure报告的附件中显示提取的数据：

```json
{
  "user_id": 11
}
```

## 注意事项

1. **响应体大小限制**
   - HTML报告：响应体超过5000字符会截断
   - Allure报告：完整显示响应体

2. **附件格式**
   - JSON类型的附件可以下载为.json文件
   - TEXT类型的附件可以下载为.txt文件

3. **报告存储**
   - HTML报告：单个文件，便于分享
   - Allure报告：需要安装Allure命令行工具

## 故障排除

### Allure命令未找到

```bash
# Windows
# 下载Allure并配置PATH环境变量
# 或使用scoop安装
scoop install allure

# macOS
brew install allure

# Linux
# 下载并解压，配置PATH
```

### 报告无法打开

- **HTML报告**: 确保浏览器支持JavaScript
- **Allure报告**: 确保已安装Allure并配置PATH

### 报告内容为空

- 确保测试已执行完成
- 检查日志文件 `logs/test.log`
- 重新运行测试生成报告
