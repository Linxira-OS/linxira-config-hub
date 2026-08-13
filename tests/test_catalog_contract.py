from pathlib import Path
import shutil
import subprocess
import unittest


CLI = Path(__file__).parents[1] / "cli/linxira-config"


class CatalogContractTests(unittest.TestCase):
    def test_headless_mode_commands_switch_systemd_targets(self):
        # 2026-08-13: 桌面⇄无头快速切换(运行时释放内存)
        script = CLI.read_text(encoding="utf-8")
        self.assertIn("systemctl set-default multi-user.target", script)
        self.assertIn("systemctl isolate multi-user.target", script)
        self.assertIn("systemctl set-default graphical.target", script)
        self.assertIn("systemctl isolate graphical.target", script)
        self.assertIn("systemctl get-default", script)
        # 立即切换必须交互确认(防未保存数据丢失)
        self.assertIn("立即切换将退出桌面会话", script)
        self.assertIn("read -rp", script)

    def test_cli_consumes_catalog_v3_and_retains_v2_compatibility(self):
        script = CLI.read_text(encoding="utf-8")
        self.assertIn("catalog-v3.json", script)
        self.assertIn(".catalogVersion == 2 or .catalogVersion == 3", script)
        self.assertIn(".artifact.ids // .packages", script)
        self.assertNotIn("catalog-v1.json", script)

    def test_cli_does_not_expose_software_installation(self):
        script = CLI.read_text(encoding="utf-8")
        self.assertIn("Software installation is owned by Shelly and Quick System Software Setup", script)
        self.assertNotIn("Install (post-install packages)", script)
        self.assertNotIn("install_catalog_", script)
        self.assertNotIn("install_packages()", script)
        self.assertNotIn("Installing Profiles", script)
        self.assertNotIn("Installing Applications", script)
        self.assertFalse((CLI.parents[1] / "profiles/science.conf").exists())

    @unittest.skipUnless(shutil.which("bash"), "bash is not available")
    def test_legacy_install_entrypoints_fail_closed(self):
        for arguments in (("install", "firefox"), ("workflow", "science")):
            result = subprocess.run(
                ["bash", "cli/linxira-config", *arguments],
                cwd=CLI.parents[1],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Software installation is owned by Shelly and Quick System Software Setup", result.stdout)

    def test_catalog_queries_are_read_only_and_status_filtered(self):
        script = CLI.read_text(encoding="utf-8")
        self.assertIn("catalog <kind>", script)
        self.assertIn("use software/component/bundle", script)
        self.assertIn("installed|partial|external|pending|drifted|reboot-required", script)
        self.assertIn("--all", script)
        self.assertIn("(.software // .applications // [])", script)
        self.assertIn("(.components // .profiles // [])", script)
        self.assertIn("(.bundles // .desktopBundles // [])", script)
        catalog_section = script.split("# ─── Catalog Queries", 1)[1].split("# ─── Service Management", 1)[0]
        self.assertNotIn("sudo ", catalog_section)
        self.assertNotIn("pacman -S", catalog_section)

    def test_ssh_key_and_authorized_key_boundaries_are_explicit(self):
        script = CLI.read_text(encoding="utf-8")
        self.assertIn("ssh key list", script)
        self.assertIn("ssh key fingerprint", script)
        self.assertIn("ssh authorized add", script)
        self.assertIn("Refusing to use a symlinked SSH directory", script)
        self.assertIn("without authorized_keys options", script)
        self.assertIn("removal requires --yes", script)
        self.assertNotIn('read -p "Overwrite?', script)
        self.assertNotIn("-N ''", script)

    def test_cli_has_no_generic_shell_executor(self):
        script = CLI.read_text(encoding="utf-8")
        self.assertNotIn("eval ", script)
        self.assertNotIn("bash -c", script)
        self.assertNotIn("sh -c", script)

    @unittest.skipUnless(shutil.which("bash"), "bash is not available")
    def test_cli_has_valid_bash_syntax(self):
        subprocess.run(
            ["bash", "-n", "cli/linxira-config"],
            cwd=CLI.parents[1],
            check=True,
        )

    def test_kernel_report_only_matches_official_names(self):
        script = CLI.read_text(encoding="utf-8")
        self.assertIn("/^linux(-lts|-zen|-hardened)?$/", script)
        self.assertNotIn("linux-cachyos|linux-linxira", script)

    def test_config_cli_exposes_explicit_flatpak_remote_management(self):
        script = CLI.read_text(encoding="utf-8")
        self.assertIn("flatpak)", script)
        self.assertIn("flatpak remote-modify", script)
        self.assertIn("mirror flatpak", script)

    def test_config_cli_exposes_explicit_go_proxy_management(self):
        script = CLI.read_text(encoding="utf-8")
        self.assertIn("go env -w", script)
        self.assertIn("GOPROXY", script)
        self.assertIn("mirror go", script)

    def test_config_cli_uses_miniforge_and_allowlists_scientific_channels(self):
        script = CLI.read_text(encoding="utf-8")
        self.assertIn("miniforge_root", script)
        self.assertIn("conda-forge", script)
        self.assertIn("bioconda", script)
        self.assertIn("refusing to configure a generic Conda distribution", script)
        self.assertNotIn("conda config --add channels defaults", script)

    def test_help_examples_do_not_advertise_disabled_mutations(self):
        script = CLI.read_text(encoding="utf-8")
        examples = script.split("${BOLD}Examples:${NC}", 1)[1].split("EOF", 1)[0]
        for disabled in ("security harden", "rdp on", "virt kvm-on", "net fix"):
            self.assertNotIn(disabled, examples)
        self.assertIn("runtime status", examples)
        self.assertIn("mirror arch list", examples)

    @unittest.skipUnless(shutil.which("bash"), "bash is not available")
    def test_power_status_is_read_only_and_dispatches(self):
        result = subprocess.run(
            ["bash", "cli/linxira-config", "power", "status"],
            cwd=CLI.parents[1],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Power Settings", result.stdout)

    @unittest.skipUnless(shutil.which("bash"), "bash is not available")
    def test_unsafe_system_mutations_fail_closed_at_dispatch(self):
        commands = (
            ("net", "fix"),
            ("security", "harden"),
            ("service", "ssh", "on"),
            ("virt", "docker-on"),
            ("power", "nosleep"),
            ("rdp", "off"),
        )
        for arguments in commands:
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    ["bash", "cli/linxira-config", *arguments],
                    cwd=CLI.parents[1],
                    text=True,
                    capture_output=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "disabled until the Linxira system transaction backend",
                    result.stdout,
                )

    @unittest.skipUnless(shutil.which("bash"), "bash is not available")
    def test_config_mutations_are_now_dispatched_not_gated(self):
        # Config-class commands were decoupled from the transaction backend:
        # they must reach their implementation (never hit the backend_pending
        # gate). Under root they may actually succeed; as a non-root user they
        # must fail with a permission error instead.
        commands = (
            ("net", "dns", "set", "1.1.1.1"),
            ("security", "ufw", "on"),
            ("ssh", "port", "2222"),
            ("mirror", "arch", "set", "official"),
            ("mirror", "flatpak", "reset"),
        )
        for arguments in commands:
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    ["bash", "cli/linxira-config", *arguments],
                    cwd=CLI.parents[1],
                    text=True,
                    capture_output=True,
                )
                self.assertNotIn(
                    "disabled until the Linxira system transaction backend",
                    result.stdout,
                )

if __name__ == "__main__":
    unittest.main()
