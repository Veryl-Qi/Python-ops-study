import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = "ops_monitor") -> logging.Logger:
    """
    创建并返回项目日志对象

    日志输出位置：
    ops_monitor/logs/ops-monitor.log

    日志策略：
    - 单个日志文件最大 2MB
    - 最多保留 3 个备份文件
    - 同时输出到文件和终端
    """

    logger = logging.getLogger(name)

    # 避免重复添加 handler，防止日志重复打印
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    base_dir = Path(__file__).resolve().parent
    log_dir = base_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "ops-monitor.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
