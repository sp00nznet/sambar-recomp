# Testing

## The conformance check: `tools/http_diff.py`

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

