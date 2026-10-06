import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import dashboard
import watch


class DashboardTests(unittest.TestCase):
    def test_snapshot_metadata(self):
        report = watch.snapshot([])
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["tool_version"], watch.__version__)
        self.assertIsNotNone(datetime.fromisoformat(report["generated_at"]).tzinfo)

    @patch("watch.latest_release", return_value={"repository": "a/b", "status": "release"})
    def test_deduplication(self, latest):
        self.assertEqual(len(watch.collect(["a/b", "a/b"])), 1)
        latest.assert_called_once()

    @patch("watch.latest_release", side_effect=RuntimeError("Network request failed"))
    def test_error_preserved(self, _):
        self.assertEqual(watch.collect(["a/b"])[0]["status"], "error")

    def test_write_utf8_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "report.json"
            watch.write_json(path, {"name": "Тест"})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["name"], "Тест")

    @patch("dashboard.collect", return_value=[{"repository": "a/b", "status": "error"}])
    def test_dashboard_publishes_error_report(self, _):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            path = Path(directory) / "snapshot.json"
            self.assertEqual(dashboard.main(["--output", str(path)]), 0)
            self.assertEqual(json.loads(path.read_text())["repositories"][0]["status"], "error")

    @patch("watch.collect", return_value=[])
    def test_cli_snapshot_output(self, _):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            self.assertEqual(watch.main(["--snapshot", "--output", str(path)]), 0)
            self.assertEqual(json.loads(path.read_text())["schema_version"], 1)

    @patch("watch.collect", return_value=[])
    @patch("watch.write_json", side_effect=PermissionError())
    def test_output_failure(self, *_):
        self.assertEqual(watch.main(["--output", "unwritable.json"]), 1)

    def test_package_version_matches(self):
        project = Path("pyproject.toml").read_text()
        self.assertIn('version = "' + watch.__version__ + '"', project)


if __name__ == "__main__":
    unittest.main()
