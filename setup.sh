#!/bin/sh
# Sambar Server recomp: no Linux or macOS build yet.
# The host calls the real ws2_32, kernel32 and advapi32 through pcrecomp's
# native32 runtime and builds with MSVC, so it is Windows only for now, and
# running it under Wine has not been tested. Use Setup.cmd on Windows
# (docs/building.md).
echo "Sambar Server recomp builds on Windows only for now: run Setup.cmd there. See docs/building.md." >&2
exit 1
