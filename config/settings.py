"""配置加载器"""
import yaml
from pathlib import Path
from typing import Dict, Any
from utils.path_helper import PathHelper


class Settings:
    """配置管理类"""

    def __init__(self, config_path: str = None):
        """初始化配置

        Args:
            config_path: 配置文件路径，默认为 config/config.yaml
        """
        self.config_path = config_path or self._get_default_config_path()
        self._config = self._load_config()

        # 初始化时创建带时间戳的目录
        self._init_timestamped_dirs()

    def _init_timestamped_dirs(self):
        """初始化带时间戳的目录和文件"""
        # 获取项目根目录
        project_root = Path(__file__).parent.parent

        # HTML报告：直接在html目录下创建带时间戳的文件
        self._html_report_file = PathHelper.create_timestamped_file(
            str(project_root / "reports" / "html"),
            filename="report",
            extension="html"
        )

        # Allure报告：创建带时间戳的子目录
        self._allure_report_dir = PathHelper.create_timestamped_dir(
            str(project_root / "reports" / "allure"),
            prefix="allure"
        )

        # 日志文件：直接在logs目录下创建带时间戳的文件
        self._log_file = PathHelper.create_timestamped_file(
            str(project_root / "logs"),
            filename="api-log",
            extension="log"
        )

    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        # 获取项目根目录
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        return str(project_root / "config" / "config.yaml")

    def _load_config(self) -> Dict[str, Any]:
        """加载YAML配置文件

        Returns:
            配置字典
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")

    @property
    def env(self) -> str:
        """获取当前环境"""
        return self._config.get('env', {}).get('current', 'dev')

    @property
    def base_url(self) -> str:
        """获取当前环境的base_url"""
        return self._config.get('environments', {}).get(self.env, {}).get('base_url', '')

    @property
    def timeout(self) -> int:
        """获取超时时间"""
        return self._config.get('environments', {}).get(self.env, {}).get('timeout', 30)

    @property
    def default_headers(self) -> Dict[str, str]:
        """获取默认请求头"""
        return self._config.get('environments', {}).get(self.env, {}).get('headers', {})

    @property
    def excel_path(self) -> str:
        """获取Excel文件路径"""
        path_str = self._config.get('excel', {}).get('file_path', 'data/test_cases/test_cases.xlsx')
        # 转换为绝对路径
        project_root = Path(__file__).parent.parent
        return str(project_root / path_str)

    @property
    def excel_sheet_name(self) -> str:
        """获取Excel sheet名称"""
        return self._config.get('excel', {}).get('sheet_name', 'Sheet1')

    @property
    def extract_data_path(self) -> str:
        """获取提取数据存储路径"""
        path_str = self._config.get('extract', {}).get('file_path', 'data/extract_data/extract_data.yaml')
        # 转换为绝对路径
        project_root = Path(__file__).parent.parent
        return str(project_root / path_str)

    @property
    def log_level(self) -> str:
        """获取日志级别"""
        return self._config.get('log', {}).get('level', 'INFO')

    @property
    def log_format(self) -> str:
        """获取日志格式"""
        return self._config.get('log', {}).get(
            'format',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    @property
    def log_file(self) -> str:
        """获取日志文件路径（带时间戳）"""
        return str(self._log_file)

    @property
    def html_report_file(self) -> str:
        """获取HTML报告文件路径（带时间戳）"""
        return str(self._html_report_file)

    @property
    def allure_report_dir(self) -> str:
        """获取Allure报告目录路径（带时间戳）"""
        return str(self._allure_report_dir)

    def reload(self):
        """重新加载配置文件"""
        self._config = self._load_config()


# 全局配置实例
settings = Settings()
