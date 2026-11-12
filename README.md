# Sambar Server — Static Recompilation

Static recompilation of **Sambar Server** 6.4 (Sambar Technologies, 2006), the
freeware Win32 web, FTP, mail and proxy server, from its shipping
`ntserver.exe` and the five DLLs it runs (`sambar.dll`, `sambarcm.dll`,
`sambarcs.dll`, `sqlite3.dll`, `samples.dll`) to native C. pcrecomp lifts them,
MSVC compiles the C, and pcrecomp's `native32` host runs it against the real
ws2_32, kernel32 and advapi32. It runs Sambar's own code; it is not a rewrite,
and no emulator or wrapper DLL is involved.

Built on the [pcrecomp](https://github.com/sp00nznet/pcrecomp) toolchain, on
its **`pcrecomp-sambar`** branch until that is merged, and following its
shared house style, like the other
[pcrecomp projects](https://github.com/sp00nznet/pcrecomp#the-projects-that-built-this).

> **Security:** Sambar is a 2000s-era server with known, published
> vulnerabilities, and the recompiled build has every one of them. Only ever
> run it bound to `127.0.0.1`, for testing. Read [SECURITY.md](SECURITY.md).

There is no screenshot: Sambar's console server has no window. What it
serves is its output, and the harness compares that byte for byte.

## Getting Started

You need **your own copy of Sambar Server 6.4**: its installer,
`sambar64p.exe` (6,887,021 bytes, SHA-256
`e81cba69ee6b22552b1d669bd43976f2307581bf3c9b9b2f6309f5325e22c5b3`), or a
folder it installed. The Internet Archive's Wayback Machine has it from
sambar.com, captured 2006-07-08. Sambar's license allows using it, not
redistributing it: nothing of it is in this repository or downloaded for you,
and the generated C is made on your machine, into gitignored folders.

### The setup scripts

1. Download this repository (the green **Code** button, then **Download ZIP**)
   and unzip it somewhere with 1.5 GB free.
2. Put `sambar64p.exe` in that folder (or install Sambar to `C:\sambar`).
3. Windows: double-click **`Setup.cmd`**. There is no Linux or macOS build
   yet; `setup.sh` says so and exits.
4. Run `Sambar Server (recomp)` in that folder, then open `http://127.0.0.1/`.

The script asks before installing anything (Python 3.10+, `pefile` and
`capstone`, git, the Visual Studio 2022 C++ Build Tools), clones pcrecomp's
`pcrecomp-sambar` branch beside the repo if it isn't there, unpacks the
installer into `game\` (reading it, never running it), writes a config bound
to `127.0.0.1`, catalogs, lifts and builds. About 15 minutes; a rerun skips
finished steps, and `setup.log` has the details if it stops. `-GameDir
<file or folder>` skips the question, `-Yes` answers yes to every install.

Building by hand, the command line and its flags are in
**[docs/building.md](docs/building.md)**.

## Status

**v0.1.0, alpha. It serves HTTP, and its responses match the original's byte
for byte.** The conformance harness, `tools/http_diff.py`, runs the original
and the recomp on `127.0.0.1` against the same 31 raw requests: **31/31**
(2026-11-12). Without the program it reports SKIP.

| | |
|---|---|
| Functions found (`disasm32`, seeded from Sambar's MAP files) | 17,383 in 6 modules |
| Lifted to C | 17,384 dispatch entries (6,126 bodies, 11,258 alias stubs), 0 errors |
| Imports bound | 1,135: 531 to Windows, 586 guest to guest, 18 shimmed, 0 unresolved |
| HTTP: static files, HEAD, ranges, 304, 404, directory lists, redirects, `.stm` pages, Perl CGI | byte-identical on the harness |
| FTP, SMTP/POP3, proxy, DNS, HTTPS, the admin console | not checked |
| Windows service (`-i`) | not run: the recomp runs `-d`, the console server |

[docs/architecture.md](docs/architecture.md) is how it fits together and what
each wall was, and [ROADMAP.md](ROADMAP.md) what comes next.

## Screenshots

None: the console server has no window ([docs/testing.md](docs/testing.md)
shows what the harness compares instead).

## Documentation

- [docs/building.md](docs/building.md): building by hand, the command line, another toolkit checkout
- [docs/testing.md](docs/testing.md): the HTTP conformance harness and netlab
- [docs/architecture.md](docs/architecture.md): the modules, the loader, the lift and the walls
- [SECURITY.md](SECURITY.md): keeping it on localhost
- [ROADMAP.md](ROADMAP.md), [CHANGELOG.md](CHANGELOG.md), [CONTRIBUTING.md](CONTRIBUTING.md)

## Contributors

See **[CONTRIBUTORS.md](CONTRIBUTORS.md)** for who did what. Thank you, all of
you.

## License

MIT for this repository's own code ([LICENSE](LICENSE)). Sambar Server is
© 1996-2006 Sambar Technologies; none of its files, and nothing generated
from them, is in this repository ([NOTICE.md](NOTICE.md)).
