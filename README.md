# Sambar Server, recompiled

Static recompilation of **Sambar Server** 6.4 (Sambar Technologies, 2006), the
freeware Win32 web, FTP, mail and proxy server, from its shipping executable
and DLLs to native C. No emulator, no wrapper DLLs. It is pcrecomp's first
application with threads, Winsock, a Windows service front end, plug-in DLLs
and config files, and its first network server.

> **Security:** Sambar is a 2000s-era server with known, published
> vulnerabilities, and the recompiled build has every one of them. Only ever
> run it bound to `127.0.0.1`, for testing. Read [SECURITY.md](SECURITY.md).

Built on the [pcrecomp](https://github.com/sp00nznet/pcrecomp) toolchain and
following its shared house style (layout, CLI, conformance harness), like the
other [pcrecomp projects](https://github.com/sp00nznet/pcrecomp#the-projects-that-built-this).

## What it is

A static recompilation of `ntserver.exe` (the service and console front end)
and the five DLLs it runs: `sambar.dll` (the server), `sambarcm.dll`,
`sambarcs.dll`, `sqlite3.dll` and the `samples.dll` plug-in. pcrecomp lifts
them to C, MSVC compiles the C, and pcrecomp's `native32` host runs it, calling
the real ws2_32, kernel32 and advapi32. It runs Sambar's own code; it is not a
rewrite.

## Status: v0.1.0, alpha. It serves HTTP, and its responses match the original

| Stage | State |
|---|---|
| Version recompiled | Sambar Server 6.4 production (`sambar64p.exe`, 2006-07-08), the last 6.x release, freeware |
| Function catalog (`disasm32`, seeded from Sambar's MAP files) | 17,383 functions in 6 modules |
| Lift (`run_lift.py`, pcrecomp `drive32`) | 17,384 dispatch entries (6,126 lifted bodies, 11,258 alias stubs into them), 0 errors |
| Host (`build/sambarrecomp.exe`, 32-bit, pcrecomp `native32` + `modules32`) | 1,135 imports: 531 to Windows, 586 guest-to-guest, 18 shimmed, 0 unresolved |
| HTTP: static files, HEAD, ranges, 304, 404, directory lists, redirects | works, **byte-identical** to the original on the harness corpus |
| `.stm` server-side pages, `/cgi-bin/` Perl CGI | work, byte-identical (a generated page, the bundled `results.stm` and `notfnd.stm`, `environ.pl`) |
| FTP, SMTP/POP3, proxy, DNS, HTTPS, the admin console | not checked ([ROADMAP.md](ROADMAP.md)) |
| Windows service (`-i`, `StartServiceCtrlDispatcher`) | not run: the recomp runs `-d`, the console server |
| Headless | it is: `-d` is a console program with no window |
| Conformance harness | `tools/http_diff.py`: **31/31** on a machine with the program; SKIP without it |

Built and tested against pcrecomp branch `pcrecomp-sambar` at `6aed261` (not yet on
`main`; see Building from source).

## Screenshots

None: Sambar's console server has no window. What it serves is the output,
and `tools/http_diff.py` compares it byte for byte.

## What is not in this repo

Nothing of Sambar: no executable, DLL, MAP file, page, configuration and
**no generated source**. The recompiled C is produced on your machine from
your own copy by `run_lift.py`, into `src/recomp/gen/`, which is gitignored.

## Getting Started

You need **your own copy of Sambar Server 6.4**: its installer,
`sambar64p.exe` (6,887,021 bytes, SHA-256
`e81cba69ee6b22552b1d669bd43976f2307581bf3c9b9b2f6309f5325e22c5b3`). The
Internet Archive's Wayback Machine has it from sambar.com, captured
2006-07-08. Sambar's license allows using it, not redistributing it, so
nothing is downloaded for you. The installer does not need to be run: Setup
unpacks it.

### Quick start: Setup.cmd

1. Download this repository (the green **Code** button, then **Download ZIP**)
   and unzip it somewhere with 1.5 GB free.
2. Put `sambar64p.exe` in that folder (or install Sambar to `C:\sambar`).
3. Double-click **`Setup.cmd`**.

It checks for Python 3.10+, the `pefile` and `capstone` packages, the pcrecomp
toolkit and the Visual Studio 2022 C++ compiler, and **asks** before
installing any of them, saying what and how big. It finds `sambar64p.exe` or
`C:\sambar`, or asks where Sambar is (`Setup.cmd -GameDir <file or folder>`
skips the question, `-Yes` answers yes to every install). Then it unpacks
Sambar into `game\` (reading the installer, never running it), writes a
`game\config\config.ini` bound to `127.0.0.1`, rebases and catalogs the six
modules, recompiles them and builds `build\sambarrecomp.exe`. A rerun skips
the finished steps. If it stops, it says why in one sentence, and the details
are in `setup.log`.

It ends with a **`Sambar Server (recomp)`** shortcut in the folder, which
starts the recompiled server in a console on `http://127.0.0.1/`.

The [recomp-launcher](https://github.com/sp00nznet/recomp-launcher) installer
uses `launcher/launcher.json` to do the same.

### Step by step

Prerequisites: Windows 10/11, **Python 3.10+** (`py -3 --version`), **git**,
**Visual Studio 2022** (or its Build Tools) with *Desktop development with
C++*, and the pcrecomp toolkit cloned **beside** this repository as
`pcrecomp`:

```
some-folder\
  pcrecomp\                     <- git clone https://github.com/sp00nznet/pcrecomp
  sambar\                       <- this repository
```

1. Python packages:
   ```
   py -3 -m pip install --user pefile capstone
   ```
2. Unpack Sambar into `game\` (the installer is an NSIS 2.0 beta, which 7-Zip
   lists as empty; pcrecomp reads it), or copy an installed `C:\sambar` there:
   ```
   py -3 -I ..\pcrecomp\tools\assets\extract_nsis.py sambar64p.exe game
   ```
   Expected: `1411 files placed, 2 unnamed blocks, 6-int entries`.
3. A config bound to localhost, from the shipped template:
   ```
   powershell -c "(gc game\config\config.bkp) -replace '^Force IP Bind =.*','Force IP Bind = 127.0.0.1' | sc game\config\config.ini"
   ```
4. Rebase the six modules and catalog their functions (about 15 minutes,
   most of it `sambar.dll`):
   ```
   py -3 tools\catalog.py
   ```
   Expected, among the output: `sambarcm.dll  0x10400000-0x10502000  (linked
   0x10000000)` and, for `sambar.dll`, `[*] Functions: 10419`.
5. Recompile to C (about a minute):
   ```
   py -3 run_lift.py
   ```
   Expected, at the end:
   `17384 entries in the dispatch table, lift errors 0, unimplemented instructions 1`.
6. Build (20 to 40 minutes on 8 cores; netlab does it too, below):
   ```
   build.cmd
   ```
   Expected: `Linking C executable sambarrecomp.exe`.
7. Check it without starting the server:
   ```
   build\sambarrecomp.exe
   ```
   Expected: `6 modules mapped and bound, 0 unresolved`.
8. Run it: `build\sambarrecomp.exe --run`, then open `http://127.0.0.1/`.

The usual trip-ups: `python` opening the Microsoft Store (that is Windows'
alias placeholder; use `py -3`, or turn the alias off in *Settings > Apps >
Advanced app settings > App execution aliases*); a freshly installed Python
not being on `PATH` until you open a new window; `run_lift.py` refusing a
different version (it checks the 6.4p PE stamps); and port 80 already taken
(set `HTTP Port` in `game\config\config.ini`).

## Usage

```
build\sambarrecomp.exe --run                               # the console server, game\config\config.ini
build\sambarrecomp.exe --run --args "-d -c C:\scratch\cfg" # another config folder
build\sambarrecomp.exe --run --watchdog 60                 # stop after 60 s, saying where it was
build\sambarrecomp.exe --run --native-trace                # one line per call into Windows
py -3 tools\http_diff.py                                   # the conformance check, below
```

| Flag | |
|---|---|
| `--run` | start the server (without it: map and bind the modules and stop) |
| `--game DIR` | the Sambar folder (default `game`); `GetModuleFileName` reports `DIR\bin\...` |
| `--modules DIR` | the rebased modules (default `work\rebased`) |
| `--args "..."` | `ntserver.exe`'s command line (default `-d`, the console server) |
| `--watchdog S` | stop after S seconds and say where it was |
| `--native-trace`, `--callbacks` | one line per call into Windows, or back from it |

### The conformance check

```
py -3 tools\http_diff.py           # -v prints each difference, --keep keeps the logs
```

copies `game\` twice into a scratch folder, writes each copy a `config.ini`
from `config.bkp` (HTTP only, `Force IP Bind = 127.0.0.1`, ports 18080 and
18081, the proxy off), generates one docroot with fixed file times, and runs the original
`ntserver.exe -d` and then the recomp on it, one at a time: two Sambars on one
machine do not work (the second accepts connections and never answers them,
two originals included). It sends both the same 31
raw requests: static text and binary files, an empty file, HTTP/1.0, 1.1 and
0.9, HEAD, four byte ranges and a bad one, `If-Modified-Since`, two 404s
(the bundled `notfnd.stm` page), a directory index, a redirect, two directory
listings, a file name with a space, a generated `.stm` page and the bundled
`results.stm`, the bundled `/cgi-bin/environ.pl` (run by the bundled Perl),
two `../` escapes, an unknown method, OPTIONS and garbage. It compares the
responses byte for byte after dropping `Date` and replacing each server's
port and folder with a placeholder, and prints `http_diff: PASS n/31`. Without
`game\bin\ntserver.exe` it prints `http_diff: skipped` and exits 0. Nothing
listens anywhere but `127.0.0.1`.

Current figure: **31/31** (2026-11-11).

On [netlab](https://github.com/sp00nznet/recomp-netlab) the recipe is
`projects/sambar-recomp.env`: `netlab build sambar-recomp`, and
`netlab check sambar-recomp` runs this check (SKIP on the test VMs, which
have no copy of the program).

## Building from source

Steps 4 to 6 above. `PCRECOMP` (Python) and `-DPCRECOMP=` (CMake, through
`set CMAKE_ARGS=...` for `build.cmd`) point at a toolkit checkout other than
`..\pcrecomp`; the lifter and the runtime must come from the same tree.

This needs pcrecomp's `pcrecomp-sambar` branch until it is merged:
`tools/pe/rebase.py`, `tools/lift/drive32.py` (alias stubs: without them one
20 KB function in `sambar.dll` lifts to an 84 MB file MSVC cannot finish),
`runtime/native32/modules32.c` (the module loader) and
`tools/assets/extract_nsis.py`. More in
[docs/architecture.md](docs/architecture.md).

## License

MIT, for the code in this repository ([LICENSE](LICENSE); attribution in
[NOTICE](NOTICE)). Sambar Server is (c) 1996-2006 Sambar Technologies; none
of it is here.
