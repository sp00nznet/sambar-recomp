# Security

## Read this first

Sambar Server is a **2000s-era web server with known, published
vulnerabilities**. Sambar Technologies stopped developing it in 2007 and never
fixed them. Its advisories go back years: directory traversal, cross-site
scripting in the bundled pages and the admin console, default accounts,
buffer overflows and denial-of-service bugs. Version 6.4 (2006), the one
recompiled here, is the last 6.x release, and it is not the fixed one.

A static recompilation runs **the same code**. Every bug in the original,
security bugs included, is in the recompiled build. This project makes Sambar
run as native code on a modern Windows. It does not make it safe.

**Only ever run it bound to localhost, for testing.**

- Bind it to `127.0.0.1`: `Force IP Bind = 127.0.0.1` in `config\config.ini`.
  The conformance harness (`tools\http_diff.py`) does this for both servers it
  starts, and gives each a port above 18000.
- Do not open it in Windows Firewall, forward a port to it, put it behind a
  reverse proxy or run it on a machine others can reach.
- Do not install it as a Windows service (`ntserver.exe -i`). The recomp runs
  only the console mode (`-d`).
- Turn off everything the test does not need. The harness's `config.ini` runs
  the HTTP server only: no proxy, FTP, mail, DNS, SSL or admin features.
- Do not serve real files from it. Give it a scratch docroot, as the harness
  does.
- The shipped `config\passwd` has an `admin` account with no password, and the
  admin console (`/session/adminlogin`) is reachable from `127.0.0.1`. Anything
  else running on the machine can use it.

## What the recomp adds

The host (`src/runtime/host.c`) and pcrecomp's runtime have the same access as
the server: files, the registry, sockets and child processes (CGI) under your
account. The host adds no network code of its own. Everything on the network
is Sambar's.

## Reporting

A problem in **this repository's own code** (the host, the harness, Setup or
the scripts) can be reported privately through GitHub's *Report a
vulnerability* on this repository. Sambar's own vulnerabilities are not ours to
fix, and there is no upstream left to report them to. Their only fix here is
the rule above: keep it on localhost.
