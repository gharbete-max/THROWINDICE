"""Brand assets for throwindice: mark, wordmark (Inter 800 outlined to paths), lockups, favicon, app icons, share image.

usage: python3 scripts/brand/build.py <inter-800.ttf> [<logo3d.png>] [<hero-poster.webp>]
  inter-800.ttf : Inter ExtraBold (npm @fontsource/inter, files/inter-latin-800-normal.woff2, saved as ttf with fontTools)
  logo3d.png    : objects.py logo3d render (1024 px, transparent) -> apple-touch-icon / manifest icons
Writes assets/brand/* and prints the inline header snippets (mark + wordmark) used in index.html.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import wm

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'brand')
INK_L, INK_D = '#1d1d1f', '#f5f5f7'
GOLD = [('0', '#f6dc8c'), ('.55', '#d9a84a'), ('1', '#a87a30')]
GOLD_SIDE = [('0', '#9c6f2a'), ('1', '#6e4c1c')]
TOK = [('0', '#b4c0ff'), ('.55', '#7d86f2'), ('1', '#5145c8')]
TOK_SIDE = [('0', '#4b3fb0'), ('1', '#2f2780')]
WORD_GOLD = [('0', '#e9bf62'), ('1', '#a87a30')]
WORD_TOK = [('0', '#a9b4ff'), ('1', '#5f52d8')]

def grad(id_, stops, x2='1', y2='1'):
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">' + ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) + '</linearGradient>'

def mark_body(p, ink='currentColor', tok=False):
    """the mark in a 100 x 76 box: a price-tag bracket with its hole, a die (two pips) tipping into it. p = id prefix"""
    return (f'<defs>{grad(p + "f", TOK if tok else GOLD)}{grad(p + "s", TOK_SIDE if tok else GOLD_SIDE, "0", "1")}</defs>'
            f'<path d="M9 22V11a3 3 0 0 1 3-3h46M9 22v33a3 3 0 0 0 3 3h46" fill="none" stroke="{ink}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="20" cy="38" r="5" fill="{ink}"/>'
            f'<g transform="translate(62 36) rotate(45)"><rect x="-21" y="-17" width="42" height="42" rx="10" fill="url(#{p}s)"/>'
            f'<rect x="-21" y="-21" width="42" height="42" rx="10" fill="url(#{p}f)"/><rect x="-17" y="-18" width="34" height="9" rx="4.5" fill="#fff" opacity=".35"/>'
            '<circle cx="-8" cy="-8" r="4.6" fill="#fffaf0"/><circle cx="8" cy="8" r="4.6" fill="#fffaf0"/></g>')

def word(font, size=100):
    """'throwindice' with 'indice' (index) in gold; returns (paths markup with class g on the gold part, width). baseline y=0, cap top ~ -0.73*size"""
    parts, w = wm.text(font, 'throwindice', size, -0.045)
    out = ''.join(f'<path d="{d}"' + (' class="g"' if i >= 5 else '') + '/>' for i, (ch, d, x) in enumerate(parts))
    return out, w

def write(name, s):
    open(os.path.join(OUT, name), 'w').write(s); print('wrote', name)

def main():
    font = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
    wp, ww = word(font)
    # standalone files
    for th, ink in (('light', INK_L), ('dark', INK_D)):
        write(f'mark-{th}.svg', f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 76">{mark_body("m", ink)}</svg>')
        W = 100 + 26 + ww
        write(f'logo-{th}.svg', f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -2 {W:.0f} 80"><g>{mark_body("m", ink)}</g>'
              f'<defs>{grad("wg", WORD_GOLD, "0", "1")}</defs><g transform="translate(126 66) scale(.82)" fill="{ink}"><style>.g{{fill:url(#wg)}}</style>{wp}</g></svg>')
    write('favicon.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -12 100 100"><style>.i{color:#1d1d1f}@media (prefers-color-scheme:dark){.i{color:#f5f5f7}}</style>'
          f'<g class="i">{mark_body("f")}</g></svg>')
    # inline header snippets (ink follows var(--text) through currentColor)
    hdr_mark = (f'<svg class="real-logo" viewBox="0 0 100 76" aria-hidden="true">{mark_body("hr")}</svg>'
                f'<svg class="token-logo" viewBox="0 0 100 76" aria-hidden="true">{mark_body("ht", tok=True)}</svg>')
    hdr_word = (f'<svg class="brandWord" viewBox="0 -76 {ww:.0f} 78" aria-hidden="true"><defs>{grad("bwg", WORD_GOLD, "0", "1")}{grad("bwt", WORD_TOK, "0", "1")}</defs>'
                f'<g fill="currentColor">{wp}</g></svg>')
    open('/tmp/brand_snippets.txt', 'w').write(hdr_mark + '\n@@\n' + hdr_word); print('snippets -> /tmp/brand_snippets.txt', 'word width', round(ww))

if __name__ == '__main__':
    main()

def icons(logo3d):
    """app icons from the 3D render: soft light background, logo fitted (maskable keeps the 80% safe zone)"""
    from PIL import Image
    src = Image.open(logo3d).convert('RGBA'); src = src.crop(src.getbbox())
    def bg(n):
        im = Image.new('RGBA', (n, n)); top, bot = (255, 255, 255), (236, 236, 240)
        for y in range(n):
            t = y / (n - 1); im.paste(tuple(round(a + (b - a) * t) for a, b in zip(top, bot)) + (255,), (0, y, n, y + 1))
        return im
    def make(n, fill):
        im = bg(n); k = fill * n / max(src.size); s = src.resize((round(src.width * k), round(src.height * k)), Image.LANCZOS)
        im.alpha_composite(s, ((n - s.width) // 2, (n - s.height) // 2 + round(n * .01))); return im.convert('RGB')
    for name, n, fill in (('apple-touch-icon.png', 180, .78), ('icon-192.png', 192, .78), ('icon-512.png', 512, .78), ('icon-maskable-512.png', 512, .6)):
        make(n, fill).save(os.path.join(OUT, name), optimize=True); print('wrote', name)

if __name__ == '__main__' and len(sys.argv) > 2:
    icons(sys.argv[2])
