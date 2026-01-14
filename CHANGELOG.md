# 更新日志

本文档记录 AI API 测试框架的所有重要变更。

## [1.1.0] - 2024-01-14

### 新增
- 🚀 **性能测试功能**
  - 支持并发压力测试（多线程并发执行）
  - 响应时间统计（最小、最大、平均、中位数、P95、P99）
  - 性能阈值断言（响应时间、成功率、TPS）
  - HTML 和 JSON 格式的性能报告
  - Excel 配置化性能测试（支持性能配置列和最大响应时间列）
- 新增性能测试命令行参数：
  - `--concurrent-users`: 并发用户数
  - `--duration`: 测试持续时间（秒）
  - `--ramp-up`: 启动时间（秒）

### 改进
- ✨ 优化测试运行方式说明
  - 区分运行指定测试文件和运行所有测试两种方式
  - 提供更清晰的命令示例和使用场景说明
- ✨ 更新文档结构
  - 添加文档目录索引，方便快速查找
  - 创建快速入门指南（QUICK_START.md）
  - 归档开发记录文档到 docs/development/
- ✨ 建立版本更新日志机制

### 修复
- 🐛 修复 PerformanceExecutor 中 DataManager 可选参数处理问题
- 🐛 修复 RequestBuilder 方法调用错误（私有方法命名）
- 🐛 修复 Settings 属性名称错误（excel_path 和 extract_data_path）
- 🐛 修复 pytest_addoption 函数重复定义问题

### 文档
- 📝 新增性能测试完整指南（PERFORMANCE_TESTING.md）
- 📝 新增性能测试快速参考（PERFORMANCE_QUICK_REFERENCE.md）
- 📝 新增 Bug 修复报告（BUG_FIX_REPORT.md）
- 📝 更新 README.md，添加性能测试功能说明

## [1.0.0] - 初始版本

### 功能
- ✨ Excel 用例管理（可视化编辑，无需编写代码）
- ✨ 多环境配置（开发、测试、生产环境切换）
- ✨ 参数化数据依赖（`${variable}` 语法）
- ✨ 数据提取功能（从响应中提取数据供后续用例使用）
- ✨ 多 Sheet 支持（按模块管理测试用例）
- ✨ 多 Excel 文件支持（灵活的用例组织方式）
- ✨ HTML 和 Allure 测试报告
- ✨ 完整的日志系统（自动归档，带时间戳）

### 测试框架
- pytest 7.4.3 - 测试执行框架
- requests 2.31.0 - HTTP 请求库
- openpyxl 3.1.2 - Excel 处理
- PyYAML 6.0.1 - YAML 配置管理
- loguru 0.7.2 - 日志记录

### 报告
- pytest-html 4.1.1 - HTML 测试报告
- allure-pytest 2.13.5 - Allure 报告

---

## 版本命名规则

- **主版本号（Major）**：重大架构变更或不兼容的 API 修改
- **次版本号（Minor）**：向后兼容的功能新增
- **修订号（Patch）**：向后兼容的问题修复

## 更新时间线

```
2024-01-14  v1.1.0  性能测试功能
????-??-??  v1.0.0  初始版本
```
