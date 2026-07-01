import unittest

from ops_monitor.system import grade


class TestSystemGrade(unittest.TestCase):
    """
    测试系统指标状态分级函数
    """

    def test_ok_level(self):
        self.assertEqual(grade(10, warning=80, critical=90), "OK")
        self.assertEqual(grade(79.9, warning=80, critical=90), "OK")

    def test_warning_level(self):
        self.assertEqual(grade(80, warning=80, critical=90), "WARNING")
        self.assertEqual(grade(85, warning=80, critical=90), "WARNING")
        self.assertEqual(grade(89.9, warning=80, critical=90), "WARNING")

    def test_critical_level(self):
        self.assertEqual(grade(90, warning=80, critical=90), "CRITICAL")
        self.assertEqual(grade(95, warning=80, critical=90), "CRITICAL")
        self.assertEqual(grade(100, warning=80, critical=90), "CRITICAL")


if __name__ == "__main__":
    unittest.main()
