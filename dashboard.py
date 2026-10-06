"""Generate a static dashboard snapshot, preserving per-repository API errors."""

import argparse
import os

from watch import DEFAULT_REPOS, collect, snapshot, validate_repo, write_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="site/snapshot.json")
    parser.add_argument("--repo", action="append")
    args = parser.parse_args(argv)
    repos = args.repo or DEFAULT_REPOS
    try:
        for repo in repos:
            validate_repo(repo)
    except ValueError as error:
        parser.error(str(error))
    results = collect(repos, os.environ.get("GITHUB_TOKEN"))
    try:
        write_json(args.output, snapshot(results))
    except OSError:
        parser.exit(1, "Unable to write dashboard snapshot\n")
    errors = sum(item["status"] == "error" for item in results)
    print(f"Snapshot written: {len(results)} repositories, {errors} API errors")
    # A valid report containing API failures remains publishable; the UI shows them.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
