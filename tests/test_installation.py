"""Installation checks only write isolated temporary folders."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bundle_installer', ROOT / 'scripts/install_skills.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class ClientInstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.project = self.root / '论文 project'
        self.project.mkdir()

    def test_client_paths_and_user_scope(self):
        self.assertEqual(installer.destinations('both', self.project), [
            self.project / '.agents/skills', self.project / '.claude/skills'])
        fake_home = self.root / 'fake-user'
        self.assertEqual(installer.destinations('codex', user=True, home=fake_home),
                         [fake_home / '.agents/skills'])
        self.assertEqual(installer.destinations('claude', user=True, home=fake_home),
                         [fake_home / '.claude/skills'])
        self.assertFalse(fake_home.exists())
        with self.assertRaises(ValueError):
            installer.destinations('codex', self.root / 'typo')
        with self.assertRaises(ValueError):
            installer.destinations('codex', self.project, user=True)

    def test_both_clients_receive_complete_resources(self):
        targets = installer.destinations('both', self.project)
        names = installer.install_many(ROOT / 'skills', targets)
        self.assertEqual(len(names), 8)
        for source in (ROOT / 'skills').rglob('*'):
            if not source.is_file() or '__pycache__' in source.parts or source.suffix == '.pyc':
                continue
            for target in targets:
                self.assertEqual((target / source.relative_to(ROOT / 'skills')).read_bytes(),
                                 source.read_bytes())
        self.assertEqual(sorted(p.name for p in self.project.iterdir()), ['.agents', '.claude'])

    def test_conflict_in_second_client_prevents_first_client_write(self):
        targets = installer.destinations('both', self.project)
        sentinel = targets[1] / 'empirical-writing/SKILL.md'
        sentinel.parent.mkdir(parents=True)
        sentinel.write_text('local customization', encoding='utf-8')
        with self.assertRaises(ValueError):
            installer.install_many(ROOT / 'skills', targets)
        self.assertFalse(targets[0].exists())
        self.assertEqual(sentinel.read_text(), 'local customization')
        self.assertEqual(len(list(targets[1].iterdir())), 1)

    def test_invalid_second_destination_prevents_partial_install(self):
        blocker = self.root / 'file'
        blocker.write_text('keep')
        first = self.root / 'new-skills'
        with self.assertRaises(ValueError):
            installer.install_many(ROOT / 'skills', [first, blocker / 'skills'])
        self.assertFalse(first.exists())
        self.assertEqual(blocker.read_text(), 'keep')

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/install_skills.py'), *args],
                              capture_output=True, text=True)

    def test_cli_preview_and_explicit_claude_install(self):
        result = self.cli('--client', 'both', '--project', str(self.project), '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(self.project.iterdir()), [])
        result = self.cli('--client', 'claude', '--project', str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / '.claude/skills/empirical-setup/SKILL.md').is_file())
        self.assertFalse((self.project / '.agents').exists())

    def test_legacy_cli_defaults_to_codex(self):
        result = self.cli('--project', str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list((self.project / '.agents/skills').iterdir())), 8)
        self.assertFalse((self.project / '.claude').exists())

    def test_ambiguous_destination_rejected_without_writes(self):
        result = self.cli('--destination', str(self.project / 'skills'), '--client', 'both')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_marketplace_resolves_plugin_with_all_eight_skills(self):
        catalog = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['plugins']), 1)
        entry = catalog['plugins'][0]
        plugin_root = (ROOT / entry['source']).resolve()
        manifest = json.loads((plugin_root / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(entry['name'], manifest['name'])
        self.assertEqual(len(list((plugin_root / 'skills').glob('*/SKILL.md'))), 8)
        for field in ['hooks', 'mcpServers', 'lspServers']:
            self.assertNotIn(field, manifest)


if __name__ == '__main__':
    unittest.main()
