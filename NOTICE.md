# Notice

The MIT license in [LICENSE](LICENSE) covers what is ours in this repository:
the host, the setup scripts, the tools, the conformance harness and the
documentation. It does not cover Sambar Server.

*Sambar Server* is © 1996-2006 Sambar Technologies, freeware under its own
license (`license.txt` in its installer), which forbids redistributing it. Its
executables, DLLs, MAP files, pages, Perl and configuration are not in this
repository and are excluded by `.gitignore`.

- You need your own copy of Sambar Server 6.4 to use any of this. Setup unpacks
  your `sambar64p.exe` (or copies your installed folder) into `game/`; the
  pipeline reads it from there.
- Lifted code is a derivative work of the binary it came from. Anything the
  pipeline writes into `work/` or `src/recomp/gen*/` carries whatever license
  the original carries, not this one. The MIT grant stops at our own work.
- The host is derived from the AmazingMIDI recomp's host and the lift driver
  from the Unreal Tournament recomp's; both are ours and MIT, and run on
  [pcrecomp](https://github.com/sp00nznet/pcrecomp)'s `native32` runtime (MIT).
  No third-party code is vendored in this repository.
