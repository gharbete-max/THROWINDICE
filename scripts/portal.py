"""Token portal transition: black hole -> lightspeed jump with spinning 8-bit coins -> white flash.
Vertical 9:16, 2.5 s @ 30 fps. Usage: python3 portal.py out.mp4 [width]"""
import sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = sys.argv[1] if len(sys.argv) > 1 else 'portal.mp4'
W = int(sys.argv[2]) if len(sys.argv) > 2 else 720
H = W * 16 // 9; FPS, DUR = 30, 2.5; N = int(FPS * DUR)
CX, CY = W / 2, H * 0.46; F = W * 0.9           # vanishing point a touch above centre, focal length in px
rng = np.random.default_rng(3)

def smooth(a, b, x): x = min(1.0, max(0.0, (x - a) / (b - a))); return x * x * (3 - 2 * x)

# ---------- 8-bit coin sprites (original design: round gold coin with a pixel star) ----------
STAR = ["..#..", ".###.", "#####", ".###.", "#.#.#"]
def coin_sprite(width_frac):
    """16x16 coin seen at a spin angle: width_frac 1 = face on, ~0.15 = edge on."""
    S = 16; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); px = im.load()
    rx = max(0.9, 7.5 * width_frac); ry = 7.5
    for y in range(S):
        for x in range(S):
            dx, dy = (x + 0.5 - 8) / rx, (y + 0.5 - 8) / ry; d = dx * dx + dy * dy
            if d > 1: continue
            if d > 0.62: c = (176, 92, 18)        # dark rim
            elif dx < -0.25 and dy < -0.1: c = (255, 246, 160)  # highlight
            else: c = (255, 196, 40)              # gold
            if width_frac < 0.3: c = (214, 138, 26) if abs(dx) < 0.7 else (150, 78, 14)  # edge
            px[x, y] = (*c, 255)
    if width_frac > 0.55:  # emblem, squashed with the spin
        for j, row in enumerate(STAR):
            for i, ch in enumerate(row):
                if ch == '#':
                    x = int(round(8 + (i - 2) * width_frac)); y = 5 + j
                    if 0 <= x < S: px[x, y] = (205, 120, 20, 255)
    return im
SPRITES = [coin_sprite(f) for f in (1.0, 0.8, 0.5, 0.18, 0.5, 0.8)]  # classic stepped spin

# ---------- scene ----------
NS, NC = 1600, 70
stars = np.c_[rng.normal(0, 1, (NS, 2)) * [1.4, 2.2], rng.uniform(0.3, 12, NS)]  # x, y, z
star_col = rng.choice(np.array([[255, 255, 255], [190, 210, 255], [200, 170, 255], [140, 200, 255]]), NS)
coins = np.c_[rng.normal(0, 1, (NC, 2)) * [1.1, 1.7], rng.uniform(2, 14, NC)]
coin_phase = rng.uniform(0, 6, NC); coin_spd = rng.uniform(10, 18, NC)

ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
R = np.hypot(xs - CX, ys - CY) / W; TH = np.arctan2(ys - CY, xs - CX)
vign = np.clip(1.25 - 0.9 * R, 0.25, 1)[..., None]

def black_hole(t, scale):
    """Dark event horizon, thin photon ring and a swirling accretion disk (blue -> violet)."""
    r = R / scale; img = np.zeros((H, W, 3), np.float32)
    rd = np.hypot((xs - CX) / W, (ys - CY) / W / 0.38) / scale; thd = np.arctan2((ys - CY) / 0.38, xs - CX)  # tilted disk
    swirl = 0.7 + 0.18 * np.sin(3 * thd + 18 * rd - 7 * t) + 0.12 * np.sin(7 * thd - 30 * rd + 11 * t)
    near = 0.75 + 0.25 * np.sin(thd)                                       # near side of the disk a little brighter
    disk = np.exp(-((rd - 0.27) / 0.1) ** 2) * swirl * near
    disk += np.exp(-((r - 0.2) / 0.05) ** 2) * 0.45 * (ys < CY)             # lensed back of the disk arching over the top
    mix = np.clip((rd - 0.15) / 0.3, 0, 1)[..., None]
    img += disk[..., None] * (np.array([0.35, 0.65, 1.0]) * (1 - mix) + np.array([0.7, 0.35, 1.0]) * mix) * 1.4
    img += (np.exp(-((r - 0.165) / 0.012) ** 2) * 1.6)[..., None] * np.array([0.85, 0.9, 1.0])   # photon ring
    img *= np.clip((r - 0.13) / 0.03, 0, 1)[..., None] * np.clip(1 - 0 * r, 0, 1)[..., None]        # horizon
    img += (np.exp(-r / 0.5) * 0.12)[..., None] * np.array([0.3, 0.2, 0.6])                        # nebula haze
    return img

ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for f in range(N):
    t = f / FPS
    jump = smooth(0.55, 1.15, t)                       # 0 = drifting toward the hole, 1 = full lightspeed
    speed = 0.6 + 26 * jump ** 2                       # z units per second
    dz = speed / FPS
    hole = black_hole(t, 1 + 2.2 * smooth(0.0, 1.1, t) ** 2) * (1 - smooth(0.7, 1.15, t))
    base = hole + (np.exp(-R / 0.18) * 0.35 * jump)[..., None] * np.array([0.5, 0.6, 1.0])          # tunnel glow
    frame = Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)

    # stars: dots that stretch into radial streaks as speed builds (pulled into a slight swirl before the jump)
    stars[:, 2] -= dz
    swirl = 0.35 * (1 - jump) / FPS
    c, s = math.cos(swirl), math.sin(swirl); stars[:, :2] = stars[:, :2] @ np.array([[c, -s], [s, c]])
    dead = stars[:, 2] < 0.15; stars[dead, 2] += 12; stars[dead, :2] = rng.normal(0, 1, (dead.sum(), 2)) * [1.4, 2.2]
    z0 = stars[:, 2]; z1 = z0 + dz * (1 + 5 * jump)    # tail = where the star was a moment ago (longer at speed)
    x0, y0 = CX + F * stars[:, 0] / z0, CY + F * stars[:, 1] / z0
    x1, y1 = CX + F * stars[:, 0] / z1, CY + F * stars[:, 1] / z1
    for i in np.argsort(-z0):
        b = min(1.0, 2.2 / z0[i]) * (0.5 + 0.5 * jump); w = max(1, int(3.2 / z0[i]))
        col = tuple(int(v) for v in star_col[i]) + (int(255 * b),)
        if jump < 0.05: d.ellipse([x0[i] - w / 2, y0[i] - w / 2, x0[i] + w / 2, y0[i] + w / 2], fill=col)
        else: d.line([(x1[i], y1[i]), (x0[i], y0[i])], fill=col, width=w)

    # coins: fly out of the centre like stars, spinning in 8-bit steps, with a short glowing smear behind
    if t > 0.45:
        coins[:, 2] -= dz * 0.75
        dead = coins[:, 2] < 0.35; coins[dead, 2] += 13; coins[dead, :2] = rng.normal(0, 1, (dead.sum(), 2)) * [1.1, 1.7]
        for i in np.argsort(-coins[:, 2]):
            z = coins[i, 2]; sx, sy = CX + F * coins[i, 0] / z, CY + F * coins[i, 1] / z
            size = int(min(W * 0.22, F * 0.16 / z)); fade = smooth(0.45, 0.8, t) * min(1, (13 - z) / 3)
            if size < 6 or not (-size < sx < W + size and -size < sy < H + size): continue
            spr = SPRITES[int(coin_phase[i] + t * coin_spd[i]) % len(SPRITES)].resize((size, size), Image.NEAREST)
            if fade < 1: a = spr.getchannel('A').point(lambda v: int(v * fade)); spr.putalpha(a)
            zt = z + dz * 0.75 * 3; tx, ty = CX + F * coins[i, 0] / zt, CY + F * coins[i, 1] / zt
            d.line([(tx, ty), (sx, sy)], fill=(255, 210, 110, int(70 * fade)), width=max(1, size // 7))
            lay.alpha_composite(spr, (int(sx - size / 2), int(sy - size / 2)))

    frame.alpha_composite(lay)
    rgb = np.asarray(frame.convert('RGB'), np.float32) / 255
    bloom = np.asarray(frame.convert('RGB').resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR), np.float32) / 255
    out = (rgb + 0.8 * bloom ** 1.4) * vign
    out = out + (1 - smooth(0.0, 0.2, t)) * 0                                          # (cut in from the page)
    flash = smooth(1.95, 2.45, t)                                                       # white-out into the token page
    core = np.exp(-R / (0.05 + 1.5 * flash ** 2))[..., None] * smooth(1.6, 2.1, t)
    out = out + core * np.array([0.9, 0.9, 1.0])
    out = out * (1 - flash) + flash * np.array([0.93, 0.92, 1.0])
    ff.stdin.write((np.clip(out, 0, 1) * 255).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait()
