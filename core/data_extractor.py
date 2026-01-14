"""数据提取器 - 从响应中提取数据"""
import json
import re
from typing import Dict, Any

from core.data_manager import DataManager
from utils.logger import get_logger

logger = get_logger(__name__)


class DataExtractor:
    """数据提取器

    从HTTP响应中提取数据并保存到YAML文件，
    支持JSON路径和正则表达式两种提取方式
    """

    def __init__(self, data_manager: DataManager):
        """初始化数据提取器

        Args:
            data_manager: 数据管理器实例
        """
        self.data_manager = data_manager
        self.logger = logger

    def extract_and_save(self, response_data: Any, extract_rules: Dict[str, str]) -> Dict[str, Any]:
        """从响应中提取数据并保存

        Args:
            response_data: 响应数据
            extract_rules: 提取规则字典
                格式: {"变量名": "提取规则"}
                示例:
                - JSON路径: {"user_id": "data.user.id", "token": "data.token"}
                - 正则表达式: {"code": '"code": (\\d+)'}

        Returns:
            提取的数据字典
        """
        if not extract_rules:
            self.logger.debug("无提取规则，跳过数据提取")
            return {}

        extracted = {}

        for var_name, rule in extract_rules.items():
            try:
                value = self._extract_value(response_data, rule)
                if value is not None:
                    extracted[var_name] = value
                    self.logger.info(f"提取数据: {var_name} = {value}")
                else:
                    self.logger.warning(f"提取失败: {var_name} (规则: {rule})")
            except Exception as e:
                self.logger.error(f"提取数据异常: {var_name}, 错误: {e}")

        # 保存到yaml文件
        if extracted:
            self.data_manager.update(extracted)

        return extracted

    def _extract_value(self, data: Any, rule: str) -> Any:
        """根据规则提取值

        Args:
            data: 响应数据
            rule: 提取规则

        Returns:
            提取的值，失败返回None
        """
        # 尝试直接键名提取 (如: id, token)
        if isinstance(data, dict) and rule in data:
            return data[rule]

        # 尝试JSON路径提取 (如: data.user.id)
        if '.' in rule and not rule.startswith('$'):
            return self._extract_by_path(data, rule)

        # 尝试正则表达式提取
        return self._extract_by_regex(data, rule)

    def _extract_by_path(self, data: Any, path: str) -> Any:
        """通过JSON路径提取数据

        支持格式:
        - data.user.id
        - data.list.0 (访问数组元素)

        Args:
            data: 响应数据
            path: JSON路径

        Returns:
            提取的值，失败返回None
        """
        try:
            keys = path.split('.')
            current = data

            for key in keys:
                if isinstance(current, dict):
                    current = current.get(key)
                elif isinstance(current, list) and key.isdigit():
                    index = int(key)
                    current = current[index] if index < len(current) else None
                else:
                    return None

                if current is None:
                    return None

            return current

        except Exception as e:
            self.logger.debug(f"JSON路径提取失败: {path}, 错误: {e}")
            return None

    def _extract_by_regex(self, data: Any, pattern: str) -> Any:
        """通过正则表达式提取数据

        Args:
            data: 响应数据
            pattern: 正则表达式

        Returns:
            提取的值，失败返回None
        """
        try:
            # 将数据转换为字符串
            text = json.dumps(data, ensure_ascii=False)
            match = re.search(pattern, text)

            if match:
                return match.group(1) if match.groups() else match.group(0)

            return None

        except Exception as e:
            self.logger.debug(f"正则提取失败: {pattern}, 错误: {e}")
            return None
