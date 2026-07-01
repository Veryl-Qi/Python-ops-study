import unittest

from ops_monitor.monitor import get_exit_code, get_overall_level


class TestMonitorLogic(unittest.TestCase):
    """
    测试主程序中的状态汇总与退出码逻辑
    """

    def test_overall_level_ok(self):
        report = {
            "system_metrics": {
                "cpu": {"value": 10, "level": "OK"},
                "memory": {"value": 30, "level": "OK"},
                "disk": {"value": 40, "level": "OK"}
            },
            "services": [
                {"name": "ssh", "status": "active", "level": "OK"}
            ],
            "apis": [
                {"name": "Httpbin", "ok": True, "level": "OK"}
            ]
        }

        self.assertEqual(get_overall_level(report), "OK")

    def test_overall_level_warning(self):
        report = {
            "system_metrics": {
                "cpu": {"value": 85, "level": "WARNING"}
            },
            "services": [
                {"name": "ssh", "status": "active", "level": "OK"}
            ],
            "apis": []
        }

        self.assertEqual(get_overall_level(report), "WARNING")

    def test_overall_level_critical(self):
        report = {
            "system_metrics": {
                "cpu": {"value": 30, "level": "OK"}
            },
            "services": [
                {"name": "nginx", "status": "inactive", "level": "CRITICAL"}
            ],
            "apis": []
        }

        self.assertEqual(get_overall_level(report), "CRITICAL")

    def test_exit_code_ok(self):
        self.assertEqual(get_exit_code("OK"), 0)

    def test_exit_code_warning(self):
        self.assertEqual(get_exit_code("WARNING"), 1)

    def test_exit_code_critical(self):
        self.assertEqual(get_exit_code("CRITICAL"), 2)


if __name__ == "__main__":
    unittest.main()
