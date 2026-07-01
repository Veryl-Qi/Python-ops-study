# Python 自动化运维监控系统 ops_monitor

## 项目简介

ops_monitor 是一个基于 Python 的轻量级自动化运维巡检工具，主要用于定时检查服务器基础资源、本地 systemd 服务状态和外部 API 可用性。

Python 自动化运维学习项目，覆盖了虚拟环境、配置文件、日志轮转、异常处理、命令行参数、单元测试、报告生成和 systemd 定时部署等完整流程。

## 功能

- 采集 CPU、内存、磁盘使用率
- 检查 Linux systemd 服务状态
- 探测外部 HTTP API 可用性
- 支持 JSON 配置文件
- 支持 dry-run 空运行模式
- 支持日志轮转
- 自动生成 JSON 巡检报告
- 支持 unittest 单元测试
- 支持 systemd timer 定时运行

## 项目结构

```text
python-ops/
├── ops_monitor/
│   ├── __init__.py
│   ├── api.py
│   ├── config.py
│   ├── config.json
│   ├── logger.py
│   ├── monitor.py
│   ├── system.py
│   ├── logs/
│   │   └── .gitkeep
│   └── reports/
│       └── .gitkeep
├── tests/
│   ├── test_config.py
│   ├── test_monitor.py
│   └── test_system.py
├── deploy/
│   ├── ops-monitor.service
│   └── ops-monitor.timer
├── examples/
│   └── hello.py
├── requirements.txt
├── README.md
└── .gitignore
