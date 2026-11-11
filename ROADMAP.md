# Roadmap

## Next
- Track the harness figure over time and fail on regression (REPO_RULES
  section 9): a `conformance.json` baseline, like hover's.
- More of the corpus: keep-alive (several requests on one connection), POST to
  a `.stm` form, `.htaccess`, virtual hosts, user directories (`/~user/`),
  `/session/` admin pages, large files and concurrent clients.
- The FTP server (`Act As FTP Server`): a second corpus, same harness shape.

## Then
- The service path: `ntserver.exe -i` / `-u` and `StartServiceCtrlDispatcher`
  in the recomp, tested on a netlab VM only (it installs a Windows service).
- Lift the modules this configuration does not load: `sambardb.dll` (DBMS),
  `sambarje.dll` (Java engine), `sqlite2.dll`, and OpenSSL's `libeay32.dll` and
  `ssleay32.dll` for HTTPS. Turning those features on today loads the original
  DLLs natively.
- `server.exe`, the tray-icon front end, run headless or on offstage.
- Setup.cmd: check `sambar64p.exe`'s SHA-256 before unpacking it.

## Out of scope
- Fixing Sambar's security bugs. The point is the original's behavior, byte
  for byte; [SECURITY.md](SECURITY.md) says how to keep it on localhost.
- Exposing the recomp to a network.
