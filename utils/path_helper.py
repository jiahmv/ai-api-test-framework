"""路径工具类"""
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class PathHelper:
    """路径辅助类，用于处理带时间戳的路径"""

    @staticmethod
    def get_timestamp() -> str:
        """获取时间戳字符串（下划线格式，用于文件夹）

        Returns:
            格式化后的时间戳字符串，如：20240112_143025
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def get_timestamp_file() -> str:
        """获取时间戳字符串（连字符格式，用于文件名）

        Returns:
            格式化后的时间戳字符串，如：20240112-143025
        """
        return datetime.now().strftime("%Y%m%d-%H%M%S")

    @staticmethod
    def create_timestamped_dir(base_dir: str, prefix: str = "") -> Path:
        """创建带时间戳的子目录（用于Allure报告）

        Args:
            base_dir: 基础目录路径
            prefix: 子目录前缀（如 "allure"）

        Returns:
            创建的目录路径对象

        Examples:
            >>> PathHelper.create_timestamped_dir("reports/allure", "allure")
            Path('reports/allure/allure_20240112_143025')
        """
        timestamp = PathHelper.get_timestamp()

        # 如果有前缀，格式为：前缀_时间戳
        # 如果没有前缀，直接使用时间戳
        dir_name = f"{prefix}_{timestamp}" if prefix else timestamp

        # 创建完整路径
        full_path = Path(base_dir) / dir_name

        # 创建目录（包括父目录）
        full_path.mkdir(parents=True, exist_ok=True)

        return full_path

    @staticmethod
    def create_timestamped_file(base_dir: str, filename: str, extension: str = "") -> Path:
        """创建带时间戳的文件（用于HTML报告和日志文件）

        Args:
            base_dir: 基础目录路径
            filename: 文件名（如 "report"、"api-log"）
            extension: 文件扩展名（如 "html"、"log"）

        Returns:
            创建的文件路径对象

        Examples:
            >>> PathHelper.create_timestamped_file("reports/html", "report", "html")
            Path('reports/html/report-20240112-143025.html')

            >>> PathHelper.create_timestamped_file("logs", "api-log", "log")
            Path('logs/api-log-20240112-143025.log')
        """
        timestamp = PathHelper.get_timestamp_file()

        # 构建文件名：文件名-时间戳.扩展名
        if extension:
            file_name = f"{filename}-{timestamp}.{extension}"
        else:
            file_name = f"{filename}-{timestamp}"

        # 创建完整路径
        base_path = Path(base_dir)
        base_path.mkdir(parents=True, exist_ok=True)

        full_path = base_path / file_name

        return full_path

    @staticmethod
    def get_latest_dir(base_dir: str, prefix: str = "") -> Optional[Path]:
        """获取最新的带时间戳的目录

        Args:
            base_dir: 基础目录路径
            prefix: 目录前缀

        Returns:
            最新的目录路径对象，如果不存在则返回None
        """
        base_path = Path(base_dir)

        if not base_path.exists():
            return None

        # 获取所有匹配前缀的目录
        if prefix:
            pattern = f"{prefix}_*"
        else:
            pattern = "*"

        # 查找所有匹配的目录
        dirs = [d for d in base_path.glob(pattern) if d.is_dir()]

        if not dirs:
            return None

        # 按修改时间排序，返回最新的
        latest_dir = max(dirs, key=lambda x: x.stat().st_mtime)

        return latest_dir

    @staticmethod
    def get_latest_file(base_dir: str, filename: str, extension: str = "") -> Optional[Path]:
        """获取最新的带时间戳的文件

        Args:
            base_dir: 基础目录路径
            filename: 文件名（不含时间戳）
            extension: 文件扩展名

        Returns:
            最新的文件路径对象，如果不存在则返回None

        Examples:
            >>> PathHelper.get_latest_file("reports/html", "report", "html")
            Path('reports/html/report-20240112-143025.html')
        """
        base_path = Path(base_dir)

        if not base_path.exists():
            return None

        # 构建匹配模式
        if extension:
            pattern = f"{filename}-*.{extension}"
        else:
            pattern = f"{filename}-*"

        # 查找所有匹配的文件
        files = [f for f in base_path.glob(pattern) if f.is_file()]

        if not files:
            return None

        # 按修改时间排序，返回最新的
        latest_file = max(files, key=lambda x: x.stat().st_mtime)

        return latest_file


# 全局实例
path_helper = PathHelper()
