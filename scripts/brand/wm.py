"""text -> SVG path outlines (so the wordmark looks the same on every device). usage: wm.text(font, 'throwindice', size, tracking_em) -> (paths per char, width)"""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

_cache = {}
def font(path):
    if path not in _cache: _cache[path] = TTFont(path)
    return _cache[path]

def text(path, s, size, track=0.0):
    f = font(path); gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm; k = size / upm
    kern = {}
    try:  # simple pair kerning from GPOS is complex; use legacy kern if present
        for t in f['kern'].kernTables: kern.update(t.kernTable)
    except Exception: pass
    x = 0.0; out = []; prev = None
    for ch in s:
        g = cmap.get(ord(ch))
        if g is None: continue
        if prev and (prev, g) in kern: x += kern[(prev, g)] * k
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, x, 0)))
        out.append((ch, pen.getCommands(), x))
        x += gs[g].width * k + track * size; prev = g
    return out, x - track * size

def svg_text(path, s, size, track=0.0, fills=None):
    """returns (svg <g> markup with baseline at y=0, width). fills: list of (start_index, end_index, fill)"""
    parts, w = text(path, s, size, track); out = []
    for i, (ch, d, x) in enumerate(parts):
        fill = 'currentColor'
        for a, b, f in (fills or []):
            if a <= i < b: fill = f
        out.append(f'<path d="{d}" fill="{fill}"/>')
    return ''.join(out), w
