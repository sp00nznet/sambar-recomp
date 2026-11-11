#!/usr/bin/env python3
"""Rebase every module, then catalog its functions: work/<module>.functions.json.

The six modules ntserver.exe runs are all linked at 0x10000000 but the EXE;
pcrecomp's tools/pe/rebase.py gives each its own base (work/bases.json, the
copies in work/rebased/), which src/runtime/host.c holds too.

Sambar ships the linker MAP of each of its own modules (bin/*.map), so its
functions are seeded from there (shifted by the module's rebase delta, code
section only), and pcrecomp's disasm32 finds the rest. sqlite3.dll has no MAP.

    py -3 tools/catalog.py          # a few minutes; sambar.dll is most of it
"""
import json
import os
import subprocess
import sys

import pefile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(os.environ.get('PCRECOMP', os.path.join(ROOT, '..', 'pcrecomp')), 'tools')
WORK = os.path.join(ROOT, 'work')
BIN = os.path.join(ROOT, 'game', 'bin')
# Keep in step with g_modules in src/runtime/host.c.
MODULES = ['ntserver.exe', 'sambar.dll', 'sambarcm.dll', 'sambarcs.dll', 'sqlite3.dll', 'samples.dll']


def main():
    subprocess.check_call([sys.executable, os.path.join(TOOLS, 'pe', 'rebase.py'), BIN,
                           os.path.join(WORK, 'rebased')] + MODULES + ['--json', os.path.join(WORK, 'bases.json')])
    bases = {n: int(b, 16) for n, b in json.load(open(os.path.join(WORK, 'bases.json'))).items()}
    for name, base in bases.items():
        img = os.path.join(WORK, 'rebased', name)
        stem = os.path.splitext(name)[0]
        seeds = os.path.join(WORK, name + '.mapseeds.json')
        names = {}
        mp = os.path.join(BIN, stem + '.map')
        if os.path.exists(mp):
            out = os.path.join(WORK, name + '.mapnames.json')
            subprocess.check_call([sys.executable, os.path.join(TOOLS, 'pe', 'map_names.py'), 'resolve',
                                   mp, os.path.join(BIN, name), '-o', out], stdout=subprocess.DEVNULL)
            pe = pefile.PE(img, fast_load=True)
            delta = base - pefile.PE(os.path.join(BIN, name), fast_load=True).OPTIONAL_HEADER.ImageBase
            text = [s for s in pe.sections if s.Characteristics & 0x20000000]
            code = [(base + s.VirtualAddress, base + s.VirtualAddress + s.Misc_VirtualSize) for s in text]
            for va, nm in json.load(open(out)).items():
                v = int(va, 16) + delta
                if any(lo <= v < hi for lo, hi in code):
                    names['0x%08X' % v] = nm
            json.dump(names, open(os.path.join(WORK, name + '.names.json'), 'w'), indent=0)
        json.dump(sorted(int(v, 16) for v in names), open(seeds, 'w'))
        print('[*] %s: %d MAP seeds' % (name, len(names)), flush=True)
        subprocess.check_call([sys.executable, os.path.join(TOOLS, 'disasm', 'disasm32.py'), img,
                               '-o', os.path.join(WORK, name + '.functions.json'), '--seed-functions', seeds])


if __name__ == '__main__':
    main()
