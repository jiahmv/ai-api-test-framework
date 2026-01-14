"""测试执行主程序"""
import pytest
import json
import allure
from typing import List

from core.case_loader import CaseLoader, MultiFileCaseLoader, TestCase
from core.api_executor import APIExecutor
from core.data_extractor import DataExtractor
from core.data_manager import DataManager
from core.request_builder import RequestBuilder
from utils.assertions import Assertions
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def get_test_cases(excel_files: str = None, sheet_names: str = "all") -> List[TestCase]:
    """获取测试用例

    Args:
        excel_files: 指定的Excel文件路径（逗号分隔），默认为None加载所有
        sheet_names: 指定的sheet名称（逗号分隔），默认"all"加载所有sheet

    Returns:
        测试用例列表
    """
    # 处理sheet_names参数
    if sheet_names == "all":
        sheet_names_list = "all"
    else:
        sheet_names_list = [s.strip() for s in sheet_names.split(',')]

    if excel_files:
        # 用户指定了文件
        file_list = [f.strip() for f in excel_files.split(',')]
        logger.info(f"加载指定的Excel文件: {file_list}")
        logger.info(f"加载指定的sheet: {sheet_names}")
        loader = MultiFileCaseLoader(file_list, sheet_names_list)
        return loader.load_cases()
    else:
        # 加载配置中的所有文件
        logger.info(f"加载配置中的Excel文件: {settings.excel_path}")
        logger.info(f"加载指定的sheet: {sheet_names}")
        loader = CaseLoader(settings.excel_path, sheet_names_list)
        return loader.load_cases()


class TestAPI:
    """API测试类

    从Excel加载测试用例并执行
    """

    def pytest_generate_tests(self, metafunc):
        """动态生成测试用例

        支持通过命令行参数 --excel-files 选择文件
        支持通过命令行参数 --sheet-names 选择sheet

        Args:
            metafunc: pytest元函数对象
        """
        # 获取命令行参数
        excel_files = metafunc.config.getoption("--excel-files")
        sheet_names = metafunc.config.getoption("--sheet-names")

        # 加载测试用例
        cases = get_test_cases(excel_files, sheet_names)

        # 参数化测试用例
        metafunc.parametrize("case", cases, ids=[c.case_id for c in cases])

    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置设置

        在每个测试用例执行前初始化所需组件
        """
        self.data_manager = DataManager(settings.extract_data_path)
        self.extractor = DataExtractor(self.data_manager)
        self.request_builder = RequestBuilder(settings.base_url, self.data_manager)
        self.executor = APIExecutor(timeout=settings.timeout)
        self.assertions = Assertions()

        # 初始化请求和响应记录（用于HTML报告）
        self._last_request = {}
        self._last_response = {}

        yield

        # 测试后清理（可选）
        logger.debug("测试用例执行完成")

    def test_api_case(self, case):
        """测试单个API用例

        Args:
            case: 测试用例对象
        """
        # Allure测试用例基本信息
        allure.dynamic.title(f"[{case.case_id}] {case.api_name}")
        allure.dynamic.description(
            f"**模块**: {case.module}\n\n"
            f"**接口**: {case.api_name}\n\n"
            f"**用例ID**: {case.case_id}"
        )

        logger.info("\n" + "=" * 60)
        logger.info(f"执行测试用例: [{case.case_id}] {case.api_name}")
        logger.info(f"所属模块: {case.module}")
        logger.info("=" * 60)

        # 步骤1: 构建请求
        with allure.step("1. 构建请求"):
            url, method, headers, params = self.request_builder.build(case)

            # 记录请求信息（用于HTML报告）
            self._last_request = {
                'url': url,
                'method': method,
                'headers': headers,
                'params': params
            }

            # 记录请求信息到Allure报告
            allure.attach(
                f"{method} {url}",
                name="请求信息",
                attachment_type=allure.attachment_type.TEXT
            )

            # 记录请求头
            if headers:
                headers_json = json.dumps(headers, indent=2, ensure_ascii=False)
                allure.attach(
                    headers_json,
                    name="请求头",
                    attachment_type=allure.attachment_type.JSON
                )

            # 记录请求参数
            if params:
                params_json = json.dumps(params, indent=2, ensure_ascii=False)
                allure.attach(
                    params_json,
                    name="请求参数",
                    attachment_type=allure.attachment_type.JSON
                )

        # 步骤2: 执行请求
        with allure.step("2. 发送HTTP请求"):
            response = self.executor.execute(url, method, headers, params, case.param_type)

        # 步骤3: 记录响应信息
        with allure.step("3. 解析响应"):
            # 记录响应信息（用于HTML报告）
            self._last_response = response

            # 记录状态码
            allure.attach(
                str(response['status_code']),
                name="响应状态码",
                attachment_type=allure.attachment_type.TEXT
            )

            # 记录响应头
            if response.get('headers'):
                headers_json = json.dumps(
                    dict(list(response['headers'].items())[:10]),  # 只显示前10个
                    indent=2,
                    ensure_ascii=False
                )
                allure.attach(
                    headers_json,
                    name="响应头",
                    attachment_type=allure.attachment_type.JSON
                )

            # 记录响应体
            if response.get('body'):
                body_json = json.dumps(response['body'], indent=2, ensure_ascii=False)
                allure.attach(
                    body_json,
                    name="响应体",
                    attachment_type=allure.attachment_type.JSON
                )

            # 记录响应时间
            allure.attach(
                f"{response['response_time']:.3f}秒",
                name="响应时间",
                attachment_type=allure.attachment_type.TEXT
            )

        # 步骤4: 断言状态码
        with allure.step("4. 断言状态码"):
            # 传入响应体，以便断言失败时显示更多信息
            self.assertions.assert_status_code(
                response['status_code'],
                case.expected_status,
                response_body=response.get('body')
            )

        # 步骤5: 断言响应体
        with allure.step("5. 断言响应体"):
            try:
                expected_result = json.loads(case.expected_result) if case.expected_result else {}
                self.assertions.assert_response_body(response['body'], expected_result)
            except json.JSONDecodeError:
                logger.warning(f"期望结果JSON解析失败，跳过响应体断言: {case.expected_result}")

        # 步骤6: 提取并保存数据（如果有前置条件定义）
        if case.pre_condition:
            with allure.step("6. 提取并保存数据"):
                try:
                    extract_rules = json.loads(case.pre_condition)
                    extracted = self.extractor.extract_and_save(response['body'], extract_rules)
                    if extracted:
                        logger.info(f"提取并保存数据: {extracted}")
                        # 记录提取的数据到报告
                        extracted_json = json.dumps(extracted, indent=2, ensure_ascii=False)
                        allure.attach(
                            extracted_json,
                            name="提取的数据",
                            attachment_type=allure.attachment_type.JSON
                        )
                except json.JSONDecodeError:
                    logger.warning(f"前置条件JSON解析失败，跳过数据提取: {case.pre_condition}")

        logger.info("测试用例执行通过\n")


if __name__ == "__main__":
    # pytest.main([__file__, "-v", "--self-contained-html"])
    pytest.main([
        "--excel-files=data/test_cases/test_cases.xlsx",
        "-v",
        "--self-contained-html"
    ])

