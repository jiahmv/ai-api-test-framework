"""日志工具"""
import logging
import sys
from pathlib import Path
from loguru import logger

from config.settings import settings


class Logger:
    """日志管理类"""

    _loggers = {}

    @classmethod
    def setup(cls):
        """配置日志系统"""
        # 移除默认的handler
        logger.remove()

        # loguru格式字符串
        log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

        # 添加控制台handler
        logger.add(
            sys.stdout,
            format=log_format,
            level=settings.log_level,
            colorize=True,
            enqueue=True
        )

        # 添加文件handler
        log_file = Path(settings.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",  # 文件记录所有级别
            rotation="10 MB",  # 日志文件大小达到10MB时轮转
            retention="7 days",  # 保留7天的日志
            encoding="utf-8",
            enqueue=True
        )

    @classmethod
    def get_logger(cls, name: str = None):
        """获取日志器

        Args:
            name: 日志器名称

        Returns:
            logger实例
        """
        if not cls._loggers:
            cls.setup()

        # 使用loguru的logger
        if name:
            return logger.bind(name=name)
        return logger


def get_logger(name: str = None):
    """获取日志器的便捷函数

    Args:
        name: 日志器名称

    Returns:
        logger实例
    """
    return Logger.get_logger(name)
