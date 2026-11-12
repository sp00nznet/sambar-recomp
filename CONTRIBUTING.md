# Contributing

Issues and pull requests are welcome.

## The one rule

**Nothing from Sambar goes in the repository.** No executables or DLLs, no
MAP files, pages or config from its installer, no lifted C
(`src/recomp/gen/`), no catalogs (`work/`), no disassembly listings, nothing
generated from its binaries. The tool ships; its output is made on each
person's machine from their own copy. `.gitignore` covers the usual paths;
check `git status` before you commit anyway.

## Before a pull request

1. Build from a clean lift: `py -3 run_lift.py` (expected: `lift errors 0`),
   then `build.cmd`.
2. Run the conformance harness:
   ```
   py -3 tools\http_diff.py
   ```
   It must print `http_diff: PASS 31/31` (or the new total). A new behavior
   comes with a request in its corpus that shows it ([docs/testing.md](docs/testing.md)).
3. Keep it on `127.0.0.1` ([SECURITY.md](SECURITY.md)). A change that makes
   anything listen elsewhere won't be merged.

## Where your code comes from

Contributions must be your own or MIT-compatible. Don't port code from GPL or
LGPL projects (Wine and ReactOS are the likely ones for Win32 API work).

## Where a fix belongs

- A bug in the lifter, the catalog, the module loader or the native bridge
  belongs in [pcrecomp](https://github.com/sp00nznet/pcrecomp), not here.
- A fix to Sambar itself is a patch in `run_lift.py` or a shim in
  `src/runtime/host.c`, with a comment that says what it fixes and why.
- A wall you got past goes in `docs/architecture.md`: what it looked like,
  what it was, what moved it.
