#!/usr/bin/env python3
"""Render a distressed rubber-stamp style cover (paper grain, ink speckle, rough edges).

Usage: make_cover.py CONFIG.json OUT.png [--jpg OUT.jpg]
Only the Cairo font family is used (downloaded from Google Fonts on first run and cached).
Wide / condensed letterforms come from textLength + vertical scale, never from another typeface.
Needs: python3, Pillow, and a Chromium/Chrome binary.
"""
import base64, glob, json, os, random, re, shutil, subprocess, sys, tempfile

W, H, SCALE = 1240, 1754, 2          # A4 at 150 dpi, rendered at 2x -> 2480x3508


def chromium():
    for c in ['chromium', 'chromium-browser', 'google-chrome', 'chrome']:
        p = shutil.which(c)
        if p:
            return p
    for pat in ['/opt/pw-browsers/chromium-*/chrome-linux/chrome', '/usr/bin/chromium*']:
        g = sorted(glob.glob(pat))
        if g:
            return g[-1]
    sys.exit('no chromium found')


def fonts_css():
    cache = os.path.expanduser('~/.cache/stamp-cover/cairo.css')
    if os.path.exists(cache):
        return open(cache).read()
    css = subprocess.run(['curl', '-sS', '-m', '30', '-A', 'Mozilla/5.0',
                          'https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;800;900&display=swap'],
                         capture_output=True, text=True).stdout
    out = []
    for b in re.findall(r'@font-face\s*{(.*?)}', css, flags=re.S):
        url = re.search(r'url\((https://[^)]+)\)', b).group(1)
        wt = re.search(r'font-weight:\s*(\d+)', b).group(1)
        data = subprocess.run(['curl', '-sS', '-m', '40', url], capture_output=True).stdout
        out.append("@font-face{font-family:'Cairo';font-weight:%s;src:url(data:font/ttf;base64,%s) format('truetype');}" % (
            wt, base64.b64encode(data).decode()))
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    open(cache, 'w').write('\n'.join(out))
    return '\n'.join(out)


def logo_svg(cfg, base_dir):
    """Recolour a logo (any dark or light shape on a white background) to solid ink and place it.
    cfg['images'] = [{"src": "assets/logo.webp", "x": 620, "top": 110, "width": 200}]"""
    import io
    from PIL import Image
    ink = cfg.get('ink', '#1b1b1a')
    rgb = tuple(int(ink[i:i + 2], 16) for i in (1, 3, 5))
    out = ''
    for im_cfg in cfg.get('images', []):
        src = Image.open(os.path.join(base_dir, im_cfg['src']))
        if 'A' in src.getbands() and src.getchannel('A').getextrema()[0] < 255:
            a = src.getchannel('A')                     # transparent logo: the alpha is the shape
        else:                                           # opaque logo on white: shape = distance from white
            im = src.convert('RGB')
            px = im.load()
            a = Image.new('L', im.size)
            ap = a.load()
            for x in range(im.width):
                for y in range(im.height):
                    ap[x, y] = max(0, min(255, (255 - min(px[x, y]) - 4) * 20))
        bbox = a.getbbox()
        a = a.crop(bbox)
        w = im_cfg['width']
        h = round(w * a.height / a.width)
        a = a.resize((w * 3, h * 3), Image.LANCZOS)
        png = Image.new('RGBA', a.size, rgb + (0,))
        png.putalpha(a)
        buf = io.BytesIO()
        png.save(buf, 'PNG')
        out += '<image href="data:image/png;base64,%s" x="%s" y="%s" width="%d" height="%d"/>' % (
            base64.b64encode(buf.getvalue()).decode(), im_cfg.get('x', W // 2) - w // 2, im_cfg['top'], w, h)
    return out


def build(cfg, base_dir='.'):
    paper, ink, seed = cfg.get('paper', '#e8e8e4'), cfg.get('ink', '#1b1b1a'), cfg.get('seed', 11)
    rnd = random.Random(seed)
    txt = ''
    for l in cfg['lines']:
        txt += ('<text transform="translate(%s %s) scale(1 %s)" text-anchor="middle" font-family="Cairo" font-weight="%d" '
                'font-size="%d" textLength="%d" lengthAdjust="spacingAndGlyphs" fill="%s">%s</text>') % (
            l.get('x', W // 2), l['y'], l.get('sy', 1), l.get('weight', 800), l['size'], l['width'], ink, l['t'])
    dust = ''
    for _ in range(cfg.get('dust', 220)):
        dust += '<circle cx="%.1f" cy="%.1f" r="%s" fill="%s" opacity="%.2f"/>' % (
            rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice([.6, .8, 1, 1.4, 2.2]), ink, rnd.uniform(.12, .55))
    for _ in range(cfg.get('scratches', 14)):
        x, y, L, a = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(30, 160), rnd.uniform(-.5, .5)
        dust += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width=".7" opacity="%.2f"/>' % (
            x, y, x + L, y + L * a, ink, rnd.uniform(.08, .25))
    return '''<!doctype html><html><head><meta charset="utf-8"><style>%s html,body{margin:0;background:%s}svg{display:block}</style></head><body>
<svg width="%d" height="%d" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg"><defs>
<filter id="ink" x="-5%%" y="-5%%" width="110%%" height="110%%" color-interpolation-filters="sRGB">
 <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" seed="4" result="warp"/>
 <feDisplacementMap in="SourceGraphic" in2="warp" scale="4" result="d"/>
 <feGaussianBlur in="d" stdDeviation="1.1" result="b"/>
 <feComponentTransfer in="b" result="hard"><feFuncA type="linear" slope="5" intercept="-2.1"/></feComponentTransfer>
 <feTurbulence type="fractalNoise" baseFrequency="0.62" numOctaves="3" seed="9" result="n"/>
 <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  20 0 0 0 -12.6" result="holes"/>
 <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="2" seed="21" result="blot"/>
 <feColorMatrix in="blot" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  10 0 0 0 -7.4" result="blotm"/>
 <feComposite in="hard" in2="holes" operator="out" result="speck"/>
 <feComposite in="speck" in2="blotm" operator="out"/>
</filter>
<filter id="grain" x="0" y="0" width="100%%" height="100%%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="5"/><feColorMatrix type="matrix" values="0 0 0 0 .1  0 0 0 0 .1  0 0 0 0 .1  0 0 0 .55 -.12"/></filter>
<filter id="mottle" x="0" y="0" width="100%%" height="100%%"><feTurbulence type="fractalNoise" baseFrequency="0.004 0.006" numOctaves="3" seed="2"/><feColorMatrix type="matrix" values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .48  0 0 0 .5 -.18"/></filter>
<radialGradient id="vg" cx="50%%" cy="48%%" r="75%%"><stop offset="60%%" stop-color="#000" stop-opacity="0"/><stop offset="100%%" stop-color="#000" stop-opacity=".10"/></radialGradient>
</defs>
<rect width="%d" height="%d" fill="%s"/><rect width="%d" height="%d" filter="url(#mottle)" opacity=".5"/>
<g filter="url(#ink)">%s%s</g><g>%s</g>
<rect width="%d" height="%d" fill="url(#vg)"/>
<rect width="%d" height="%d" filter="url(#grain)" opacity=".8" style="mix-blend-mode:multiply"/>
</svg></body></html>''' % (fonts_css(), paper, W, H, W, H, W, H, paper, W, H, logo_svg(cfg, base_dir), txt, dust, W, H, W, H)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cfg = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    from PIL import Image
    tmp = tempfile.mkdtemp()
    html = os.path.join(tmp, 'cover.html')
    open(html, 'w').write(build(cfg, os.path.dirname(os.path.abspath(sys.argv[1]))))
    full = os.path.join(tmp, 'full.png')
    subprocess.run([chromium(), '--headless', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=%d' % SCALE, '--window-size=%d,%d' % (W, H + 150),
                    '--screenshot=' + full, 'file://' + html], capture_output=True)
    im = Image.open(full).convert('RGB').crop((0, 0, W * SCALE, H * SCALE))
    im.save(out)
    if '--jpg' in sys.argv:
        im.save(sys.argv[sys.argv.index('--jpg') + 1], quality=88, optimize=True)
    print('wrote', out, im.size)


if __name__ == '__main__':
    main()
