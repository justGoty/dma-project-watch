"""Read public GitHub release metadata for DMA/ESP projects. No dependencies."""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

__version__ = "0.2.0"

DEFAULT_REPOS = ("ufrisk/MemProcFS", "ufrisk/LeechCore", "ufrisk/pcileech",
                 "justGoty/goty-esp-dma-tarkov", "justGoty/dma-project-watch")
REPO_PATTERN = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")


def validate_repo(value):
    if not REPO_PATTERN.fullmatch(value) or any(part in (".", "..") for part in value.split("/")):
        raise ValueError("Expected owner/repository, not a URL or path")
    return value


def latest_release(repo, token=None):
    validate_repo(repo)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "dma-project-watch",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request("https://api.github.com/repos/" + repo + "/releases/latest", headers=headers)
    try:
        with urlopen(request, timeout=20) as response:
            data = json.load(response)
        return {"repository": repo, "status": "release", "tag": data["tag_name"],
                "published_at": data.get("published_at"), "url": data["html_url"]}
    except HTTPError as error:
        if error.code == 404:
            return {"repository": repo, "status": "not-found-or-no-release"}
        if error.code in (403, 429):
            raise RuntimeError("GitHub denied the request or its rate limit was reached") from None
        raise RuntimeError("GitHub HTTP error " + str(error.code)) from None
    except (URLError, TimeoutError, OSError):
        raise RuntimeError("Network request failed") from None
    except (KeyError, ValueError, TypeError):
        raise RuntimeError("Unexpected GitHub response") from None


def collect(repos, token=None):
    results = []
    for repo in dict.fromkeys(repos):
        validate_repo(repo)
        try:
            results.append(latest_release(repo, token))
        except RuntimeError as error:
            results.append({"repository": repo, "status": "error", "message": str(error)})
    return results


def snapshot(results):
    return {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": __version__, "source": "GitHub REST API",
            "repositories": results}


def write_json(path, data):
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", help="owner/repo; repeat for multiple projects")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--output", help="save JSON to a file instead of stdout")
    parser.add_argument("--snapshot", action="store_true", help="include timestamp and schema metadata")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)
    repos = args.repo or DEFAULT_REPOS
    try:
        for repo in repos:
            validate_repo(repo)
    except ValueError as error:
        parser.error(str(error))
    results = collect(repos, os.environ.get("GITHUB_TOKEN"))
    failed = any(item["status"] == "error" for item in results)
    data = snapshot(results) if args.snapshot else results
    if args.output:
        try:
            write_json(args.output, data)
        except OSError:
            print("Unable to write output file", file=sys.stderr)
            return 1
    elif args.json or args.snapshot:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        for item in results:
            print(item["repository"] + " | " + item.get("tag", item["status"]) +
                  " | " + item.get("url", item.get("message", "")))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
