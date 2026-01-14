"""数据管理器 - 处理提取数据的存储和读取"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class DataManager:
    """数据管理器

    负责从YAML文件读取和写入提取的数据，
    支持在测试用例之间共享数据
    """

    def __init__(self, data_file: str):
        """初始化数据管理器

        Args:
            data_file: YAML数据文件路径
        """
        self.data_file = Path(data_file)
        self.logger = logger
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """确保数据文件存在"""
        if not self.data_file.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            self.save({})
            self.logger.info(f"创建数据文件: {self.data_file}")

    def load(self) -> Dict[str, Any]:
        """加载提取的数据

        Returns:
            数据字典，文件不存在或为空时返回空字典
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except Exception as e:
            self.logger.error(f"加载数据文件失败: {e}")
            return {}

    def save(self, data: Dict[str, Any]):
        """保存提取的数据

        Args:
            data: 要保存的数据字典
        """
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
            self.logger.debug(f"保存数据到文件: {self.data_file}")
        except Exception as e:
            self.logger.error(f"保存数据文件失败: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """获取单个数据

        Args:
            key: 数据键名
            default: 默认值

        Returns:
            数据值，不存在时返回默认值
        """
        data = self.load()
        return data.get(key, default)

    def set(self, key: str, value: Any):
        """设置单个数据

        Args:
            key: 数据键名
            value: 数据值
        """
        data = self.load()
        data[key] = value
        self.save(data)
        self.logger.debug(f"设置数据: {key} = {value}")

    def update(self, new_data: Dict[str, Any]):
        """批量更新数据

        Args:
            new_data: 要更新的数据字典
        """
        if not new_data:
            return

        data = self.load()
        data.update(new_data)
        self.save(data)
        self.logger.debug(f"批量更新数据: {list(new_data.keys())}")

    def delete(self, key: str):
        """删除单个数据

        Args:
            key: 数据键名
        """
        data = self.load()
        if key in data:
            del data[key]
            self.save(data)
            self.logger.debug(f"删除数据: {key}")

    def clear(self):
        """清空所有数据"""
        self.save({})
        self.logger.info("清空所有数据")
