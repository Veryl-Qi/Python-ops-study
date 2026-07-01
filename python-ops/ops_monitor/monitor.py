import argparse
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

from ops_monitor.api import monitor_api
from ops_monitor.config import ConfigError, load_config
from ops_monitor.logger import setup_logger
from ops_monitor.system import check_service_active, get_system_metrics


def parse_args() -> argparse.Namespace:
    """
    解析命令行参数
    """

    default_config_path = Path(__file__).with_name("config.json")
    default_report_dir = Path(__file__).with_name("reports")

    parser = argparse.ArgumentParser(
        description="Python 自动化运维监控工具"
    )

    parser.add_argument(
        "--config",
        default=str(default_config_path),
        help="指定配置文件路径，默认使用 ops_monitor/config.json"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="开启详细日志模式"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="空运行模式，只检查配置和将要执行的任务，不真正执行监控"
    )

    parser.add_argument(
        "--report-dir",
        default=str(default_report_dir),
        help="指定巡检报告输出目录，默认使用 ops_monitor/reports"
    )

    return parser.parse_args()


def check_services(services: list, logger: logging.Logger) -> list:
    """
    检查 Linux 本地服务状态
    """

    results = []

    for service_name in services:
        logger.info(f"开始检查系统服务: {service_name}")

        try:
            status = check_service_active(service_name)

            if status == "active":
                level = "OK"
            else:
                level = "CRITICAL"

            results.append({
                "name": service_name,
                "status": status,
                "level": level
            })

            logger.info(f"服务检查完成: {service_name}, status={status}, level={level}")

        except subprocess.TimeoutExpired:
            logger.error(f"检查服务超时: {service_name}")

            results.append({
                "name": service_name,
                "status": "timeout",
                "level": "CRITICAL"
            })

        except FileNotFoundError:
            logger.error("当前系统可能不支持 systemctl 命令")

            results.append({
                "name": service_name,
                "status": "systemctl_not_found",
                "level": "CRITICAL"
            })

        except Exception as error:
            logger.error(f"检查服务时发生未知错误: {service_name}, error={error}")

            results.append({
                "name": service_name,
                "status": "error",
                "level": "CRITICAL",
                "reason": str(error)
            })

    return results


def check_apis(apis: list, warning_response_time: float, logger: logging.Logger) -> list:
    """
    检查外部 API 状态
    """

    results = []

    for api_config in apis:
        name = api_config["name"]
        url = api_config["url"]
        expected_status = api_config.get("expected_status", 200)

        logger.info(f"开始检查 API: {name}, url={url}")

        result = monitor_api(
            url=url,
            expected_status=expected_status
        )

        api_result = {
            "name": name,
            "url": url,
            "expected_status": expected_status,
            "ok": result.get("ok", False)
        }

        if not result.get("ok"):
            api_result["level"] = "CRITICAL"
            api_result["reason"] = result.get("reason", "未知错误")
            logger.warning(f"API 检查失败: {name}, reason={api_result['reason']}")

        else:
            response_time = result.get("response_time", 0)
            api_result["response_time"] = response_time

            if response_time >= warning_response_time:
                api_result["level"] = "WARNING"
                logger.warning(f"API 响应较慢: {name}, response_time={response_time:.2f}s")
            else:
                api_result["level"] = "OK"
                logger.info(f"API 检查正常: {name}, response_time={response_time:.2f}s")

        results.append(api_result)

    return results


def get_overall_level(report: dict) -> str:
    """
    汇总整体巡检状态
    """

    levels = []

    system_metrics = report.get("system_metrics", {})
    for metric_result in system_metrics.values():
        levels.append(metric_result.get("level", "OK"))

    for service_result in report.get("services", []):
        levels.append(service_result.get("level", "OK"))

    for api_result in report.get("apis", []):
        levels.append(api_result.get("level", "OK"))

    if "CRITICAL" in levels:
        return "CRITICAL"

    if "WARNING" in levels:
        return "WARNING"

    return "OK"


def get_exit_code(overall_level: str) -> int:
    """
    根据整体状态返回 Linux 退出码

    0：正常
    1：存在警告
    2：存在严重异常
    """

    if overall_level == "OK":
        return 0

    if overall_level == "WARNING":
        return 1

    return 2


def save_report(report: dict, report_dir: str, logger: logging.Logger) -> Path:
    """
    保存巡检报告到 JSON 文件
    """

    output_dir = Path(report_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = datetime.now().strftime("report_%Y%m%d_%H%M%S.json")
    report_path = output_dir / filename

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    logger.info(f"巡检报告已生成: {report_path}")

    return report_path


def print_summary(report: dict, report_path: Path | None = None) -> None:
    """
    在终端输出巡检摘要
    """

    print("=" * 60)
    print("Python 自动化运维巡检结果")
    print("=" * 60)
    print(f"巡检时间: {report['checked_at']}")
    print(f"整体状态: {report['overall_level']}")

    print("\n[系统资源]")
    for name, item in report.get("system_metrics", {}).items():
        print(f"- {name}: {item['value']}%, level={item['level']}")

    print("\n[系统服务]")
    for item in report.get("services", []):
        print(f"- {item['name']}: status={item['status']}, level={item['level']}")

    print("\n[API 监控]")
    for item in report.get("apis", []):
        if item.get("ok"):
            print(
                f"- {item['name']}: ok=True, "
                f"response_time={item.get('response_time', 0):.2f}s, "
                f"level={item['level']}"
            )
        else:
            print(
                f"- {item['name']}: ok=False, "
                f"reason={item.get('reason')}, "
                f"level={item['level']}"
            )

    if report_path:
        print(f"\n巡检报告文件: {report_path}")

    print("=" * 60)


def main() -> int:
    """
    主程序入口
    """

    args = parse_args()

    logger = setup_logger("ops_monitor.monitor")

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("已开启 verbose 详细日志模式")

    logger.info("ops_monitor 开始运行")

    try:
        config = load_config(args.config)
    except ConfigError as error:
        logger.error(f"配置加载失败: {error}")
        print(f"配置加载失败: {error}")
        return 2

    if args.dry_run:
        logger.info("当前为 dry-run 模式，不执行真实巡检")

        print("=" * 60)
        print("Dry-run 模式：配置文件加载成功，将要执行以下任务")
        print("=" * 60)
        print(f"配置文件: {Path(args.config).expanduser().resolve()}")
        print(f"服务检查: {config.get('services', [])}")
        print(f"API 检查: {[api.get('name') for api in config.get('apis', [])]}")
        print(f"报告目录: {Path(args.report_dir).expanduser().resolve()}")
        print("=" * 60)

        return 0

    report = {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system_metrics": {},
        "services": [],
        "apis": [],
        "overall_level": "UNKNOWN"
    }

    try:
        logger.info("开始采集系统资源指标")
        report["system_metrics"] = get_system_metrics()
    except Exception as error:
        logger.error(f"系统资源指标采集失败: {error}")

        report["system_metrics"] = {
            "error": {
                "value": None,
                "level": "CRITICAL",
                "reason": str(error)
            }
        }

    report["services"] = check_services(
        services=config.get("services", []),
        logger=logger
    )

    report["apis"] = check_apis(
        apis=config.get("apis", []),
        warning_response_time=config.get("warning_response_time", 2),
        logger=logger
    )

    overall_level = get_overall_level(report)
    report["overall_level"] = overall_level

    report_path = save_report(
        report=report,
        report_dir=args.report_dir,
        logger=logger
    )

    print_summary(report, report_path)

    exit_code = get_exit_code(overall_level)

    logger.info(f"ops_monitor 运行结束，overall_level={overall_level}, exit_code={exit_code}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
