"""性能测试报告生成器"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from utils.logger import get_logger
from core.performance_executor import PerformanceResult

logger = get_logger(__name__)


class PerformanceReporter:
    """性能测试报告生成器

    生成 HTML 格式的性能测试报告
    """

    def __init__(self, output_dir: str = "reports/performance"):
        """初始化报告生成器

        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger

    def generate_html_report(self, result: PerformanceResult,
                            test_config: Dict[str, Any] = None) -> str:
        """生成 HTML 性能报告

        Args:
            result: 性能测试结果
            test_config: 测试配置信息

        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"perf_report_{timestamp}.html"

        # 生成 HTML 内容
        html_content = self._generate_html_content(result, test_config)

        # 写入文件
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.logger.info(f"性能报告已生成: {report_file}")
        return str(report_file)

    def _generate_html_content(self, result: PerformanceResult,
                               test_config: Dict[str, Any] = None) -> str:
        """生成 HTML 内容

        Args:
            result: 性能测试结果
            test_config: 测试配置

        Returns:
            HTML 内容
        """
        # 计算成功率
        success_rate = (result.success_count / result.total_requests * 100) if result.total_requests > 0 else 0

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>性能测试报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            border-left: 4px solid #4CAF50;
            padding-left: 10px;
            margin-top: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .metric-card.success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .metric-card.warning {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .metric-label {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
        }}
        .metric-unit {{
            font-size: 14px;
            opacity: 0.8;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .status-pass {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .status-fail {{
            color: #f44336;
            font-weight: bold;
        }}
        .progress-bar {{
            width: 100%;
            background-color: #f0f0f0;
            border-radius: 4px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 20px;
            background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
            transition: width 0.3s ease;
        }}
        .config-info {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .timestamp {{
            text-align: right;
            color: #999;
            font-size: 12px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 性能测试报告</h1>

        <!-- 测试概要 -->
        <h2>📊 测试概要</h2>
        <div class="summary">
            <div class="metric-card">
                <div class="metric-label">总请求数</div>
                <div class="metric-value">{result.total_requests}</div>
            </div>
            <div class="metric-card success">
                <div class="metric-label">成功请求</div>
                <div class="metric-value">{result.success_count}</div>
            </div>
            <div class="metric-card warning">
                <div class="metric-label">失败请求</div>
                <div class="metric-value">{result.failure_count}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">成功率</div>
                <div class="metric-value">{success_rate:.2f}<span class="metric-unit">%</span></div>
            </div>
        </div>

        <!-- 响应时间统计 -->
        <h2>⏱️ 响应时间统计</h2>
        <table>
            <tr>
                <th>指标</th>
                <th>值</th>
                <th>说明</th>
            </tr>
            <tr>
                <td>最小响应时间</td>
                <td>{result.min_time:.3f} 秒</td>
                <td>所有请求中最快的响应时间</td>
            </tr>
            <tr>
                <td>最大响应时间</td>
                <td>{result.max_time:.3f} 秒</td>
                <td>所有请求中最慢的响应时间</td>
            </tr>
            <tr>
                <td>平均响应时间</td>
                <td>{result.avg_time:.3f} 秒</td>
                <td>所有请求的平均响应时间</td>
            </tr>
            <tr>
                <td>中位数响应时间</td>
                <td>{result.median_time:.3f} 秒</td>
                <td>50%的请求响应时间小于此值</td>
            </tr>
            <tr>
                <td><strong>P95 响应时间</strong></td>
                <td><strong>{result.p95_time:.3f} 秒</strong></td>
                <td>95%的请求响应时间小于此值</td>
            </tr>
            <tr>
                <td><strong>P99 响应时间</strong></td>
                <td><strong>{result.p99_time:.3f} 秒</strong></td>
                <td>99%的请求响应时间小于此值</td>
            </tr>
        </table>

        <!-- 吞吐量统计 -->
        <h2>📈 吞吐量统计</h2>
        <div class="summary">
            <div class="metric-card">
                <div class="metric-label">TPS (每秒事务数)</div>
                <div class="metric-value">{result.tps:.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">实际测试时长</div>
                <div class="metric-value">{result.actual_duration:.2f}<span class="metric-unit">秒</span></div>
            </div>
        </div>

        <!-- 用例级别统计 -->
        <h2>📋 用例级别统计</h2>
        <table>
            <tr>
                <th>用例ID</th>
                <th>执行次数</th>
                <th>成功次数</th>
                <th>失败次数</th>
                <th>平均响应时间</th>
                <th>最大响应时间</th>
                <th>成功率</th>
            </tr>
"""

        # 添加每个用例的统计信息
        for case_id, case_stat in result.case_stats.items():
            case_total = case_stat['count']
            case_success = case_stat['success_count']
            case_fail = case_total - case_success
            case_response_times = case_stat['response_times']

            if case_response_times:
                case_avg_time = sum(case_response_times) / len(case_response_times)
                case_max_time = max(case_response_times)
            else:
                case_avg_time = 0
                case_max_time = 0

            case_success_rate = (case_success / case_total * 100) if case_total > 0 else 0

            html += f"""
            <tr>
                <td>{case_id}</td>
                <td>{case_total}</td>
                <td class="status-pass">{case_success}</td>
                <td class="status-fail">{case_fail}</td>
                <td>{case_avg_time:.3f} 秒</td>
                <td>{case_max_time:.3f} 秒</td>
                <td>{case_success_rate:.2f}%</td>
            </tr>
"""

        html += """
        </table>

        <!-- 错误统计 -->
        """

        if result.errors:
            html += """
        <h2>❌ 错误统计</h2>
        <table>
            <tr>
                <th>错误类型</th>
                <th>次数</th>
            </tr>
"""
            for error_msg, count in result.errors.items():
                html += f"""
            <tr>
                <td>{error_msg}</td>
                <td>{count}</td>
            </tr>
"""
            html += """
        </table>
"""

        # 测试配置信息
        if test_config:
            html += f"""
        <!-- 测试配置 -->
        <h2>⚙️ 测试配置</h2>
        <div class="config-info">
            <p><strong>并发数:</strong> {test_config.get('concurrent_users', 'N/A')}</p>
            <p><strong>测试时长:</strong> {test_config.get('duration', 'N/A')} 秒</p>
            <p><strong>启动时间:</strong> {test_config.get('ramp_up', 'N/A')} 秒</p>
        </div>
"""

        # 时间戳
        html += f"""
        <div class="timestamp">
            报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""

        return html

    def generate_json_report(self, result: PerformanceResult,
                            test_config: Dict[str, Any] = None) -> str:
        """生成 JSON 格式的性能报告

        Args:
            result: 性能测试结果
            test_config: 测试配置

        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"perf_report_{timestamp}.json"

        # 构建报告数据
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'test_config': test_config or {},
            'summary': {
                'total_requests': result.total_requests,
                'success_count': result.success_count,
                'failure_count': result.failure_count,
                'success_rate': (result.success_count / result.total_requests * 100) if result.total_requests > 0 else 0,
                'tps': result.tps,
                'actual_duration': result.actual_duration
            },
            'response_times': {
                'min': result.min_time,
                'max': result.max_time,
                'avg': result.avg_time,
                'median': result.median_time,
                'p95': result.p95_time,
                'p99': result.p99_time
            },
            'errors': result.errors,
            'case_stats': result.case_stats
        }

        # 写入文件
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"JSON报告已生成: {report_file}")
        return str(report_file)
