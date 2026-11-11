#!/usr/bin/env python3
"""The conformance check: the original Sambar and the recomp answer the same
HTTP requests the same way.

Each server gets its own copy of game\\ in a scratch folder, a config.ini made
from the shipped config.bkp (HTTP only, bound to 127.0.0.1, its own port, the
proxy off) and one generated docroot they both serve. The servers run one
after the other (two Sambars at once do not work). A fixed corpus of
requests goes to each (static files, a 404, a directory listing, HEAD, byte
ranges, a .stm script page, the bundled /cgi-bin/environ.pl, and a few odd
ones), and the responses are compared with the Date header dropped and each
server's own port and folder replaced by a placeholder.

    py -3 tools\\http_diff.py            # PASS n/m; exit 0 when every one matches
    py -3 tools\\http_diff.py -v         # also print each difference
    py -3 tools\\http_diff.py --recomp X # test another host build (netlab's)
    py -3 tools\\http_diff.py --keep     # keep the scratch folder and both logs

Without game\\bin\\ntserver.exe it prints `http_diff: skipped` and exits 0.
Both servers bind to 127.0.0.1 only: nothing is reachable from outside.
"""
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, 'game')
HOST = os.path.join(ROOT, 'build', 'sambarrecomp.exe')
MODS = os.path.join(ROOT, 'work', 'rebased')
PORTS = {'original': 18080, 'recomp': 18081}

# A deterministic docroot: every byte is a function of its name.
def docroot(d):
    os.makedirs(os.path.join(d, 'sub', 'deeper'))
    os.makedirs(os.path.join(d, 'listme'))
    open(os.path.join(d, 'index.htm'), 'w', newline='\n').write(
        '<html><head><title>conformance</title></head><body>index</body></html>\n')
    open(os.path.join(d, 'hello.txt'), 'w', newline='\n').write('hello, world\n' * 3)
    open(os.path.join(d, 'style.css'), 'w', newline='\n').write('body { color: #123456 }\n')
    open(os.path.join(d, 'blob.bin'), 'wb').write(bytes((i * 7 + (i >> 8)) & 0xFF for i in range(70000)))
    open(os.path.join(d, 'empty.txt'), 'wb').close()
    open(os.path.join(d, 'sub', 'index.html'), 'w', newline='\n').write('<p>sub index</p>\n')
    open(os.path.join(d, 'sub', 'deeper', 'a b.txt'), 'w', newline='\n').write('space in name\n')
    for i in range(5):
        open(os.path.join(d, 'listme', 'file%d.txt' % i), 'w', newline='\n').write('x' * (i * 100 + 1))
    # Sambar's server-side scripting (.stm): RC macros.
    open(os.path.join(d, 'page.stm'), 'w', newline='\n').write(
        '<html><body>\nuri=<RCEdocument_uri>\nq=<RC@txt2html(RC$q)>\n'
        'upper=<RC@upper(RC$q)>\n</body></html>\n')
    shutil.copy(os.path.join(GAME, 'docs', 'results.stm'), os.path.join(d, 'results.stm'))
    # A fixed mtime: Last-Modified and the directory listing show it.
    t = 1136073600                                 # 2006-01-01
    for dp, dn, fn in os.walk(d):
        for n in fn + dn:
            os.utime(os.path.join(dp, n), (t, t))


def corpus():
    g = lambda p, extra='', m='GET', v='1.0': ('%s %s HTTP/%s\r\nHost: 127.0.0.1\r\n%s'
                                                'Connection: close\r\n\r\n' % (m, p, v, extra)).encode()
    return [
        ('index', g('/')),
        ('index-explicit', g('/index.htm')),
        ('text', g('/hello.txt')),
        ('css', g('/style.css')),
        ('binary', g('/blob.bin')),
        ('empty', g('/empty.txt')),
        ('http11', g('/hello.txt', v='1.1')),
        ('head', g('/hello.txt', m='HEAD')),
        ('head-binary', g('/blob.bin', m='HEAD')),
        ('404', g('/nope.html')),
        ('404-deep', g('/sub/nope/x.txt')),
        ('subdir-index', g('/sub/')),
        ('subdir-no-slash', g('/sub')),
        ('dir-listing', g('/listme/')),
        ('dir-listing-nested', g('/sub/deeper/')),
        ('space-name', g('/sub/deeper/a%20b.txt')),
        ('range-first', g('/blob.bin', 'Range: bytes=0-99\r\n')),
        ('range-middle', g('/blob.bin', 'Range: bytes=1000-1999\r\n')),
        ('range-suffix', g('/blob.bin', 'Range: bytes=-500\r\n')),
        ('range-open', g('/hello.txt', 'Range: bytes=10-\r\n')),
        ('range-bad', g('/hello.txt', 'Range: bytes=9999-\r\n')),
        ('if-modified-since', g('/hello.txt', 'If-Modified-Since: Tue, 01 Jan 2030 00:00:00 GMT\r\n')),
        ('stm', g('/page.stm?q=a%3Cb%26c')),
        ('stm-bundled', g('/results.stm?query=zzz')),
        ('cgi-environ', g('/cgi-bin/environ.pl?x=1')),
        ('dotdot', g('/../config/config.ini')),
        ('dotdot-encoded', g('/%2e%2e/config/config.ini')),
        ('bad-method', g('/', m='BREW')),
        ('options', g('/', m='OPTIONS')),
        ('http09', b'GET /hello.txt\r\n\r\n'),
        ('garbage', b'\x00\x01\x02 nonsense\r\n\r\n'),
    ]


def config(dst, port, docs):
    """config.ini from the shipped template: HTTP only, 127.0.0.1, port."""
    keys = {'HTTP Port': str(port), 'Force IP Bind': '127.0.0.1', 'Documents Directory': docs,
            'Act As HTTP Proxy': 'false', 'Act As HTTPS Server': 'false', 'Act As FTP Server': 'false',
            'Run Watcher': 'false', 'Resolve Host Names': 'false', 'Compress Content': 'false',
            'Trace Performance': 'false'}
    lines = []
    for ln in open(os.path.join(GAME, 'config', 'config.bkp'), encoding='latin-1').read().splitlines():
        k = ln.split('=')[0].strip()
        lines.append('%s = %s' % (k, keys[k]) if k in keys else ln)
    open(os.path.join(dst, 'config', 'config.ini'), 'w', encoding='latin-1', newline='\r\n').write(
        '\n'.join(lines) + '\n')


def ask(port, req):
    s = socket.create_connection(('127.0.0.1', port), timeout=10)
    s.sendall(req)
    out = b''
    try:
        while True:
            b = s.recv(65536)
            if not b:
                break
            out += b
    except socket.timeout:
        out += b'<timeout>'
    s.close()
    return out


def norm(resp, port, folder):
    head, _, body = resp.partition(b'\r\n\r\n')
    lines = [ln for ln in head.split(b'\r\n') if not re.match(rb'(?i)date:', ln)]
    out = b'\r\n'.join(lines) + b'\r\n\r\n' + body
    for f in {folder, folder.replace('\\', '/'), folder.lower(), folder.replace('\\', '/').lower()}:
        out = out.replace(f.encode(), b'<ROOT>')
    return out.replace(str(port).encode(), b'<PORT>')


def wait_up(port, proc, secs=60):
    t = time.time() + secs
    while time.time() < t:
        if proc.poll() is not None:
            return False
        try:
            socket.create_connection(('127.0.0.1', port), timeout=1).close()
            return True
        except OSError:
            time.sleep(0.3)
    return False


def main():
    global HOST
    verbose = '-v' in sys.argv
    if '--recomp' in sys.argv:                     # netlab: the host it built
        HOST = os.path.abspath(sys.argv[sys.argv.index('--recomp') + 1])
    if not os.path.exists(os.path.join(GAME, 'bin', 'ntserver.exe')):
        print('http_diff: skipped (no game\\bin\\ntserver.exe)')
        return 0
    if not os.path.exists(HOST):
        print('http_diff: no %s -- build first' % HOST)
        return 1
    scratch = tempfile.mkdtemp(prefix='sambar_diff_')
    docs = os.path.join(scratch, 'docs')
    docroot(docs)
    cases, got, proc = corpus(), {}, None
    try:
        # One server at a time: a second Sambar on the same machine accepts
        # connections and never answers them. Two originals do it too. Likely
        # the one-instance named pipe ntserver -d opens for its display,
        # \\.\pipe\SambarServer.
        for who, port in PORTS.items():
            d = os.path.join(scratch, who)
            shutil.copytree(GAME, d)
            config(d, port, docs)
            cmd = ([os.path.join(d, 'bin', 'ntserver.exe'), '-d'] if who == 'original'
                   else [HOST, '--run', '--game', d, '--modules', MODS])
            with open(os.path.join(scratch, who + '.log'), 'wb') as log:
                proc = subprocess.Popen(cmd, cwd=os.path.join(d, 'bin'), stdin=subprocess.DEVNULL,
                                        stdout=log, stderr=subprocess.STDOUT)
                if not wait_up(port, proc):
                    print('http_diff: %s did not start listening on 127.0.0.1:%d (log %s)'
                          % (who, port, os.path.join(scratch, who + '.log')))
                    return 1
                # Listening is not ready: the server opens its socket before
                # its plug-ins' INIT hooks have run, and a request that early
                # waits on them.
                time.sleep(5)
                got[who] = [norm(ask(port, req), port, d) for _, req in cases]
                proc.kill()
                proc.wait()
                proc = None
        passed = 0
        for k, (name, _) in enumerate(cases):
            # Both timing out is not agreement: the check proves nothing then.
            ok = got['original'][k] == got['recomp'][k] and not got['original'][k].endswith(b'<timeout>')
            passed += ok
            print('  %-20s %s' % (name, 'ok' if ok else 'DIFFERENT'))
            if verbose and not ok:
                for w in PORTS:
                    print('    --- %s (%d bytes)' % (w, len(got[w][k])))
                    print(got[w][k][:600].decode('ascii', 'backslashreplace'))
        print('http_diff: PASS %d/%d' % (passed, len(cases)))
        return 0 if passed == len(cases) else 1
    finally:
        if proc:
            proc.kill()
            proc.wait()
        if '--keep' not in sys.argv:
            shutil.rmtree(scratch, ignore_errors=True)
        else:
            print('kept', scratch)


if __name__ == '__main__':
    sys.exit(main())
