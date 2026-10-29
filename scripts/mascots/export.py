"""Turn rendered frames into site WebPs (transparent) and preview GIFs."""
import os, subprocess, json
from PIL import Image
F, OUT, SITE = '/home/claude/bl/frames', '/home/claude/bl/out', '/home/claude/throwindice/assets/mascots'
os.makedirs(OUT, exist_ok=True); os.makedirs(SITE, exist_ok=True)

import numpy as np
def edge_fade(im):
    """Fade alpha near the left/right/bottom borders so floor shadows don't end in a hard edge."""
    a = np.asarray(im).astype(np.float32); n = a.shape[0]; r = np.linspace(0, 1, n)
    fx = np.clip(np.minimum(r, 1 - r) / 0.16, 0, 1); fy = np.clip((1 - r) / 0.1, 0, 1)
    a[..., 3] *= (fx[None, :] * fy[:, None]) ** 1.5; return Image.fromarray(a.astype(np.uint8))

def load(name, size):
    d = f'{F}/{name}'; fr = [Image.open(f'{d}/{f}').convert('RGBA').resize((size, size), Image.LANCZOS) for f in sorted(os.listdir(d))]
    return fr if name.startswith('kitten') else [edge_fade(im) for im in fr]

def webp(frames, path, ms):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=ms, loop=0, quality=86, method=6)

def gif(frames, path, fps):
    tmp = path + '_tmp'; os.makedirs(tmp, exist_ok=True)
    for i, im in enumerate(frames):
        bg = Image.new('RGBA', im.size, (238, 234, 252, 255)); bg.alpha_composite(im); bg.convert('RGB').save(f'{tmp}/{i:03d}.png')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', str(fps), '-i', f'{tmp}/%03d.png', '-vf',
                    'split[a][b];[a]palettegen=max_colors=240:stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a', '-loop', '0', path], check=True)

for char, idle, special in (('pug', 'pug_idle', 'pug_special'), ('alien', 'alien_idle', 'alien_special'), ('kitten', 'kitten_hang', None)):
    if not os.path.isdir(f'{F}/{idle}'): continue
    size = 240
    fr = load(idle, size); webp(fr, f'{SITE}/{char}-idle.webp', 62); fr[0].save(f'{SITE}/{char}-still.webp', quality=88, method=6)
    if special and os.path.isdir(f'{F}/{special}'): webp(load(special, size), f'{SITE}/{char}-move.webp', 62)
    big = load(idle, 320)
    if special and os.path.isdir(f'{F}/{special}'): big = big + load(idle, 320) + load(special, 320)  # preview: two loops then the click move
    gif(big, f'{OUT}/{char}-dance.gif', 16)
    print(char, {f: os.path.getsize(f'{SITE}/{f}') // 1024 for f in os.listdir(SITE) if f.startswith(char)})
print(json.load(open('/home/claude/bl/kitten_frame.json')))

def sheet(frames, path, cols=8, size=200):
    """Pack frames into a grid (cols wide) for the site's sprite player, which can vary playback speed."""
    rows = -(-len(frames) // cols); S = Image.new('RGBA', (cols * size, rows * size), (0, 0, 0, 0))
    for i, f in enumerate(frames): S.alpha_composite(f.resize((size, size), Image.LANCZOS), ((i % cols) * size, (i // cols) * size))
    S.save(path, quality=84, method=6); return len(frames), rows

def export_dancers():
    """Dance loop + three tap specials per dancer, as sprite sheets, plus a still and a preview GIF."""
    for c in ('pug', 'alien'):
        dance = load(f'{c}_idle', 240); dance[0].save(f'{SITE}/{c}-still.webp', quality=88, method=6)
        info = {'dance': sheet(dance, f'{SITE}/{c}-dance.webp')}
        for mode, name in (('special', 'spin'), ('flip', 'flip'), ('pose', 'pose')):
            info[name] = sheet(load(f'{c}_{mode}', 240), f'{SITE}/{c}-{name}.webp')
        big = load(f'{c}_idle', 360)
        gif(big + load(f'{c}_special', 360) + load(f'{c}_flip', 360) + load(f'{c}_pose', 360), f'{OUT}/{c}-dance.gif', 24)
        print(c, info, {f: os.path.getsize(f'{SITE}/{f}') // 1024 for f in os.listdir(SITE) if f.startswith(c)})
