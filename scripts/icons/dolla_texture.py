"""Dolla banknote texture (Washington-bill layout, a smiley in the portrait oval). Writes scripts/icons/dolla_tex.png for o_dolla()."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, sys
W, H = 1410, 600
INK, INK2, PAPER = (24, 74, 46), (46, 112, 70), (214, 230, 206)
SER = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
F = lambda s: ImageFont.truetype(SER, s)
im = Image.new('RGB', (W, H), PAPER); d = ImageDraw.Draw(im)
for y in range(0, H, 3):  # faint paper fibres / engraving grain
    d.line([(0, y), (W, y)], fill=(206, 224, 199) if (y // 3) % 2 else PAPER)
for k in range(3):        # guilloche border: three interlaced sine rosettes
    m = 18 + k * 9
    for t in range(0, 3600):
        a = t / 3600
        x = m + (W - 2 * m) * a; y1 = m + 7 * math.sin(a * 220 + k); y2 = H - m + 7 * math.sin(a * 220 + k)
        d.point((x, y1), fill=INK2); d.point((x, y2), fill=INK2)
        yy = m + (H - 2 * m) * a; x1 = m + 7 * math.sin(a * 95 + k); x2 = W - m + 7 * math.sin(a * 95 + k)
        d.point((x1, yy), fill=INK2); d.point((x2, yy), fill=INK2)
d.rounded_rectangle([46, 46, W - 46, H - 46], 18, outline=INK, width=6)
d.rounded_rectangle([62, 62, W - 62, H - 62], 14, outline=INK2, width=2)
cx, cy, rx, ry = W // 2, H // 2 + 4, 150, 150   # portrait oval with engraved hatching
for r in range(0, 44):
    d.ellipse([cx - rx - r * .3, cy - ry - r * .3, cx + rx + r * .3, cy + ry + r * .3], outline=INK2 if r % 2 else INK)
for y in range(cy - ry, cy + ry, 4):
    hw = rx * math.sqrt(max(0, 1 - ((y - cy) / ry) ** 2)); d.line([(cx - hw, y), (cx + hw, y)], fill=(170, 200, 165), width=1)
# the smiley, engraved: shaded face (concentric hatching darker toward the lower right), eyes, big smile
fr = 118
for r in range(fr, 0, -5):
    sh = 1 - r / fr; col = tuple(int(c1 + (c2 - c1) * (0.25 + 0.5 * sh)) for c1, c2 in zip(INK, PAPER))
    d.ellipse([cx - r + (fr - r) * .12, cy - r + (fr - r) * .1, cx + r + (fr - r) * .12, cy + r + (fr - r) * .1], outline=col, width=2)
d.ellipse([cx - fr, cy - fr, cx + fr, cy + fr], outline=INK, width=6)
for ex in (-40, 40): d.ellipse([cx + ex - 16, cy - 46, cx + ex + 16, cy - 4], fill=INK)
d.arc([cx - 70, cy - 34, cx + 70, cy + 74], 20, 160, fill=INK, width=11)
for ex in (-80, 80): d.ellipse([cx + ex - 18, cy + 12, cx + ex + 18, cy + 36], outline=INK2, width=3)  # engraved cheeks
# text
def ct(t, y, s, fill=INK):
    w = d.textlength(t, font=F(s)); d.text((cx - w / 2, y), t, font=F(s), fill=fill)
ct('THE UNITED BALLS OF BOUNCE', 78, 42)
ct('ONE DOLLA', H - 118, 50)
d.text((210, cy + 92), 'IN BULLS WE TRUST', font=F(22), fill=INK2)
for (x, y) in ((70, 70), (W - 150, 70), (70, H - 160), (W - 150, H - 160)):  # corner numerals
    d.text((x + 8, y), '1', font=F(84), fill=INK)
def seal(x, y, r, txt, fill):  # treasury-style seals: toothed ring + glyph
    for t in range(48):
        a = t / 48 * 2 * math.pi; d.polygon([(x + r * math.cos(a), y + r * math.sin(a)), (x + (r + 12) * math.cos(a + .065), y + (r + 12) * math.sin(a + .065)), (x + r * math.cos(a + .13), y + r * math.sin(a + .13))], fill=fill)
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill); d.ellipse([x - r + 10, y - r + 10, x + r - 10, y + r - 10], outline=PAPER, width=3)
    w = d.textlength(txt, font=F(int(r * 1.1))); d.text((x - w / 2, y - r * .72), txt, font=F(int(r * 1.1)), fill=PAPER)
seal(300, cy + 10, 62, '$', INK2); seal(W - 300, cy + 10, 62, 'D', (34, 96, 60))
d.text((150, 168), 'B 0700 7000 S', font=F(30), fill=(40, 120, 80)); d.text((W - 410, H - 210), 'B 0700 7000 S', font=F(30), fill=(40, 120, 80))
im = im.filter(ImageFilter.SMOOTH)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dolla_tex.png'); im.save(out); print(out)
