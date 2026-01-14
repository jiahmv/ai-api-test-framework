"""性能测试执行入口"""
import pytest
import json
from typing import List, Dict, Any

from core.case_loader import CaseLoader, TestCase
from core.performance_executor import PerformanceExecutor
from core.request_builder import RequestBuilder
from core.data_manager import DataManager
from utils.performance_reporter import PerformanceReporter
from utils.assertions import Assertions
from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class TestPerformance:
    """性能测试类"""

    def __init__(self):
        """初始化性能测试"""
        self.settings = Settings()
        self.assertions = Assertions()

    def execute_performance_test(self,
                                 excel_files: str = None,
                                 sheet_names: str = "all",
                                 concurrent_users: int = 10,
                                 duration: int = 60,
                                 ramp_up: int = 0):
        """执行性能测试

        Args:
            excel_files: Excel文件路径（逗号分隔）
            sheet_names: Sheet名称（逗号分隔）
            concurrent_users: 并发用户数
            duration: 测试持续时间（秒）
            ramp_up: 启动时间（秒）

        Returns:
            性能测试结果
        """
        logger.info(f"开始性能测试: 并发数={concurrent_users}, 持续时间={duration}秒")

        # 加载测试用例
        if excel_files:
            files = excel_files.split(',')
        else:
            files = [self.settings.excel_path]

        all_cases = []
        for file in files:
            loader = CaseLoader(file.strip(), sheet_names)
            cases = loader.load_cases()
            all_cases.extend(cases)

        if not all_cases:
            raise ValueError("没有找到测试用例")

        logger.info(f"加载了 {len(all_cases)} 个测试用例")

        # 初始化数据管理器
        data_manager = DataManager(self.settings.extract_data_path)

        # 创建性能测试执行器
        executor = PerformanceExecutor(
            max_workers=concurrent_users,
            duration=duration,
            ramp_up=ramp_up
        )
        executor.configure(self.settings.base_url, data_manager)

        # 执行性能测试
        result = executor.execute_performance_test(all_cases)

        # 生成报告
        reporter = PerformanceReporter()
        test_config = {
            'concurrent_users': concurrent_users,
            'duration': duration,
            'ramp_up': ramp_up,
            'total_cases': len(all_cases)
        }

        html_report = reporter.generate_html_report(result, test_config)
        json_report = reporter.generate_json_report(result, test_config)

        logger.info(f"HTML报告: {html_report}")
        logger.info(f"JSON报告: {json_report}")

        # 检查性能阈值（如果有配置）
        self._check_performance_thresholds(result, all_cases)

        return result

    def _check_performance_thresholds(self, result, test_cases: List[TestCase]):
        """检查性能阈值

        Args:
            result: 性能测试结果
            test_cases: 测试用例列表
        """
        for case in test_cases:
            # 检查用例级别的最大响应时间
            if case.max_response_time > 0:
                case_stat = result.case_stats.get(case.case_id, {})
                if case_stat.get('response_times'):
                    avg_time = sum(case_stat['response_times']) / len(case_stat['response_times'])
                    max_time = case.max_response_time / 1000.0  # 转换为秒

                    try:
                        self.assertions.assert_response_time(
                            avg_time,
                            max_time,
                            'less',
                            case.case_id
                        )
                    except Exception as e:
                        logger.warning(f"用例 {case.case_id} 性能阈值检查失败: {e}")

            # 检查性能配置中的阈值
            if case.performance_config and case.performance_config != "{}":
                try:
                    perf_config = json.loads(case.performance_config)
                    thresholds = perf_config.get('thresholds', {})

                    if thresholds:
                        case_stat = result.case_stats.get(case.case_id, {})
                        metrics = {}

                        # 计算用例级别的指标
                        if case_stat.get('response_times'):
                            import statistics
                            response_times = case_stat['response_times']
                            metrics['avg_time'] = statistics.mean(response_times)
                            if len(response_times) >= 20:
                                metrics['p95_time'] = statistics.quantiles(response_times, n=20)[18]
                            if len(response_times) >= 100:
                                metrics['p99_time'] = statistics.quantiles(response_times, n=100)[98]

                        metrics['success_rate'] = (
                            case_stat.get('success_count', 0) / case_stat.get('count', 1)
                        )

                        # 执行断言
                        self.assertions.assert_performance_metrics(metrics, thresholds)
                except Exception as e:
                    logger.warning(f"用例 {case.case_id} 性能配置解析失败: {e}")


@pytest.fixture(scope="session")
def performance_test():
    """性能测试fixture"""
    return TestPerformance()


def test_performance(performance_test, pytestconfig):
    """性能测试主函数

    使用示例:
        pytest tests/test_performance.py --concurrent-users 50 --duration 300
        pytest tests/test_performance.py --excel-files perf_cases.xlsx --concurrent-users 100
    """
    excel_files = pytestconfig.getoption("--excel-files")
    sheet_names = pytestconfig.getoption("--sheet-names")
    concurrent_users = pytestconfig.getoption("--concurrent-users")
    duration = pytestconfig.getoption("--duration")
    ramp_up = pytestconfig.getoption("--ramp-up")

    result = performance_test.execute_performance_test(
        excel_files=excel_files,
        sheet_names=sheet_names,
        concurrent_users=concurrent_users,
        duration=duration,
        ramp_up=ramp_up
    )

    # 断言：确保测试成功执行
    assert result.total_requests > 0, "没有执行任何请求"
    assert result.success_count > 0, "所有请求都失败了"

    logger.info("性能测试完成")

# pytest tests/test_performance.py --excel-files data/test_cases/demo_cases.xlsx --sheet-names Sheet1

