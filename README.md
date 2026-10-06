# DMA Project Watch

![Tests](https://github.com/justGoty/dma-project-watch/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-3776ab?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-3fb950?style=flat-square)

A small, dependency-free release tracker for the DMA/ESP ecosystem.
It reads public GitHub release metadata; it does not access memory, install firmware,
download release assets or run third-party executables.

## Run

```console
python watch.py
python watch.py --repo ufrisk/MemProcFS --repo ufrisk/LeechCore --json
python -m unittest -v
```

Defaults: MemProcFS, LeechCore, PCILeech and the public GOTY Tarkov source snapshot.
Python 3.10 or newer is required. No packages need installing.

An optional `GITHUB_TOKEN` environment variable raises GitHub's authenticated rate
limit. Do not put tokens into files or command-line arguments. Public queries work
without authentication.

GitHub returns the same 404 response for a missing/inaccessible repository and for
a repository without a published release, so the tool reports
`not-found-or-no-release` without guessing. Network/rate-limit errors produce exit
code 1; repository argument errors produce exit code 2.

Only the latest non-prerelease published release is requested. This tool is not
a compatibility checker and does not prove that a DMA hardware setup works.

## API and support

Uses GitHub's [latest release endpoint](https://docs.github.com/en/rest/releases/releases#get-the-latest-release).
For support, open an issue in this repository. Maintained by [justGoty](https://github.com/justGoty).
