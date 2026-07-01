import json
import os
from pathlib import Path


class ConfigError(Exception):
    """
    配置文件相关异常
    """
    pass


DEFAULT_CONFIG = {
    "timeout": 5,
    "warning_response_time": 2,
    "services": [],
    "apis": []
}


def load_config(config_path: str) -> dict:
    """
    加载并校验 config.json 配置文件

    配置优先级：
    程序默认值 < 配置文件 < 环境变量
    """

    path = Path(config_path).expanduser().resolve()

    if not path.exists():
        raise ConfigError(f"配置文件不存在: {path}")

    if not path.is_file():
        raise ConfigError(f"配置路径不是文件: {path}")

    try:
        with open(path, "r", encoding="utf-8") as file:
            user_config = json.load(file)
    except json.JSONDecodeError as error:
        raise ConfigError(f"配置文件 JSON 格式错误: {error}") from error

    if not isinstance(user_config, dict):
        raise ConfigError("配置文件最外层必须是 JSON 对象")

    config = DEFAULT_CONFIG.copy()
    config.update(user_config)

    validate_config(config)

    config = apply_env_overrides(config)

    return config


def apply_env_overrides(config: dict) -> dict:
    """
    从环境变量读取配置，覆盖 config.json 中的配置
    """

    timeout = os.getenv("OPS_MONITOR_TIMEOUT")
    if timeout:
        try:
            config["timeout"] = int(timeout)
        except ValueError as error:
            raise ConfigError("环境变量 OPS_MONITOR_TIMEOUT 必须是整数") from error

    warning_response_time = os.getenv("OPS_MONITOR_WARNING_RESPONSE_TIME")
    if warning_response_time:
        try:
            config["warning_response_time"] = float(warning_response_time)
        except ValueError as error:
            raise ConfigError("环境变量 OPS_MONITOR_WARNING_RESPONSE_TIME 必须是数字") from error

    validate_config(config)

    return config


def validate_config(config: dict) -> None:
    """
    校验配置字段是否合法
    """

    timeout = config.get("timeout")
    if not isinstance(timeout, int) or timeout <= 0:
        raise ConfigError("timeout 必须是大于 0 的整数")

    warning_response_time = config.get("warning_response_time")
    if not isinstance(warning_response_time, (int, float)) or warning_response_time <= 0:
        raise ConfigError("warning_response_time 必须是大于 0 的数字")

    services = config.get("services")
    if not isinstance(services, list):
        raise ConfigError("services 必须是列表")

    for service in services:
        if not isinstance(service, str) or not service.strip():
            raise ConfigError("services 中的每一项都必须是非空字符串")

    apis = config.get("apis")
    if not isinstance(apis, list):
        raise ConfigError("apis 必须是列表")

    for api in apis:
        if not isinstance(api, dict):
            raise ConfigError("apis 中的每一项都必须是对象")

        if not api.get("name"):
            raise ConfigError("每个 API 配置必须包含 name")

        if not api.get("url"):
            raise ConfigError("每个 API 配置必须包含 url")

        expected_status = api.get("expected_status", 200)
        if not isinstance(expected_status, int):
            raise ConfigError("expected_status 必须是整数")
