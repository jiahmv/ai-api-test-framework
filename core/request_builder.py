"""请求构建器 - 构建HTTP请求"""
import json
import re
from typing import Dict, Any, Tuple
from urllib.parse import urljoin

from core.case_loader import TestCase
from core.data_manager import DataManager
from utils.logger import get_logger

logger = get_logger(__name__)


class RequestBuilder:
    """请求构建器

    负责构建HTTP请求，包括URL拼接、请求头解析、
    参数处理和参数化替换
    """

    def __init__(self, base_url: str, data_manager: DataManager):
        """初始化请求构建器

        Args:
            base_url: 基础URL
            data_manager: 数据管理器实例
        """
        self.base_url = base_url
        self.data_manager = data_manager
        self.logger = logger

    def build(self, case: TestCase) -> Tuple[str, str, Dict, Any]:
        """构建请求

        Args:
            case: 测试用例对象

        Returns:
            (完整URL, 请求方法, 请求头, 请求参数) 元组
        """
        # 构建完整URL
        url = self._build_url(case.url)

        # 处理请求头
        headers = self._parse_headers(case.headers)

        # 处理请求参数
        params = self._parse_params(case.params, case.param_type)

        # 参数化替换
        url = self._replace_placeholders(url)
        headers = self._replace_placeholders_dict(headers)
        params = self._replace_placeholders_dict(params)

        self.logger.info(f"构建请求: {case.method} {url}")
        self.logger.debug(f"请求头: {headers}")
        self.logger.debug(f"请求参数: {params}")

        return url, case.method, headers, params

    def _build_url(self, path: str) -> str:
        """构建完整URL

        Args:
            path: 相对路径或完整URL

        Returns:
            完整URL
        """
        # 如果已经是完整URL，直接返回
        if path.startswith('http://') or path.startswith('https://'):
            return path

        # 拼接base_url和相对路径
        return urljoin(self.base_url, path)

    def _parse_headers(self, headers_str: str) -> Dict[str, str]:
        """解析请求头

        Args:
            headers_str: 请求头JSON字符串

        Returns:
            请求头字典
        """
        try:
            if not headers_str or headers_str.strip() == '{}':
                return {}
            return json.loads(headers_str)
        except json.JSONDecodeError as e:
            self.logger.warning(f"请求头JSON解析失败: {e}, 使用空字典")
            return {}

    def _parse_params(self, params_str: str, param_type: str) -> Any:
        """解析请求参数

        Args:
            params_str: 参数JSON字符串
            param_type: 参数类型（params/data/json）

        Returns:
            解析后的参数对象
        """
        try:
            if not params_str or params_str.strip() == '{}':
                return {}

            return json.loads(params_str)
        except json.JSONDecodeError as e:
            self.logger.warning(f"参数JSON解析失败: {e}, 使用空字典")
            return {}

    def _replace_placeholders(self, text: str) -> str:
        """替换文本中的占位符

        支持 ${variable_name} 格式的占位符

        Args:
            text: 包含占位符的文本

        Returns:
            替换后的文本
        """
        if not text or not isinstance(text, str):
            return text

        # 匹配 ${variable_name} 格式
        pattern = r'\$\{(\w+)\}'

        def replacer(match):
            var_name = match.group(1)
            value = self.data_manager.get(var_name)
            if value is not None:
                self.logger.debug(f"替换占位符: ${{{var_name}}} -> {value}")
                return str(value)
            else:
                self.logger.warning(f"未找到占位符对应的值: ${{{var_name}}}")
                return match.group(0)

        return re.sub(pattern, replacer, text)

    def _replace_placeholders_dict(self, data: Any) -> Any:
        """替换字典中的占位符（递归）

        Args:
            data: 数据对象（字典、列表或字符串）

        Returns:
            替换后的数据
        """
        if not isinstance(data, dict):
            return data

        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                # 字符串类型，替换占位符
                result[key] = self._replace_placeholders(value)
            elif isinstance(value, dict):
                # 字典类型，递归替换
                result[key] = self._replace_placeholders_dict(value)
            elif isinstance(value, list):
                # 列表类型，处理每个元素
                result[key] = [
                    self._replace_placeholders(item) if isinstance(item, str)
                    else self._replace_placeholders_dict(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                # 其他类型，保持原样
                result[key] = value

        return result
