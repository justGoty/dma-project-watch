# DMA Project Watch

**Release intelligence for the DMA ecosystem.** A real API-powered dashboard,
an installable Python CLI and a small, transparent DevOps delivery pipeline.

[Open the dashboard →](https://justgoty.github.io/dma-project-watch/)

![Tests](https://github.com/justGoty/dma-project-watch/actions/workflows/tests.yml/badge.svg)
![Deployment](https://github.com/justGoty/dma-project-watch/actions/workflows/dashboard.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/justGoty/dma-project-watch?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10%2B-3776ab?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-3fb950?style=flat-square)

## What it does

- Tracks MemProcFS, LeechCore, PCILeech, the public GOTY Tarkov source snapshot
  and this project's own release.
- Displays real versions, publication dates and source links from GitHub's API.
- Shows snapshot freshness, missing releases and request errors without inventing
  uptime, performance history or compatibility results.
- Provides search, status filters, a chronological release feed and JSON export.
- Builds a fresh static snapshot daily through GitHub Actions, without bot commits.

No memory access, firmware changes, release-asset execution or telemetry collection
by this application. The web UI fetches only its own snapshot.json artifact.

## CLI

Python 3.10+; no runtime dependencies. From the checkout:

```console
python -m pip install .
dma-watch
dma-watch --repo ufrisk/MemProcFS --repo ufrisk/LeechCore --json
dma-watch --snapshot --output report.json
dma-watch --version
```

Alternatively download the wheel from [Releases](https://github.com/justGoty/dma-project-watch/releases)
and install it with `python -m pip install <downloaded-wheel.whl>`.
The original `python watch.py` entry point still works.

An optional GITHUB_TOKEN environment variable raises GitHub's authenticated rate
limit. Do not put tokens in files, Docker images or command-line arguments. Public
queries work without authentication. Tokens are never included in snapshots.

GitHub returns the same 404 for missing/inaccessible repositories and repositories
without a release, so the tool reports `not-found-or-no-release` without guessing.
Only the latest non-prerelease published release is requested. Network/rate-limit
errors produce CLI exit code 1; invalid arguments produce exit code 2.

## Docker

```console
docker build -t dma-project-watch .
docker run --rm dma-project-watch --json
docker run --rm dma-project-watch --repo ufrisk/MemProcFS --snapshot
```

The multi-stage image builds a wheel and runs as unprivileged UID/GID 10001.
No device access, privileged mode, secrets or host mounts are required.

## Dashboard and delivery

```console
python dashboard.py
python -m http.server 8080 --directory site
```

Open http://localhost:8080. dashboard.py generates site/snapshot.json, which
is ignored by Git and included only in the deployed artifact.

```text
GitHub release API → Python collector → versioned JSON → GitHub Pages dashboard
                         ↑
                 daily scheduled workflow

Pull request → tests + wheel/CLI check + Docker build → merge
Version tag  → tests + package build + checksums → GitHub Release
```

Daily refresh is scheduled for 07:17 UTC (10:17 Moscow); GitHub may delay scheduled
runs. Reloading the page fetches the latest deployed snapshot, not a new API scan.
A valid snapshot containing API errors remains publishable; the UI shows those
errors. Data older than 30 hours is explicitly marked stale.

## Checks and releases

```console
python -m unittest -v
python -m pip install build
python -m build
```

CI checks Python 3.10 and 3.13, package installation/CLI entry points and Docker.
Tagged releases publish a wheel, source archive and SHA256SUMS.txt. Distribution
publishing is limited to GitHub Releases; no PyPI account or registry credentials
are needed. To release, keep watch.__version__ and pyproject.toml consistent,
update RELEASE_NOTES.md, then push the matching vX.Y.Z tag.

## Data and support

Uses GitHub's [latest release endpoint](https://docs.github.com/en/rest/releases/releases#get-the-latest-release).
This is not a hardware or game compatibility checker.
For support, [open an issue](https://github.com/justGoty/dma-project-watch/issues).
Maintained by [justGoty](https://github.com/justGoty). [MIT](LICENSE).
