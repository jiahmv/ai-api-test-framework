"""性能测试执行器 - 支持并发执行和性能统计"""
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import statistics

from utils.logger import get_logger
from core.api_executor import APIExecutor
from core.request_builder import RequestBuilder
from core.data_manager import DataManager

logger = get_logger(__name__)


@dataclass
class PerformanceResult:
    """性能测试结果"""

    # 基本统计
    total_requests: int = 0
    success_count: int = 0
    failure_count: int = 0

    # 响应时间统计（秒）
    response_times: List[float] = field(default_factory=list)
    min_time: float = 0.0
    max_time: float = 0.0
    avg_time: float = 0.0
    median_time: float = 0.0
    p95_time: float = 0.0
    p99_time: float = 0.0

    # 吞吐量
    tps: float = 0.0  # 每秒事务数
    actual_duration: float = 0.0  # 实际测试时长（秒）

    # 错误统计
    errors: Dict[str, int] = field(default_factory=dict)

    # 每个用例的详细统计
    case_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def calculate_statistics(self):
        """计算性能统计指标"""
        if not self.response_times:
            return

        self.min_time = min(self.response_times)
        self.max_time = max(self.response_times)
        self.avg_time = statistics.mean(self.response_times)
        self.median_time = statistics.median(self.response_times)
        self.p95_time = statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else self.max_time
        self.p99_time = statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) >= 100 else self.max_time

    def calculate_tps(self, duration: float):
        """计算TPS

        Args:
            duration: 测试时长（秒）
        """
        if duration > 0:
            self.tps = self.success_count / duration
        self.actual_duration = duration


class PerformanceExecutor:
    """性能测试执行器

    支持并发执行测试用例，收集性能指标
    """

    def __init__(self, max_workers: int = 10,
                 duration: int = 60,
                 ramp_up: int = 0):
        """初始化性能测试执行器

        Args:
            max_workers: 最大并发数
            duration: 测试持续时间（秒）
            ramp_up: 启动时间（秒），在此时间内逐步增加并发
        """
        self.max_workers = max_workers
        self.duration = duration
        self.ramp_up = ramp_up
        self.logger = logger

        # 线程安全锁
        self.lock = threading.Lock()

        # 初始化组件
        self.api_executor = APIExecutor()
        self.request_builder = None
        self.data_manager = None

    def configure(self, base_url: str, data_manager: DataManager = None):
        """配置执行器

        Args:
            base_url: 基础URL
            data_manager: 数据管理器（可选，如果为None则创建一个临时的）
        """
        # 如果没有提供data_manager，创建一个临时的
        if data_manager is None:
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
            temp_file.write('{}')
            temp_file.close()
            data_manager = DataManager(temp_file.name)

        self.request_builder = RequestBuilder(base_url, data_manager)
        self.data_manager = data_manager

    def execute_performance_test(self,
                                 test_cases: List[Any],
                                 execute_func: Optional[Callable] = None) -> PerformanceResult:
        """执行性能测试

        Args:
            test_cases: 测试用例列表
            execute_func: 自定义执行函数（可选）

        Returns:
            PerformanceResult: 性能测试结果
        """
        if not test_cases:
            raise ValueError("测试用例列表为空")

        self.logger.info(f"开始性能测试: 并发数={self.max_workers}, 持续时间={self.duration}秒")

        result = PerformanceResult()
        start_time = time.time()

        # 使用线程池并发执行
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            # 根据持续时间计算需要执行多少轮
            if self.duration > 0:
                # 持续时间模式：循环执行用例直到时间结束
                elapsed = 0
                round_num = 0
                while elapsed < self.duration:
                    round_start = time.time()

                    # 提交本轮所有用例
                    for case in test_cases:
                        future = executor.submit(
                            self._execute_single_case,
                            case,
                            execute_func,
                            round_num
                        )
                        futures.append(future)

                    # 等待本轮完成
                    for future in as_completed(futures):
                        try:
                            case_result = future.result()
                            with self.lock:
                                self._update_result(result, case_result)
                        except Exception as e:
                            self.logger.error(f"用例执行异常: {e}")
                            with self.lock:
                                result.failure_count += 1

                    futures.clear()

                    # 更新已用时间
                    round_elapsed = time.time() - round_start
                    elapsed = time.time() - start_time
                    round_num += 1

                    self.logger.info(f"完成第 {round_num} 轮，已用时 {elapsed:.1f}秒")
            else:
                # 固定次数模式：每个用例执行一次
                for case in test_cases:
                    future = executor.submit(
                        self._execute_single_case,
                        case,
                        execute_func,
                        0
                    )
                    futures.append(future)

                # 收集结果
                for future in as_completed(futures):
                    try:
                        case_result = future.result()
                        with self.lock:
                            self._update_result(result, case_result)
                    except Exception as e:
                        self.logger.error(f"用例执行异常: {e}")
                        with self.lock:
                            result.failure_count += 1

        # 计算最终统计
        actual_duration = time.time() - start_time
        result.total_requests = result.success_count + result.failure_count
        result.calculate_statistics()
        result.calculate_tps(actual_duration)

        self.logger.info(
            f"性能测试完成: 总请求数={result.total_requests}, "
            f"成功={result.success_count}, 失败={result.failure_count}, "
            f"平均响应时间={result.avg_time:.3f}s, TPS={result.tps:.2f}"
        )

        return result

    def _execute_single_case(self, case: Any, execute_func: Optional[Callable], round_num: int) -> Dict[str, Any]:
        """执行单个测试用例

        Args:
            case: 测试用例
            execute_func: 自定义执行函数
            round_num: 轮次编号

        Returns:
            用例执行结果
        """
        case_id = getattr(case, 'case_id', 'unknown')

        try:
            if execute_func:
                # 使用自定义执行函数
                return execute_func(case)
            else:
                # 使用默认执行逻辑
                return self._default_execute(case)

        except Exception as e:
            self.logger.error(f"用例 {case_id} 执行失败: {e}")
            return {
                'case_id': case_id,
                'success': False,
                'error': str(e),
                'response_time': 0.0
            }

    def _default_execute(self, case: Any) -> Dict[str, Any]:
        """默认执行逻辑

        Args:
            case: 测试用例

        Returns:
            执行结果
        """
        # 构建请求
        url = self.request_builder._build_url(case.url)
        headers = self.request_builder._parse_headers(case.headers)
        params = self.request_builder._parse_params(case.params, case.param_type)

        # 执行请求
        response = self.api_executor.execute(
            url=url,
            method=case.method,
            headers=headers,
            params=params,
            param_type=case.param_type
        )

        return {
            'case_id': case.case_id,
            'success': response['status_code'] == case.expected_status,
            'status_code': response['status_code'],
            'response_time': response.get('response_time', 0.0),
            'response_body': response.get('body')
        }

    def _update_result(self, result: PerformanceResult, case_result: Dict[str, Any]):
        """更新结果统计

        Args:
            result: 性能结果对象
            case_result: 用例执行结果
        """
        case_id = case_result.get('case_id', 'unknown')

        # 更新总体统计
        if case_result.get('success', False):
            result.success_count += 1
        else:
            result.failure_count += 1

            # 记录错误
            error_msg = case_result.get('error', 'unknown error')
            result.errors[error_msg] = result.errors.get(error_msg, 0) + 1

        # 记录响应时间
        response_time = case_result.get('response_time', 0.0)
        result.response_times.append(response_time)

        # 更新用例级别统计
        if case_id not in result.case_stats:
            result.case_stats[case_id] = {
                'count': 0,
                'success_count': 0,
                'response_times': []
            }

        result.case_stats[case_id]['count'] += 1
        if case_result.get('success', False):
            result.case_stats[case_id]['success_count'] += 1
        result.case_stats[case_id]['response_times'].append(response_time)

    def execute_concurrent_test(self,
                                test_cases: List[Any],
                                iterations: int = 1) -> PerformanceResult:
        """执行并发测试（固定次数）

        Args:
            test_cases: 测试用例列表
            iterations: 每个用例的重复执行次数

        Returns:
            PerformanceResult: 性能测试结果
        """
        self.logger.info(f"开始并发测试: 并发数={self.max_workers}, 每个用例重复{iterations}次")

        # 构建完整的用例列表（每个用例重复N次）
        all_cases = []
        for _ in range(iterations):
            all_cases.extend(test_cases)

        # 执行测试（不设置持续时间）
        original_duration = self.duration
        self.duration = 0  # 禁用持续时间模式

        try:
            result = self.execute_performance_test(all_cases)
        finally:
            self.duration = original_duration  # 恢复原始设置

        return result
