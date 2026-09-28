from pathlib import Path
import shutil
import subprocess
import tempfile
import shutil
import unittest


CLI = Path(__file__).parents[1] / "cli/linxira-config"


class StackBridgeContractTests(unittest.TestCase):
    def test_stack_env_tui_dispatch_exist(self):
        # 2026-09-28 用户决策: WSL 用户用 config 一站式配置 ——
        # stack 转发 component-manager, env 管 /etc/profile.d/linxira-env.sh,
        # tui 纯 bash 数字菜单(零依赖)。
        script = CLI.read_text(encoding="utf-8")
        for marker in (
            "stack_manage()",
            "env_manage()",
            "config_tui()",
            "    stack)",
            "    env)",
            "    tui)",
        ):
            self.assertIn(marker, script)

    def test_env_file_location_is_fixed(self):
        script = CLI.read_text(encoding="utf-8")
        self.assertIn("ENV_FILE=/etc/profile.d/linxira-env.sh", script)
        self.assertIn("chmod 644 \"$ENV_FILE\"", script)

    @unittest.skipUnless(shutil.which("bash"), "bash is not available")
    def test_env_roundtrip_in_sandbox(self):
        # 在沙盒里覆盖 ENV_FILE 与 root 检查, 验证 set/list/get/unset 全链。
        sandbox = tempfile.mkdtemp()
        try:
            env_file = Path(sandbox) / "linxira-env.sh"
            harness = Path(sandbox) / "harness.sh"
            functions = CLI.read_text(encoding="utf-8")
            start = functions.index("env_list()")
            end = functions.index("# ─── TUI")
            body = functions[start:end]
            harness.write_text(
                "set -eu\n"
                "require_root() { :; }\n"
                "success() { echo \"$1\"; }\n"
                "error() { echo \"$1\" >&2; exit 1; }\n"
                'ENV_FILE="$(pwd)/linxira-env.sh"\n'
                + body.replace("ENV_FILE=/etc/profile.d/linxira-env.sh", ""),
                encoding="utf-8", newline="\n",
            )
            run = lambda *args: subprocess.run(
                ["bash", "-c", f"source ./harness.sh; {args[0]}"], cwd=sandbox,
                capture_output=True, text=True,
            )
            result = run(f"env_manage set EDITOR test-value")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("export EDITOR='test-value'", env_file.read_text(encoding="utf-8"))
            result = run("env_manage get EDITOR")
            self.assertIn("EDITOR=test-value", result.stdout)
            result = run("env_manage set EDITOR second")
            self.assertEqual("export EDITOR='second'\n", env_file.read_text(encoding="utf-8"))
            result = run("env_manage unset EDITOR")
            self.assertNotIn("EDITOR", env_file.read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
