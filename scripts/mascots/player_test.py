import subprocess, sys, time
from playwright.sync_api import sync_playwright
srv = subprocess.Popen([sys.executable,'-m','http.server','8769'], cwd='/home/claude/throwindice', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
try:
  with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 390, "height": 844}, has_touch=False); errs=[]
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("requestfailed", lambda r: errs.append('FAIL '+r.url))
    pg.goto("http://localhost:8769/index.html"); pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelector('.dogMascot').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
    st = lambda: pg.eval_on_selector('.dogMascot .mascot', 'e=>({t:+(e._s&&e._s.t||0).toFixed(1), v:+(e._s&&e._s.v||0).toFixed(2), fx:e.classList.contains("fx"), k:e._s&&e._s.fx&&e._s.fx.k, bg:e.querySelector(".mBase").style.backgroundImage.slice(-20)})')
    print('idle  ', st())
    bx = pg.query_selector('.dogMascot .mascot').bounding_box(); cx, cy = bx['x'] + bx['width']/2, bx['y'] + bx['height']/2
    pg.mouse.move(cx, cy); pg.mouse.down(); pg.wait_for_timeout(700); print('held  ', st()); pg.mouse.up(); pg.wait_for_timeout(50)
    print('release', st()); pg.wait_for_timeout(900); print('eased ', st())
    for k in range(3):
        pg.mouse.click(cx, cy); pg.wait_for_timeout(120); print('tap', k, st()); pg.wait_for_timeout(1300)
    print('after ', st(), 'errors:', errs)
    b.close()
finally: srv.terminate()
