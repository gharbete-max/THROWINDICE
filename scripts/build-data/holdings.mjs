// Top-10 holdings + concentration per fund -> data/holdings.json (stockanalysis.com, no key).
// Usage: node scripts/build-data/holdings.mjs   (reads fund tickers from index.html's TIER table)
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
// curl, not fetch: Node's fetch ignores HTTPS_PROXY
const get = u => execFileSync('curl', ['-sf', '-m', '25', u], { encoding: 'utf8', maxBuffer: 1 << 26 });
const html = fs.readFileSync('index.html', 'utf8');
const tiers = html.match(/const TIER=(\{[^}]*\})/)[1];
const ids = Object.keys(JSON.parse(tiers));
const clean = s => s.replace(/<!--.*?-->/gs, '').replace(/&amp;/g, '&').replace(/&#39;/g, "'");
const out = {};
for (const t of ids) {
  try {
    const h = clean(get(`https://stockanalysis.com/etf/${t.toLowerCase()}/holdings/`));
    const n = +(h.match(/Total Holdings\s*<div[^>]*>([\d,]+)</)?.[1] || '').replace(/,/g, '') || null;
    const top = parseFloat(h.match(/Top 10 Percentage\s*<div[^>]*>([\d.]+)%/)?.[1]);
    const rows = [...h.matchAll(/<tr[^>]*><td[^>]*>\d+<\/td><td[^>]*class="sym[^"]*"[^>]*>(?:<a[^>]*>)?([^<]*)(?:<\/a>)?<\/td><td[^>]*>([^<]*)<\/td><td[^>]*>([\d.]+)%<\/td>/g)]
      .slice(0, 10).map(m => [m[1].trim(), m[2].trim(), +m[3]]);
    if (!rows.length) continue;
    out[t] = { n, top10: isNaN(top) ? +rows.reduce((a, x) => a + x[2], 0).toFixed(2) : top, h: rows };
  } catch (e) { /* skip */ }
  await new Promise(r => setTimeout(r, 250));
}
fs.writeFileSync('data/holdings.json', JSON.stringify({ asOf: new Date().toISOString().slice(0, 10), from: 'stockanalysis.com', t: out }));
console.log(Object.keys(out).length, 'of', ids.length);
