import requests

def monitor_api(url: str, expected_status: int = 200) -> dict:
    """
    执行带请求头、状态码校验以及网络超时控制的 GET 请求
    """
    try:
        # 推荐连接超时(3秒)和读取超时(10秒)，以防网络异常导致程序卡死
        response = requests.get(
            url,
            headers={"Accept": "application/json"},
            timeout=(3,10)
        )

        status_code = response.status_code
        response_time = response.elapsed.total_seconds()  #获取相应耗时

        # 校验响应状态码是否与期望相符
        if status_code != expected_status:
                return {
                    "ok": False,
                    "reason": f"HTTP 状态码异常: 实际为 {status_code}, 期望为 {expected_status}"
                }

        # 不能假设所有响应都是 JSON，必须捕获解析错误
        try:
            data = response.json()  # 把 JSON 响应转换为 Python 数据
            return {
                "ok": True,
                "response_time": response_time,
                "data": data                                                                             }
        except requests.JSONDecodeError:
            # 接口返回的不是合法 JSON 时，记录提示并截取前 500 个字符用于排查
            return {
                "ok": False,
                "reason": "接口返回不是合法JSON格式",
                "preview": response.text[:500]
            }

    except requests.RequestException as error:
        # 捕获网络中断、命令超时等各种请求层面的异常，防止程序堆栈直接崩溃退出
        return {
            "ok": False,
            "reason": f"网络请求连接失败：{str(error)}"
        }
