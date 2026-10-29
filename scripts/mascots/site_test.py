"""End-to-end check of the merged site: dancers (hold/tap), slider kitten scare, smiley spin, portal video. Phone + desktop."""
import subprocess, sys, time
from playwright.sync_api import sync_playwright
srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8770'], cwd='/home/claude/throwindice', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
show = "sel=>{const el=document.querySelector(sel);const pg=el&&el.closest('section.page');if(pg&&getComputedStyle(pg).display==='none'){(window.openPage||setPage)(pg.id);if(getComputedStyle(pg).display==='none')pg.classList.add('active')}setTimeout(()=>el.scrollIntoView({block:'center'}),50)}"
try:
  with sync_playwright() as p:
    b = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    for vw, vh, tag in ((1280, 900, 'desktop'), (390, 844, 'phone')):
        ctx = b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2); ctx.add_init_script("try{localStorage.setItem('td-region','eu')}catch(e){}")
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('requestfailed', lambda r: errs.append('FAIL ' + r.url))
        pg.goto('http://localhost:8770/index.html'); pg.wait_for_timeout(1500)
        # pug: dance, hold, tap
        pg.evaluate(show, '.dogMascot'); pg.wait_for_timeout(600)
        st = lambda: pg.eval_on_selector('.dogMascot .mascot', 'e=>({v:+(e._s?e._s.v:0).toFixed(2),fx:e.classList.contains("fx"),k:e._s&&e._s.fx&&e._s.fx.k})')
        bx = pg.query_selector('.dogMascot .mascot').bounding_box(); cx, cy = bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2
        pg.mouse.move(cx, cy); pg.mouse.down(); pg.wait_for_timeout(700); held = st(); pg.mouse.up(); pg.wait_for_timeout(1200)
        pg.mouse.click(cx, cy); pg.wait_for_timeout(150); tap = st()
        pg.screenshot(path=f'/home/claude/m_{tag}_pug.png', clip={'x': max(0, bx['x'] - 20), 'y': max(0, bx['y'] - 20), 'width': bx['width'] + 40, 'height': bx['height'] + 40})
        # slider kitten scare
        pg.evaluate(show, '.kitty'); pg.wait_for_timeout(600); ib = pg.query_selector('.kitty input').bounding_box(); y = ib['y'] + ib['height'] / 2
        pg.mouse.move(ib['x'] + ib['width'] * 0.3, y); pg.mouse.down(); pg.mouse.move(ib['x'] + ib['width'] + 40, y, steps=4)
        sc = []
        for k in range(8): pg.wait_for_timeout(80); sc.append(pg.eval_on_selector('.kitty .kCat', 'c=>c.classList.contains("scared")'))
        pg.mouse.up()
        # smiley hover spin
        pg.hover('.tokenCoin'); pg.wait_for_timeout(200); spin = pg.eval_on_selector('.tokenCoin .coin-normal', 'i=>i.src.split("/").pop()'); pg.mouse.move(2, 2)
        # portal video into Token World, then the alien dancer there
        pg.click('.tokenCoin'); pg.wait_for_timeout(900)
        vid = pg.eval_on_selector('#portalOverlay', 'o=>o.classList.contains("video")&&!o.querySelector("video").paused')
        pg.wait_for_timeout(2200); token = pg.evaluate("document.body.classList.contains('token-world')")
        pg.evaluate(show, '.alienCat'); pg.wait_for_timeout(500)
        alien = pg.eval_on_selector('.alienCat .mBase', 'e=>e.style.background.includes("alien-dance")')
        ab = pg.query_selector('.alienRow').bounding_box(); pg.screenshot(path=f'/home/claude/m_{tag}_alien.png', clip={'x': ab['x'], 'y': ab['y'], 'width': min(ab['width'], vw - ab['x']), 'height': ab['height'] + 20})
        print(f"{tag}: pug hold speed {held['v']} | tap -> {tap['k']} | kitten scared {''.join('S' if v else '.' for v in sc)} | smiley hover {spin} | portal video playing {vid} | in Token World {token} | alien dancing {alien} | errors {errs}")
        ctx.close()
    b.close()
finally: srv.terminate()
