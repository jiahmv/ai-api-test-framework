"""接口执行器 - 执行HTTP请求"""
import json
from typing import Dict, Any
import requests

from utils.logger import get_logger

logger = get_logger(__name__)


class APIExecutor:
    """接口执行器

    封装HTTP请求的发送和响应处理
    """

    def __init__(self, timeout: int = 30):
        """初始化接口执行器

        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.logger = logger

    def execute(self, url: str, method: str, headers: Dict,
                params: Any, param_type: str) -> Dict[str, Any]:
        """执行HTTP请求

        Args:
            url: 请求URL
            method: 请求方法（GET/POST/PUT/DELETE）
            headers: 请求头
            params: 请求参数
            param_type: 参数类型（params/data/json）

        Returns:
            响应字典，包含:
            - status_code: HTTP状态码
            - headers: 响应头
            - body: 响应体
            - response_time: 响应时间（秒）

        Raises:
            requests.exceptions.Timeout: 请求超时
            requests.exceptions.RequestException: 请求异常
        """
        self.logger.info(f"执行请求: {method} {url}")
        self.logger.debug(f"请求头: {headers}")
        self.logger.debug(f"请求参数: {params}")
        self.logger.debug(f"参数类型: {param_type}")

        try:
            # 根据参数类型决定如何发送
            if param_type == 'params':
                kwargs = {'params': params}
            elif param_type == 'data':
                kwargs = {'data': params}
            else:  # json
                kwargs = {'json': params}

            # 发送请求
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )

            # 构建响应结果
            result = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': self._parse_response_body(response),
                'response_time': response.elapsed.total_seconds()
            }

            self.logger.info(f"响应状态码: {result['status_code']}")
            self.logger.info(f"响应时间: {result['response_time']:.3f}s")
            self.logger.debug(f"响应体: {result['body']}")

            return result

        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {url}")
            raise
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"连接错误: {e}")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {e}")
            raise

    def _parse_response_body(self, response: requests.Response) -> Any:
        """解析响应体

        Args:
            response: 响应对象

        Returns:
            解析后的响应体（JSON或文本）
        """
        try:
            # 尝试解析为JSON
            return response.json()
        except ValueError:
            # JSON解析失败，返回原始文本
            return response.text
