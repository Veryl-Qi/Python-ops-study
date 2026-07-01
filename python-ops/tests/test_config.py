import json
import os
import tempfile
import unittest
from pathlib import Path

from ops_monitor.config import ConfigError, load_config


class TestConfig(unittest.TestCase):
    """
    测试配置文件读取与校验逻辑
    """

    def write_temp_config(self, config_data: dict) -> str:
        """
        创建临时 config.json 文件，并返回文件路径
        """
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)

        config_path = Path(temp_dir.name) / "config.json"

        with open(config_path, "w", encoding="utf-8") as file:
            json.dump(config_data, file, ensure_ascii=False)

        return str(config_path)

    def test_load_valid_config(self):
        config_path = self.write_temp_config({
            "timeout": 5,
            "warning_response_time": 2,
            "services": ["ssh", "cron"],
            "apis": [
                {
                    "name": "Httpbin",
                    "url": "https://httpbin.org/get",
                    "expected_status": 200
                }
            ]
        })

        config = load_config(config_path)

        self.assertEqual(config["timeout"], 5)
        self.assertEqual(config["warning_response_time"], 2)
        self.assertEqual(config["services"], ["ssh", "cron"])
        self.assertEqual(config["apis"][0]["name"], "Httpbin")

    def test_default_config_values(self):
        config_path = self.write_temp_config({})

        config = load_config(config_path)

        self.assertEqual(config["timeout"], 5)
        self.assertEqual(config["warning_response_time"], 2)
        self.assertEqual(config["services"], [])
        self.assertEqual(config["apis"], [])

    def test_invalid_timeout(self):
        config_path = self.write_temp_config({
            "timeout": -1
        })

        with self.assertRaises(ConfigError):
            load_config(config_path)

    def test_invalid_services_type(self):
        config_path = self.write_temp_config({
            "services": "ssh"
        })

        with self.assertRaises(ConfigError):
            load_config(config_path)

    def test_invalid_api_missing_url(self):
        config_path = self.write_temp_config({
            "apis": [
                {
                    "name": "BadApi"
                }
            ]
        })

        with self.assertRaises(ConfigError):
            load_config(config_path)

    def test_env_override_timeout(self):
        config_path = self.write_temp_config({
            "timeout": 5
        })

        old_value = os.environ.get("OPS_MONITOR_TIMEOUT")

        try:
            os.environ["OPS_MONITOR_TIMEOUT"] = "10"
            config = load_config(config_path)
            self.assertEqual(config["timeout"], 10)
        finally:
            if old_value is None:
                os.environ.pop("OPS_MONITOR_TIMEOUT", None)
            else:
                os.environ["OPS_MONITOR_TIMEOUT"] = old_value


if __name__ == "__main__":
    unittest.main()
