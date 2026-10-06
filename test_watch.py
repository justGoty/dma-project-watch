import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import watch


class WatchTests(unittest.TestCase):
    def test_valid_repo(self):
        self.assertEqual(watch.validate_repo("ufrisk/MemProcFS"), "ufrisk/MemProcFS")

    def test_invalid_repos(self):
        for value in ("https://github.com/a/b", "../b", "a/b/c", "a/b?token=x", "a/..", "a/ b"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                watch.validate_repo(value)

    @patch("watch.urlopen")
    def test_release(self, open_mock):
        open_mock.return_value.__enter__.return_value = io.StringIO(json.dumps({
            "tag_name": "v1", "published_at": "2026-10-06T00:00:00Z",
            "html_url": "https://github.com/a/b/releases/tag/v1"}))
        self.assertEqual(watch.latest_release("a/b")["tag"], "v1")
        request = open_mock.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.github.com/repos/a/b/releases/latest")

    @patch("watch.urlopen", side_effect=HTTPError("", 404, "", {}, None))
    def test_no_release_is_not_network_error(self, _):
        self.assertEqual(watch.latest_release("a/b")["status"], "not-found-or-no-release")

    @patch("watch.urlopen", side_effect=HTTPError("", 403, "", {}, None))
    def test_rate_limit(self, _):
        with self.assertRaisesRegex(RuntimeError, "rate limit"):
            watch.latest_release("a/b", "secret-test-token")

    @patch("watch.urlopen", side_effect=URLError("secret detail"))
    def test_network_details_not_exposed(self, _):
        with self.assertRaisesRegex(RuntimeError, "^Network request failed$"):
            watch.latest_release("a/b")

    @patch("watch.urlopen")
    def test_malformed_response(self, open_mock):
        open_mock.return_value.__enter__.return_value = io.StringIO("{}")
        with self.assertRaisesRegex(RuntimeError, "Unexpected"):
            watch.latest_release("a/b")

    @patch("watch.latest_release", side_effect=RuntimeError("Network request failed"))
    def test_json_failure_exit_code(self, _):
        output = io.StringIO()
        with redirect_stdout(output):
            code = watch.main(["--repo", "a/b", "--json"])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output.getvalue())[0]["status"], "error")


if __name__ == "__main__":
    unittest.main()
