from pathlib import Path
import unittest


CLI = Path(__file__).parents[1] / "cli/linxira-config"


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


if __name__ == "__main__":
    unittest.main()
