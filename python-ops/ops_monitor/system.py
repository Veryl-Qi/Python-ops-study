import psutil
import subprocess

def grade(value: float, warning: float, critical: float) -> str:
    """
    统一阈值状态分级函数
    规则必须从最严重、最具体的条件开始判断
    """
    if value >= critical:
        return "CRITICAL"
    if value >= warning:
         return "WARNING"
    return "OK"

def get_system_metrics() -> dict:
    """
    本机 CPU、内存、磁盘资源采集
    """
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    return {
            "cpu": {"value":cpu, "level":grade(cpu, warning=80, critical=90)},
            "memory": {"value":memory, "level":grade(memory, warning=80, critical=90)},
            "disk": {"value":disk, "level":grade(disk, warning=80, critical=90)}
         }

def check_service_active(service_name: str) -> str:
    """
    使用 subprocess 安全调用 Linux 命令检查 systemd 服务状态
    """
    # 优先使用列表参数(shell=False), 避免因字符串拼接引发命令注入风险
    result = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True, # 捕获标准输出和错误输出
            text=True,           # 把输出解码为字符串
            timeout=5,           # 命令超过 5 秒则抛出
            check=False,         # 由代码主机分析退出码
        )
    # 返回去除了首尾空格的命令输出结果
    return result.stdout.strip()
