// Copies data/facts.json into index.html between the FACTS markers, so the
// site stays one self-contained file. Run after build-data.
import { readFile, writeFile } from "node:fs/promises";
const html = new URL("../index.html", import.meta.url);
const { generatedAt, facts } = JSON.parse(await readFile(new URL("../data/facts.json", import.meta.url), "utf8"));
const block = `/*FACTS*/const FACTS=${JSON.stringify(facts)};const FACTS_AT=${JSON.stringify(generatedAt.slice(0, 10))};/*END FACTS*/`;
const s = await readFile(html, "utf8");
const out = s.replace(/\/\*FACTS\*\/[\s\S]*?\/\*END FACTS\*\//, () => block);
if (out === s && !s.includes(block)) throw new Error("FACTS markers not found in index.html");
await writeFile(html, out);
console.log(`injected ${Object.keys(facts).length} tickers`);
