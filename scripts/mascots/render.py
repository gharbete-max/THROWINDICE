# Re-render the 3D mascots: npm i three@0.160.0 here, then e.g. `python3 render.py pug:idle:24:640 pug:special:24:640 alien:idle:24:640 alien:special:24:640 kitten:idle:32:360`
# Frames land in frames/<char>_<mode>/; export to assets/mascots/*.webp (240px, kitten 300px, 50 ms per frame).
import sys, base64, subprocess, os, time
from playwright.sync_api import sync_playwright
srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8777'], cwd=os.path.dirname(os.path.abspath(__file__)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
# char, mode, frames, size
jobs = [a.split(':') for a in sys.argv[1:]]
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        for char, mode, n, size in jobs:
            pg = b.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
            pg.goto(f'http://localhost:8777/scene.html?char={char}&size={size}')
            pg.wait_for_function('window.ready===true', timeout=60000)
            out = f'frames/{char}_{mode}'; os.makedirs(out, exist_ok=True)
            n = int(n); t0 = time.time()
            for i in range(n):
                url = pg.evaluate(f'frame({i}/{n}, {str(mode=="special").lower()})')
                open(f'{out}/{i:03d}.png', 'wb').write(base64.b64decode(url.split(',')[1]))
            print(char, mode, n, 'frames', round(time.time() - t0, 1), 's', errs[:3])
            pg.close()
        b.close()
finally:
    srv.terminate()
