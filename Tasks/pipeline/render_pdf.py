#!/usr/bin/env python3
"""render_pdf.py: print a ChandRush page (index.html) to a one-page 12 x 9 in PDF, and optionally a PNG preview.

  python3 pipeline/render_pdf.py PAGE.html OUT.pdf [--png OUT.png] [--dpi 110]

Uses the system Firefox in headless mode through its built-in Marionette protocol (WebDriver:Print), so
nothing has to be installed. The page must be a single 12in x 9in sheet (see PdfSheetsGenTask/design/base.css).
After printing it checks with pdfinfo that the PDF has exactly 1 page of 864 x 648 pt, and fails otherwise.
"""
import argparse
import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time

PAGE_CM = (30.48, 22.86)  # 12 x 9 in


class Marionette:
    def __init__(self, port):
        self.sock = socket.create_connection(("127.0.0.1", port), timeout=120)
        self.buf = b""
        self.n = 0
        self._read()  # greeting

    def _read(self):
        while b":" not in self.buf:
            self.buf += self.sock.recv(65536)
        size, rest = self.buf.split(b":", 1)
        size = int(size)
        while len(rest) < size:
            rest += self.sock.recv(1 << 20)
        msg, self.buf = rest[:size], rest[size:]
        return json.loads(msg)

    def cmd(self, name, params=None):
        self.n += 1
        data = json.dumps([0, self.n, name, params or {}]).encode()
        self.sock.sendall(str(len(data)).encode() + b":" + data)
        while True:
            msg = self._read()
            if msg[0] == 1 and msg[1] == self.n:
                if msg[2]:
                    raise RuntimeError(f"{name}: {msg[2]}")
                return msg[3]


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def chrome_print(html, pdf):
    """Fallback when Firefox is not installed (e.g. cloud containers): headless Chrome/Chromium print."""
    exe = next((shutil.which(x) for x in ("google-chrome", "chromium", "chromium-browser") if shutil.which(x)), None)
    if not exe:
        sys.exit("Neither firefox nor google-chrome/chromium is installed")
    subprocess.run([exe, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", "--run-all-compositor-stages-before-draw",
                    f"--print-to-pdf={pdf}", "file://" + html],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180, check=False)


def render(html, pdf, png=None, dpi=110):
    html, pdf = os.path.abspath(html), os.path.abspath(pdf)
    os.makedirs(os.path.dirname(pdf), exist_ok=True)
    if not shutil.which("firefox"):
        chrome_print(html, pdf)
        return finish(pdf, png, dpi)
    port = free_port()
    prof = tempfile.mkdtemp(prefix="cr-ff-", dir=os.environ.get("CR_TMP") or None)
    with open(os.path.join(prof, "user.js"), "w") as fh:
        fh.write(f'user_pref("marionette.port", {port});\n'
                 'user_pref("browser.shell.checkDefaultBrowser", false);\n'
                 'user_pref("datareporting.policy.dataSubmissionEnabled", false);\n'
                 'user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);\n'
                 'user_pref("print.always_print_silent", true);\n')
    proc = subprocess.Popen(["firefox", "--headless", "--marionette", "--no-remote", "--profile", prof],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        m = None
        for _ in range(120):
            try:
                m = Marionette(port)
                break
            except OSError:
                time.sleep(0.5)
        if m is None:
            sys.exit("Firefox Marionette did not start")
        m.cmd("WebDriver:NewSession", {"capabilities": {}})
        m.cmd("WebDriver:Navigate", {"url": "file://" + html})
        # wait for web fonts and images
        m.cmd("WebDriver:ExecuteAsyncScript", {"script": (
            "const done = arguments[arguments.length-1];"
            "Promise.all([document.fonts.ready, ...Array.from(document.images).map(i => i.complete ? 0 :"
            " new Promise(r => { i.onload = i.onerror = r; }))]).then(() => setTimeout(done, 300));"), "args": []})
        res = m.cmd("WebDriver:Print", {"page": {"width": PAGE_CM[0], "height": PAGE_CM[1]},
                                         "margin": {"top": 0, "bottom": 0, "left": 0, "right": 0},
                                         "background": True, "shrinkToFit": False, "orientation": "portrait"})
        with open(pdf, "wb") as fh:
            fh.write(base64.b64decode(res["value"]))
        try:
            m.cmd("Marionette:Quit", {"flags": ["eForceQuit"]})
        except Exception:
            pass
    finally:
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(prof, ignore_errors=True)
    finish(pdf, png, dpi)


def finish(pdf, png, dpi):
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    pages = next((l.split()[-1] for l in info.splitlines() if l.startswith("Pages:")), "?")
    size = next((l.split(":", 1)[1].strip() for l in info.splitlines() if l.startswith("Page size:")), "?")
    ok = pages == "1" and size.startswith("864 x 648")
    print(f"{'OK' if ok else 'BAD'} {pdf}: {pages} page(s), {size}")
    if png:
        base = os.path.splitext(os.path.abspath(png))[0]
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-singlefile", "-f", "1", "-l", "1", pdf, base], check=True)
        print(f"preview {base}.png")
    if not ok:
        sys.exit("the page overflowed or has the wrong size: fix the HTML so everything fits one 12x9 in sheet")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("pdf")
    ap.add_argument("--png")
    ap.add_argument("--dpi", type=int, default=110)
    a = ap.parse_args()
    render(a.html, a.pdf, a.png, a.dpi)
