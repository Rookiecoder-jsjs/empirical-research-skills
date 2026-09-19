"""Behavioral tests use temporary workspaces and synthetic data only."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


init = module("project_init", "skills/empirical-project/scripts/init_project.py")
install = module("installer", "scripts/install_skills.py")
csvcheck = module("csvcheck", "skills/empirical-data/scripts/check_csv.py")
runner = module("runner", "skills/empirical-analysis/scripts/run_workflow.py")
envcheck = module("envcheck", "skills/empirical-setup/scripts/check_environment.py")


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path


class InitializationTests(WorkspaceTest):
    def test_preview_has_no_side_effects(self):
        project = self.root / "new paper"
        report = init.initialize(project)
        self.assertFalse(project.exists())
        self.assertFalse(report["created"])

    def test_create_then_refuse_existing_project(self):
        project = self.root / "new paper"
        init.initialize(project, True)
        self.assertTrue((project / "data").is_dir())
        self.assertEqual(json.loads((project / "workflow.json").read_text())["steps"], [])
        with self.assertRaises(ValueError):
            init.initialize(project, True)

    def test_install_and_protect_existing_skills(self):
        destination = self.root / "paper/.agents/skills"
        installed = install.install(ROOT / "skills", destination)
        self.assertEqual(len(installed), 8)
        sentinel = destination / "empirical-data/SKILL.md"
        sentinel.write_text("user customization", encoding="utf-8")
        with self.assertRaises(ValueError):
            install.install(ROOT / "skills", destination)
        self.assertEqual(sentinel.read_text(), "user customization")

    def test_install_conflict_does_not_partially_install(self):
        destination = self.root / "skills"
        (destination / "empirical-writing").mkdir(parents=True)
        with self.assertRaises(ValueError):
            install.install(ROOT / "skills", destination)
        self.assertEqual([p.name for p in destination.iterdir()], ["empirical-writing"])


class CSVTests(WorkspaceTest):
    def test_valid_panel_and_read_only(self):
        path = self.write("x.csv", "id,year,y\nA,1,0\nA,2,2\n")
        before = path.read_bytes()
        result = csvcheck.check_csv(path, ["id", "year"], ["y"], ["y"], {"y": 0})
        self.assertTrue(result["ok"])
        self.assertEqual(path.read_bytes(), before)

    def test_duplicate_missing_and_nonfinite_values(self):
        path = self.write("x.csv", "id,y\nA,1\nA,2\n,NA\nB,inf\n")
        result = csvcheck.check_csv(path, ["id"], ["y"], ["y"])
        self.assertFalse(result["ok"])
        for kind in ["duplicate_keys", "empty_keys", "required_missing", "invalid_numeric"]:
            self.assertEqual(result["counts"][kind], 1)
        self.assertNotIn("inf", json.dumps(result))

    def test_malformed_and_out_of_range_rows(self):
        path = self.write("x.csv", "id,y\nA,-1\nB,3,extra\nC\n")
        result = csvcheck.check_csv(path, lower={"y": 0})
        self.assertEqual(result["counts"]["malformed_rows"], 2)
        self.assertEqual(result["counts"]["out_of_range"], 1)

    def test_duplicate_headers_are_rejected(self):
        path = self.write("x.csv", "x,x\n1,2\n")
        with self.assertRaises(ValueError):
            csvcheck.check_csv(path)

    def test_empty_data_is_not_a_pass(self):
        self.assertFalse(csvcheck.check_csv(self.write("x.csv", "x,y\n"))["ok"])


class EnvironmentTests(WorkspaceTest):
    def test_wrong_environment_and_missing_package_are_visible(self):
        result = envcheck.inspect(self.root, "0.0", ["nonexistent-research-test-package-987654321"])
        self.assertFalse(result["ok"])
        self.assertTrue(any(".venv" in x for x in result["issues"]))
        self.assertTrue(any("Missing distribution" in x for x in result["issues"]))
        self.assertTrue(result["stdlib_smoke_ok"])
        self.assertEqual(list(self.root.iterdir()), [])


class WorkflowTests(WorkspaceTest):
    def setUp(self):
        super().setUp()
        shutil.copytree(ROOT / "examples/synthetic-demo", self.root, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("processed", "__pycache__"))
        self.raw = json.loads((self.root / "workflow.json").read_text())

    def manifest(self):
        self.write("workflow.json", json.dumps(self.raw))
        return runner.load_manifest(self.root, "workflow.json")

    def test_plan_does_not_create_results(self):
        self.assertEqual(runner.plan(self.manifest(), ["summary"]), ["summary"])
        self.assertFalse((self.root / "processed").exists())

    def test_execute_then_resume(self):
        manifest = self.manifest()
        result = runner.execute(self.root, manifest, ["summary"])
        self.assertTrue(result["ok"])
        data = json.loads((self.root / "processed/results/summary.json").read_text())
        self.assertEqual(data, {"synthetic": True, "n": 6, "mean": 3.5})
        resumed = runner.execute(self.root, manifest, ["summary"], True)
        self.assertEqual(resumed["steps"][0]["status"], "skipped")

    def test_input_change_invalidates_cache(self):
        manifest = self.manifest()
        runner.execute(self.root, manifest, [], True)
        with (self.root / "data/synthetic.csv").open("a") as out:
            out.write("D,2020,7\n")
        result = runner.execute(self.root, manifest, [], True)
        self.assertEqual(result["steps"][0]["status"], "success")
        data = json.loads((self.root / "processed/results/summary.json").read_text())
        self.assertEqual(data["n"], 7)

    def test_code_change_invalidates_cache(self):
        manifest = self.manifest()
        runner.execute(self.root, manifest, [])
        with (self.root / "scripts/summarize.py").open("a") as out:
            out.write("\n# changed code version\n")
        self.assertEqual(runner.execute(self.root, manifest, [], True)["steps"][0]["status"], "success")

    def test_output_tampering_invalidates_cache(self):
        manifest = self.manifest()
        runner.execute(self.root, manifest, [])
        self.write("processed/results/summary.json", "{}")
        self.assertEqual(runner.execute(self.root, manifest, [], True)["steps"][0]["status"], "success")

    def test_failure_stops_downstream_and_does_not_resume_partial_output(self):
        self.raw["steps"][0]["command"] += ["unused"]
        self.write("scripts/summarize.py", "from pathlib import Path\np=Path('processed/results/summary.json')\np.parent.mkdir(parents=True,exist_ok=True)\np.write_text('partial')\nraise SystemExit(7)\n")
        self.write("scripts/next.py", "from pathlib import Path\nPath('processed/results/next.txt').write_text('wrong')\n")
        self.raw["steps"].append({"id": "next", "command": ["{python}", "scripts/next.py"],
                                  "inputs": ["processed/results/summary.json"], "code": ["scripts/next.py"],
                                  "outputs": ["processed/results/next.txt"], "depends_on": ["summary"]})
        manifest = self.manifest()
        for _ in range(2):
            report = runner.execute(self.root, manifest, ["next"], True)
            self.assertFalse(report["ok"])
            self.assertEqual(report["steps"][0]["status"], "failed")
            self.assertEqual(len(report["steps"]), 1)
            self.assertFalse((self.root / "processed/results/next.txt").exists())

    def test_missing_output_is_failure(self):
        self.write("scripts/summarize.py", "print('no artifact')\n")
        self.assertFalse(runner.execute(self.root, self.manifest(), [])["ok"])

    def test_old_output_cannot_mask_a_noop_success(self):
        runner.execute(self.root, self.manifest(), [])
        self.write("scripts/summarize.py", "print('exits successfully but leaves stale output')\n")
        report = runner.execute(self.root, self.manifest(), [], True)
        self.assertFalse(report["ok"])
        self.assertIn("not refreshed", report["steps"][0]["error"])

    def test_mutated_input_is_failure(self):
        self.write("scripts/summarize.py", "from pathlib import Path\nPath('data/synthetic.csv').write_text('changed')\np=Path('processed/results/summary.json')\np.parent.mkdir(parents=True,exist_ok=True)\np.write_text('{}')\n")
        report = runner.execute(self.root, self.manifest(), [])
        self.assertFalse(report["ok"])
        self.assertIn("changed during", report["steps"][0]["error"])

    def test_raw_output_rejected(self):
        self.raw["steps"][0]["outputs"] = ["data/changed.csv"]
        with self.assertRaises(ValueError):
            self.manifest()

    def test_parent_and_windows_path_escape_rejected(self):
        for value in ["../outside.csv", "C:\\outside.csv", "/outside.csv"]:
            with self.subTest(value=value):
                self.raw["steps"][0]["outputs"] = [value]
                with self.assertRaises(ValueError):
                    self.manifest()

    def test_unknown_dependency_and_cycle_rejected(self):
        for deps in [["missing"], ["summary"]]:
            self.raw["steps"][0]["depends_on"] = deps
            with self.assertRaises(ValueError):
                self.manifest()

    def test_undeclared_producer_dependency_rejected(self):
        self.write("scripts/next.py", "pass\n")
        self.raw["steps"].append({"id": "next", "command": ["{python}", "scripts/next.py"],
                                  "inputs": ["processed/results/summary.json"], "code": ["scripts/next.py"],
                                  "outputs": ["processed/results/next.txt"], "depends_on": []})
        with self.assertRaises(ValueError):
            self.manifest()

    def test_symlink_escape_rejected_when_supported(self):
        with tempfile.TemporaryDirectory() as outside:
            try:
                (self.root / "outside").symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("Symlink creation not permitted on this platform")
            self.raw["steps"][0]["outputs"] = ["outside/x.csv"]
            with self.assertRaises(ValueError):
                self.manifest()


if __name__ == "__main__":
    unittest.main()
