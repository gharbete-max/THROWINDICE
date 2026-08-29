// One-off icon generator — renders a simple vector mark (no emoji-font
// dependency, so it rasterizes identically everywhere) to the PWA icon
// sizes via headless Chromium. Not part of the build or a persistent
// dependency — `npm install -D playwright` first, run this, then
// `npm uninstall playwright`. Only needed again if the mark changes.

import { chromium } from "playwright";
import { writeFile, mkdir } from "node:fs/promises";

const GOLD = "#e8b55c";
const BG = "#161826";
const ARC = "#c0a8f0";

// Fixed 100x100 composition (a sun peeking from behind a cloud, no emoji
// font needed), scaled to whatever pixel size via the outer <svg>. Tuned
// by eye on a 100-unit grid, not size-relative fractions — much easier to
// get proportions right that way.
function mark(maskable) {
  // Maskable icons need everything inside the inner ~80% safe circle —
  // shrink and recentre the same composition rather than redraw it.
  const s = maskable ? 0.78 : 1;
  const o = (100 - 100 * s) / 2;
  return `<g transform="translate(${o} ${o}) scale(${s})">
    <circle cx="62" cy="38" r="21" fill="${GOLD}"/>
    <rect x="20" y="52" width="60" height="26" rx="13" fill="${ARC}"/>
    <circle cx="34" cy="54" r="16" fill="${ARC}"/>
    <circle cx="56" cy="48" r="20" fill="${ARC}"/>
  </g>`;
}

function svg(size, { maskable = false } = {}) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 100 100">
    <rect width="100" height="100" fill="${BG}"/>
    ${mark(maskable)}
  </svg>`;
}

const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
await mkdir("public/icons", { recursive: true });

async function render(size, opts, outPath) {
  const page = await browser.newPage({ viewport: { width: size, height: size }, deviceScaleFactor: 1 });
  await page.setContent(`<style>html,body{margin:0;padding:0}</style>${svg(size, opts)}`);
  await page.screenshot({ path: outPath, omitBackground: false });
  await page.close();
}

await render(192, {}, "public/icons/icon-192.png");
await render(512, {}, "public/icons/icon-512.png");
await render(512, { maskable: true }, "public/icons/icon-512-maskable.png");
await writeFile("public/favicon.svg", svg(64));

await browser.close();
console.log("icons written to public/icons/, favicon.svg updated");
