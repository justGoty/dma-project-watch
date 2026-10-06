## 0.2.0 — release intelligence dashboard

- Responsive dashboard with real upstream versions, release dates and freshness.
- Search, status filters, release timeline, JSON export and CLI command copy.
- Daily GitHub Pages snapshot deployment; API errors remain visible in the report.
- Installable `dma-watch` and `dma-dashboard` commands; no runtime dependencies.
- Non-root multi-stage Docker image; CI builds and checks the container.
- Wheel/source distributions and SHA-256 checksums built by release automation.
- Expanded offline unit tests and package/CLI smoke checks.

The dashboard observes public release metadata only. It does not test hardware,
access memory, install firmware or claim compatibility with a specific game.
