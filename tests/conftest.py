"""pytest配置文件"""
import pytest
import sys
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def pytest_addoption(parser):
    """添加命令行参数

    Args:
        parser: pytest参数解析器
    """
    parser.addoption(
        "--excel-files",
        action="store",
        default=None,
        help="指定要运行的Excel文件路径（逗号分隔）"
    )
    parser.addoption(
        "--sheet-names",
        action="store",
        default="all",
        help="指定要运行的sheet名称（逗号分隔），默认'all'执行所有sheet"
    )
    # 性能测试相关参数
    parser.addoption(
        "--concurrent-users",
        action="store",
        type=int,
        default=10,
        help="性能测试：并发用户数"
    )
    parser.addoption(
        "--duration",
        action="store",
        type=int,
        default=60,
        help="性能测试：测试持续时间（秒）"
    )
    parser.addoption(
        "--ramp-up",
        action="store",
        type=int,
        default=0,
        help="性能测试：启动时间（秒）"
    )


def pytest_configure(config):
    """pytest配置钩子

    Args:
        config: pytest配置对象
    """
    # 添加自定义标记
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "regression: 回归测试")

    # 动态设置报告路径（使用带时间戳的路径）
    from config.settings import settings

    # 设置HTML报告路径
    config.option.htmlpath = settings.html_report_file

    # 设置Allure报告路径
    config.option.allure_report_dir = settings.allure_report_dir

    # 输出报告路径信息
    logger.info(f"\n{'='*60}")
    logger.info(f"报告路径配置")
    logger.info(f"{'='*60}")
    logger.info(f"HTML报告: {settings.html_report_file}")
    logger.info(f"Allure报告: {settings.allure_report_dir}")
    logger.info(f"日志文件: {settings.log_file}")
    logger.info(f"{'='*60}\n")


@pytest.fixture(autouse=True)
def setup_test_environment():
    """测试环境设置

    在测试开始前初始化，测试结束后清理
    """
    # 测试开始
    logger.info("\n" + "=" * 60)
    logger.info("测试环境配置")
    logger.info("=" * 60)
    logger.info(f"当前环境: {settings.env}")
    logger.info(f"Base URL: {settings.base_url}")
    logger.info(f"超时时间: {settings.timeout}s")
    logger.info(f"Excel文件: {settings.excel_path}")
    logger.info(f"数据文件: {settings.extract_data_path}")
    logger.info("=" * 60 + "\n")

    yield

    # 测试结束
    logger.info("\n测试结束")


@pytest.fixture(scope="session")
def base_url():
    """获取base_url的fixture

    Returns:
        当前环境的base_url
    """
    return settings.base_url


@pytest.fixture(autouse=True)
def add_request_response_report(request):
    """为每个测试用例添加请求和响应报告的fixture

    自动捕获测试过程中的额外信息并添加到HTML报告中
    """
    # 测试开始
    request.node.report_setup = {}

    yield

    # 测试结束，添加额外信息到报告
    if hasattr(request.node, 'report_setup'):
        # 这里可以添加更多自定义信息
        pass


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """优化测试报告输出

    对自定义异常提供更清晰的输出

    Args:
        item: 测试项
        call: 测试调用信息
    """
    outcome = yield
    report = outcome.get_result()

    # 优化自定义异常的错误输出
    if report.when == "call" and report.failed:
        if call.excinfo:
            exc_type = call.excinfo.type
            exc_value = call.excinfo.value

            # 导入自定义异常类
            from utils.assertions import APIAssertionError

            # 如果是自定义异常，简化输出
            if issubclass(exc_type, APIAssertionError):
                # 直接使用异常的格式化消息
                report.longrepr = str(exc_value)
