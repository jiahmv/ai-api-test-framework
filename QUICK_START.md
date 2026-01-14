# 快速入门指南

5分钟快速上手 AI API 测试框架。

## 前置条件

- Python 3.8+
- pip

## 安装

```bash
# 1. 进入项目目录
cd ai-api-test-framework

# 2. 安装依赖
pip install -r requirements.txt
```

## 第一步：配置环境

编辑 `config/config.yaml`，修改测试环境的 API 地址：

```yaml
env:
  current: test  # 当前环境: dev/test/prod

environments:
  test:
    base_url: "http://your-api.com"  # 修改为你的API地址
    timeout: 30
```

## 第二步：编写测试用例

在 `data/test_cases/` 目录下创建 Excel 文件（例如 `test_cases.xlsx`），包含以下列：

| 测试用例ID | 模块 | 接口名称 | 请求地址 | 请求方法 | 参数类型 | 请求参数 | 状态码 | 是否运行 |
|-----------|------|---------|---------|---------|------------|---------|--------|---------|
| TEST001 | 用户 | 登录 | /api/login | POST | json | {"username":"test"} | 200 | Y |

**完整列定义**请参考：[README.md - Excel 用例编写规范](README.md#excel用例编写规范)

## 第三步：运行测试

```bash
# 运行 API 测试
pytest tests/test_api.py

# 查看报告
# HTML 报告自动生成在 reports/html/ 目录下
# 用浏览器打开最新的报告文件
```

## 常用命令

```bash
# 指定 Excel 文件
pytest tests/test_api.py --excel-files data/test_cases/test_cases.xlsx

# 指定 Sheet
pytest tests/test_api.py --sheet-names Sheet1

# 生成 HTML 报告
pytest tests/test_api.py --html=reports/html/report.html --self-contained-html
```

## 性能测试

```bash
# 运行性能测试（10并发，持续60秒）
pytest tests/test_performance.py

# 指定并发数和持续时间
pytest tests/test_performance.py --concurrent-users 50 --duration 300
```

## 下一步

- 📖 [阅读完整文档](README.md) 了解所有功能
- 📖 [学习性能测试](PERFORMANCE_TESTING.md) 进行压测
- 📖 [查看报告指南](REPORT_GUIDE.md) 理解测试报告
- 📖 [参考多Excel管理](MULTI_EXCEL_GUIDE.md) 组织用例

## 遇到问题？

- 查看 [CHANGELOG.md](CHANGELOG.md) 了解最新更新
- 检查 [config/config.yaml](config/config.yaml) 配置是否正确
- 确认 Excel 文件格式是否正确
