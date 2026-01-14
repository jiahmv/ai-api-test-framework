"""断言工具"""
import json
from typing import Dict, Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class APIAssertionError(AssertionError):
    """API测试断言错误基类

    提供更结构化的错误信息，便于阅读和调试
    """

    def __init__(self, message: str, **context):
        """初始化断言错误

        Args:
            message: 错误消息
            **context: 错误上下文信息
        """
        self.message = message
        self.context = context

        # 构建完整的错误消息
        full_message = self._format_message()
        super().__init__(full_message)

    def _format_message(self) -> str:
        """格式化错误消息"""
        msg = [f"[ERROR] {self.message}"]

        # 添加上下文信息
        if self.context:
            msg.append("\n[Details]")
            for key, value in self.context.items():
                if isinstance(value, (dict, list)):
                    # JSON格式化
                    value_str = json.dumps(value, indent=2, ensure_ascii=False)
                    msg.append(f"  - {key}:\n{self._indent(value_str, '    ')}")
                else:
                    msg.append(f"  - {key}: {value}")

        return "\n".join(msg)

    @staticmethod
    def _indent(text: str, prefix: str) -> str:
        """缩进多行文本"""
        lines = text.split('\n')
        return '\n'.join(prefix + line if line else prefix for line in lines)


class StatusCodeError(APIAssertionError):
    """状态码断言错误"""

    def __init__(self, expected: int, actual: int, response_body: Any = None):
        super().__init__(
            f"HTTP状态码不匹配",
            expected_status=expected,
            actual_status=actual,
            response_body=response_body
        )


class ResponseBodyError(APIAssertionError):
    """响应体断言错误"""

    def __init__(self, field: str, expected: Any, actual: Any, full_response: Any = None):
        super().__init__(
            f"响应字段 '{field}' 不匹配",
            field=field,
            expected_value=expected,
            actual_value=actual,
            response_context=full_response
        )


class MissingFieldError(APIAssertionError):
    """缺少字段错误"""

    def __init__(self, field: str, available_fields: list = None):
        super().__init__(
            f"响应中缺少字段 '{field}'",
            missing_field=field,
            available_fields=available_fields or []
        )


class PerformanceAssertionError(APIAssertionError):
    """性能断言错误

    当响应时间或其他性能指标不符合预期时抛出
    """

    def __init__(self, message: str, actual_time: float, expected_time: float,
                 metric: str = "response_time"):
        """初始化性能断言错误

        Args:
            message: 错误消息
            actual_time: 实际响应时间（秒）
            expected_time: 期望响应时间（秒）
            metric: 性能指标类型
        """
        super().__init__(
            message,
            metric=metric,
            actual_time=f"{actual_time:.3f}s",
            expected_time=f"{expected_time:.3f}s",
            diff=f"{(actual_time - expected_time):.3f}s"
        )


class Assertions:
    """断言工具类

    提供各种断言方法，使用自定义异常提供清晰的错误信息
    """

    def __init__(self):
        """初始化断言工具"""
        self.logger = logger

    def assert_status_code(self, actual: int, expected: int, response_body: Any = None):
        """断言HTTP状态码

        Args:
            actual: 实际状态码
            expected: 期望状态码
            response_body: 响应体（可选，用于错误时显示）

        Raises:
            StatusCodeError: 状态码不匹配
        """
        if actual != expected:
            raise StatusCodeError(expected, actual, response_body)

        self.logger.info(f"状态码断言通过: {actual}")

    def assert_response_body(self, actual: Dict[str, Any], expected: Dict[str, Any]):
        """断言响应体

        验证实际响应体中是否包含期望的字段和值

        Args:
            actual: 实际响应体
            expected: 期望响应体（需要验证的字段）

        Raises:
            MissingFieldError: 缺少字段
            ResponseBodyError: 字段值不匹配
        """
        if not expected:
            self.logger.info("无期望结果，跳过响应体断言")
            return

        # 遍历期望结果进行断言
        for key, expected_value in expected.items():
            if key not in actual:
                raise MissingFieldError(key, list(actual.keys()) if actual else None)

            actual_value = actual[key]
            if actual_value != expected_value:
                raise ResponseBodyError(key, expected_value, actual_value, actual)

        self.logger.info(f"响应体断言通过，验证了 {len(expected)} 个字段")

    def assert_contains(self, actual: Any, expected: Any):
        """断言包含关系

        Args:
            actual: 实际值（字符串或容器）
            expected: 期望包含的值

        Raises:
            AssertionError: 不包含
        """
        if isinstance(actual, str):
            if expected not in actual:
                raise AssertionError(
                    f"字符串不包含期望值\n期望: '{expected}'\n实际: '{actual}'"
                )
        else:
            if expected not in actual:
                raise AssertionError(
                    f"容器不包含期望值\n期望: {expected}\n实际: {actual}"
                )

        self.logger.info(f"包含断言通过: {expected}")

    def assert_schema(self, response_body: Dict[str, Any], schema: Dict[str, Any]):
        """断言JSON Schema

        验证响应体是否符合指定的Schema

        Args:
            response_body: 响应体
            schema: JSON Schema（字段类型定义）

        Raises:
            MissingFieldError: 缺少字段
            AssertionError: 类型不匹配
        """
        for key, expected_type in schema.items():
            if key not in response_body:
                raise MissingFieldError(key, list(response_body.keys()))

            actual_value = response_body[key]
            actual_type = type(actual_value).__name__

            if actual_type != expected_type:
                raise AssertionError(
                    f"字段 '{key}' 类型不匹配\n"
                    f"期望类型: {expected_type}\n"
                    f"实际类型: {actual_type}\n"
                    f"实际值: {actual_value}"
                )

        self.logger.info(f"Schema断言通过，验证了 {len(schema)} 个字段")

    def assert_response_time(self, actual_time: float, expected_time: float,
                            comparison: str = 'less', case_id: str = None):
        """断言响应时间

        Args:
            actual_time: 实际响应时间（秒）
            expected_time: 期望响应时间（秒）
            comparison: 比较方式 ('less' 或 'greater')
            case_id: 测试用例ID（可选）

        Raises:
            PerformanceAssertionError: 响应时间不符合预期
        """
        if comparison == 'less' and actual_time > expected_time:
            case_info = f"[{case_id}] " if case_id else ""
            raise PerformanceAssertionError(
                f"{case_info}响应时间超过阈值",
                actual_time=actual_time,
                expected_time=expected_time,
                metric="response_time"
            )
        elif comparison == 'greater' and actual_time < expected_time:
            case_info = f"[{case_id}] " if case_id else ""
            raise PerformanceAssertionError(
                f"{case_info}响应时间低于最小值",
                actual_time=actual_time,
                expected_time=expected_time,
                metric="response_time"
            )

        self.logger.info(f"响应时间断言通过: {actual_time:.3f}s (期望: {comparison} {expected_time:.3f}s)")

    def assert_performance_metrics(self, metrics: Dict[str, Any],
                                   thresholds: Dict[str, float]):
        """断言性能指标

        Args:
            metrics: 性能指标字典，包含:
                - avg_time: 平均响应时间
                - p95_time: P95响应时间
                - p99_time: P99响应时间
                - success_rate: 成功率
            thresholds: 阈值字典

        Raises:
            PerformanceAssertionError: 性能指标不符合预期
        """
        # 检查平均响应时间
        if 'avg_time' in thresholds:
            if metrics.get('avg_time', 0) > thresholds['avg_time']:
                raise PerformanceAssertionError(
                    "平均响应时间超过阈值",
                    actual_time=metrics.get('avg_time', 0),
                    expected_time=thresholds['avg_time'],
                    metric="avg_response_time"
                )

        # 检查P95响应时间
        if 'p95_time' in thresholds:
            if metrics.get('p95_time', 0) > thresholds['p95_time']:
                raise PerformanceAssertionError(
                    "P95响应时间超过阈值",
                    actual_time=metrics.get('p95_time', 0),
                    expected_time=thresholds['p95_time'],
                    metric="p95_response_time"
                )

        # 检查成功率
        if 'success_rate' in thresholds:
            if metrics.get('success_rate', 0) < thresholds['success_rate']:
                raise PerformanceAssertionError(
                    f"成功率低于阈值",
                    actual_time=metrics.get('success_rate', 0),
                    expected_time=thresholds['success_rate'],
                    metric="success_rate"
                )

        self.logger.info("性能指标断言通过")
