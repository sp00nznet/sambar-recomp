# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-11-20

- Builds against pcrecomp main; the `pcrecomp-sambar` branch is merged.

### Added
- `CONTRIBUTING.md`, `CONTRIBUTORS.md`, `docs/building.md`, `docs/testing.md`,
  a `setup.sh` that says there is no Linux or macOS build yet, and a
  hand-run installer workflow.

### Changed
- Setup and `launcher/launcher.json` clone pcrecomp's `pcrecomp-sambar`
  branch, which the build needs, instead of `main`.
- The README follows the house layout; `NOTICE` is now `NOTICE.md`.

## [0.1.0] - 2026-11-11

### Added
- Sambar Server 6.4 production (2006-07-08) lifted to C: `ntserver.exe` and
  five DLLs (`sambar.dll`, `sambarcm.dll`, `sambarcs.dll`, `sqlite3.dll`,
  `samples.dll`), rebased to their own bases, 17,384 dispatch entries, 0 lift
  errors, on pcrecomp's native32 host and its new module loader.
- `tools/catalog.py`: rebase plus catalog, seeded from Sambar's own MAP files.
- `tools/http_diff.py`: the conformance check. The original and the recomp on
  `127.0.0.1`, one generated docroot, a fixed corpus of raw HTTP requests.
- `Setup.cmd` (`tools/setup.ps1`): one-click setup from `sambar64p.exe` (read,
  never run) or an installed folder; writes a `config.ini` bound to
  `127.0.0.1`.
- `launcher/launcher.json`, `SECURITY.md`, `docs/architecture.md`.
- A netlab recipe (`projects/sambar-recomp.env` in recomp-netlab), with
  `tools/http_diff.py` as its QA.
