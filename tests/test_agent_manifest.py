import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "agent" / "capabilities.json"
SKILL = ROOT / "agent" / "skills" / "linxira-config" / "SKILL.md"


class AgentManifestTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_schema_and_version(self):
        self.assertEqual(self.data["schemaVersion"], 1)
        self.assertEqual(self.data["tool"], "linxira-config")
        cli = (ROOT / "cli" / "linxira-config").read_text(encoding="utf-8")
        self.assertIn(f'VERSION="{self.data["version"]}"', cli)

    def test_command_ids_unique_and_well_formed(self):
        ids = [command["id"] for command in self.data["commands"]]
        self.assertEqual(len(ids), len(set(ids)))
        for command in self.data["commands"]:
            self.assertTrue(command["summary"])
            self.assertIsInstance(command["argv"], list)
            self.assertEqual(command["argv"][0], "linxira-config")
            self.assertIn(command["privilege"], {"none", "root", "polkit"})
            self.assertIsInstance(command["mutating"], bool)
            self.assertIn(command.get("output", "text"), {"text", "json"})

    def test_mutating_commands_are_privileged(self):
        for command in self.data["commands"]:
            if command["mutating"]:
                self.assertEqual(command["privilege"], "root", command["id"])

    def test_cli_dispatch_and_help(self):
        cli = (ROOT / "cli" / "linxira-config").read_text(encoding="utf-8")
        self.assertIn("capabilities_manifest", cli)
        self.assertIn("capabilities)", cli)
        self.assertIn("/usr/share/linxira/agent/capabilities.json", cli)

    def test_skill_frontmatter(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: linxira-config\n"))
        self.assertIn("linxira-config capabilities", text)
        self.assertIn("sudo", text)


if __name__ == "__main__":
    unittest.main()
