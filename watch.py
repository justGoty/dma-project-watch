"""Read public GitHub release metadata for DMA/ESP projects. No dependencies."""

import argparse
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_REPOS = ("ufrisk/MemProcFS", "ufrisk/LeechCore", "ufrisk/pcileech",
                 "justGoty/goty-esp-dma-tarkov")
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", help="owner/repo; repeat for multiple projects")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)
    repos = args.repo or DEFAULT_REPOS
    try:
        for repo in repos:
            validate_repo(repo)
    except ValueError as error:
        parser.error(str(error))
    results = []
    failed = False
    for repo in repos:
        try:
            results.append(latest_release(repo, os.environ.get("GITHUB_TOKEN")))
        except RuntimeError as error:
            failed = True
            results.append({"repository": repo, "status": "error", "message": str(error)})
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for item in results:
            print(item["repository"] + " | " + item.get("tag", item["status"]) +
                  " | " + item.get("url", item.get("message", "")))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
