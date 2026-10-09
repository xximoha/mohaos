#!/usr/bin/env python3
"""Put the stamp cover in front of any PDF.

Usage: add_cover.py BODY.pdf OUT.pdf CONFIG.json
  e.g. add_cover.py report.pdf report_with_cover.pdf ../examples/sharps.json

Builds the cover with make_cover.py, turns it into a full-bleed A4 page, and merges it as page 1.
Needs: Chromium, Pillow, and either pdfunite (poppler) or the pypdf package.
"""
import os, shutil, subprocess, sys, tempfile

here = os.path.dirname(os.path.abspath(__file__))


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    body, out, cfg = sys.argv[1:]
    tmp = tempfile.mkdtemp()
    png = os.path.join(tmp, 'cover.png')
    subprocess.run([sys.executable, os.path.join(here, 'make_cover.py'), cfg, png], check=True)
    html = os.path.join(tmp, 'cover_page.html')
    open(html, 'w').write('<!doctype html><html><head><style>@page{size:A4;margin:0}html,body{margin:0;background:#e8e8e4}'
                          'img{width:210mm;height:297mm;display:block}</style></head><body><img src="file://%s"></body></html>' % png)
    sys.path.insert(0, here)
    from make_cover import chromium
    cover_pdf = os.path.join(tmp, 'cover.pdf')
    subprocess.run([chromium(), '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    '--print-background', '--print-to-pdf=' + cover_pdf, 'file://' + html], capture_output=True, check=True)
    if shutil.which('pdfunite'):
        subprocess.run(['pdfunite', cover_pdf, body, out], check=True)
    else:
        from pypdf import PdfWriter
        w = PdfWriter()
        for f in (cover_pdf, body):
            w.append(f)
        w.write(out)
    print('wrote', out)


if __name__ == '__main__':
    main()
