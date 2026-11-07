// Balance harness: plays the runner with bots and prints the economy numbers docs/BALANCE.md targets.
// Usage (repo root): node scripts/balance/sim.js [game seconds=60] [modes=passive,trader,trickster,reader] [runs=1]
// The bots fast-forward the game (60 Hz steps in a tight loop), so 300 s of play takes about 10 s. Ends with an average per bot and the BALANCE.md section 7 acceptance rows.
// Needs playwright (npm i playwright). Writes _test.html (instrumented copy) and deletes it afterwards.
// Bots are kept alive (crashes respawn) on purpose: this measures the economy, not survival skill.
const fs = require('fs'), http = require('http'), path = require('path');
const { chromium } = require('playwright');
const ROOT = path.resolve(__dirname, '../..'), TEST = path.join(ROOT, '_test.html');
const NOTICKS = process.argv[5] === 'noticks', SEC = +(process.argv[2] || 60), MODES = (process.argv[3] || 'passive,trader,trickster,reader').split(','), RUNS = +(process.argv[4] || 1);

function instrument() {
  let h = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  const inj = (a, b) => { if (h.split(a).length !== 2) throw new Error('instrument anchor not unique/found: ' + a.slice(0, 60)); h = h.replace(a, b) };
  inj('function step(dt){if(R.dead)return;', 'function step(dt){window.__R=R;if(R.dead)return;');
  inj('function bank(){', 'function bank(){(window.__L.bank=window.__L.bank||[]).push(+(R.open+R.cash).toFixed(2));(window.__L.bph=window.__L.bph||[]).push(phaseOf(Math.max(0,R.lvl-1)));');
  inj('function alpha(a){', 'function alpha(a){(window.__L.alpha=window.__L.alpha||[]).push(a);');
  inj('function slip(){', 'function slip(){(window.__L.slip=(window.__L.slip||0)+1);');
  inj('const al=.25*R.cn*R.cn;', 'const al=.25*R.cn*R.cn;(window.__L.chain=window.__L.chain||[]).push(R.cn);');
  inj('function crash(why){', 'function crash(why){(window.__L.crash=window.__L.crash||[]).push(why);if(window.__L.immortal){respawn();return}');
  inj("alpha(.25);pop(R.sx,R.y-220*VK,'PERFECT'", "alpha(.25);window.__L.perf=(window.__L.perf||0)+1;pop(R.sx,R.y-220*VK,'PERFECT'");
  h = h.replace('<script>', '<script>window.__L={};');
  fs.writeFileSync(TEST, h);
}
// (anchors above follow the code as of Nov 2026; when the scoring code changes, update them together with the change)

function serve() {
  const types = { '.html': 'text/html', '.js': 'text/javascript', '.webp': 'image/webp', '.png': 'image/png', '.svg': 'image/svg+xml', '.json': 'application/json', '.css': 'text/css', '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.woff2': 'font/woff2' };
  return new Promise(ok => { const s = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end() } r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r) }); s.listen(0, () => ok(s)) });
}

// Fast-forward bot: steps the game itself at 60 Hz in a tight loop (no waiting for animation frames), so minutes of play take seconds.
const BOT = ({ mode, sec, NT }) => {
  const K = ['cork', 'spin', 'split', 'goo'], R0 = window.__R, S = { openMin: 0, openMax: 0, capFrames: 0, pos: { long1: 0, long2: 0, short1: 0, short2: 0, cash: 0, allin: 0 }, g0: R0.t, bullAt: [] };
  window.__L.immortal = true;   // crashes respawn instead of ending the run
  let lastLvl = R0.lvl, relAt = -1, cashedLvl = -1;
  const act = i => { const R = window.__R; if (!R || R.dead) return; if (NT) R.ticks.length = 0;
    if ((!R.air && Math.random() < .35) || (R.blocked && !R.air)) { _cp.hold = true; _cp.tap(); relAt = i + Math.round((R.blocked ? .42 : .15 + Math.random() * .26) * 60) }   // hold-to-jump: random hold length, a full hold against a wall
    if (mode === 'trader' && Math.random() < .08) _cp.trick(R.open > 8 ? 'cork' : Math.random() < .5 ? 'split' : 'goo');   // take risk, move to cash when up
    if (mode === 'trickster' && R.air && Math.random() < .3) _cp.trick(K[Math.random() * 4 | 0]);
    if (mode === 'reader') {   // reads the phase: long in a bull market, short in a bear one, cash once up 8% until the next bull
      const P = R.pos;
      if (R.open > 8 && P.d !== 0) { _cp.trick('cork'); cashedLvl = R.lvl }
      else if (P.d === 0 && cashedLvl !== R.lvl) _cp.trick(R.phase === 'bull' ? 'split' : 'goo');
      else if (P.d !== 0) { if (R.phase === 'bull' && P.d < 0) _cp.trick('split'); if (R.phase === 'bear' && P.d > 0) _cp.trick('goo') }
    } };
  const dt = 1 / 60; let n = 0;
  for (let i = 0; i < sec * 60; i++) {
    const R = window.__R; if (R.dead) break;
    if (i % 7 === 0) act(i);
    if (i === relAt) _cp.release();
    _cp.step(dt); n++;
    S.openMin = Math.min(S.openMin, R.open); S.openMax = Math.max(S.openMax, R.open); if (Math.abs(R.open) >= 59.9) S.capFrames++;
    const P = R.pos, k = P.d === 0 ? 'cash' : P.allin ? 'allin' : (P.d > 0 ? 'long' : 'short') + (P.lev >= 2 ? 2 : 1); S.pos[k] += dt;
    if (R.lvl !== lastLvl) { S.bullAt.push(+(R.t - S.g0).toFixed(1)); lastLvl = R.lvl } }
  const R = window.__R, L = window.__L, ch = L.chain || [];
  const al = (L.alpha || []).reduce((a, b) => a + b, 0), bk = (L.bank || []).reduce((a, b) => a + b, 0);
  return { gameSec: +(R.t - S.g0).toFixed(1), score: R.score, V: Math.round(R.V), bulls: R.lvl, bullAt: S.bullAt, banks: L.bank || [], bankPhases: L.bph || [], bankPct: +bk.toFixed(1),
    alphaPct: +al.toFixed(1), chains: ch, perfects: L.perf || 0, slips: L.slip || 0, crashes: (L.crash || []).length,
    openMin: +S.openMin.toFixed(1), openMax: +S.openMax.toFixed(1), capFrames: S.capFrames, posSec: Object.fromEntries(Object.entries(S.pos).map(([k, v]) => [k, +v.toFixed(1)])) };
};

(async () => {
  instrument(); const srv = await serve(), port = srv.address().port, b = await chromium.launch(), all = [];
  try {
    for (let run = 0; run < RUNS; run++) for (const mode of MODES) {
      const cx = await b.newContext({ viewport: { width: 390, height: 844 } }); await cx.addInitScript(() => localStorage.setItem('cp-learn', '5')); const p = await cx.newPage(), errs = [];   // bots are experienced players
      p.on('pageerror', e => errs.push(e.message));
      await p.goto(`http://localhost:${port}/_test.html`); await p.waitForTimeout(1200);
      await p.evaluate(() => { document.querySelectorAll('.modalShade').forEach(m => m.remove()); setPage('parallel') }); await p.waitForTimeout(600);
      await p.click('.navbtn[data-page="game"]'); await p.waitForTimeout(800); await p.click('#gcGo'); await p.waitForTimeout(500);
      const r = await p.evaluate(BOT, { mode, sec: SEC, NT: NOTICKS }); r.mode = mode; r.errors = errs; all.push(r);
      const perMin = x => Math.round(x * 60 / r.gameSec);
      console.log(`${mode.padEnd(9)} score/min ${String(perMin(r.score)).padStart(4)} | bank ${String(r.bankPct).padStart(6)}% alpha ${String(r.alphaPct).padStart(5)}% (market share ${r.bankPct > 0 ? Math.round(100 * (r.bankPct - r.alphaPct) / r.bankPct) : '-'}%) | perfects/min ${perMin(r.perfects)} slips ${r.slips} | bull every ${r.bulls ? (r.gameSec / r.bulls).toFixed(1) : '-'}s | open ${r.openMin}..${r.openMax}% cap ${r.capFrames ? 'yes' : 'no'} | errors ${errs.length}`);
      { const by = { bull: [], bear: [] }; r.banks.forEach((v, i) => by[r.bankPhases[i]] && by[r.bankPhases[i]].push(v)); const av = a => a.length ? (a.reduce((x, y) => x + y, 0) / a.length).toFixed(1) : '-'; console.log(`          banks by phase: bull ${av(by.bull)}% (n=${by.bull.length}) bear ${av(by.bear)}% (n=${by.bear.length})`) }
      await p.close(); await cx.close();
    }
    fs.writeFileSync(path.join(ROOT, 'scripts/balance/last-run.json'), JSON.stringify(all, null, 1));
    // averages and the acceptance rows (BALANCE.md section 7)
    const avg = (m, f) => { const rs = all.filter(r => r.mode === m); return rs.length ? rs.reduce((s, r) => s + f(r), 0) / rs.length : NaN };
    const spm = r => r.score * 60 / r.gameSec, bi = r => { const b = r.bullAt, g = b.map((x, i) => x - (i ? b[i - 1] : 0)); return g.length ? g.reduce((a, c) => a + c, 0) / g.length : NaN };
    const share = r => r.bankPct > 0 ? 100 * (r.bankPct - r.alphaPct) / r.bankPct : NaN, ashare = r => r.bankPct > 0 ? 100 * r.alphaPct / r.bankPct : NaN;
    console.log('\n--- averages over ' + RUNS + ' run(s) of ' + SEC + ' s ---');
    const rows = [], chk = (name, v, ok, want) => rows.push(`${ok ? 'PASS' : 'FAIL'}  ${name}: ${Number.isFinite(v) ? v.toFixed(1) : '-'}  (${want})`);
    for (const m of MODES) console.log(`${m.padEnd(9)} score/min ${avg(m, spm).toFixed(0).padStart(5)} | bull gap ${avg(m, bi).toFixed(1)}s | alpha share ${avg(m, ashare).toFixed(0)}% | perfects/min ${avg(m, r => r.perfects * 60 / r.gameSec).toFixed(1)} | cap runs ${all.filter(r => r.mode === m && r.capFrames).length}/${all.filter(r => r.mode === m).length}`);
    const pass = avg('passive', spm);
    if (MODES.includes('passive')) { chk('passive score/min', pass, pass >= 20 && pass <= 60, '20-60'); chk('passive perfects/min', avg('passive', r => r.perfects * 60 / r.gameSec), avg('passive', r => r.perfects * 60 / r.gameSec) <= 6, '<= 6'); chk('passive never hits the cap', all.filter(r => r.mode === 'passive' && r.capFrames).length, !all.some(r => r.mode === 'passive' && r.capFrames), '0 runs') }
    if (MODES.includes('trader') && MODES.includes('passive')) { const v = avg('trader', spm) / pass; chk('trader / passive', v, v >= 2, '>= 2x'); chk('trader market share %', avg('trader', share), avg('trader', share) >= 60, '>= 60') }
    if (MODES.includes('reader') && MODES.includes('passive')) { const v = avg('reader', spm) / pass; chk('reader / passive', v, v >= 2, '>= 2x') }
    if (MODES.includes('trickster')) { chk('trickster alpha share %', avg('trickster', ashare), avg('trickster', ashare) >= 35 && avg('trickster', ashare) <= 55, '35-55'); const cr = all.filter(r => r.mode === 'trickster' && r.capFrames).length / Math.max(1, all.filter(r => r.mode === 'trickster').length); chk('trickster cap runs %', 100 * cr, cr <= .3, '<= 30') }
    const bis = all.map(bi).filter(Number.isFinite); if (bis.length) { const b = bis.reduce((a, c) => a + c, 0) / bis.length; chk('bull interval s', b, b >= 22 && b <= 28, '22-28') }
    chk('page errors', all.reduce((s, r) => s + r.errors.length, 0), all.every(r => r.errors.length === 0), '0');
    console.log(rows.join('\n'));
  } finally { await b.close(); srv.close(); fs.rmSync(TEST, { force: true }) }
})();
