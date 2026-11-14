# Building

The Quick start (`Setup.cmd`) runs exactly these steps; this is the same by hand.

## Step by step

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
4. Rebase the six modules and catalog their functions (about 10 minutes,
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
6. Build (about 3 minutes; netlab does it too, below):
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

## Another toolkit checkout

Steps 4 to 6 above. `PCRECOMP` (Python) and `-DPCRECOMP=` (CMake, through
`set CMAKE_ARGS=...` for `build.cmd`) point at a toolkit checkout other than
`..\pcrecomp`; the lifter and the runtime must come from the same tree.

This needs pcrecomp main:
`tools/pe/rebase.py`, `tools/lift/drive32.py` (alias stubs: without them one
20 KB function in `sambar.dll` lifts to an 84 MB file MSVC cannot finish),
`runtime/native32/modules32.c` (the module loader) and
`tools/assets/extract_nsis.py`. More in
[docs/architecture.md](docs/architecture.md).


## Linux and macOS

Not yet. The host calls the real ws2_32, kernel32 and advapi32 through pcrecomp `native32`, so it builds with MSVC for Windows only. `setup.sh` says so and exits. Running it under Wine has not been tried.
