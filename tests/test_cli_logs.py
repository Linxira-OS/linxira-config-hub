from pathlib import Path
import unittest


CLI = Path(__file__).parents[1] / "cli/linxira-config"


class LogsCommandTests(unittest.TestCase):
    def test_logs_dispatch_and_helpers_exist(self):
        # 2026-09-21: 诊断日志一键收集/上传 —— 安装失败、更新异常等场景的
        # 远程协助基础。2026-09-30 通道重排(国内实测): paste.rs 主通道,
        # termbin(bash /dev/tcp, 无 nc 依赖)兜底, dpaste 末位; 0x0.st 停服剔除。
        source = CLI.read_text(encoding="utf-8")
        self.assertIn("logs_collect()", source)
        self.assertIn("logs_upload()", source)
        self.assertIn("    logs)", source)
        self.assertIn("https://paste.rs", source)
        self.assertIn("termbin.com 9999", source)
        self.assertIn("dpaste.com/api/v2/text", source)
        self.assertNotIn("0x0.st", source)
        self.assertIn("linxira-config logs upload", source)


if __name__ == "__main__":
    unittest.main()
