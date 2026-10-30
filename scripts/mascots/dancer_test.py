import subprocess, sys, time
from playwright.sync_api import sync_playwright
srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8772'], cwd='/home/claude/throwindice', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
try:
  with sync_playwright() as p:
    b = p.chromium.launch()
    for vw, vh, tag in ((1280, 900, 'desktop'), (390, 844, 'phone')):
        ctx = b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2); ctx.add_init_script("try{localStorage.setItem('td-region','eu')}catch(e){}")
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('requestfailed', lambda r: errs.append('FAIL ' + r.url))
        pg.goto('http://localhost:8772/index.html'); pg.wait_for_timeout(1200)
        pg.evaluate("openPage('basics')"); pg.wait_for_timeout(1500)
        el = pg.query_selector('.basicsDancer'); bb = el.bounding_box(); t0 = pg.eval_on_selector('.basicsDancer', 'e=>e._s&&e._s.t')
        pg.wait_for_timeout(500); t1 = pg.eval_on_selector('.basicsDancer', 'e=>e._s&&e._s.t')
        pg.screenshot(path=f'/home/claude/d_{tag}_basics.png', clip={'x': max(0, bb['x'] - 260), 'y': max(0, bb['y'] - 20), 'width': min(vw, 400), 'height': bb['height'] + 40})
        # Token World game
        pg.evaluate("setPage('parallel')"); pg.wait_for_timeout(500)
        has = pg.evaluate("typeof navGame==='function'")
        pg.evaluate("(()=>{const b=[...document.querySelectorAll('.navbtn')].find(x=>(x.getAttribute('onclick')||'').includes('navGame'));b&&b.click()})()"); pg.wait_for_timeout(2500)
        layer = pg.evaluate("!document.getElementById('gameLayer').hidden")
        pg.screenshot(path=f'/home/claude/d_{tag}_game.png')
        sheet = pg.evaluate("!!(window._dancerSheet&&window._dancerSheet.naturalWidth)")
        print(f"{tag}: basics dancer advancing {t0 is not None and t1 != t0} | game open {layer} | dancer sheet loaded in game {sheet} | errors {errs}")
        ctx.close()
    b.close()
finally: srv.terminate()
