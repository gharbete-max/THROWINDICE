"""Turn rendered frames into site WebPs (transparent) and preview GIFs."""
import os, subprocess, json
from PIL import Image
F, OUT, SITE = '/home/claude/bl/frames', '/home/claude/bl/out', '/home/claude/throwindice/assets/mascots'
os.makedirs(OUT, exist_ok=True); os.makedirs(SITE, exist_ok=True)

def load(name, size):
    d = f'{F}/{name}'; return [Image.open(f'{d}/{f}').convert('RGBA').resize((size, size), Image.LANCZOS) for f in sorted(os.listdir(d))]

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
