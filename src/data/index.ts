// Single point where the app decides what data to render.
//
// Live on scripts/build-data's real output: .github/workflows/monthly-data.yml
// runs the free fallback-chain pipeline on the 1st of every month (or on
// demand) and commits this file with real ETF/index prices baked in.
// buildStore() copes fine with a partial run (fewer families/countries
// than usual) since every aggregate is computed over whatever's present —
// so a rough month from the data pipeline degrades the board, it doesn't
// crash it. Falls back to the mock dataset only if generated.json is ever
// completely missing (e.g. a fresh checkout before the workflow's first run).
import { buildStore } from "../lib/build";
import { MOCK_DATA } from "./mock";
import type { SourceRoot } from "./types";
import generated from "./generated.json";

const source = (generated?.families?.length ? generated : MOCK_DATA) as SourceRoot;

export const store = buildStore(source);
export type { Store } from "./built";
export type { BuiltInstrument, BuiltFamily } from "./built";
