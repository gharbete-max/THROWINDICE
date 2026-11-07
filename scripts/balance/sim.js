// Balance harness: plays the runner with bots and prints the economy numbers docs/BALANCE.md targets.
// Usage (repo root): node scripts/balance/sim.js [seconds=60] [modes=passive,trader,trickster] [runs=1]
// Needs playwright (npm i playwright). Writes _test.html (instrumented copy) and deletes it afterwards.
// Bots are kept alive (shield every tick) on purpose: this measures the economy, not survival skill.
const fs = require('fs'), http = require('http'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.resolve(__dirname, '../..'), TEST = path.join(ROOT, '_test.html');
const SEC = +(process.argv[2] || 60), MODES = (process.argv[3] || 'passive,trader,trickster').split(','), RUNS = +(process.argv[4] || 1);

function instrument() {
  let h = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  const inj = (a, b) => { if (h.split(a).length !== 2) throw new Error('instrument anchor not unique/found: ' + a.slice(0, 60)); h = h.replace(a, b) };
  inj('function step(dt){if(R.dead)return;', 'function step(dt){window.__R=R;if(R.dead)return;');
  inj('function bank(){', 'function bank(){(window.__L.bank=window.__L.bank||[]).push(+(R.open+R.cash).toFixed(2));');
  inj('const pts=3*R.cn*R.cn;R.score+=pts;', 'const pts=3*R.cn*R.cn;R.score+=pts;(window.__L.chain=window.__L.chain||[]).push(R.cn);');
  inj('function crash(why){', 'function crash(why){(window.__L.crash=window.__L.crash||[]).push(why);');
  inj("R.score+=2;pop(R.sx,R.y-220*VK,'PERFECT'", "R.score+=2;window.__L.perf=(window.__L.perf||0)+1;pop(R.sx,R.y-220*VK,'PERFECT'");
  h = h.replace('<script>', '<script>window.__L={};');
  fs.writeFileSync(TEST, h);
}
// (anchors above follow the code as of Nov 2026; when the scoring code changes, update them together with the change)

function serve() {
  const types = { '.html': 'text/html', '.js': 'text/javascript', '.webp': 'image/webp', '.png': 'image/png', '.svg': 'image/svg+xml', '.json': 'application/json', '.css': 'text/css', '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.woff2': 'font/woff2' };
  return new Promise(ok => { const s = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end() } r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r) }); s.listen(0, () => ok(s)) });
}

const BOT = ({ mode, sec }) => new Promise(done => {
  const K = ['cork', 'spin', 'split', 'goo'], t0 = performance.now(), R0 = window.__R, S = { openMin: 0, openMax: 0, capFrames: 0, pos: { long1: 0, long2: 0, short1: 0, short2: 0, cash: 0, allin: 0 }, g0: R0.t, bullAt: [] };
  let lastLvl = R0.lvl, lastT = performance.now();
  const act = setInterval(() => { const R = window.__R; if (!R || R.dead) return; R.shield = true;
    if (!R.air && Math.random() < .35) _cp.tap();
    if (mode === 'trader' && Math.random() < .08) _cp.trick(R.open > 8 ? 'cork' : Math.random() < .5 ? 'split' : 'goo');   // take risk, move to cash when up
    if (mode === 'trickster' && R.air && Math.random() < .3) _cp.trick(K[Math.random() * 4 | 0]);
  }, 120);
  const fr = () => { const R = window.__R, now = performance.now();
    if (R && !R.dead) { S.openMin = Math.min(S.openMin, R.open); S.openMax = Math.max(S.openMax, R.open); if (Math.abs(R.open) >= 59.9) S.capFrames++;
      const P = R.pos, k = P.d === 0 ? 'cash' : P.allin ? 'allin' : (P.d > 0 ? 'long' : 'short') + (P.lev >= 2 ? 2 : 1); S.pos[k] += (now - lastT) / 1000;
      if (R.lvl !== lastLvl) { S.bullAt.push(+(R.t - S.g0).toFixed(1)); lastLvl = R.lvl } }
    lastT = now;
    if (now - t0 < sec * 1000 && !(R && R.dead)) return requestAnimationFrame(fr);
    clearInterval(act); const L = window.__L, ch = L.chain || [];
    done({ gameSec: +(R.t - S.g0).toFixed(1), score: R.score, bulls: R.lvl, bullAt: S.bullAt, banks: L.bank || [], bankPts: Math.round((L.bank || []).reduce((a, b) => a + b, 0)),
      chainPts: ch.reduce((a, n) => a + 3 * n * n, 0), chains: ch, perfects: L.perf || 0, crashes: (L.crash || []).length,
      openMin: +S.openMin.toFixed(1), openMax: +S.openMax.toFixed(1), capFrames: S.capFrames, posSec: Object.fromEntries(Object.entries(S.pos).map(([k, v]) => [k, +v.toFixed(1)])) });
  };
  requestAnimationFrame(fr);
});

(async () => {
  instrument(); const srv = await serve(), port = srv.address().port, b = await chromium.launch(), all = [];
  try {
    for (let run = 0; run < RUNS; run++) for (const mode of MODES) {
      const p = await b.newPage({ viewport: { width: 390, height: 844 } }), errs = [];
      p.on('pageerror', e => errs.push(e.message));
      await p.goto(`http://localhost:${port}/_test.html`); await p.waitForTimeout(1200);
      await p.evaluate(() => { document.querySelectorAll('.modalShade').forEach(m => m.remove()); setPage('parallel') }); await p.waitForTimeout(600);
      await p.click('.navbtn[data-page="game"]'); await p.waitForTimeout(800); await p.click('#gcGo'); await p.waitForTimeout(500);
      const r = await p.evaluate(BOT, { mode, sec: SEC }); r.mode = mode; r.errors = errs; all.push(r);
      const perMin = x => Math.round(x * 60 / r.gameSec);
      console.log(`${mode.padEnd(9)} score/min ${String(perMin(r.score)).padStart(4)} | bank ${String(perMin(r.bankPts)).padStart(4)} chain ${String(perMin(r.chainPts)).padStart(4)} perfect ${String(perMin(2 * r.perfects)).padStart(4)} | bull every ${r.bulls ? (r.gameSec / r.bulls).toFixed(1) : '-'}s | open ${r.openMin}..${r.openMax}% | errors ${errs.length}`);
      await p.close();
    }
    fs.writeFileSync(path.join(ROOT, 'scripts/balance/last-run.json'), JSON.stringify(all, null, 1));
  } finally { await b.close(); srv.close(); fs.rmSync(TEST, { force: true }) }
})();
