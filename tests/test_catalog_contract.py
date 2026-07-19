from pathlib import Path
import unittest


CLI = Path(__file__).parents[1] / "cli/linxira-config"
SOFTWARE_CENTER = Path(__file__).parents[1] / "cli/linxira-software-center"


class CatalogContractTests(unittest.TestCase):
    def test_cli_consumes_catalog_v2(self):
        script = CLI.read_text(encoding="utf-8")
        self.assertIn("catalog-v2.json", script)
        self.assertIn(".catalogVersion == 2", script)
        self.assertNotIn("catalog-v1.json", script)

    def test_bio_alias_uses_the_reviewed_profile(self):
        script = CLI.read_text(encoding="utf-8")
        self.assertIn("bio) install_catalog_profile bioinformatics", script)

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

    def test_software_center_owns_the_install_transaction(self):
        script = SOFTWARE_CENTER.read_text(encoding="utf-8")
        self.assertIn("pkexec pacman", script)
        self.assertIn(".applications", script)
        self.assertNotIn("CONFIG_CLI", script)
        self.assertNotIn("pkexec \"$CONFIG_CLI\"", script)


if __name__ == "__main__":
    unittest.main()
